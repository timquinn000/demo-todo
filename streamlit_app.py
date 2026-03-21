# -*- coding: utf-8 -*-

import uuid
from dataclasses import dataclass, field

import requests
import streamlit as st

st.set_page_config(page_title="Clean Energy Regulator Data", page_icon="emrld_logo.png")
st.logo("emrld_logo.png")
state = st.session_state

CER_API_URL = "https://api.cer.gov.au/datahub-public/v1/api/ODataDataset/NGER/dataset/ID0121"
CER_API_KEY = "YOUR_REAL_API_KEY"  # only if required


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
def fetch_cer_data():
    try:
        headers = {}
        if CER_API_KEY and CER_API_KEY != "YOUR_REAL_API_KEY":
            headers["Authorization"] = f"Bearer {CER_API_KEY}"

        resp = requests.get(CER_API_URL, headers=headers, timeout=15)
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


@dataclass
class Todo:
    text: str
    is_done: bool = False
    uid: uuid.UUID = field(default_factory=uuid.uuid4)


if "todos" not in state:
    state.todos = [
        Todo(text=CER_API_URL),
        #Todo(text="Link to second CER data set via API"),
        #Todo(text="Link to third CER data set via API"),
    ]

if "cer_records" not in state:
    state.cer_records = fetch_cer_data()


def remove_todo(i):
    state.todos.pop(i)


def add_todo():
    state.todos.append(Todo(text=state.new_item_text))
    state.new_item_text = ""


def check_todo(i, new_value):
    state.todos[i].is_done = new_value


def delete_all_checked():
    state.todos = [t for t in state.todos if not t.is_done]


with st.container(horizontal_alignment="left"):
    st.title(
        ":orange[:material/checklist:] Clean Energy Regulator Data",
        width="content",
        anchor=False,
    )

with st.expander("CER dataset (ID0121)", expanded=True):
    if st.button("Load / Refresh CER data"):
        fetch_cer_data.clear()
        state.cer_records = fetch_cer_data()

    if state.cer_records:
        st.write(f"Loaded {len(state.cer_records)} records")
        st.table(records_to_table(state.cer_records))
    else:
        st.info("No CER data available yet. Click Load / Refresh CER data.")

with st.form(key="new_item_form", border=False):
    with st.container(
        horizontal=True,
        vertical_alignment="bottom",
    ):
        st.text_input(
            "New item",
            label_visibility="collapsed",
            placeholder="Add to-do item",
            key="new_item_text",
        )

        st.form_submit_button(
            "Add",
            icon=":material/add:",
            on_click=add_todo,
        )

if state.todos:
    with st.container(gap=None, border=True):
        for i, todo in enumerate(state.todos):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.checkbox(
                    todo.text,
                    value=todo.is_done,
                    width="stretch",
                    on_change=check_todo,
                    args=[i, not todo.is_done],
                    key=f"todo-chk-{todo.uid}",
                )
                st.button(
                    ":material/delete:",
                    type="tertiary",
                    on_click=remove_todo,
                    args=[i],
                    key=f"delete_{i}", 
                )

    with st.container(horizontal=True, horizontal_alignment="center"):
        st.button(
            ":small[Delete all checked]",
            icon=":material/delete_forever:",
            type="tertiary",
            on_click=delete_all_checked,
        )

else:
    st.info("No to-do items. Go fly a kite! :material/family_link:")
