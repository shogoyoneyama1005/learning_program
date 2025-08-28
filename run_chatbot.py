#!/usr/bin/env python3
"""
Startup script for the Sales Data Analysis Chatbot.
This script helps check dependencies and environment before starting the Streamlit app.
"""

import os
import sys
import subprocess


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'streamlit',
        'duckdb', 
        'pandas',
        'anthropic',
        'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: uv add " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are installed")
    return True


def check_data_file():
    """Check if the sample data file exists."""
    data_file = "data/sample_sales.csv"
    if os.path.exists(data_file):
        print(f"✅ Data file found: {data_file}")
        return True
    else:
        print(f"❌ Data file not found: {data_file}")
        return False


def check_api_key():
    """Check if Anthropic API key is configured."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print("✅ Anthropic API key found")
        return True
    else:
        print("⚠️  Anthropic API key not found in environment variables")
        print("   The app will look for it in Streamlit secrets or you can set it during runtime")
        return True  # Non-blocking warning


def main():
    """Main function to run startup checks and launch the app."""
    print("🚀 Starting Sales Data Analysis Chatbot...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check data file
    if not check_data_file():
        sys.exit(1)
    
    # Check API key (warning only)
    check_api_key()
    
    print("=" * 50)
    print("🎉 All checks passed! Starting Streamlit app...")
    print("\n📖 Usage:")
    print("   - Open your browser to the URL shown below")
    print("   - Ask questions about the sales data in natural language")
    print("   - Use sample questions from the sidebar")
    print("   - View generated SQL queries in the expandable sections")
    print("\n🔧 If you need to set your Anthropic API key:")
    print("   export ANTHROPIC_API_KEY='your_key_here'")
    print("\n" + "=" * 50)
    
    # Launch Streamlit app
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "chatbot_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")


if __name__ == "__main__":
    main()