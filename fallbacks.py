"""
Fallback SQL queries for common sales analysis patterns.
These queries are used when SQL generation fails or produces unsafe queries.
"""

FALLBACKS = {
    "月毎のカテゴリー別の売り上げ": """
        SELECT month, category, SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY 1,2
        ORDER BY 1,2
        LIMIT 1000;
    """,
    
    "チャネルごとの売り上げ": """
        SELECT sales_channel, SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY 1
        ORDER BY 1
        LIMIT 1000;
    """,
    
    "地域ごとの売り上げの合計": """
        SELECT region, SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY 1
        ORDER BY 1
        LIMIT 1000;
    """,
    
    "カテゴリ別売上": """
        SELECT category, SUM(revenue) AS total_revenue, SUM(units) AS total_units
        FROM sales
        GROUP BY 1
        ORDER BY total_revenue DESC
        LIMIT 1000;
    """,
    
    "月別売上": """
        SELECT month, SUM(revenue) AS total_revenue, SUM(units) AS total_units
        FROM sales
        GROUP BY 1
        ORDER BY 1
        LIMIT 1000;
    """,
    
    "顧客セグメント別売上": """
        SELECT customer_segment, SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY 1
        ORDER BY total_revenue DESC
        LIMIT 1000;
    """,
    
    "全体集計": """
        SELECT 
            COUNT(*) AS total_transactions,
            SUM(revenue) AS total_revenue,
            SUM(units) AS total_units,
            AVG(unit_price) AS avg_unit_price,
            AVG(revenue) AS avg_transaction_value
        FROM sales
        LIMIT 1000;
    """
}

# Keywords to match user questions to fallback queries
FALLBACK_KEYWORDS = {
    "月毎のカテゴリー別の売り上げ": [
        "月", "month", "カテゴリ", "category", "月別", "月ごと", "カテゴリ別", "カテゴリー別"
    ],
    
    "チャネルごとの売り上げ": [
        "チャネル", "channel", "販売チャネル", "sales_channel", "online", "store", "オンライン", "店舗"
    ],
    
    "地域ごとの売り上げの合計": [
        "地域", "region", "地域別", "north", "south", "east", "west", "北", "南", "東", "西"
    ],
    
    "カテゴリ別売上": [
        "カテゴリ", "category", "商品", "製品", "electronics", "clothing", "groceries"
    ],
    
    "月別売上": [
        "月", "month", "月別", "月ごと", "時間", "期間", "推移"
    ],
    
    "顧客セグメント別売上": [
        "顧客", "customer", "セグメント", "segment", "consumer", "corporate", "business"
    ],
    
    "全体集計": [
        "全体", "total", "合計", "サマリー", "summary", "概要", "統計"
    ]
}


def find_best_fallback(question: str) -> tuple[str, str]:
    """
    Find the best matching fallback query for a given question.
    
    Args:
        question: Natural language question
        
    Returns:
        Tuple of (fallback_name, fallback_sql)
    """
    question_lower = question.lower()
    
    # Count keyword matches for each fallback
    best_match = None
    max_matches = 0
    
    for fallback_name, keywords in FALLBACK_KEYWORDS.items():
        matches = 0
        for keyword in keywords:
            if keyword.lower() in question_lower:
                matches += 1
        
        if matches > max_matches:
            max_matches = matches
            best_match = fallback_name
    
    # If no keywords match, use the general summary
    if best_match is None or max_matches == 0:
        best_match = "全体集計"
    
    return best_match, FALLBACKS[best_match].strip()


def get_all_fallbacks() -> dict:
    """
    Get all available fallback queries.
    
    Returns:
        Dictionary of fallback names to SQL queries
    """
    return FALLBACKS.copy()


def is_fallback_question(question: str) -> bool:
    """
    Check if a question matches any fallback patterns.
    
    Args:
        question: Natural language question
        
    Returns:
        True if question matches fallback patterns
    """
    question_lower = question.lower()
    
    for keywords in FALLBACK_KEYWORDS.values():
        for keyword in keywords:
            if keyword.lower() in question_lower:
                return True
    
    return False