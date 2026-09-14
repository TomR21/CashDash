from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf
import json


class AssetClass(ABC):
    
    # Load setting parameters
    base_dir = str(Path.cwd())
    with open(base_dir + r"\config\settings.json", 'r') as f:
        settings = json.load(f)
    
    # Get settings parameter required for all child classes 
    START_DATE = settings["START_DATE"]
    END_DATE = settings["END_DATE"]
    INTERVAL_DUR = settings["INTERVAL_DUR"]
    
    @abstractmethod
    def load_data(self) -> None:
        """ Loads raw dataset from file and stores it within class variable. """
        pass
    
    @abstractmethod
    def calc_agg_data(self) -> None:
        """ Calculates the aggregated calculated values from raw dataset and stores it within new class variable. """
        pass
    
    @abstractmethod
    def get_agg_data(self) -> pd.DataFrame:
        """ Returns the aggregated calculated values stored within the class. """
        pass


class Savings(AssetClass):

    def __init__(self, filename: str) -> None:
        self.data_file_path: str = super().__getattribute__("base_dir") + r"\data\raw\\" + filename
        self.agg_data: pd.DataFrame | None = None
    
    
    def load_data(self) -> None:
        self.raw_data = pd.read_csv(self.data_file_path)
        
        
    def calc_agg_data(self) -> None:
  
        # Resample the columns to totals per month and calculate cumulative sum
        df = self.raw_data.copy()
        df["DATE"] = pd.to_datetime(df["DATE"], format="%d/%m/%Y")
        
        # Separate balance changes to user spending and interest accrueing
        df["Spent"] = np.where(df["INTEREST_FLAG"]==False, df["AMOUNT"], 0)
        df["Interest"] = np.where(df["INTEREST_FLAG"]==True, df["AMOUNT"], 0)
        df.drop(columns=["INTEREST_FLAG", "AMOUNT"], inplace=True)
        
        # Create current worth column
        df[["Spent", "Interest"]] = df[["Spent", "Interest"]].cumsum()
        df["Current worth"] = df["Spent"] + df["Interest"]

        # Create date range from start to end date 
        date_range = pd.date_range(
            start=super().__getattribute__("START_DATE"),
            end=super().__getattribute__("END_DATE"),
            freq=super().__getattribute__("INTERVAL_DUR"), 
        )
        date_series = pd.DataFrame({'DATE': date_range})

        # Map cumulative data onto date_range, backwards filling any interval without activity
        result = pd.merge_asof(date_series, df, on='DATE', direction='backward')
        result.set_index("DATE", inplace=True)
                
        # Fill NaN values (from dates before first savings trxs) with 0
        columns = ["Spent", "Interest", "Current worth"]
        result[columns] = result[columns].fillna(0.00)
        
        # Store resulting df in self
        self.agg_data = result 

    
    def get_agg_data(self) -> pd.DataFrame:
        return self.agg_data
    
    

class Stocks(AssetClass):
    
    def __init__(self, filename: str) -> None:
        self.data_file_path: str = super().__getattribute__("base_dir") + r"\data\raw\\" + filename
        self.agg_data: pd.DataFrame | None = None
        
    def load_data(self) -> None:
        self.raw_data = pd.read_csv(self.data_file_path, delimiter=";")
        
    def calc_agg_data(self) -> None:
      
        # Resample the columns to totals per month and calculate cumulative sum
        df = self.raw_data.copy()
        df["DATE"] = pd.to_datetime(df["DATE"], format="%d/%m/%Y")
        
        # Create date range from start to end date 
        date_range = pd.date_range(
            start=super().__getattribute__("START_DATE"),
            end=super().__getattribute__("END_DATE"),
            freq=super().__getattribute__("INTERVAL_DUR"), 
        )
        date_range = pd.DataFrame({'DATE': date_range})
        
        # Obtain stock prices for every interval in date range
        TICKER_MAPPING = {"AMS:VWRL": "VWRD.L"}
        stock_prices = self._calc_stock_prices(TICKER_MAPPING["AMS:VWRL"], date_range)
            
        # Calc cumulative sum of shares for every time 
        df[["Spent", "Current shares"]] = df[["AMOUNT", "NUM_STOCKS"]].cumsum()
        
        # Map cumulative data onto date_range, backwards filling any interval without activity
        result = pd.merge_asof(date_range, df, on='DATE', direction='backward')
        result = pd.merge_asof(result, stock_prices, on='DATE', direction='backward')
        result.set_index("DATE", inplace=True)
        
        # Create current worth column
        result["Current worth"] = result["Current shares"] * result["PRICE_EUR"]
        result["Interest"] = result["Current worth"] - result["Spent"]       
        
        # Fill NaN values (from dates before first savings trxs) with 0
        columns = ["Spent", "Interest", "Current worth"]
        result[columns] = result[columns].fillna(0.00)
        
        # Store resulting df in self
        self.agg_data = result[["Spent", "Interest", "Current worth"]]
    
        
    def get_agg_data(self) -> pd.DataFrame:
        return self.agg_data
    
    
    def _calc_stock_prices(self, ticker: str, date_range: pd.DataFrame) -> pd.DataFrame:
        
        start_date = date_range["DATE"].iloc[0]-pd.Timedelta(days=10)
        end_date = date_range["DATE"].iloc[-1]
        
        # Retrieve stock price (USD) and forex 
        stock_prices = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval='1d',
            progress=False,
            auto_adjust=True,
        )['Close']
        
        fx = yf.download(
            "USDEUR=X",
            start=start_date,
            end=end_date,
            interval='1d',
            progress=False,
            auto_adjust=True,
        )['Close']
        
        stock_prices["PRICE_EUR"] = stock_prices["VWRD.L"] * fx["USDEUR=X"]
        
        # Map cumulative data onto date_range, backwards filling any interval without activity
        stock_prices.index = stock_prices.index.astype('datetime64[us]')
        result = pd.merge_asof(date_range, stock_prices["PRICE_EUR"], left_on='DATE', right_index=True, direction='backward')
        #result.set_index("DATE", inplace=True)
        
        print(result)
        
        return result