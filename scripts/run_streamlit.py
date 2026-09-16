from cashdash.asset_classes import Savings, Stocks, Debt
from pathlib import Path
import matplotlib.pyplot as plt
import streamlit as st
import json

base_dir = str(Path.cwd())
with open(base_dir + r"\config\asset_types.json", 'r') as f:
    assets = json.load(f)

# Load savings data
asn = Savings(assets["T"]["Savings"]["ASN"])
asn.load_data()
asn.calc_agg_data()

df = asn.agg_data

# Plot figure
fig, ax = plt.subplots()
ax.plot(df["Current worth"])
ax.set_xlabel("Date")
ax.set_ylabel("Portfolio worth (€)")
ax.set_title("Asset growth over time")

# Homepage
st.header("Portfolio Growth")
st.pyplot(fig)
st.dataframe(df.tail(10), width='stretch')
