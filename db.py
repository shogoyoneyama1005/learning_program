import pandas as pd
import duckdb
from typing import Any
import streamlit as st


@st.cache_resource
def init_db(csv_path: str = "data/sample_sales.csv") -> Any:
    """
    Initialize DuckDB connection and create the sales table with derived month column.
    
    Args:
        csv_path: Path to the CSV file containing sales data
        
    Returns:
        DuckDB connection object
    """
    try:
        # Read CSV data
        df = pd.read_csv(csv_path)
        
        # Create DuckDB connection
        con = duckdb.connect(":memory:")
        
        # Add month column (YYYY-MM format)
        df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
        
        # Create table in DuckDB
        con.execute("CREATE TABLE sales AS SELECT * FROM df")
        
        return con
        
    except Exception as e:
        st.error(f"Failed to initialize database: {str(e)}")
        return None


def query_df(con: Any, sql: str) -> pd.DataFrame:
    """
    Execute SQL query and return results as DataFrame.
    
    Args:
        con: DuckDB connection object
        sql: SQL query string to execute
        
    Returns:
        DataFrame containing query results
    """
    try:
        if con is None:
            raise Exception("Database connection is not initialized")
            
        result = con.execute(sql).fetchdf()
        return result
        
    except Exception as e:
        st.error(f"Failed to execute query: {str(e)}")
        return pd.DataFrame()


def get_data_summary(con: Any) -> dict:
    """
    Get summary information about the sales data.
    
    Args:
        con: DuckDB connection object
        
    Returns:
        Dictionary containing summary statistics
    """
    if con is None:
        return {}
        
    try:
        summary = {}
        
        # Total records
        total_records = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        summary['total_records'] = total_records
        
        # Date range
        date_range = con.execute("SELECT MIN(date) as min_date, MAX(date) as max_date FROM sales").fetchone()
        summary['date_range'] = {
            'min_date': date_range[0],
            'max_date': date_range[1]
        }
        
        # Categories
        categories = con.execute("SELECT DISTINCT category FROM sales ORDER BY category").fetchall()
        summary['categories'] = [cat[0] for cat in categories]
        
        # Regions
        regions = con.execute("SELECT DISTINCT region FROM sales ORDER BY region").fetchall()
        summary['regions'] = [region[0] for region in regions]
        
        # Sales channels
        channels = con.execute("SELECT DISTINCT sales_channel FROM sales ORDER BY sales_channel").fetchall()
        summary['sales_channels'] = [channel[0] for channel in channels]
        
        # Customer segments
        segments = con.execute("SELECT DISTINCT customer_segment FROM sales ORDER BY customer_segment").fetchall()
        summary['customer_segments'] = [segment[0] for segment in segments]
        
        # Total revenue
        total_revenue = con.execute("SELECT SUM(revenue) FROM sales").fetchone()[0]
        summary['total_revenue'] = total_revenue
        
        return summary
        
    except Exception as e:
        st.error(f"Failed to get data summary: {str(e)}")
        return {}