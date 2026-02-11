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
