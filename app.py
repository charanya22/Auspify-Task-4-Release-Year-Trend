
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Netflix Release-Year Trend Analysis",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #F3E8FF 0%, #E8EAFE 50%, #FCE7F3 100%);
}
h1, h2, h3 {
    color: #5B3F8C !important;
    font-weight: 750 !important;
}
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid #D8C9F0;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 4px 14px rgba(91, 63, 140, 0.08);
}
[data-testid="stMetricLabel"] {
    color: #75658F !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: #5B3F8C !important;
    font-weight: 800 !important;
}
.stButton button, .stDownloadButton button {
    background: linear-gradient(90deg, #8B72C7, #B18AD9);
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
}
.stButton button:hover, .stDownloadButton button:hover {
    background: linear-gradient(90deg, #7559B5, #986CCB);
    color: white !important;
}
[data-testid="stDataFrame"] {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid #DED3F0;
    border-radius: 12px;
    overflow: hidden;
}
hr {
    border-color: #D8C9F0;
}
[data-testid="stAlert"] {
    border-radius: 12px;
}
.stCaption {
    color: #76658E;
}
[data-testid="stSidebar"] {
    background: #F0E8FC;
}
</style>
""", unsafe_allow_html=True)

data_path = Path(__file__).parent / "Dataset.csv"

try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    st.error("Dataset.csv was not found. Place it in the same folder as app.py.")
    st.stop()

required_columns = {"show_id", "title", "type", "release_year"}
missing_columns = required_columns - set(df.columns)

if missing_columns:
    st.error(
        "Dataset is missing required columns: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()

df["release_year"] = pd.to_numeric(
    df["release_year"], errors="coerce"
)

df = df.dropna(subset=["release_year"]).copy()
df["release_year"] = df["release_year"].astype(int)

year_counts = (
    df.groupby("release_year")
    .size()
    .reset_index(name="Titles")
    .sort_values("release_year")
)

st.title("📈 Netflix Release-Year Trend Analysis")
st.caption("Auspify Technologies | Data Analysis Using Python")
st.markdown("---")

c1, c2, c3 = st.columns(3)

c1.metric("Titles Analyzed", f"{len(df):,}")
c2.metric("Earliest Release Year", str(df["release_year"].min()))
c3.metric("Latest Release Year", str(df["release_year"].max()))

st.markdown("---")
st.subheader("📊 Netflix Titles by Release Year")

line_chart = px.line(
    year_counts,
    x="release_year",
    y="Titles",
    markers=True,
    labels={
        "release_year": "Release Year",
        "Titles": "Number of Titles"
    },
    title="Distribution of Netflix Titles Across Release Years"
)

line_chart.update_traces(
    line=dict(color="#8B72C7", width=3),
    marker=dict(
        size=6,
        color="#E7A8D8",
        line=dict(color="#FFFFFF", width=1)
    ),
    hovertemplate="Year: %{x}<br>Titles: %{y:,}<extra></extra>"
)

line_chart.update_layout(
    template="plotly_white",
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0.55)",
    font=dict(color="#66508F"),
    title_font=dict(color="#5B3F8C"),
    hovermode="x unified",
    xaxis=dict(
        title="Release Year",
        gridcolor="#E5DDF2"
    ),
    yaxis=dict(
        title="Number of Titles",
        gridcolor="#E5DDF2",
        rangemode="tozero"
    ),
    margin=dict(l=10, r=10, t=60, b=10)
)

st.plotly_chart(
    line_chart,
    width="stretch",
    key="release_year_line_chart"
)

st.markdown("---")
st.subheader("🏆 Top 10 Release Years by Title Count")

top10 = (
    year_counts.nlargest(10, "Titles")
    .sort_values("Titles", ascending=True)
)

bar_chart = px.bar(
    top10,
    x="Titles",
    y="release_year",
    orientation="h",
    text="Titles",
    labels={
        "release_year": "Release Year",
        "Titles": "Number of Titles"
    },
    title="Years with the Most Netflix Titles",
    color="Titles",
    color_continuous_scale=["#E8EAFE", "#C3B1E8", "#8B72C7"]
)

bar_chart.update_traces(
    textposition="outside",
    cliponaxis=False,
    hovertemplate="Year: %{y}<br>Titles: %{x:,}<extra></extra>"
)

bar_chart.update_layout(
    template="plotly_white",
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0.55)",
    font=dict(color="#66508F"),
    title_font=dict(color="#5B3F8C"),
    coloraxis_showscale=False,
    xaxis=dict(
        title="Number of Titles",
        gridcolor="#E5DDF2",
        rangemode="tozero"
    ),
    yaxis=dict(
        title="Release Year",
        gridcolor="#E5DDF2"
    ),
    margin=dict(l=10, r=35, t=60, b=10)
)

st.plotly_chart(
    bar_chart,
    width="stretch",
    key="top_release_years_chart"
)

st.markdown("---")
st.subheader("🔎 Explore Titles by Release Year")

min_year = int(df["release_year"].min())
max_year = int(df["release_year"].max())
default_start = min(max(2000, min_year), max_year)

start_year, end_year = st.slider(
    "Select a release-year range",
    min_value=min_year,
    max_value=max_year,
    value=(default_start, max_year),
    key="release_year_range"
)

filtered = df[
    df["release_year"].between(start_year, end_year)
].copy()

c1, c2, c3 = st.columns(3)

c1.metric("Titles in Selected Range", f"{len(filtered):,}")
c2.metric(
    "Movies",
    f"{(filtered['type'] == 'Movie').sum():,}"
)
c3.metric(
    "TV Shows",
    f"{(filtered['type'] == 'TV Show').sum():,}"
)

preview_columns = [
    column for column in [
        "title", "type", "release_year", "country", "rating"
    ]
    if column in filtered.columns
]

st.dataframe(
    filtered[preview_columns].head(200),
    width="stretch",
    hide_index=True
)

st.caption("Showing up to 200 matching titles in the preview.")

st.markdown("---")
st.subheader("📥 Download Analysis")

c1, c2 = st.columns(2)

with c1:
    st.download_button(
        "📄 Download Release-Year Summary CSV",
        data=year_counts.to_csv(index=False).encode("utf-8"),
        file_name="release_year_analysis.csv",
        mime="text/csv",
        key="download_year_summary",
        use_container_width=True
    )

with c2:
    st.download_button(
        "📊 Download Filtered Titles CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_release_year_titles.csv",
        mime="text/csv",
        key="download_filtered_titles",
        use_container_width=True
    )

st.markdown("---")
st.caption("Netflix Release-Year Analysis | Python • Pandas • Plotly • Streamlit")
