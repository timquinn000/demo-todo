# -*- coding: utf-8 -*-
 
import uuid
from dataclasses import dataclass, field
 
import pandas as pd
import requests
import streamlit as st
 
st.set_page_config(page_title="Clean Energy Regulator Data", page_icon=":memo:")
 
# Declare alias for st.session_state, just for convenience.
state = st.session_state
 
CER_API_URL = (
    "https://api.cer.gov.au/datahub-public/v1/api/ODataDataset/RET/dataset/ID0110?select=%2A"
)
 
# Replace with your actual CER API key if required.
CER_API_KEY = "YOUR_API_KEY_HERE"
 
 
@st.cache_data(ttl=300)
def fetch_cer_data():
    try:
        headers = {"Authorization": f"Bearer {CER_API_KEY}"}
        resp = requests.get(CER_API_URL, headers=headers, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
        records = payload.get("value") if isinstance(payload, dict) else payload
        if not records:
            return []
        return records
    except Exception as e:
        st.error(f"Failed to load CER API data: {e}")
        return []
 
 
@dataclass
class Todo:
    text: str
    is_done: bool = False
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
 
 
if "todos" not in state:
    state.todos = [
        Todo(text="Link to first CER data set via API"),
        Todo(text="Link to second CER data set via API"),
        Todo(text="Link to third CER data set via API"),
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
 
with st.expander("CER dataset (ID0110)", expanded=True):
    if st.button("Load / Refresh CER data"):
        fetch_cer_data.clear()
        state.cer_records = fetch_cer_data()
 
    if state.cer_records:
        st.write(f"Loaded {len(state.cer_records)} records")
        df = pd.json_normalize(state.cer_records)
        st.dataframe(df)
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
 