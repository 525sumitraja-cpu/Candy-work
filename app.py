import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Nassau Candy Profitability Dashboard")

# ===== LOAD DATA =====
df = pd.read_excel("candy.xlsx", sheet_name="Nassau Candy Distributor")

# clean column names
df.columns = df.columns.str.strip()

# ===== CALCULATIONS =====
df["Margin %"] = df["Gross Profit"] / df["Sales"]
df["Profit per Unit"] = df["Gross Profit"] / df["Units"]

# ===== KPI =====
c1,c2,c3 = st.columns(3)
c1.metric("Total Sales", int(df["Sales"].sum()))
c2.metric("Total Profit", int(df["Gross Profit"].sum()))
c3.metric("Avg Margin", round(df["Margin %"].mean(),2))

# =============================
# PRODUCT RANKING
# =============================
st.header("Top Profit Products")

rank = df.groupby("Product Name")["Gross Profit"].sum().sort_values(ascending=False).head(10)
st.bar_chart(rank)

# =============================
# DIVISION
# =============================
st.header("Division Performance")

div = df.groupby("Division")[["Sales","Gross Profit"]].sum()
st.bar_chart(div)

# =============================
# SCATTER
# =============================
st.header("Cost vs Sales")

fig = px.scatter(df,
                 x="Sales",
                 y="Cost",
                 size="Gross Profit",
                 hover_name="Product Name")
st.plotly_chart(fig, use_container_width=True)

# =============================
# PARETO
# =============================
st.header("Pareto Profit")

pareto = df.groupby("Product Name")["Gross Profit"].sum().sort_values(ascending=False)
cum = pareto.cumsum()/pareto.sum()
st.line_chart(cum)
# =========================
# DATE COLUMN FIX
# =========================
df["Order Date"] = pd.to_datetime(df["Order Date"])

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("Filters")

# Date range
date_range = st.sidebar.date_input(
    "Date Range",
    [df["Order Date"].min(), df["Order Date"].max()]
)

# Division filter
division_filter = st.sidebar.multiselect(
    "Division",
    df["Division"].dropna().unique()
)

# Margin slider
margin_filter = st.sidebar.slider(
    "Margin Threshold",
    0.0, 1.0, 0.0
)

# Product search
product_search = st.sidebar.text_input("Search Product")

# =========================
# APPLY FILTERS
# =========================
filtered = df.copy()

# Date filter
if len(date_range) == 2:
    filtered = filtered[
        (filtered["Order Date"] >= pd.to_datetime(date_range[0])) &
        (filtered["Order Date"] <= pd.to_datetime(date_range[1]))
    ]

# Division
if division_filter:
    filtered = filtered[filtered["Division"].isin(division_filter)]

# Product search
if product_search:
    filtered = filtered[
        filtered["Product Name"].str.contains(product_search, case=False)
    ]

# Margin
filtered = filtered[filtered["Margin %"] >= margin_filter]

# =========================
# PARETO – REVENUE
# =========================
st.header("80% Revenue Contributors")

rev = filtered.groupby("Product Name")["Sales"].sum().sort_values(ascending=False)
rev_cum = rev.cumsum()/rev.sum()

rev_df = rev_cum.reset_index()
rev_df.columns = ["Product Name","Cumulative Revenue %"]

top_rev = rev_df[rev_df["Cumulative Revenue %"] <= 0.8]

st.write("Products contributing to 80% Revenue")
st.dataframe(top_rev)

# =========================
# PARETO – PROFIT
# =========================
st.header("80% Profit Contributors")

profit = filtered.groupby("Product Name")["Gross Profit"].sum().sort_values(ascending=False)
profit_cum = profit.cumsum()/profit.sum()

profit_df = profit_cum.reset_index()
profit_df.columns = ["Product Name","Cumulative Profit %"]

top_profit = profit_df[profit_df["Cumulative Profit %"] <= 0.8]

st.write("Products contributing to 80% Profit")
st.dataframe(top_profit)

# =========================
# DEPENDENCY RISK
# =========================
st.header("Over-Dependency Risk (Product)")

dependency = filtered.groupby("Product Name")["Sales"].sum()/filtered["Sales"].sum()
risk_products = dependency[dependency > 0.10]

st.write("Products contributing >10% of total revenue")
st.dataframe(risk_products)

# =========================
# REGION DEPENDENCY
# =========================
st.header("Region Dependency Risk")

region_dep = filtered.groupby("Region")["Sales"].sum()/filtered["Sales"].sum()
region_risk = region_dep[region_dep > 0.25]

st.write("Regions contributing >25% revenue")
st.dataframe(region_risk)

# =========================
# MARGIN RISK PRODUCTS
# =========================
st.header("Margin Risk Products")

margin_risk = filtered[
    (filtered["Margin %"] < 0.15) &
    (filtered["Sales"] > filtered["Sales"].median())
]

st.dataframe(margin_risk[[
    "Product Name","Sales","Gross Profit","Margin %"
]])

