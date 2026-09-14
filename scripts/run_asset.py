from cashdash.asset_classes import Savings, Stocks, Debt
from pathlib import Path
import matplotlib.pyplot as plt
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

#print("SAVINGS: ", asn.agg_data + bunq.agg_data)

stocks = Stocks(assets["DeGiro"]["filename"])
stocks.load_data()
stocks.calc_agg_data()

#print("STOCKS: ", stocks.agg_data)

debt = Debt(assets["DUO"]["filename"])
debt.load_data()
debt.calc_agg_data()

print(debt.agg_data)

total_data = asn.agg_data + bunq.agg_data + stocks.agg_data + debt.agg_data
#print("TOTAL: ", total_data)

plt.plot(total_data["Current worth"])
#plt.plot(debt.agg_data.index, debt.agg_data["Current worth"])
plt.xlabel("Date")
plt.ylabel("Portfolio worth")
plt.show()