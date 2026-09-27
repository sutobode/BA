"""Decision dashboard (SPEC §11, CODE SPEC §10 step 11). Owner: M3.

Reads ONLY files in outputs/tables (produced by the pipeline). No model training or
data cleaning happens here. This skeleton runs before the pipeline has produced
outputs and tells the user what is missing.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

TABLES = Path(__file__).resolve().parents[1] / "outputs" / "tables"
REQUIRED = ["scenario_results.csv", "policy_comparison.csv", "customer_targeting_table.csv"]
BANNER = ("Results are scenario-based simulations under stated assumptions. Online Retail II contains "
          "no promotion treatment/control; figures are not causal uplift or ROI.")

st.set_page_config(page_title="Promotion Targeting — Topic 1", layout="wide")
st.title("Customer Value & Promotion Targeting")
st.warning(BANNER)

missing = [f for f in REQUIRED if not (TABLES / f).exists()]
if missing:
    st.info("Pipeline outputs not found yet: " + ", ".join(missing)
            + ". Run `docker compose run --rm pipeline run all`.")
    st.stop()

# TODO(M3, T5.3): implement the 3 views of SPEC §11 — Overview, Promotion Scenario, Actionable view.
results = pd.read_csv(TABLES / "scenario_results.csv")
st.dataframe(results.head(50))
