from pathlib import Path

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from tanf_data import (
    DATA_DIR,
    METRIC_LABELS,
    REGIONS,
    STATE_ABBREVIATIONS,
    STATE_NAMES,
    load_caseload_data,
    validate_caseload_data,
)


st.set_page_config(
    page_title="TANF Across America",
    page_icon="🇺🇸",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner="Loading official ACF tables...")
def get_data() -> pd.DataFrame:
    data = load_caseload_data(DATA_DIR)
    validate_caseload_data(data)
    return data


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    .stApp { background: #f5f7fa; color: #17283f; }
    [data-testid="stSidebar"] { background: #10233f; }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label { color: #edf4ff; }
    [data-testid="stSidebar"] [data-baseweb="select"] * { color: #17283f !important; }
    .hero {
        padding: 1.65rem 1.8rem 1.5rem; border-radius: 18px;
        background: linear-gradient(118deg, #10233f 0%, #173c60 68%, #216b78 100%);
        color: #f7fbff; margin-bottom: 1.2rem;
    }
    .hero h1 { font-family: Manrope, sans-serif; font-size: 2rem; margin: 0 0 .35rem; color: #fff; }
    .hero p { color: #d3e2ef; font-size: 1rem; margin: 0; }
    .section-title { font-family: Manrope, sans-serif; color: #152b47; font-weight: 700; }
    .note-card {
        border: 1px solid #dfe7ef; border-radius: 12px; padding: 1rem 1.1rem;
        background: white; min-height: 120px;
    }
    .muted { color: #64748b; font-size: .9rem; }
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #e3eaf1; border-radius: 12px;
        padding: .8rem 1rem;
    }
    div[data-testid="stMetricValue"] { font-size: 1.55rem; }
    div[data-testid="stMetricLabel"] { font-size: .88rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## TANF Across America")
    st.caption("A state-by-state view of federal TANF cash-assistance data.")
    st.divider()
    region = st.selectbox("Census region", ["All regions", *REGIONS.keys()])
    state_choices = [
        state
        for state in STATE_NAMES
        if region == "All regions" or state in REGIONS[region]
    ]
    if st.session_state.get("selected_state") not in state_choices:
        st.session_state["selected_state"] = state_choices[0]
    selected_state = st.selectbox(
        "State",
        state_choices,
        key="selected_state",
    )

    data = get_data()
    years = sorted(data["fiscal_year"].unique(), reverse=True)
    selected_year = st.selectbox("Fiscal year", years, format_func=lambda year: f"FY {year}")

    st.divider()
    st.caption("Federal tables only. No person-level records or combined demographic filters.")

st.markdown(
    """
    <div class="hero">
      <h1>TANF Across America</h1>
      <p>Explore monthly Temporary Assistance for Needy Families (TANF) cash-assistance caseloads by state.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

selected = data.loc[
    (data["state"] == selected_state) & (data["fiscal_year"] == selected_year)
].sort_values("month")
if selected.empty:
    st.error(f"No monthly caseload observations are available for {selected_state}, FY {selected_year}.")
    st.stop()

monthly_count = selected["month"].nunique()
fiscal_start = pd.Timestamp(year=selected_year - 1, month=10, day=1)
fiscal_end = pd.Timestamp(year=selected_year, month=9, day=30)
coverage = f"{fiscal_start:%b %Y} – {fiscal_end:%b %Y}"
averages = selected[list(METRIC_LABELS)].mean()

map_col, metrics_col = st.columns([1.13, 1], gap="large")
with map_col:
    st.markdown(f"### {selected_state}", help="Selected state highlighted; outlines show U.S. state boundaries.")
    map_figure = go.Figure(
        go.Choropleth(
            locations=[STATE_ABBREVIATIONS[state] for state in STATE_ABBREVIATIONS],
            z=[int(state == selected_state) for state in STATE_ABBREVIATIONS],
            customdata=list(STATE_ABBREVIATIONS),
            locationmode="USA-states",
            colorscale=[
                [0, "#e8edf2"],
                [0.499, "#e8edf2"],
                [0.5, "#32a6a0"],
                [1, "#32a6a0"],
            ],
            zmin=0,
            zmax=1,
            showscale=False,
            marker_line_color="#ffffff",
            marker_line_width=1,
            hovertemplate="<b>%{customdata}</b><extra></extra>",
        )
    )
    map_figure.update_layout(
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="#e8edf2",
            showlakes=True,
            lakecolor="#f5f7fa",
            bgcolor="#f5f7fa",
            showcountries=False,
            subunitcolor="#ffffff",
            showsubunits=True,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
        paper_bgcolor="#f5f7fa",
    )
    st.plotly_chart(map_figure, width="stretch", config={"displayModeBar": False})

with metrics_col:
    st.markdown("### Average monthly caseload")
    st.caption(f"FY {selected_year} · {coverage} · {monthly_count} months in this state’s file")
    metrics = ("total_recipients", "adults", "children", "families")
    metric_labels = {
        "total_recipients": "Avg total recipients",
        "adults": "Avg adult recipients",
        "children": "Avg child recipients",
        "families": "Avg families",
    }
    for row_start in (0, 2):
        metric_columns = st.columns(2)
        for column, metric in zip(metric_columns, metrics[row_start:row_start + 2]):
            with column:
                column.metric(
                    metric_labels[metric],
                    f"{averages[metric]:,.0f}" if pd.notna(averages[metric]) else "Unavailable",
                )
    st.caption(
        "Recipients are people; adults and children are recipient subgroups. "
        "Families are assistance units, not people."
    )

st.markdown("---")
chart_col, gap_col = st.columns([1.55, 1])
with chart_col:
    st.markdown("### Monthly caseload")
    st.caption(
        f"{selected_state} · FY {selected_year} ({coverage}). "
        "Monthly reported counts; families are kept distinct from individual recipients."
    )
    population = st.radio(
        "Population",
        ["People (total, adults, and children)", "Families"],
        horizontal=True,
        label_visibility="collapsed",
        key="population_view",
    )
    chart = go.Figure()
    series = (
        ("total_recipients", "Total recipients", "#176b87"),
        ("adults", "Adult recipients", "#e6903c"),
        ("children", "Child recipients", "#6378bd"),
    ) if population.startswith("People") else (("families", "Families", "#2c8a77"),)
    for column, label, color in series:
        chart.add_trace(
            go.Scatter(
                x=selected["month"],
                y=selected[column],
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=3),
                marker=dict(size=6),
                hovertemplate=f"%{{x|%b %Y}}<br>{label}: %{{y:,.0f}}<extra></extra>",
            )
        )
    chart.update_layout(
        height=400,
        margin=dict(l=0, r=12, t=16, b=10),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.13, x=0),
        xaxis=dict(title=None, tickformat="%b\n%Y", showgrid=False),
        yaxis=dict(title="Reported caseload", separatethousands=True, gridcolor="#e5eaf0"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="DM Sans, sans-serif", color="#43546b"),
    )
    st.plotly_chart(chart, width="stretch")

with gap_col:
    st.markdown("### What federal data supports")
    st.markdown(
        f"""
        <div class="note-card">
          <strong>Monthly cash assistance per recipient</strong><br>
          <span class="muted">Unavailable. ACF reports average monthly cash assistance per family, not per individual. FY2024: <strong>$673 per family per month</strong> nationally.</span>
        </div><br>
        <div class="note-card">
          <strong>Average recipient age</strong><br>
          <span class="muted">Unavailable. Recipient characteristics are published in age bands; exact ages cannot be calculated from those bands.</span>
        </div><br>
        <div class="note-card">
          <strong>Demographic detail</strong><br>
          <span class="muted">Annual state tables are available separately. No joint tables support combined filters in this stage.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
with st.expander("Sources, definitions, and data coverage"):
    st.markdown(
        """
        - [ACF FY2024 TANF caseload workbook](https://acf.gov/sites/default/files/documents/ofa/fy2024-15months-tanf-caseload.xlsx) · monthly families, all recipients, adults, and children, October 2023–December 2024.
        - [ACF FY2023 TANF caseload workbook](https://acf.gov/sites/default/files/documents/ofa/fy2023_tanf_caseload.xlsx) · monthly counts, October 2022–September 2023.
        - [ACF FY2022 TANF caseload workbook](https://acf.gov/sites/default/files/documents/ofa/fy2022_tanf_caseload.xlsx) · monthly counts, October 2021–December 2022.
        - [ACF FY2024 recipient characteristics and financial circumstances](https://acf.gov/ofa/data/characteristics-and-financial-circumstances-tanf-recipients-fiscal-year-2024) · annual state-level characteristics; includes age bands and financial measures reported per family.
        - Coverage currently shown: 50 states, FY2022–FY2024. The selected fiscal-year view uses the 12 months October–September; extra months in the FY2022/FY2024 files are excluded from those fiscal-year averages.
        - TANF cash assistance only; SSP-MOE is not included. Counts describe reported cases/recipients, not unique people over a year.
        """
    )
    st.markdown(
        "Download the data definitions, validation steps, and later-stage coverage plan."
    )
    st.download_button(
        "Download data coverage notes",
        data=(Path(__file__).parent / "docs" / "DATA_COVERAGE.md").read_text(encoding="utf-8"),
        file_name="TANF_DATA_COVERAGE.md",
        mime="text/markdown",
    )

with st.expander("Monthly values"):
    display = selected[["month", *METRIC_LABELS]].copy()
    display["month"] = display["month"].dt.strftime("%b %Y")
    display = display.rename(columns={"month": "Month", **METRIC_LABELS})
    st.dataframe(display, hide_index=True, width="stretch")

st.caption(
    "Sources: U.S. Department of Health and Human Services, Administration for Children and Families, "
    "Office of Family Assistance. Dashboard data is descriptive; demographic characteristics do not "
    "indicate misuse, and reaching a time limit does not by itself indicate improper receipt."
)
