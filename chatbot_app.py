"""
Sales Data Analysis AI Chatbot
A Streamlit application for analyzing sales data using natural language queries.
"""

import streamlit as st
import pandas as pd
import traceback

# Import our custom modules
from db import init_db, query_df, get_data_summary
from llm_sql_openai import process_sql_query
from fallbacks import find_best_fallback
from viz import display_data_with_chart


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "db_connection" not in st.session_state:
        st.session_state.db_connection = None
    if "data_summary" not in st.session_state:
        st.session_state.data_summary = {}


def setup_database():
    """Setup database connection and load data."""
    if st.session_state.db_connection is None:
        with st.spinner("Loading sales data..."):
            st.session_state.db_connection = init_db()
            if st.session_state.db_connection:
                st.session_state.data_summary = get_data_summary(st.session_state.db_connection)
                st.success("✅ Database loaded successfully!")
                
                # Check API key status
                import os
                if not os.getenv("OPENAI_API_KEY"):
                    st.info("💡 To enable AI-powered SQL generation, set your OPENAI_API_KEY environment variable. For now, the app will use predefined queries.")
            else:
                st.error("❌ Failed to load database")
                st.stop()


def display_sidebar():
    """Display sidebar with data summary and information."""
    with st.sidebar:
        st.header("📊 Data Overview")
        
        if st.session_state.data_summary:
            summary = st.session_state.data_summary
            
            # Basic statistics
            st.metric("Total Records", f"{summary.get('total_records', 0):,}")
            st.metric("Total Revenue", f"¥{summary.get('total_revenue', 0):,}")
            
            # Date range
            if 'date_range' in summary:
                st.write("**Period:**")
                date_range = summary['date_range']
                st.write(f"{date_range['min_date']} to {date_range['max_date']}")
            
            # Categories
            if summary.get('categories'):
                st.write("**Categories:**")
                for cat in summary['categories']:
                    st.write(f"• {cat}")
            
            # Regions
            if summary.get('regions'):
                st.write("**Regions:**")
                for region in summary['regions']:
                    st.write(f"• {region}")
            
            # Sales channels
            if summary.get('sales_channels'):
                st.write("**Sales Channels:**")
                for channel in summary['sales_channels']:
                    st.write(f"• {channel}")
            
            # Customer segments
            if summary.get('customer_segments'):
                st.write("**Customer Segments:**")
                for segment in summary['customer_segments']:
                    st.write(f"• {segment}")
        
        st.divider()
        
        # API Status
        import os
        if os.getenv("OPENAI_API_KEY"):
            st.success("🤖 AI SQL Generation: Enabled (ChatGPT)")
        else:
            st.warning("🤖 AI SQL Generation: Disabled")
            st.caption("Set OPENAI_API_KEY to enable")
        
        st.divider()
        
        # Sample questions
        st.header("💡 Sample Questions")
        sample_questions = [
            "月ごとのカテゴリ別売上を見せて",
            "チャネル別の売上合計は？",
            "地域ごとの売上を教えて",
            "2025年1月の売上トップ3カテゴリは？",
            "平均単価をチャネル別に分析して"
        ]
        
        for i, question in enumerate(sample_questions):
            if st.button(question, key=f"sample_btn_{i}"):
                st.success(f"✅ Processing: {question}")
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": question})
                
                # Immediately process the question (like in button_test.py)
                try:
                    # Import required functions for processing
                    from llm_sql_openai import process_sql_query
                    from fallbacks import find_best_fallback
                    from db import query_df
                    from viz import display_data_with_chart
                    
                    # Process question
                    sql, is_generated = process_sql_query(question)
                    
                    # If SQL generation failed, use fallback
                    if not is_generated or not sql.strip():
                        fallback_name, fallback_sql = find_best_fallback(question)
                        sql = fallback_sql
                        st.info(f"🔄 Using fallback query: {fallback_name}")
                    else:
                        st.success("✅ SQL generated successfully!")
                    
                    # Display the SQL query
                    with st.expander("🔍 View SQL Query", expanded=False):
                        st.code(sql, language="sql")
                    
                    # Execute the query
                    with st.spinner("Executing query..."):
                        result_df = query_df(st.session_state.db_connection, sql)
                    
                    st.write(f"📊 Query returned {len(result_df)} rows")
                    
                    if not result_df.empty:
                        # Display results with visualization
                        display_data_with_chart(result_df, "Query Results")
                        
                        # Add some insights
                        st.subheader("🎯 Key Insights")
                        insights = generate_insights(result_df, question)
                        for insight in insights:
                            st.write(f"• {insight}")
                    else:
                        st.warning("⚠️ No data found for your query.")
                    
                    # Add success message to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"✅ Successfully analyzed: {question}"
                    })
                    
                except Exception as e:
                    st.error(f"❌ Error processing question: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"❌ Error processing: {question} - {str(e)}"
                    })
                    
                # Force rerun to update the display
                st.rerun()


