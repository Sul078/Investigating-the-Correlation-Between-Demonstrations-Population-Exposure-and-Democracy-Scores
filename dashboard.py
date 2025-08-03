import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Setting page configuration
st.set_page_config(page_title="Conflict Risk Dashboard", layout="wide")

# Loading data
try:
    df = pd.read_csv("analysis_results_2021_2023.csv")
except FileNotFoundError:
    st.error("Error: 'analysis_results_2021_2023.csv' not found. Please ensure the file is in the correct directory.")
    st.stop()

# Title and description
st.title("Conflict Risk in Europe & Central Asia (2021–2023)")
st.markdown("""
    This dashboard analyzes conflict events (protests, riots, etc.) and their correlation with democracy scores
    across 11 countries in Europe and Central Asia from 2021 to 2023. Use the filters to explore trends.
""")

# Sidebar for year selection
st.sidebar.header("Filters")
years = sorted(df['year'].unique())
selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)

# Filtering data for the selected year
df_year = df[df['year'] == selected_year]

# Choropleth map
st.header(f"Conflict Events by Country ({selected_year})")
fig_map = px.choropleth(
    df_year,
    locations="iso_alpha",
    color="TOTAL_FATALITIES",
    hover_name="country_name",
    hover_data=["PEACEFUL_PROTESTS", "VIOLENT_PROTESTS", "DEMOCRACY_SCORE"],
    color_continuous_scale=px.colors.sequential.Reds,
    title=f"Total Fatalities by Country ({selected_year})"
)
fig_map.update_layout(geo=dict(showframe=False, projection_type="mercator"))
st.plotly_chart(fig_map, use_container_width=True)

# Time series for selected country
st.header("Time Series Analysis")
countries = sorted(df['country_name'].unique())
selected_country = st.selectbox("Select Country", countries)
df_country = df[df['country_name'] == selected_country]

fig_ts = go.Figure()
fig_ts.add_trace(go.Scatter(
    x=df_country['year'], y=df_country['PEACEFUL_PROTESTS'],
    mode='lines+markers', name='Peaceful Protests'
))
fig_ts.add_trace(go.Scatter(
    x=df_country['year'], y=df_country['VIOLENT_PROTESTS'],
    mode='lines+markers', name='Violent Protests'
))
fig_ts.update_layout(
    title=f"Protest Trends in {selected_country} (2021–2023)",
    xaxis_title="Year", yaxis_title="Number of Protests",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)
st.plotly_chart(fig_ts, use_container_width=True)

# Policy brief download
st.header("Policy Brief")
policy_brief_path = "policy_brief.pdf"
if os.path.exists(policy_brief_path):
    with open(policy_brief_path, "rb") as file:
        st.download_button(
            label="Download Policy Brief",
            data=file,
            file_name="policy_brief.pdf",
            mime="application/pdf"
        )
else:
    st.warning("Policy brief PDF not found. Please add 'policy_brief.pdf' to the directory.")
