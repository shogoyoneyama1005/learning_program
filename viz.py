"""
Visualization module for automatic chart generation based on data patterns.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional


def detect_chart_type(df: pd.DataFrame) -> str:
    """
    Detect the most appropriate chart type for the given DataFrame.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Chart type string ('bar', 'line', 'pie', 'scatter', 'none')
    """
    if df.empty:
        return 'none'
    
    # Count numeric and categorical columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Handle month column as time series
    time_cols = []
    for col in categorical_cols:
        if col.lower() in ['month', 'date'] or df[col].dtype == 'datetime64[ns]':
            time_cols.append(col)
    
    # Remove time columns from categorical
    categorical_cols = [col for col in categorical_cols if col not in time_cols]
    
    # Chart selection logic
    if len(numeric_cols) >= 1:
        if len(time_cols) >= 1:
            # Time series data -> line chart
            return 'line'
        elif len(categorical_cols) >= 1:
            if len(categorical_cols) == 1 and len(df) <= 10:
                # Single category with few items -> pie chart
                return 'pie'
            else:
                # Category with numeric -> bar chart
                return 'bar'
        elif len(numeric_cols) >= 2:
            # Two numeric columns -> scatter plot
            return 'scatter'
    
    return 'bar'  # Default to bar chart


def create_bar_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Create a bar chart from DataFrame.
    
    Args:
        df: DataFrame with data to plot
        
    Returns:
        Plotly figure or None if creation fails
    """
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if not numeric_cols or not categorical_cols:
            return None
        
        x_col = categorical_cols[0]
        y_col = numeric_cols[0]
        
        # Handle multiple categories by creating grouped bar chart
        if len(categorical_cols) > 1:
            color_col = categorical_cols[1] if len(categorical_cols) > 1 else None
            fig = px.bar(df, x=x_col, y=y_col, color=color_col,
                        title=f"{y_col} by {x_col}" + (f" and {color_col}" if color_col else ""))
        else:
            fig = px.bar(df, x=x_col, y=y_col,
                        title=f"{y_col} by {x_col}")
        
        fig.update_layout(xaxis_tickangle=-45)
        return fig
        
    except Exception as e:
        st.warning(f"Failed to create bar chart: {str(e)}")
        return None


def create_line_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Create a line chart from DataFrame.
    
    Args:
        df: DataFrame with time series data
        
    Returns:
        Plotly figure or None if creation fails
    """
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Find time column
        time_col = None
        for col in categorical_cols:
            if col.lower() in ['month', 'date']:
                time_col = col
                break
        
        if not time_col or not numeric_cols:
            return None
        
        y_col = numeric_cols[0]
        
        # Check if we have multiple series (categories)
        other_cats = [col for col in categorical_cols if col != time_col]
        
        if other_cats:
            # Multiple series line chart
            color_col = other_cats[0]
            fig = px.line(df, x=time_col, y=y_col, color=color_col,
                         title=f"{y_col} over {time_col} by {color_col}",
                         markers=True)
        else:
            # Single series line chart
            fig = px.line(df, x=time_col, y=y_col,
                         title=f"{y_col} over {time_col}",
                         markers=True)
        
        fig.update_layout(xaxis_tickangle=-45)
        return fig
        
    except Exception as e:
        st.warning(f"Failed to create line chart: {str(e)}")
        return None


def create_pie_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Create a pie chart from DataFrame.
    
    Args:
        df: DataFrame with categorical data
        
    Returns:
        Plotly figure or None if creation fails
    """
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if not numeric_cols or not categorical_cols:
            return None
        
        labels_col = categorical_cols[0]
        values_col = numeric_cols[0]
        
        fig = px.pie(df, names=labels_col, values=values_col,
                    title=f"{values_col} by {labels_col}")
        
        return fig
        
    except Exception as e:
        st.warning(f"Failed to create pie chart: {str(e)}")
        return None


def create_scatter_plot(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Create a scatter plot from DataFrame.
    
    Args:
        df: DataFrame with numeric data
        
    Returns:
        Plotly figure or None if creation fails
    """
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(numeric_cols) < 2:
            return None
        
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        
        # Use category for color if available
        color_col = categorical_cols[0] if categorical_cols else None
        
        if color_col:
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                           title=f"{y_col} vs {x_col} by {color_col}")
        else:
            fig = px.scatter(df, x=x_col, y=y_col,
                           title=f"{y_col} vs {x_col}")
        
        return fig
        
    except Exception as e:
        st.warning(f"Failed to create scatter plot: {str(e)}")
        return None


def auto_chart(df: pd.DataFrame) -> None:
    """
    Automatically generate and display appropriate chart for the DataFrame.
    
    Args:
        df: DataFrame to visualize
    """
    if df.empty:
        st.warning("No data to visualize.")
        return
    
    # Detect chart type
    chart_type = detect_chart_type(df)
    
    if chart_type == 'none':
        st.info("No suitable chart type detected for this data.")
        return
    
    # Create appropriate chart
    fig = None
    
    if chart_type == 'bar':
        fig = create_bar_chart(df)
    elif chart_type == 'line':
        fig = create_line_chart(df)
    elif chart_type == 'pie':
        fig = create_pie_chart(df)
    elif chart_type == 'scatter':
        fig = create_scatter_plot(df)
    
    # Display chart
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"Could not create {chart_type} chart for this data.")


def display_data_with_chart(df: pd.DataFrame, title: str = "Results") -> None:
    """
    Display DataFrame and automatically generated chart.
    
    Args:
        df: DataFrame to display
        title: Title for the data display
    """
    if df.empty:
        st.warning("No data to display.")
        return
    
    # Display the data table
    st.subheader(f"📊 {title}")
    st.dataframe(df, use_container_width=True)
    
    # Display chart if data is suitable
    if len(df) > 0:
        st.subheader("📈 Visualization")
        auto_chart(df)