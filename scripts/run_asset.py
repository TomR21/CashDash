from cashdash.asset_classes import ASNAsset

asn = ASNAsset()

asn.load_data()

asn.calc_agg_data()

print("RAW: ", asn.agg_data)

