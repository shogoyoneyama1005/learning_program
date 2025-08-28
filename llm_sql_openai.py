import os
import re
from typing import Optional
import streamlit as st
from openai import OpenAI


def get_openai_client() -> Optional[OpenAI]:
    """Get OpenAI client with API key from environment or Streamlit secrets."""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key and hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
        
        if not api_key:
            st.warning("⚠️ OPENAI_API_KEY not found. The app will use fallback queries only.")
            return None
            
        return OpenAI(api_key=api_key)
    except Exception as e:
        st.warning(f"⚠️ Failed to initialize OpenAI client: {str(e)}. Using fallback queries only.")
        return None


def generate_sql(question: str) -> str:
    """
    Generate SQL query from natural language question using ChatGPT.
    
    Args:
        question: Natural language question about sales data
        
    Returns:
        SQL query string (SELECT only)
    """
    client = get_openai_client()
    if not client:
        raise Exception("OpenAI client not available. Please set OPENAI_API_KEY environment variable.")
    
    system_prompt = "You produce only SQL SELECT statements for DuckDB. No prose, no code fences."
    
    user_prompt = f"""あなたはデータ分析のためのSQLアシスタントです。以下の制約を厳守して、DuckDB方言の SELECT 文のみを1つ出力してください。

【制約】
- 出力はSQLのみ（前後説明やコードブロック記号は不要）
- SELECT文のみ。サブクエリは可。DDL/DMLは不可（CREATE/UPDATE/DELETE/INSERT等禁止）
- テーブル名は sales
- 列: date (DATE), month (TEXT: 'YYYY-MM'), category (TEXT), units (INT), unit_price (INT), region (TEXT), sales_channel (TEXT), customer_segment (TEXT), revenue (INT)
- 期間集計が必要なら month を使う（例: '2025-01'）
- 集計列は SUM(revenue) や SUM(units)
- 並び順は理解しやすい順（期間×カテゴリ等）
- LIMIT は不要（アプリ側で付与）

【ユーザーの質問】
{question}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use cheaper, faster model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0,
            timeout=30  # Add timeout
        )
        
        sql = response.choices[0].message.content.strip()
        
        # Remove code fences if present
        if sql.startswith('```') and sql.endswith('```'):
            lines = sql.split('\n')
            sql = '\n'.join(lines[1:-1])
        elif sql.startswith('```sql') and sql.endswith('```'):
            lines = sql.split('\n')
            sql = '\n'.join(lines[1:-1])
        
        return sql.strip()
        
    except Exception as e:
        raise Exception(f"Failed to generate SQL: {str(e)}")


def is_safe_select_sql(sql: str) -> bool:
    """
    Check if SQL query is safe (SELECT-only, no dangerous keywords).
    
    Args:
        sql: SQL query string to check
        
    Returns:
        True if safe, False otherwise
    """
    if not sql.strip():
        return False
    
    # Normalize SQL (remove extra whitespace, convert to uppercase)
    normalized_sql = ' '.join(sql.strip().split()).upper()
    
    # Must start with SELECT
    if not normalized_sql.startswith('SELECT'):
        return False
    
    # Dangerous keywords that should not appear
    dangerous_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 
        'CREATE', 'REPLACE', 'TRUNCATE', 'ATTACH', 
        'COPY', 'PRAGMA'
    ]
    
    for keyword in dangerous_keywords:
        if f' {keyword} ' in f' {normalized_sql} ':
            return False
            
    return True


def enforce_limit(sql: str, max_limit: int = 1000) -> str:
    """
    Add or enforce LIMIT clause in SQL query.
    
    Args:
        sql: SQL query string
        max_limit: Maximum allowed limit (default 1000)
        
    Returns:
        SQL query with appropriate LIMIT clause
    """
    sql = sql.strip()
    
    # Remove trailing semicolon if present
    if sql.endswith(';'):
        sql = sql[:-1].strip()
    
    # Check if LIMIT already exists
    limit_pattern = r'\bLIMIT\s+(\d+)\b'
    match = re.search(limit_pattern, sql, re.IGNORECASE)
    
    if match:
        # Extract existing limit value
        existing_limit = int(match.group(1))
        # If existing limit is greater than max_limit, replace it
        if existing_limit > max_limit:
            sql = re.sub(limit_pattern, f'LIMIT {max_limit}', sql, flags=re.IGNORECASE)
    else:
        # Add LIMIT clause
        sql += f' LIMIT {max_limit}'
    
    # Add semicolon at the end
    sql += ';'
    
    return sql


def process_sql_query(question: str) -> tuple[str, bool]:
    """
    Process natural language question to generate safe SQL query.
    
    Args:
        question: Natural language question
        
    Returns:
        Tuple of (sql_query, is_generated) where is_generated indicates if SQL was successfully generated
    """
    try:
        # Generate SQL from question
        sql = generate_sql(question)
        
        # Check if SQL is safe
        if not is_safe_select_sql(sql):
            raise Exception("Generated SQL failed safety check")
        
        # Enforce LIMIT
        sql = enforce_limit(sql)
        
        return sql, True
        
    except Exception as e:
        st.warning(f"SQL generation failed: {str(e)}. Using fallback query.")
        return "", False