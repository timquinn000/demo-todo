import uuid
from dataclasses import dataclass, field

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Clean Energy Regulator Data", page_icon=":memo:")
state = st.session_state

CER_API_URL = "https://api.cer.gov.au/datahub-public/v1/api/ODataDataset/NGER/dataset/ID0121"
CER_API_KEY = "YOUR_REAL_API_KEY"  # only if required


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


@dataclass
class Todo:
    text: str
    is_done: bool = False
    uid: uuid.UUID = field(default_factory=uuid.uuid4)