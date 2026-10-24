
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
    background: linear-gradient(135deg, #fff8f0, #ffeddc, #fffaf5);
}
h1, h2, h3 {
    color: #925b3c;
}
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid #f0d4bf;
    padding: 18px;
    border-radius: 16px;
}
.stButton button, .stDownloadButton button {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

data_path = Path(__file__).parent / "Dataset.csv"

try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    st.error("Dataset.csv not found. Place it in the same folder as app.py.")
    st.stop()

required_columns = {"show_id", "title", "type", "release_year"}
missing_columns = required_columns - set(df.columns)

if missing_columns:
    st.error(
        "Dataset is missing required columns: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()

df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")
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

col1, col2, col3 = st.columns(3)

col1.metric("Titles Analyzed", f"{len(df):,}")
col2.metric("Earliest Release Year", str(df["release_year"].min()))
col3.metric("Latest Release Year", str(df["release_year"].max()))

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
    line=dict(color="#d98960", width=3),
    marker=dict(size=5)
)

line_chart.update_layout(
    template="plotly_white",
    hovermode="x unified",
    margin=dict(l=10, r=10, t=55, b=10)
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
    title="Years with the Most Netflix Titles"
)

bar_chart.update_traces(
    marker_color="#e8ad88",
    textposition="outside",
    cliponaxis=False
)

bar_chart.update_layout(
    template="plotly_white",
    margin=dict(l=10, r=35, t=55, b=10)
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
default_start = max(2000, min_year)

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

left, middle, right = st.columns(3)

left.metric("Titles in Selected Range", f"{len(filtered):,}")
middle.metric("Movies", f"{(filtered['type'] == 'Movie').sum():,}")
right.metric("TV Shows", f"{(filtered['type'] == 'TV Show').sum():,}")

preview_columns = [
    col for col in [
        "title", "type", "release_year", "country", "rating"
    ] if col in filtered.columns
]

st.dataframe(
    filtered[preview_columns].head(200),
    width="stretch",
    hide_index=True
)

st.caption("Showing up to 200 matching titles in the preview.")

st.markdown("---")
st.subheader("📥 Download Analysis")

st.download_button(
    label="Download Release-Year Summary CSV",
    data=year_counts.to_csv(index=False).encode("utf-8"),
    file_name="release_year_analysis.csv",
    mime="text/csv",
    key="download_year_summary"
)

st.download_button(
    label="Download Filtered Titles CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_release_year_titles.csv",
    mime="text/csv",
    key="download_filtered_titles"
)

st.markdown("---")
st.caption(
    "Netflix Release-Year Analysis | Python • Pandas • Plotly • Streamlit"
)
