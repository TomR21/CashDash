from cashdash.asset_classes import Savings, Stocks
from pathlib import Path
import json

base_dir = str(Path.cwd())
with open(base_dir + r"\config\asset_types.json", 'r') as f:
    assets = json.load(f)

# Load savings data
asn = Savings(assets["ASN"]["filename"])
asn.load_data()
asn.calc_agg_data()

bunq = Savings(assets["Bunq"]["filename"])
bunq.load_data()
bunq.calc_agg_data()

# print("TOTAL: ", asn.agg_data + bunq.agg_data)

stocks = Stocks(assets["DeGiro"]["filename"])
stocks.load_data()
stocks.calc_agg_data()

print("STOCKS: ", stocks.agg_data)