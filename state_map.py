"""Clickable Plotly state map with one-shot selection events for Streamlit."""

import streamlit as st


def state_map(**kwargs):
    """Register in the current Streamlit runtime and mount the map."""
    component = st.components.v2.component(
        "tanf_state_map",
        html='<div class="state-map" aria-label="United States map. Click a state to select it."></div>',
        css=".state-map { width: 100%; height: 300px; } .state-map .choroplethlayer path { cursor: pointer; }",
        isolate_styles=False,
        js="""
        export default function({ parentElement, data, setTriggerValue }) {
            const map = parentElement.querySelector(".state-map");
            let disposed = false;
            let observer;
            if (!window.tanfPlotlyReady) {
                window.tanfPlotlyReady = new Promise((resolve, reject) => {
                    const script = document.createElement("script");
                    script.src = "https://cdn.plot.ly/plotly-3.0.1.min.js";
                    script.onload = () => resolve(window.Plotly);
                    script.onerror = () => reject(new Error("Map library could not load"));
                    document.head.appendChild(script);
                });
            }
            window.tanfPlotlyReady.then(async (Plotly) => {
                if (disposed) return;
                await Plotly.newPlot(map, data.data, data.layout, {
                    displayModeBar: false, responsive: true, scrollZoom: false
                });
                if (disposed) { Plotly.purge(map); return; }
                map.on("plotly_click", (event) => {
                    const state = event.points?.[0]?.customdata;
                    if (typeof state === "string") setTriggerValue("state_click", state);
                });
                observer = new ResizeObserver(() => Plotly.Plots.resize(map));
                observer.observe(map);
            }).catch(() => {
                if (!disposed) map.textContent = "Map unavailable. Select a state using the sidebar.";
            });
            return () => {
                disposed = true;
                observer?.disconnect();
                if (map.removeAllListeners) map.removeAllListeners("plotly_click");
                if (window.Plotly && map.data) window.Plotly.purge(map);
            };
        }
        """,
    )
    return component(**kwargs)
