import streamlit as st
import pandas as pd
import altair as alt

# =========================
# データ読み込み
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("data/sample_sales.csv", parse_dates=["date"])
    return df

st.set_page_config(page_title="販売データBIダッシュボード", layout="wide")
st.title("📊 販売データBIダッシュボード")

# =========================
# サイドバー：日付範囲 & カテゴリ選択
# =========================
df = load_data()
st.sidebar.header("フィルタ")
min_date, max_date = df["date"].min(), df["date"].max()
date_range = st.sidebar.date_input(
    "日付範囲を選択してください",
    [min_date, max_date],
    min_value=min_date, max_value=max_date
)
if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date, end_date = date_range[0], date_range[1]

# カテゴリ セレクター（複数選択）
all_categories = sorted(df["category"].unique().tolist())
selected_categories = st.sidebar.multiselect(
    "カテゴリを選択（未選択=すべて）",
    options=all_categories,
    default=all_categories
)

# 日付・カテゴリで事前フィルタ
base_df = df[
    (df["date"] >= pd.to_datetime(start_date)) &
    (df["date"] <= pd.to_datetime(end_date)) &
    (df["category"].isin(selected_categories))
].copy()

# =========================
# チャート種別切替 UI
# =========================
st.subheader("🛠 表示設定")
c1, c2, c3, c4 = st.columns([1,1,1,1])
with c1:
    cat_chart_type = st.radio("カテゴリ", ["棒グラフ", "ドーナツ"], index=0, horizontal=True)
with c2:
    region_chart_type = st.radio("地域", ["棒(横)", "棒(縦)"], index=0, horizontal=True)
with c3:
    ts_chart_type = st.radio("日次推移", ["折れ線", "面"], index=0, horizontal=True)
with c4:
    seg_chart_type = st.radio("セグメント", ["円", "ドーナツ"], index=1, horizontal=True)

# =========================
# Altair selection（複数選択・名前固定）
# =========================
sel_cat = alt.selection_point(name="sel_category", fields=["category"], toggle=True, clear="dblclick")
sel_region = alt.selection_point(name="sel_region", fields=["region"], toggle=True, clear="dblclick")
sel_seg = alt.selection_point(name="sel_segment", fields=["customer_segment"], toggle=True, clear="dblclick")

# どのチャートでも参照可能にするため、共通の add_params を適用
def with_params(chart: alt.Chart) -> alt.Chart:
    return chart.add_params(sel_cat, sel_region, sel_seg)

# KPI/時系列で使う総合フィルタ（空選択時は全件）
combined_sel = sel_cat & sel_region & sel_seg

# =========================
# KPI（選択に連動）
# =========================
st.subheader("📌 全体KPI（クリック選択に連動）")
kpi_rev = with_params(
    alt.Chart(base_df, title="売上合計")
    .transform_filter(combined_sel)
    .mark_text(fontSize=28)
    .encode(text=alt.Text("revenue:Q", aggregate="sum", format="¥,.0f"))
    .properties(height=60, width=260)
)
kpi_units = with_params(
    alt.Chart(base_df, title="販売数量合計")
    .transform_filter(combined_sel)
    .mark_text(fontSize=28)
    .encode(text=alt.Text("units:Q", aggregate="sum", format=",.0f"))
    .properties(height=60, width=260)
)
kpi_cats = with_params(
    alt.Chart(base_df, title="商品カテゴリ数")
    .transform_filter(combined_sel)
    .mark_text(fontSize=28)
    .encode(text=alt.Text("category:N", aggregate="distinct", format=",.0f"))
    .properties(height=60, width=260)
)
st.altair_chart(alt.hconcat(kpi_rev, kpi_units, kpi_cats), use_container_width=True)

# =========================
# 商品カテゴリ別 売上（種別切替 + 複数選択）
#   ※ 他選択（地域/セグメント）でフィルタ、自身は sel_cat でハイライト
# =========================
st.subheader("📦 商品カテゴリごとの売上（クリックで複数選択・ダブルクリックで解除）")
cat_sales = base_df.groupby("category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)

if cat_chart_type == "棒グラフ":
    cat_chart = (
        alt.Chart(cat_sales)
        .transform_filter(sel_region)  # 他パラメータでフィルタ
        .transform_filter(sel_seg)
        .mark_bar()
        .encode(
            x=alt.X("revenue:Q", title="売上金額"),
            y=alt.Y("category:N", sort="-x", title="商品カテゴリ"),
            tooltip=["category:N", alt.Tooltip("revenue:Q", format=",.0f", title="売上")]
        )
        .encode(opacity=alt.condition(sel_cat, alt.value(1), alt.value(0.3)))
    )
else:  # ドーナツ
    cat_chart = (
        alt.Chart(cat_sales)
        .transform_filter(sel_region)
        .transform_filter(sel_seg)
        .mark_arc(innerRadius=80)
        .encode(
            theta=alt.Theta("revenue:Q", title="売上"),
            color=alt.Color("category:N", legend=alt.Legend(title="カテゴリ")),
            tooltip=["category:N", alt.Tooltip("revenue:Q", format=",.0f", title="売上")]
        )
        .encode(opacity=alt.condition(sel_cat, alt.value(1), alt.value(0.4)))
    )

# ここで **必ず** 3つの param を付与（未定義参照を避ける）
st.altair_chart(with_params(cat_chart).properties(height=360), use_container_width=True)

# =========================
# 地域別 売上（種別切替 + 複数選択）
# =========================
st.subheader("🌍 地域別売上（クリックで複数選択・ダブルクリックで解除）")
region_sales = base_df.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)

