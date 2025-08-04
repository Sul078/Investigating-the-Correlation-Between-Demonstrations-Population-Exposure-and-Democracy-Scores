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

# Add ISO-3 codes
iso3_map = {
    'Belgium': 'BEL', 'France': 'FRA', 'Germany': 'DEU', 'Italy': 'ITA',
    'Netherlands': 'NLD', 'Poland': 'POL', 'Kazakhstan': 'KAZ', 'Kyrgyzstan': 'KGZ',
    'Uzbekistan': 'UZB', 'Tajikistan': 'TJK', 'Turkmenistan': 'TKM'
}
df['iso_alpha'] = df['country_name'].map(iso3_map)

# Centroids for Scattergeo
centroids = {
    'Belgium': (50.85, 4.35), 'France': (46.6, 1.88), 'Germany': (51.17, 10.45), 'Italy': (41.87, 12.57),
    'Netherlands': (52.13, 5.29), 'Poland': (51.92, 19.14), 'Kazakhstan': (48.02, 66.92),
    'Kyrgyzstan': (41.20, 74.76), 'Uzbekistan': (41.38, 64.59), 'Tajikistan': (38.86, 71.28),
    'Turkmenistan': (38.97, 59.56)
}

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

# Filter data for selected year
df_year = df[df['year'] == selected_year]

# Choropleth map with Scattergeo
st.header(f"Democracy Score by Country ({selected_year})")
fig_map = go.Figure()
for yr in years:
    df_yr = df[df['year'] == yr]
    lat, lon, text = [], [], []
    for _, row in df_yr.iterrows():
        ylat, ylon = centroids.get(row['country_name'], (0, 0))
        lat.append(ylat)
        lon.append(ylon)
        text.append(
            f"<b>{row['country_name']} — {yr}</b><br>"
            f"🗳️ Democracy Score: {row['DEMOCRACY_SCORE']:.3f}<br>"
            f"Peaceful Protests: {row['PEACEFUL_PROTESTS']}<br>"
            f"Violent Protests: {row['VIOLENT_PROTESTS']}<br>"
            f"Fatalities: {row['TOTAL_FATALITIES']}<br>"
            f"Violent %: {row['VIOLENT_FREQ_PERCENT']:.1f}%<br>"
            f"Correlation: {row['CORRELATION']:.2f}"
        )
    fig_map.add_trace(go.Choropleth(
        locations=df_yr['iso_alpha'],
        z=df_yr['DEMOCRACY_SCORE'],
        locationmode='ISO-3',
        colorscale='Viridis',
        colorbar_title='Democracy Score',
        zmin=df['DEMOCRACY_SCORE'].min(),
        zmax=df['DEMOCRACY_SCORE'].max(),
        hoverinfo='skip',
        visible=(yr == selected_year)
    ))
    fig_map.add_trace(go.Scattergeo(
        lat=lat,
        lon=lon,
        mode='markers',
        marker=dict(size=13, color='white', line=dict(color='black', width=2)),
        text=text,
        hoverinfo='text',
        name=str(yr),
        visible=(yr == selected_year)
    ))

fig_map.update_layout(
    geo=dict(
        projection_type="mercator",
        showcoastlines=False,
        showland=True,
        landcolor="rgb(229, 229, 229)",
        showcountries=True,
        countrycolor="LightGray",
        lataxis_range=[30, 60],
        lonaxis_range=[-15, 90]
    )
)
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

# Scatter Plot (Violent % vs Democracy Score)
st.header("Violent Protest Frequency vs. Democracy Score")
fig_scatter = px.scatter(
    df_year,
    x='DEMOCRACY_SCORE',
    y='VIOLENT_FREQ_PERCENT',
    color='country_name',
    size='TOTAL_FATALITIES',
    hover_name='country_name',
    title=f"Violent Protest Frequency vs. Democracy Score ({selected_year})",
    labels={
        'DEMOCRACY_SCORE': 'Democracy Score',
        'VIOLENT_FREQ_PERCENT': '% Violent Protests'
    }
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Policy brief download
st.header("Policy Brief")
if os.path.exists("policy_brief.pdf"):
    with open("policy_brief.pdf", "rb") as file:
        st.download_button(
            label="Download Policy Brief",
            data=file,
            file_name="policy_brief.pdf",
            mime="application/pdf"
        )
else:
    st.warning("Policy brief PDF not found. Please add 'policy_brief.pdf' to the directory.")
