import streamlit as st
import pandas as pd

st.set_page_config(page_title="Protein Market Dashboard", layout="wide")

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

df = pd.read_csv("data/beef_prices.csv")

df["date"] = pd.to_datetime(df["date"])

df = df.groupby(["date","cut_name"], as_index=False)["price"].mean()

df = df.sort_values("date")

st.title("Protein Market Dashboard")

# ------------------------------------------------
# HELPER FUNCTION
# ------------------------------------------------

def get_value(name):

    row = df[df["cut_name"] == name]

    if len(row) == 0:
        return None

    return float(row.iloc[-1]["price"])


# ------------------------------------------------
# MARKET SNAPSHOT VALUES
# ------------------------------------------------

choice = get_value("Choice Cutout")
select = get_value("Select Cutout")
pork = get_value("Pork Cutout")
spread = get_value("Choice Select Spread")
loads = get_value("Total Loads")


# ------------------------------------------------
# TOP MARKET PANEL
# ------------------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

if col1.button(f"Choice Cutout {choice:.2f}" if choice else "Choice Cutout N/A"):
    st.session_state["cutout_chart"] = "Choice Cutout"

if col2.button(f"Select Cutout {select:.2f}" if select else "Select Cutout N/A"):
    st.session_state["cutout_chart"] = "Select Cutout"

if col3.button(f"Pork Cutout {pork:.2f}" if pork else "Pork Cutout N/A"):
    st.session_state["cutout_chart"] = "Pork Cutout"

if col4.button(f"Spread {spread:.2f}" if spread else "Spread N/A"):
    st.session_state["cutout_chart"] = "Choice Select Spread"

if col5.button(f"Loads {int(loads)}" if loads else "Loads N/A"):
    st.session_state["cutout_chart"] = "Total Loads"


# ------------------------------------------------
# SHOW CUTOUT CHART
# ------------------------------------------------

if "cutout_chart" in st.session_state:

    selected = st.session_state["cutout_chart"]

    st.subheader(selected)

    chart_df = df[df["cut_name"] == selected]

    chart_df = chart_df.set_index("date")[["price"]]

    st.line_chart(chart_df)

    st.dataframe(
        chart_df.reset_index().sort_values("date", ascending=False),
        use_container_width=True
    )

st.divider()

# ------------------------------------------------
# TABS
# ------------------------------------------------

tab1, tab2 = st.tabs(["Cut Explorer","Primal Dashboard"])


# ------------------------------------------------
# CUT EXPLORER
# ------------------------------------------------

with tab1:

    st.sidebar.header("Controls")

    cut1 = st.sidebar.selectbox(
        "Primary Cut",
        sorted(df["cut_name"].unique())
    )

    cut2 = st.sidebar.selectbox(
        "Compare With",
        ["None"] + sorted(df["cut_name"].unique())
    )

    df1 = df[df["cut_name"] == cut1]

    latest = df1.iloc[-1]["price"]

    previous = df1.iloc[-2]["price"] if len(df1) > 1 else latest

    change = latest - previous

    c1, c2, c3 = st.columns(3)

    c1.metric("Selected Cut", cut1)

    c2.metric("Latest Price", f"{latest:.2f}")

    c3.metric("Change", f"{change:.2f}")

    st.divider()

    df1_chart = df1.set_index("date")[["price"]]

    df1_chart.columns = [cut1]

    if cut2 != "None":

        df2 = df[df["cut_name"] == cut2]

        df2_chart = df2.set_index("date")[["price"]]

        df2_chart.columns = [cut2]

        chart = pd.concat([df1_chart, df2_chart], axis=1)

    else:

        chart = df1_chart

    st.line_chart(chart)

    st.dataframe(
        df1.sort_values("date", ascending=False),
        use_container_width=True
    )


# ------------------------------------------------
# PRIMAL DASHBOARD
# ------------------------------------------------

with tab2:

    st.subheader("Primal Market Dashboard")

    primal_df = df[df["cut_name"].str.contains("Primal")]

    pivot = primal_df.pivot(
        index="date",
        columns="cut_name",
        values="price"
    )

    st.line_chart(pivot)

    st.dataframe(
        primal_df.sort_values("date", ascending=False),
        use_container_width=True
    )