from .. import settings
from typing import List
import yfinance as yf
import pandas as pd
import datetime
from pandas.plotting import register_matplotlib_converters
import logging as log
import os
import numpy as np
import matplotlib.pyplot as plt
from google.cloud import storage


# Required for converting data types (e.g. dates)
register_matplotlib_converters()


def __upload_to_gcp_bucket(path, fname,date):
  storage_client = storage.Client()
  bucket = storage_client.bucket(settings.GCP_BUCKET)
  blob = bucket.blob(date + "/" + fname)
  blob.upload_from_filename(path)
  log.debug("File %s uploaded to GCP Bucket at %s", path, date + "/" + fname)


def __plot_and_save(df,fname,title):
  fig, ax = plt.subplots()
  ax.plot( np.array(df.index), np.array(df['Open']), marker='', color='skyblue', linewidth=2, linestyle='solid', label='Open')
  ax.plot( np.array(df.index), np.array(df['High']), marker='', color='green', linewidth=2, linestyle='solid', label='High')
  ax.plot( np.array(df.index), np.array(df['Low']), marker='', color='red', linewidth=2, linestyle='solid', label='Low')
  ax.plot( np.array(df.index), np.array(df['Close']), marker='', color='black', linewidth=2, linestyle='solid', label='Close')
  plt.legend()
  fig.autofmt_xdate()
  plt.title(title)
  plt.savefig(fname)
  plt.close()


def get_historical_prices(ticker: str, path: str) -> None:
  """
  Creates line charts for 3month,1month and 1week historical stock prices and stores the images in a GCP Cloud Storage bucket

  Parameters:
  ticker: stock symbol
  path: path to the temporary directory
  """
  date = datetime.datetime.today().strftime("%Y%m%d")
  ticker_path = os.path.join(path,ticker)
  log.debug("Creating ticker path: %s", str(ticker_path))
  os.mkdir(ticker_path)
  ticker_obj = yf.Ticker(ticker)
  prices_df = ticker_obj.history(period="3mo")
  if not len(prices_df.index):
    return 
  log.debug("Creating 3 month line graph")
  fname = ticker+"_3mo.png"
  path = os.path.join(ticker_path, fname)
  __plot_and_save(prices_df, path, ticker + " - Past 3 months")
  __upload_to_gcp_bucket(path, fname, date)
  
  log.debug("Creating 1 month line graph")
  fname = ticker+"_1mo.png"
  path = os.path.join(ticker_path, fname)
  __plot_and_save(prices_df.iloc[-31:], path, ticker + " - Past 1 month")
  __upload_to_gcp_bucket(path, fname, date)

  log.debug("Creating 1 week line graph")
  fname = ticker+"_1wk.png"
  path = os.path.join(ticker_path, fname)
  __plot_and_save(prices_df.iloc[-8:], path, ticker + " - Past 1 week")
  __upload_to_gcp_bucket(path, fname, date)

  log.info("Created graphs for %s and uploaded to GCP Storage Bucket", ticker)
  


def get_stock_profile(ticker:str) -> dict:
  ticker_obj = yf.Ticker(ticker)
  return ticker_obj.info