def process_user_question(question: str):
    """
    Process user question and generate response with data visualization.
    
    Args:
        question: User's natural language question
    """
    try:
        # Add debug output
        st.write(f"🔍 Processing question: {question}")
        
        # Try to generate SQL
        with st.spinner("Generating SQL query..."):
            st.write("🤖 Connecting to OpenAI...")
            sql, is_generated = process_sql_query(question)
            st.write("📝 SQL generation complete")
        
        # If SQL generation failed, use fallback
        if not is_generated or not sql.strip():
            fallback_name, fallback_sql = find_best_fallback(question)
            sql = fallback_sql
            st.info(f"🔄 Using fallback query: {fallback_name}")
        else:
            st.success("✅ SQL generated successfully!")
        
        # Display the SQL query in an expander
        with st.expander("🔍 View SQL Query", expanded=False):
            st.code(sql, language="sql")
        
        # Execute the query
        with st.spinner("Executing query..."):
            result_df = query_df(st.session_state.db_connection, sql)
        
        st.write(f"📊 Query returned {len(result_df)} rows")
        
        if result_df.empty:
            st.warning("⚠️ No data found for your query. Try rephrasing your question or being more specific.")
            return
        
        # Display results with visualization
        display_data_with_chart(result_df, "Query Results")
        
        # Add some insights
        st.subheader("🎯 Key Insights")
        if len(result_df) > 0:
            insights = generate_insights(result_df, question)
            for insight in insights:
                st.write(f"• {insight}")
    
    except Exception as e:
        st.error(f"❌ Error processing your question: {str(e)}")
        
        # Try fallback as last resort
        try:
            st.info("🔄 Attempting fallback query...")
            fallback_name, fallback_sql = find_best_fallback(question)
            
            with st.expander("🔍 View Fallback SQL Query", expanded=False):
                st.code(fallback_sql, language="sql")
            
            result_df = query_df(st.session_state.db_connection, fallback_sql)
            
            if not result_df.empty:
                display_data_with_chart(result_df, f"Fallback Results: {fallback_name}")
            else:
                st.error("❌ Fallback query also returned no results.")
                
        except Exception as fallback_error:
            st.error(f"❌ Fallback also failed: {str(fallback_error)}")
            if st.checkbox("Show detailed error information"):
                st.text(traceback.format_exc())


def generate_insights(df: pd.DataFrame, question: str = None) -> list:
    """
    Generate simple insights from the query results.
    
    Args:
        df: Query results DataFrame
        question: Original user question (unused, kept for future enhancement)
        
    Returns:
        List of insight strings
    """
    insights = []
    
    try:
        # Basic insights
        insights.append(f"Found {len(df)} records matching your query")
        
        # Numeric column insights
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        for col in numeric_cols:
            if col.lower() in ['revenue', 'total_revenue']:
                total_revenue = df[col].sum()
                avg_revenue = df[col].mean()
                insights.append(f"Total revenue: ¥{total_revenue:,.0f}")
                insights.append(f"Average revenue: ¥{avg_revenue:,.0f}")
                
                if len(df) > 1:
                    max_idx = df[col].idxmax()
                    max_row = df.loc[max_idx]
                    insights.append(f"Highest revenue: {max_row.iloc[0] if len(df.columns) > 1 else 'N/A'} (¥{df[col].max():,.0f})")
            
            elif col.lower() in ['units', 'total_units']:
                total_units = df[col].sum()
                insights.append(f"Total units sold: {total_units:,}")
        
        # If data has multiple rows, mention the range
        if len(df) > 1:
            insights.append(f"Data spans {len(df)} different categories/periods")
    
    except Exception:
        # If insight generation fails, just provide basic info
        insights = [f"Successfully retrieved {len(df)} records"]
    
    return insights


def display_chat_interface():
    """Display the main chat interface."""
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and message["content"].startswith("✅ Successfully analyzed:"):
                # Skip the success message in display as the actual response is shown above
                continue
            else:
                st.markdown(message["content"])
    
    # Handle new user input (sample questions are handled in sidebar)
    if prompt := st.chat_input("Ask me anything about the sales data..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            try:
                process_user_question(prompt)
                # Add success message to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"✅ Successfully analyzed: {prompt}"
                })
            except Exception as e:
                st.error(f"Failed to process question: {str(e)}")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"❌ Error processing: {prompt} - {str(e)}"
                })


def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title="Sales Data Analysis Chatbot",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Clear any potential session state issues
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
    
    # Initialize session state
    initialize_session_state()
    
    # Setup database
    setup_database()
    
    # Main header
    st.title("🤖 Sales Data Analysis AI Chatbot")
    st.markdown("""
    Ask me anything about your sales data in natural language! 
    I can analyze trends, compare categories, and provide insights with visualizations.
    """)
    
    # Display sidebar
    display_sidebar()
    
    # Main chat interface
    st.header("💬 Chat with Your Data")
    display_chat_interface()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    🔒 All queries are limited to SELECT operations for data safety.<br/>
    📊 Powered by ChatGPT, DuckDB, and Streamlit
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()