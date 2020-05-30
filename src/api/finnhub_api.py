from .. import settings
import requests
import datetime
from datetime import timezone
import logging as log

FINNHUB_URL = "https://finnhub.io/api/v1"


def __validate_date(date):
    try:
      datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
      raise ValueError("Incorrect date format, should be YYYY-MM-DD")

def __submit_request(url):
  url += ("&token=" + settings.FINNHUB_KEY)
  r = requests.get(url)
  if r.status_code == 200:
    return r
  log.error("Request %s failed with status %s and message %s", url, str(r.status_code), r.text)

def get_company_news(symbol:str, start_date:str, end_date:str):
  """ 
  Returns company news.
  
  Parameters:
  symbol: stock symbol as str
  start_date: start date in format YYYY-MM-DD as str
  end_date: end date in format YYYY-MM-DD as str  
  """
  __validate_date(start_date)
  __validate_date(end_date)
  log.debug("Getting news for %s between %s and %s", symbol, start_date, end_date)
  url = FINNHUB_URL + "/company-news?symbol=" + \
      symbol.upper() + "&from=" + start_date + "&to=" + end_date
  r = __submit_request(url)
  return r.json()


def get_general_news(category="general", minId=0):
  """
  Returns general stock market news.

  Parameters:
  category: one of the following categories ["general", "forex", "crypto", "merger"] as str
  minId: the news id to determine all articles retrieved after this limit as int
  """
  categories = ["general", "forex", "crypto", "merger"]
  category = category.lower()
  if category not in categories:
    raise ValueError("Invalid Category: " + category + ". Valid Categories include: " + categories)

  log.debug("Getting general news for %s", category)
  url = FINNHUB_URL + "/news?category=" + category + "&minId=" + str(minId)
  r = __submit_request(url)
  return r.json()


def get_company_profile(stock: str):
  """
  Returns company profile.

  Parameters:
  stock: either the symbol, isin or cusip of a stock as str
  """
  url = FINNHUB_URL + "/stock/profile2?symbol=" + str(stock.upper())
  log.debug("Getting company profile for %s", stock)
  r = __submit_request(url)
  return r.json()


def get_stock_quote(symbol: str):
  """ 
  Returns quote for a stock 
  """
  symbol = symbol.upper()
  url = FINNHUB_URL + "/quote?symbol=" + symbol
  log.debug("Getting stock quote for %s", symbol)
  r = __submit_request(url)
  return r.json() 


def get_stock_candle(symbol: str, resolution: str, start_date: str, end_date: str):
  """
  Returns stock candle (hi,lo,avg) for a stock

  Parameters:
  symbol: stock symbol as str
  resolution: timeframe from ["1","5","15","30","60","D","W","M"] as str
  start_date: date in format YYYY-MM-DD as str
  end_Date: date in format YYYY-MM-DD as str
  """
  def get_timestamp(date:str):
    date_split = date.split("-")
    date = datetime.datetime(int(date_split[0]), int(
      date_split[1]), int(date_split[2]))
    return str(date.timestamp())

  resolutions = ["1","5","15","30","60","D","W","M"]
  resolution = resolution.upper()
  if resolution not in resolutions:
    raise ValueError("Invalid resolution: " + resolution + ". Valid resolutions include: " + resolutions)

  __validate_date(start_date)
  __validate_date(end_date)
  start_time = get_timestamp(start_date).split(".")[0]
  end_time = get_timestamp(end_date).split(".")[0]
  symbol = symbol.upper()

  url = FINNHUB_URL + "/stock/candle?symbol=" + symbol + "&resolution=" + resolution + "&from=" + start_time + "&to=" + end_time
  log.info("Getting stock candle for %s with [resolution: %s, start time: %s, end time: %s]", symbol, resolution, start_date, end_date)
  r = __submit_request(url)
  return r.json()


def get_company_financials(value:str, type:str, accessNumber:str, freq="annual"):
  """
  Returns company financials.

  Parameters:
  value: either the symbol or cik as str
  type: the value type, either ["cik", "symbol"] as str 
  freq: the frequency as "annual" or "quartery" as str
  """
  types = ["cik", "symbol"]
  freqs = ["annual", "quarterly"]
  freq = freq.lower()
  if freq not in freqs:
    raise ValueError("Invalid freq: " + freq + ". Valid frequencies include: " + freqs)

  type = type.lower()
  if type not in types:
    raise ValueError("Invalid type: " + type + ". Valid types include: " + types)

  url = FINNHUB_URL + "/stock/financials-reported?"
  if type is "symbol":
    url += ("symbol=" + value)
  else:
    url += ("cik=" + value)
  log.debug("Getting financial statements for %s at frequency %s", value, freq)
  r = __submit_request(url)
  return r.json()

