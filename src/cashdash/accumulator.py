from cashdash.asset_classes import Savings, Stocks, Debt
from pathlib import Path
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import json


# 
class Accumulator():
    
    def __init__(self) -> None:
        base_dir = str(Path.cwd())
        with open(base_dir + r"\config\asset_types.json", 'r') as f:
            self.assets = json.load(f)
            
            
    def load_assets(self) -> None:
        """ Loads all assets from filenames mentioned in asset_types.json. 
        Stores informational df with inclusion boolean and dictionary of filenames and corresponding df in self. """
        
        print("Loading data...")
        
        # Obtain account data and store owner, asset type and company name
        include_list = []
        data_dict = dict()
        for owner in self.assets:
            for asset_type in self.assets[owner]:
                for company in self.assets[owner][asset_type]:
                    filename = self.assets[owner][asset_type][company]

                    if asset_type == "Savings":
                        account = Savings(filename)
                        account.load_data()
                        account.calc_agg_data()
                    elif asset_type == "Stocks":
                        account = Stocks(filename)
                        account.load_data()
                        account.calc_agg_data()
                    elif asset_type == "Debt":
                        account = Debt(filename)
                        account.load_data()
                        account.calc_agg_data()
                    else:
                        raise ValueError("Unknown asset type")
        
                    include_list.append([owner, asset_type, company, filename, True])
                    data_dict.update({filename: account.get_agg_data()})
        
        df_include = pd.DataFrame({
            "OWNER": [row[0] for row in include_list], 
            "ASSET_TYPE": [row[1] for row in include_list],
            "COMPANY": [row[2] for row in include_list],
            "FILENAME": [row[3] for row in include_list],
            "TO_INCLUDE": [row[4] for row in include_list]
        })
        
        # Store include data table and data dict in self
        self.included_data = df_include
        self.data_dict = data_dict
            
            
    def calc_agg_data(self) -> pd.DataFrame:
        """ Calculates aggregated Spent, Interest and Current worth of all assets that are included. """        

        agg_data = None
        
        for _, row in self.included_data.iterrows():

            # Skip excluded assets
            if not row["TO_INCLUDE"]:
                print("Excluded ", row["FILENAME"])
                continue

            # Add agg_data of specific file to existing agg_data when present
            asset_data = self.data_dict[row["FILENAME"]]
            if agg_data is None:
                agg_data = asset_data.copy()
            else:
                agg_data = agg_data + asset_data
 
        return agg_data
    
    
    def update(self, filename: str, toggle: bool) -> None:
        df = self.included_data
        df.loc[df["FILENAME"] == filename, "TO_INCLUDE"] = toggle
        
        self.included_data = df