from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
import numpy as np
import json

class AssetClass(ABC):
    
    # Load setting parameters
    base_dir = str(Path.cwd())
    with open(base_dir + r"\config\settings.json", 'r') as f:
        settings = json.load(f)
        
    START_DATE = settings["START_DATE"]
    END_DATE = settings["END_DATE"]
    INTERVAL_DUR = settings["INTERVAL_DUR"]
    
    @abstractmethod
    def load_data(self) -> None:
        pass
    
    @abstractmethod
    def calc_agg_data(self) -> None:
        pass
    
    @abstractmethod
    def get_agg_data(self) -> pd.DataFrame:
        pass


class ASNAsset(AssetClass):

    def __init__(self):
        self.data_file_path = super().__getattribute__("base_dir") + r"\data\raw\asn_savings.csv"
        self.agg_data = None
    
    
    def load_data(self) -> None:
        self.raw_data = pd.read_csv(self.data_file_path)
        
        
    def calc_agg_data(self) -> None:
        # TODO: Conform to start and end date from settings
        df = self.raw_data.copy()
        df["Spent"] = np.where(df["Rente"]==False, df["Amount"], 0)
        df["Rent"] = np.where(df["Rente"]==True, df["Amount"], 0)
        
        # Resample the columns based on 
        df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
        df_agg = df.resample(super().__getattribute__("INTERVAL_DUR"), on="Date").sum()[["Spent", "Rent"]]
        df_agg = df_agg.cumsum()
        
        # Add current worth column and return df to self
        df_agg["Current worth"] = df_agg["Spent"] + df_agg["Rent"]
        self.agg_data = df_agg 

    
    def get_agg_data(self) -> pd.DataFrame:
        return self.agg_data