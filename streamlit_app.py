# -*- coding: utf-8 -*-

import uuid
from dataclasses import dataclass, field

import requests
import streamlit as st

st.set_page_config(page_title="Clean Energy Regulator Data", page_icon="emrld_logo.png")
st.logo("emrld_logo.png")
state = st.session_state

# ── Available CER APIs ───────────────────────────────────────────
CER_APIS = {
    "NGER ID0121 - Greenhouse & Energy Info": "https://api.cer.gov.au/datahub-public/v1/api/ODataDataset/NGER/dataset/ID0121",
    "NGER ID0122 - 2016-17 Extract": "https://api.cer.gov.au/datahub-public/v1/api/ODataDataset/NGER/dataset/ID0041",  # replace with real URL
    "RET ID0109 - RET": "https://api.cer.gov.au/datahub-public/v1/api/ODataDataset/RET/dataset/ID0109",  # replace with real URL
}

CER_API_KEY = "YOUR_REAL_API_KEY"  # only if required
# ─────────────────────────────────────────────────────────────────


def flatten_record(record: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Recursively flatten a nested dict into a single-level dict."""
    items = {}
    for k, v in record.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_record(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


@st.cache_data(ttl=300)
def fetch_cer_data(url: str):
    try:
        headers = {}
        if CER_API_KEY and CER_API_KEY != "YOUR_REAL_API_KEY":
            headers["Authorization"] = f"Bearer {CER_API_KEY}"

        resp = requests.get(url, headers=headers, timeout=15)
        st.write(f"Request URL: {resp.url}")
        st.write(f"Status code: {resp.status_code}")

        resp.raise_for_status()
        payload = resp.json()

        records = payload.get("value") if isinstance(payload, dict) else payload
        return records or []

    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error: {e}")
        try:
            st.code(resp.text)
        except Exception:
            pass
        return []
    except Exception as e:
        st.error(f"Failed to load CER API data: {e}")
        return []


def records_to_table(records: list) -> dict:
    """Convert a list of (possibly nested) dicts into a column-keyed dict for st.table."""
    flat = [flatten_record(r) if isinstance(r, dict) else {"value": r} for r in records]
    all_keys = list(dict.fromkeys(k for row in flat for k in row))
    return {key: [row.get(key, "") for row in flat] for key in all_keys}


# ── Title with logo ──────────────────────────────────────────────
col1, col2 = st.columns([1, 8])
with col1:
    st.image("emrld_logo.png", width=60)
with col2:
    st.title("Clean Energy Regulator Data", anchor=False)
# ─────────────────────────────────────────────────────────────────

# ── API Selector ─────────────────────────────────────────────────
selected_label = st.selectbox("Select CER API", options=list(CER_APIS.keys()))
selected_url = CER_APIS[selected_label]
st.caption(f"URL: {selected_url}")
# ─────────────────────────────────────────────────────────────────

# ── Data Table ───────────────────────────────────────────────────
with st.expander("CER Dataset", expanded=True):
    if st.button("Load / Refresh CER data"):
        fetch_cer_data.clear()
        state.cer_records = fetch_cer_data(selected_url)

    if "cer_records" not in state:
        state.cer_records = fetch_cer_data(selected_url)

    if state.cer_records:
        st.write(f"Loaded {len(state.cer_records)} records from **{selected_label}**")
        st.table(records_to_table(state.cer_records))
    else:
        st.info("No CER data available. Click Load / Refresh CER data.")
# ─────────────────────────────────────────────────────────────────

# ── Available APIs list ──────────────────────────────────────────
st.divider()
st.subheader("Available CER APIs")

with st.container(gap=None, border=True):
    for label, url in CER_APIS.items():
        with st.container(horizontal=True, vertical_alignment="center"):
            st.write(f"**{label}**")
            st.caption(url)

# ── Add new API ──────────────────────────────────────────────────
st.divider()
with st.form(key="new_api_form", border=False):
    with st.container(horizontal=True, vertical_alignment="bottom"):
        st.text_input(
            "New API",
            label_visibility="collapsed",
            placeholder="Paste new CER API URL here",
            key="new_item_text",
        )
        st.form_submit_button(
            "Add",
            icon=":material/add:",
        )
