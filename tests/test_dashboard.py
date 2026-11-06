from pathlib import Path
from streamlit.testing.v1 import AppTest

from tanf_data import METRIC_LABELS, REGIONS, load_caseload_data


def dashboard():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run(timeout=60)
    assert not app.exception
    return app


def test_initial_and_clear_selection_zero_the_display():
    app = dashboard()
    assert [m.value for m in app.metric] == ["0"] * 5
    assert app.dataframe[0].value.empty
    app.selectbox(key="selected_state").select("California").run()
    assert not app.exception
    assert app.metric[0].value != "0"
    app.button[0].click().run()
    assert not app.exception
    assert app.selectbox(key="selected_state").value is None
    assert app.selectbox(key="selected_region").value is None
    assert [m.value for m in app.metric] == ["0"] * 5
    assert app.dataframe[0].value.empty


def test_region_totals_match_federal_monthly_sums():
    app = dashboard()
    data = load_caseload_data()
    for region in REGIONS:
        app.selectbox(key="selected_region").select(region).run()
        assert not app.exception
        assert app.selectbox(key="selected_state").value is None
        rows = data.loc[(data.fiscal_year == 2024) & data.state.isin(REGIONS[region])]
        totals = rows.groupby("month")[list(METRIC_LABELS)].sum()
        for metric, column in zip(app.metric, ("total_recipients", "adults", "children", "families")):
            assert metric.value == f"{totals[column].mean():,.0f}"
        assert app.metric[4].value == f"{totals['children'].sum() / totals['families'].sum():.2f}"
        displayed = app.dataframe[0].value
        assert len(displayed) == 12
        assert displayed["Total recipients"].tolist() == totals["total_recipients"].tolist()


def test_region_replaces_state_and_clearing_state_resets_region():
    app = dashboard()
    app.selectbox(key="selected_state").select("California").run()
    app.selectbox(key="selected_region").select("Northeast").run()
    assert not app.exception
    assert app.selectbox(key="selected_state").value is None
    app.selectbox(key="selected_state").select("New York").run()
    app.selectbox(key="selected_state").set_value(None).run()
    assert not app.exception
    assert app.selectbox(key="selected_region").value is None
    assert [m.value for m in app.metric] == ["0"] * 5


def test_child_recipients_per_family_uses_unrounded_federal_counts():
    app = dashboard()
    app.selectbox(key="selected_state").select("Alaska").run()
    app.selectbox[2].select(2022).run()
    assert not app.exception
    data = load_caseload_data()
    rows = data.loc[(data.state == "Alaska") & (data.fiscal_year == 2022)]
    assert app.metric[4].label == "Avg child recipients per family*"
    assert app.metric[4].value == f"{rows.children.sum() / rows.families.sum():.2f}"
    assert any("no adult recipient" in c.value for c in app.caption)
