import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Nassau Candy Profitability Dashboard")

# ===== LOAD DATA =====
df = pd.read_excel("candy.xlsx")

# clean column names
df.columns = df.columns.str.strip().str.lower()

# rename to safe names
df = df.rename(columns={
    "gross profit":"gross_profit",
    "sales":"sales",
    "units":"units",
    "cost":"cost",
    "division":"division",
    "product name":"product_name"
})

# ===== CALCULATIONS =====
df["margin"] = df["gross_profit"] / df["sales"]
df["profit_per_unit"] = df["gross_profit"] / df["units"]

# ===== KPI =====
c1,c2,c3 = st.columns(3)
c1.metric("Total Sales", int(df["sales"].sum()))
c2.metric("Total Profit", int(df["gross_profit"].sum()))
c3.metric("Avg Margin", round(df["margin"].mean(),2))

# ===== PRODUCT RANK =====
st.header("Top Profit Products")
rank = df.groupby("product_name")["gross_profit"].sum().sort_values(ascending=False).head(10)
st.bar_chart(rank)

# ===== DIVISION =====
st.header("Division Profit")
div = df.groupby("division")[["sales","gross_profit"]].sum()
st.bar_chart(div)

# ===== SCATTER =====
st.header("Cost vs Sales")
fig = px.scatter(df,
                 x="sales",
                 y="cost",
                 size="gross_profit",
                 hover_name="product_name")
st.plotly_chart(fig, use_container_width=True)

# ===== PARETO =====
st.header("Pareto Profit")
pareto = df.groupby("product_name")["gross_profit"].sum().sort_values(ascending=False)
cum = pareto.cumsum()/pareto.sum()
st.line_chart(cum)
