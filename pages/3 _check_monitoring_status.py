

import json
import math
from datetime import datetime, timezone

import pandas as pd
import pytz
import requests
import streamlit as st

TOTAL_ENERGY_USAGE = 'Total Electricty Usage'


def runApp():
    status = requests.get(
        st.secrets["TAILSCALE_URL"], auth=(st.secrets["TAILSCALE_KEY"], ''))

    print(status)

    res = json.loads(status.text)
    last_seen = res['lastSeen']
    print(res['lastSeen'])
    timezone = pytz.timezone("Pacific/Auckland")
    tailscale_datetime = datetime.fromisoformat(
        last_seen[:-1] + '+00:00').astimezone(tz=timezone)

    st.metric("Solar monitor last seen", str(tailscale_datetime), delta=None,
              delta_color="normal", help=None, label_visibility="visible")


runApp()
