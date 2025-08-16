import streamlit as st
import pandas as pd
import plotly.express as px

# =======================
# LOAD DATA
# =======================
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_incidents.csv")
    return df

df = load_data()

st.set_page_config(page_title="Incident Analysis Dashboard", layout="wide")

st.title("📊 Nigeria Incident Analysis Dashboard 2022-2025")
st.write("An interactive dashboard to explore incidents, fatalities, and durations by state, month, and incident type.")

# =======================
# SIDEBAR FILTERS
# =======================
st.sidebar.header("🔍 Filter Incidents")

# State filter
state_options = ["All"] + sorted(df["States"].dropna().unique().tolist())
state_filter = st.sidebar.selectbox("Select State", options=state_options)

# Year filter
year_options = ["All"] + sorted(df["Year"].dropna().unique().tolist())
year_filter = st.sidebar.selectbox("Select Year", options=year_options)

# Month filter (keeps natural order)
month_order = list(df["Month_Name"].unique())
month_options = ["All"] + month_order
month_filter = st.sidebar.selectbox("Select Month", options=month_options)

# Incident type filter
incident_options = ["All"] + sorted(df["Incident_Type"].dropna().unique().tolist())
incident_filter = st.sidebar.selectbox("Select Incident Type", options=incident_options)

# =======================
# APPLY FILTERS
# =======================
filtered_df = df.copy()

if state_filter != "All":
    filtered_df = filtered_df[filtered_df["States"] == state_filter]

if year_filter != "All":
    filtered_df = filtered_df[filtered_df["Year"] == year_filter]

if month_filter != "All":
    filtered_df = filtered_df[filtered_df["Month_Name"] == month_filter]

if incident_filter != "All":
    filtered_df = filtered_df[filtered_df["Incident_Type"] == incident_filter]

# =======================
# METRICS
# =======================
total_incidents = filtered_df.shape[0]
total_deaths = filtered_df["Number of deaths"].sum()
avg_duration = filtered_df["Duration_days"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("📝 Total Incidents", f"{total_incidents:,}")
col2.metric("⚰️ Total Deaths", f"{total_deaths:,}")
col3.metric("⏳ Avg Duration (Days)", f"{avg_duration:.1f}")

st.markdown("---")

# =======================
# CHART 1 - Fatalities by State
# =======================
st.subheader("1️⃣ States with the Highest Fatalities")
fatalities_by_state = (
    filtered_df.groupby("States")["Number of deaths"].sum()
    .reset_index().sort_values(by="Number of deaths", ascending=False)
)
fig1 = px.bar(
    fatalities_by_state,
    x="States",
    y="Number of deaths",
    title="States Ranked by Total Fatalities",
    labels={"States": "State", "Number of deaths": "Total Deaths"},
    text="Number of deaths",
    color="Number of deaths",
    color_continuous_scale="Reds"
)
fig1.update_traces(texttemplate='%{text:,}', textposition='outside')
fig1.update_layout(yaxis=dict(title="Number of Deaths"), xaxis=dict(title="State"))
st.plotly_chart(fig1, use_container_width=True)

# =======================
# CHART 2 - Incidents by Type (Pie)
# =======================
st.subheader("2️⃣ Share of Incidents by Type")
incidents_by_type = (
    filtered_df.groupby("Incident_Type")["Identifier"].count()
    .reset_index().rename(columns={"Identifier": "Count"})
)
fig2 = px.pie(
    incidents_by_type,
    names="Incident_Type",
    values="Count",
    title="Proportion of Incidents by Type",
    hole=0.4
)
fig2.update_traces(textinfo="percent+label")
st.plotly_chart(fig2, use_container_width=True)

# =======================
# CHART 3 - Monthly Trend
# =======================
st.subheader("3️⃣ Monthly Trend of Incidents")
monthly_trend = (
    filtered_df.groupby("Month_Name")["Identifier"].count()
    .reindex(month_order).reset_index()
)
fig3 = px.line(
    monthly_trend,
    x="Month_Name",
    y="Identifier",
    markers=True,
    title="How Incident Numbers Change Month-by-Month",
    labels={"Month_Name": "Month", "Identifier": "Number of Incidents"}
)
st.plotly_chart(fig3, use_container_width=True)

# =======================
# CHART 4 - Duration vs Deaths
# =======================
st.subheader("4️⃣ Relationship Between Duration and Deaths")
fig4 = px.scatter(
    filtered_df,
    x="Duration_days",
    y="Number of deaths",
    color="Incident_Type",
    size="Number of deaths",
    title="Longer Duration Incidents Often Cause More Deaths",
    labels={"Duration_days": "Duration (Days)", "Number of deaths": "Number of Deaths"},
    hover_data=["States", "Year", "Month_Name"]
)
st.plotly_chart(fig4, use_container_width=True)

# =======================
# DATA TABLE
# =======================
st.markdown("### 📄 Filtered Data Table")
st.dataframe(filtered_df)

st.markdown(f"**Showing {len(filtered_df)} records after filtering**")
