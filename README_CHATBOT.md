# Sales Data Analysis AI Chatbot 📊🤖

A powerful Streamlit application that allows you to analyze sales data using natural language queries. Ask questions in plain language and get answers with data tables and visualizations!

## 🌟 Features

- **Natural Language Queries**: Ask questions in Japanese or English about your sales data
- **SQL Generation**: Automatically converts your questions to SQL using Claude AI
- **Safety First**: All queries are limited to SELECT operations with built-in safety checks
- **Fallback System**: Pre-defined queries ensure you always get results even if AI generation fails
- **Auto Visualization**: Automatically creates appropriate charts (bar, line, pie, scatter) based on your data
- **Interactive Interface**: Clean Streamlit chat interface with sidebar data overview

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Make sure you have uv installed
pip install uv

# Install project dependencies
uv sync
```

### 2. Set Up API Key

```bash
# Set your Anthropic API key (get one from https://console.anthropic.com/)
export ANTHROPIC_API_KEY='your_anthropic_api_key_here'

# Or create a .env file
cp .env.example .env
# Then edit .env and add your API key
```

### 3. Run the Application

```bash
# Option 1: Use the startup script (recommended)
python run_chatbot.py

# Option 2: Direct Streamlit command
streamlit run chatbot_app.py

# Option 3: Using uv
uv run streamlit run chatbot_app.py
```

### 4. Open Your Browser

The app will automatically open in your browser at `http://localhost:8501`

## 📋 Sample Questions

Try these example questions to get started:

**Japanese:**
- "月ごとのカテゴリ別売上を見せて"
- "チャネル別の売上合計は？"
- "地域ごとの売上を教えて"
- "2025年1月の売上トップ3カテゴリは？"
- "平均単価をチャネル別に分析して"

**English:**
- "Show me monthly sales by category"
- "What are the total sales by channel?"
- "Compare regional sales performance"
- "Which categories had the highest revenue in January 2025?"
- "Analyze average unit price by sales channel"

## 🏗️ Project Structure

```
├── chatbot_app.py          # Main Streamlit application
├── db.py                   # Database operations (DuckDB)
├── llm_sql.py             # Claude AI integration & SQL generation
├── fallbacks.py           # Fallback SQL queries
├── viz.py                 # Visualization logic
├── run_chatbot.py         # Startup script
├── data/
│   └── sample_sales.csv   # Sample sales data
├── .env.example           # Environment variables template
└── README_CHATBOT.md      # This file
```

## 🔧 How It Works

1. **User Input**: You ask a question in natural language
2. **SQL Generation**: Claude AI converts your question to a SQL query
3. **Safety Check**: The system validates the SQL for security (SELECT-only)
4. **Fallback**: If AI generation fails, predefined queries are used
5. **Execution**: Query runs against DuckDB with your sales data
6. **Visualization**: Results are displayed as tables and appropriate charts
7. **Insights**: Key insights are automatically generated from the results

## 📊 Data Schema

The sample data includes the following columns:

- `date`: Transaction date (DATE)
- `month`: Derived month in YYYY-MM format (TEXT)
- `category`: Product category (Electronics, Clothing, etc.)
- `units`: Number of units sold (INTEGER)
- `unit_price`: Price per unit (INTEGER)
- `region`: Geographic region (North, South, East, West)
- `sales_channel`: Online or Store
- `customer_segment`: Consumer, Corporate, Small Business
- `revenue`: Total revenue (units × unit_price)

## 🔒 Security Features

- **SELECT-only queries**: No data modification possible
- **Keyword filtering**: Blocks dangerous SQL operations
- **LIMIT enforcement**: Prevents large result sets (max 1000 rows)
- **Input validation**: Sanitizes user inputs
- **Error handling**: Graceful fallbacks when queries fail

## 🎨 Visualization Types

The system automatically selects the best chart type based on your data:

- **Bar Charts**: For categorical data with numeric values
- **Line Charts**: For time series data (monthly trends)
- **Pie Charts**: For proportion/distribution data
- **Scatter Plots**: For relationships between numeric variables

## 🛠️ Customization

### Adding New Fallback Queries

Edit `fallbacks.py` to add more predefined queries:

```python
FALLBACKS["your_query_name"] = """
    SELECT your_columns
    FROM sales
    WHERE your_conditions
    LIMIT 1000;
"""
```

### Modifying Visualizations

Edit `viz.py` to customize chart generation logic or add new chart types.

### Updating Data Schema

If you change the data structure, update the schema description in `llm_sql.py` prompt template.

## 🐛 Troubleshooting

### Common Issues

1. **"ANTHROPIC_API_KEY not found"**
   - Make sure you've set the environment variable
   - Check that your API key is valid
   - Try adding it to Streamlit secrets instead

2. **"No module named 'X'"**
   - Run `uv sync` to install dependencies
   - Make sure you're in the correct virtual environment

3. **"Database connection failed"**
   - Check that `data/sample_sales.csv` exists
   - Verify the CSV file format matches the expected schema

4. **"SQL generation failed"**
   - The system will automatically use fallback queries
   - Check your internet connection for Claude API access
   - Try rephrasing your question

### Debug Mode

Set the environment variable `STREAMLIT_DEBUG=1` for more verbose logging.

## 📈 Performance Tips

- Results are cached to improve response times
- Database connections are reused across requests
- Large result sets are automatically limited
- Charts render progressively for better UX

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is provided as-is for educational and development purposes.

## 🙏 Acknowledgments

- **Claude AI** by Anthropic for SQL generation
- **Streamlit** for the amazing web app framework
- **DuckDB** for fast in-memory analytics
- **Plotly** for interactive visualizations
- **Pandas** for data manipulation

---

**Happy Data Analysis! 📊✨**