from cashdash.asset_classes import Savings, Stocks, Debt
from pathlib import Path
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
        self.metadata = df_include
        self.data_dict = data_dict
            
            
    def calc_agg_data(self) -> pd.DataFrame:
        """ Calculates aggregated Spent, Interest and Current worth of all assets that are included. """        

        agg_data = None
        
        for _, row in self.metadata.iterrows():

            # Skip excluded assets
            if not row["TO_INCLUDE"]:
                continue

            # Add agg_data of specific file to existing agg_data when present
            asset_data = self.data_dict[row["FILENAME"]]
            if agg_data is None:
                agg_data = asset_data.copy()
            else:
                agg_data = agg_data + asset_data
 
        return agg_data
    
        
    def select(self, **allowed: list) -> None:
        """ As input takes button selection, e.g. {OWNER=["T"], ASSET_TYPE=["Stocks]}. Returns the matching filenames for selection. """
        
        # Create a mask value for every metadata entry 
        mask = pd.Series(True, index=self.metadata.index)
        
        # Keep entries in common with the button allowed input
        for col, values in allowed.items():
            mask &= self.metadata[col].isin(values)
        
        # Set all non-masked values to False. First step required to reset state when retoggling values
        self.metadata.loc[mask, "TO_INCLUDE"] = True
        self.metadata.loc[~mask, "TO_INCLUDE"] = False
        
        # Catch situation where all options in the mask are set to False. Prevents lookup issues with otherwise empty df
        if not mask.any():
            raise ValueError