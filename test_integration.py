#!/usr/bin/env python3
"""
Integration test for the Sales Data Analysis Chatbot.
Tests all components working together without the Streamlit interface.
"""

import sys
import os

# Add current directory to path
sys.path.append('.')

def test_database_integration():
    """Test database initialization and queries."""
    print("🔍 Testing database integration...")
    
    try:
        from db import init_db, query_df, get_data_summary
        
        # Initialize database
        conn = init_db()
        assert conn is not None, "Failed to initialize database"
        
        # Test data summary
        summary = get_data_summary(conn)
        assert summary.get('total_records', 0) > 0, "No records found"
        print(f"   ✅ Database has {summary['total_records']} records")
        
        # Test simple query
        result = query_df(conn, "SELECT COUNT(*) as count FROM sales;")
        assert not result.empty, "Query returned no results"
        print(f"   ✅ Query executed successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database integration failed: {e}")
        return False


def test_fallback_system():
    """Test fallback query system."""
    print("🔍 Testing fallback system...")
    
    try:
        from fallbacks import find_best_fallback, is_fallback_question
        
        # Test question matching
        test_question = "月ごとのカテゴリ別売上を見せて"
        is_match = is_fallback_question(test_question)
        assert is_match, "Failed to match fallback question"
        
        # Test fallback retrieval
        name, sql = find_best_fallback(test_question)
        assert name and sql, "Failed to get fallback query"
        assert "SELECT" in sql.upper(), "Fallback query is not a SELECT statement"
        print(f"   ✅ Matched fallback: {name}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Fallback system failed: {e}")
        return False


def test_sql_safety():
    """Test SQL safety mechanisms."""
    print("🔍 Testing SQL safety...")
    
    try:
        from llm_sql import is_safe_select_sql, enforce_limit
        
        # Test safe query
        safe_query = "SELECT month, SUM(revenue) FROM sales GROUP BY month"
        assert is_safe_select_sql(safe_query), "Safe query rejected"
        
        # Test unsafe query
        unsafe_query = "DROP TABLE sales"
        assert not is_safe_select_sql(unsafe_query), "Unsafe query accepted"
        
        # Test limit enforcement
        limited = enforce_limit("SELECT * FROM sales", 100)
        assert "LIMIT 100" in limited, "LIMIT not properly enforced"
        print("   ✅ SQL safety checks working")
        
        return True
        
    except Exception as e:
        print(f"   ❌ SQL safety failed: {e}")
        return False


def test_visualization():
    """Test visualization system."""
    print("🔍 Testing visualization...")
    
    try:
        from viz import detect_chart_type
        import pandas as pd
        
        # Test chart type detection
        test_data = pd.DataFrame({
            'category': ['A', 'B', 'C'],
            'revenue': [100, 200, 150]
        })
        
        chart_type = detect_chart_type(test_data)
        assert chart_type in ['bar', 'line', 'pie', 'scatter', 'none'], f"Invalid chart type: {chart_type}"
        print(f"   ✅ Chart type detection: {chart_type}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Visualization failed: {e}")
        return False


def test_end_to_end():
    """Test end-to-end workflow without Claude API."""
    print("🔍 Testing end-to-end workflow...")
    
    try:
        from db import init_db, query_df
        from fallbacks import find_best_fallback
        from viz import display_data_with_chart
        
        # Initialize database
        conn = init_db()
        assert conn is not None, "Database initialization failed"
        
        # Get a fallback query
        _, sql = find_best_fallback("月ごとのカテゴリ別売上")
        
        # Execute query
        result = query_df(conn, sql)
        assert not result.empty, "Query returned no results"
        
        # Test visualization (without actually displaying)
        chart_type_detected = len(result.select_dtypes(include=['number']).columns) > 0
        assert chart_type_detected, "No numeric columns for visualization"
        
        print(f"   ✅ End-to-end test passed with {len(result)} result rows")
        return True
        
    except Exception as e:
        print(f"   ❌ End-to-end test failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print("🚀 Running Sales Data Analysis Chatbot Integration Tests")
    print("=" * 60)
    
    tests = [
        test_database_integration,
        test_fallback_system,
        test_sql_safety,
        test_visualization,
        test_end_to_end
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The chatbot is ready to use.")
        print("\n🚀 To start the chatbot, run:")
        print("   python run_chatbot.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())