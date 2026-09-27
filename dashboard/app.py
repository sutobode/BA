"""Decision dashboard (SPEC §11). Owner: M3.

Reads ONLY files in outputs/tables (produced by the pipeline). No model training or data
cleaning happens here. All figures are simulated expected values under stated assumptions.
Run: docker compose up dashboard  →  http://localhost:8501
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

TABLES = Path(__file__).resolve().parents[1] / "outputs" / "tables"
REQUIRED = ["scenario_results.csv", "policy_comparison.csv", "customer_targeting_table.csv",
            "rfm_segments.csv", "break_even.csv"]
BANNER = ("Results are scenario-based simulations under stated assumptions. Online Retail II contains "
          "no promotion treatment/control; figures are not causal uplift or ROI.")
POLICY_NAMES = {"A": "A · No promotion", "B": "B · Random (non-targeted)", "C": "C · RFM top-K",
                "D": "D · Model + value (EIM)", "E": "E · Lowest probability"}


def kpis(results: pd.DataFrame, scenario: str, lift: str, basis: str, frac: float, policy: str = "D") -> dict:
    """The 5 decision KPIs (SPEC §1.8), totals over the evaluation snapshots. B = mean over seeds."""
    r = results[(results["scenario"] == scenario) & (results["lift_structure"] == lift)
                & (results["value_basis"] == basis) & (results["capacity_fraction"].round(6) == round(frac, 6))
                & (results["policy"] == policy)]
    if policy == "B":
        r = r.groupby("seed").sum(numeric_only=True).mean().to_frame().T
    n = float(r["target_count"].sum())
    eim = float(r["simulated_eim"].sum())
    return {"Targeted customers": n,
            "Expected future value (£)": float(r["expected_future_value"].sum()),
            "Expected promotion cost (£)": float(r["expected_promotion_cost"].sum()),
            "Simulated incremental margin (£)": eim,
            "Margin per targeted customer (£)": eim / n if n else 0.0,
            "Capacity K (total)": float(r["capacity_k"].sum())}


def main() -> None:  # pragma: no cover - UI
    import streamlit as st

    st.set_page_config(page_title="Promotion Targeting — Topic 1", layout="wide")
    st.title("Customer Value & Promotion Targeting")
    st.warning(BANNER)
    missing = [f for f in REQUIRED if not (TABLES / f).exists()]
    if missing:
        st.info("Pipeline outputs not found yet: " + ", ".join(missing)
                + ". Run `docker compose run --rm pipeline run all`.")
        st.stop()

    @st.cache_data
    def load(name: str) -> pd.DataFrame:
        return pd.read_csv(TABLES / name, dtype={"customer_id": str})

    res, comp, tt = load("scenario_results.csv"), load("policy_comparison.csv"), load("customer_targeting_table.csv")
    seg, be = load("rfm_segments.csv"), load("break_even.csv")
    split = comp["evaluation_split"].iloc[0]

    with st.sidebar:
        st.header("Scenario controls")
        scen = list(dict.fromkeys(res["scenario"]))
        scenario = st.selectbox("Scenario", scen, index=scen.index("base") if "base" in scen else 0,
                                help="illustrative_breakeven = what the assumptions would need to be (not a plan)")
        lift = st.selectbox("Incremental-lift structure (assumption)", ["constant", "persuadable"])
        frac = st.select_slider("Campaign capacity K (% of eligible)", sorted(res["capacity_fraction"].unique()),
                                value=0.1, format_func=lambda x: f"{x:.0%}")
        basis = st.radio("Evaluate with", ["actual_outcome", "model_p"],
                         format_func=lambda x: {"actual_outcome": "realized repeat outcome (primary)",
                                                "model_p": "model probability (planning)"}[x])
        st.caption(f"Evaluation snapshots: **{split}**")
        params = tt[tt["scenario"] == scenario][["discount_rate", "gross_margin", "contact_cost"]].iloc[0]
        st.markdown(f"**Assumptions** — discount d = {params.discount_rate:.0%}, gross margin m = "
                    f"{params.gross_margin:.0%}, contact cost c = £{params.contact_cost:.2f}")

    tab1, tab2, tab3 = st.tabs(["Overview", "Promotion scenario", "Actionable customers"])

    with tab1:
        s = seg[seg["split"] == split] if split in set(seg["split"]) else seg
        c1, c2, c3 = st.columns(3)
        c1.metric("Eligible customer-snapshots", f"{int(s['customers'].sum()):,}")
        c2.metric("Observed 90-day repeat rate", f"{(s['repeat_rate'] * s['customers']).sum() / s['customers'].sum():.1%}")
        c3.metric("Segments", len(s))
        st.subheader("Segment size, value and repeat behaviour")
        st.dataframe(s.drop(columns=["split"]).style.format({"repeat_rate": "{:.1%}", "median_monetary": "£{:,.0f}",
                                                               "median_aov": "£{:,.0f}", "median_recency": "{:.0f} d"}),
                     use_container_width=True)
        st.bar_chart(s.set_index("customer_segment")[["customers"]])
        st.bar_chart(s.set_index("customer_segment")[["repeat_rate"]])

    with tab2:
        k = kpis(res, scenario, lift, basis, frac, "D")
        cols = st.columns(5)
        for col, name in zip(cols, list(k)[:5]):
            v = k[name]
            col.metric(name, f"{v:,.0f}" if name == "Targeted customers" else f"£{v:,.0f}")
        st.caption(f"Policy D targeted {k['Targeted customers']:.0f} of a capacity of {k['Capacity K (total)']:.0f}: "
                   "it only targets customers with positive simulated incremental margin.")
        pstar = be[be["scenario"] == scenario]
        st.markdown("**Break-even probability p\\*** (constant lift): target only if predicted repeat probability < p\\*  — "
                    + ", ".join(f"V=£{r.value:,.0f}: p\\*={r.p_star:.3f}" for r in pstar.itertuples()))
        st.subheader("Policy comparison (same customers, same capacity)")
        c = comp[(comp["scenario"] == scenario) & (comp["lift_structure"] == lift) & (comp["value_basis"] == basis)
                 & (comp["capacity_fraction"].round(6) == round(frac, 6))].copy()
        c["policy"] = c["policy"].map(POLICY_NAMES)
        st.dataframe(c[["policy", "target_count", "expected_promotion_cost", "simulated_eim", "simulated_eim_p5",
                        "simulated_eim_p95", "eim_per_target"]].style.format(precision=1), use_container_width=True)
        st.bar_chart(c.set_index("policy")[["simulated_eim"]])
        st.caption("B shows the mean and 5–95% range over random seeds. Negative values mean the discount given to "
                   "customers who would have bought anyway exceeds the assumed incremental margin.")

    with tab3:
        t = tt[tt["scenario"] == scenario].copy()
        only = st.checkbox("Show only TARGET", value=True)
        segs = st.multiselect("Segments", sorted(t["customer_segment"].unique()))
        if only:
            t = t[t["recommended_action"] == "TARGET"]
        if segs:
            t = t[t["customer_segment"].isin(segs)]
        st.caption("Priority = high value × low natural repeat probability (policy D, constant lift, K = 10%).")
        st.scatter_chart(tt[tt["scenario"] == scenario], x="repeat_purchase_probability", y="customer_value_proxy",
                         color="recommended_action")
        show = ["decision_date", "customer_id", "customer_segment", "repeat_purchase_probability",
                "customer_value_proxy", "expected_promotion_cost", "simulated_expected_incremental_margin",
                "target_rank", "recommended_action"]
        st.dataframe(t[show].sort_values(["decision_date", "target_rank"]), use_container_width=True)
        st.download_button("Download CSV", t[show].to_csv(index=False), file_name=f"targets_{scenario}.csv")


if __name__ == "__main__":
    main()