if region_chart_type == "棒(縦)":
    region_chart = (
        alt.Chart(region_sales)
        .transform_filter(sel_cat)
        .transform_filter(sel_seg)
        .mark_bar()
        .encode(
            x=alt.X("region:N", title="地域", sort="-y"),
            y=alt.Y("revenue:Q", title="売上金額"),
            tooltip=["region:N", alt.Tooltip("revenue:Q", format=",.0f", title="売上")]
        )
        .encode(opacity=alt.condition(sel_region, alt.value(1), alt.value(0.3)))
    )
else:  # 棒(横)
    region_chart = (
        alt.Chart(region_sales)
        .transform_filter(sel_cat)
        .transform_filter(sel_seg)
        .mark_bar()
        .encode(
            x=alt.X("revenue:Q", title="売上金額"),
            y=alt.Y("region:N", title="地域", sort="-x"),
            tooltip=["region:N", alt.Tooltip("revenue:Q", format=",.0f", title="売上")]
        )
        .encode(opacity=alt.condition(sel_region, alt.value(1), alt.value(0.3)))
    )
st.altair_chart(with_params(region_chart).properties(height=360), use_container_width=True)

# =========================
# 顧客セグメント別 売上シェア（種別切替 + 複数選択）
# =========================
st.subheader("👥 顧客セグメント別 売上シェア（クリックで複数選択・ダブルクリックで解除）")
seg_sales = base_df.groupby("customer_segment", as_index=False)["revenue"].sum()

if seg_chart_type == "円":
    seg_chart = (
        alt.Chart(seg_sales)
        .transform_filter(sel_cat)
        .transform_filter(sel_region)
        .mark_arc()
        .encode(
            theta=alt.Theta("revenue:Q", title="売上"),
            color=alt.Color("customer_segment:N", legend=alt.Legend(title="顧客セグメント")),
            tooltip=["customer_segment:N", alt.Tooltip("revenue:Q", format=",.0f", title="売上")]
        )
        .encode(opacity=alt.condition(sel_seg, alt.value(1), alt.value(0.4)))
    )
else:  # ドーナツ
    seg_chart = (
        alt.Chart(seg_sales)
        .transform_filter(sel_cat)
        .transform_filter(sel_region)
        .mark_arc(innerRadius=80)
        .encode(
            theta=alt.Theta("revenue:Q", title="売上"),
            color=alt.Color("customer_segment:N", legend=alt.Legend(title="顧客セグメント")),
            tooltip=["customer_segment:N", alt.Tooltip("revenue:Q", format=",.0f", title="売上")]
        )
        .encode(opacity=alt.condition(sel_seg, alt.value(1), alt.value(0.4)))
    )
st.altair_chart(with_params(seg_chart).properties(height=360), use_container_width=True)

# =========================
# 日毎の売上推移（選択連動）
# =========================
st.subheader("📈 日毎の売上推移（選択連動）")
ts_base = (
    alt.Chart(base_df)
    .transform_filter(combined_sel)
    .transform_aggregate(revenue="sum(revenue)", groupby=["date"])
    .encode(
        x=alt.X("date:T", title="日付"),
        y=alt.Y("revenue:Q", title="売上金額"),
        tooltip=[alt.Tooltip("date:T", title="日付"), alt.Tooltip("revenue:Q", format=",.0f", title="売上")]
    )
)
ts_chart = ts_base.mark_area() if ts_chart_type == "面" else ts_base.mark_line(point=True)
st.altair_chart(with_params(ts_chart).properties(height=380), use_container_width=True)

# =========================
# ヘルプ
# =========================
with st.expander("ℹ️ 操作ガイド"):
    st.markdown(
        """
- サイドバーの**日付/カテゴリ**で事前フィルタ  
- 各グラフの要素を**クリック**：選択に追加（複数可）  
- **再クリック**：その要素だけ解除  
- **背景ダブルクリック**：そのグラフの選択を全解除  
- 上段の**ボタン（ラジオ）**でチャートの種類を切替  
        """
    )
