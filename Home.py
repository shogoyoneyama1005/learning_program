import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Streamlit BI x Claude Code Starter", layout="wide")

st.title("Streamlit BI x Claude Code Starter")
@st.cache_data
def load_data():
    orders_df = pd.read_csv("sample_data/orders.csv")
    users_df = pd.read_csv("sample_data/users.csv")
    return orders_df, users_df

@st.cache_data
def preprocess_orders_data(orders_df):
    orders_df = orders_df.copy()
    orders_df['created_at'] = pd.to_datetime(orders_df['created_at'])
    orders_df['year_month'] = orders_df['created_at'].dt.to_period('M')
    return orders_df

@st.cache_data
def calculate_monthly_metrics(orders_df):
    monthly_data = orders_df.groupby('year_month').agg({
        'order_id': 'count',
        'status': lambda x: (x == 'Cancelled').sum()
    }).rename(columns={'order_id': 'total_orders', 'status': 'cancelled_orders'})
    
    monthly_data['cancel_rate'] = (monthly_data['cancelled_orders'] / monthly_data['total_orders'] * 100).round(2)
    monthly_data.index = monthly_data.index.astype(str)
    
    return monthly_data

orders_df, users_df = load_data()

# データの前処理
processed_orders = preprocess_orders_data(orders_df)
monthly_metrics = calculate_monthly_metrics(processed_orders)

# ダッシュボードのメイン部分
st.header("📊 月別オーダー分析ダッシュボード")

# KPIメトリクス表示
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_orders = len(processed_orders)
    st.metric("総注文数", f"{total_orders:,}")
with col2:
    avg_monthly_orders = int(monthly_metrics['total_orders'].mean())
    st.metric("月平均注文数", f"{avg_monthly_orders:,}")
with col3:
    overall_cancel_rate = (processed_orders['status'] == 'Cancelled').mean() * 100
    st.metric("全体キャンセル率", f"{overall_cancel_rate:.1f}%")
with col4:
    avg_cancel_rate = monthly_metrics['cancel_rate'].mean()
    st.metric("月平均キャンセル率", f"{avg_cancel_rate:.1f}%")

# メインチャート: 月別オーダー数と キャンセル率
st.subheader("月別オーダー数推移とキャンセル率")

# デュアル軸チャートの作成
fig = make_subplots(specs=[[{"secondary_y": True}]])

# 月別オーダー数 (棒グラフ)
fig.add_trace(
    go.Bar(
        x=monthly_metrics.index,
        y=monthly_metrics['total_orders'],
        name="オーダー数",
        marker_color='lightblue',
        yaxis='y'
    ),
    secondary_y=False,
)

# キャンセル率 (線グラフ)
fig.add_trace(
    go.Scatter(
        x=monthly_metrics.index,
        y=monthly_metrics['cancel_rate'],
        mode='lines+markers',
        name="キャンセル率 (%)",
        line=dict(color='red', width=3),
        marker=dict(size=8),
        yaxis='y2'
    ),
    secondary_y=True,
)

# レイアウト設定
fig.update_xaxes(title_text="月")
fig.update_yaxes(title_text="オーダー数", secondary_y=False)
fig.update_yaxes(title_text="キャンセル率 (%)", secondary_y=True)
fig.update_layout(
    title="月別オーダー数推移とキャンセル率",
    hovermode='x unified',
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# 詳細データテーブル
st.subheader("月別詳細データ")
st.dataframe(
    monthly_metrics.style.format({
        'total_orders': '{:,}',
        'cancelled_orders': '{:,}',
        'cancel_rate': '{:.2f}%'
    }),
    use_container_width=True
)

# 既存のデータプレビュー（折りたたみ式に変更）
with st.expander("元データプレビュー"):
    st.subheader("Orders Data (Top 10 rows)")
    st.dataframe(orders_df.head(10))
    
    st.subheader("Users Data (Top 10 rows)")
    st.dataframe(users_df.head(10))