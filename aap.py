import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Nassau Candy Profitability Dashboard")

# ===== LOAD DATA =====
df = pd.read_excel("candy.xlsx")

# remove hidden spaces in column names
df.columns = df.columns.str.strip()

# ===== CALCULATIONS =====
df["Margin %"] = df["Gross Profit"] / df["Sales"]
df["Profit per Unit"] = df["Gross Profit"] / df["Units"]

# ===== SIDEBAR FILTERS =====
st.sidebar.header("Filters")

division = st.sidebar.multiselect("Division", df["Division"].unique())
product = st.sidebar.text_input("Search Product")
margin_filter = st.sidebar.slider("Min Margin", 0.0, 1.0, 0.0)

filtered = df.copy()

if division:
    filtered = filtered[filtered["Division"].isin(division)]

if product:
    filtered = filtered[filtered["Product Name"].str.contains(product, case=False)]

filtered = filtered[filtered["Margin %"] >= margin_filter]

# ===== KPI =====
c1,c2,c3 = st.columns(3)
c1.metric("Total Sales", int(filtered["Sales"].sum()))
c2.metric("Total Profit", int(filtered["Gross Profit"].sum()))
c3.metric("Avg Margin", round(filtered["Margin %"].mean(),2))

# =============================
# PRODUCT RANKING
# =============================
st.header("Product Ranking")

profit_rank = filtered.groupby("Product Name")["Gross Profit"].sum().sort_values(ascending=False)
margin_rank = filtered.groupby("Product Name")["Margin %"].mean().sort_values(ascending=False)

col1,col2 = st.columns(2)
col1.subheader("Top Profit Products")
col1.dataframe(profit_rank.head(10))

col2.subheader("Top Margin Products")
col2.dataframe(margin_rank.head(10))

# =============================
# CATEGORY ANALYSIS
# =============================
st.header("Product Category Analysis")

st.subheader("High Sales Low Margin")
hs_lm = filtered[(filtered["Sales"]>filtered["Sales"].median()) & (filtered["Margin %"]<filtered["Margin %"].median())]
st.dataframe(hs_lm[["Product Name","Sales","Margin %"]].head())

st.subheader("Low Sales Low Profit")
ls_lp = filtered[(filtered["Sales"]<filtered["Sales"].median()) & (filtered["Gross Profit"]<filtered["Gross Profit"].median())]
st.dataframe(ls_lp[["Product Name","Sales","Gross Profit"]].head())

# =============================
# DIVISION DASHBOARD
# =============================
st.header("Division Performance")

div = filtered.groupby("Division")[["Sales","Gross Profit"]].sum().reset_index()
fig1 = px.bar(div, x="Division", y=["Sales","Gross Profit"], barmode="group")
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.box(filtered, x="Division", y="Margin %")
st.plotly_chart(fig2, use_container_width=True)

# =============================
# PARETO
# =============================
st.header("Pareto Profit Analysis")

pareto = filtered.groupby("Product Name")["Gross Profit"].sum().sort_values(ascending=False)
cum = pareto.cumsum()/pareto.sum()
fig3 = px.line(cum, title="Profit Contribution Pareto")
st.plotly_chart(fig3, use_container_width=True)

# =============================
# COST DIAGNOSTIC
# =============================
st.header("Cost vs Sales")

fig4 = px.scatter(filtered,
                  x="Sales",
                  y="Cost",
                  size="Gross Profit",
                  color="Margin %",
                  hover_name="Product Name")
st.plotly_chart(fig4, use_container_width=True)

# =============================
# RISK PRODUCTS
# =============================
st.header("Risk Products (Low Margin + High Cost)")

risk = filtered[(filtered["Cost"] > filtered["Sales"]*0.8) & (filtered["Margin %"] < 0.2)]
st.dataframe(risk)
