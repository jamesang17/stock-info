from typing import List
import logging as log
from datetime import datetime, timedelta
from progress.bar import Bar
from .api import finnhub_api
from .api import news_api
from .api import yfinance_api
from .sentiment import sentiment_analysis


def get_company_profiles(stocks: List[str]) -> dict:
  """
  Returns a dictionary of a company name to its profile object

  Parameters:
  stocks: list of stock symbols
  """
  profiles = {}
  bar = Bar('Retrieving Profiles', max=len(stocks))
  for s in stocks:
    p = {"name": "", "industry": ""}
    fp = finnhub_api.get_company_profile(s)
    if len(fp) == 0:
      yp = yfinance_api.get_stock_profile(s)
      if len(yp) == 0:
        log.warn("No profile data was found of %s. Skipping", s)
      else:
        p["name"] = yp.get("shortName", s)
        p["industry"] = yp.get("sector", s)
    else:
      p["name"] = fp.get("name",s)
      p["industry"] = fp.get("finnhubIndustry",s)
    profiles[s] = p
    bar.next()
  bar.finish()
  log.info("Retrieved %d company profiles for %d stocks",
           len(profiles), len(stocks))
  return profiles


def get_company_news(stocks: List[str]) -> dict:
  """
  Returns a dictionary of a company name to a list of news objects.
  News articles are from the day before

  Parameters:
  stocks: list of stock symbols
  """
  news = {}
  start = (datetime.today() - timedelta(days=2)).strftime("%Y-%m-%d")
  end = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
  bar = Bar('Retrieving Company News', max=len(stocks))
  for s in stocks:
    news[s] = finnhub_api.get_company_news(s, start, end)
    bar.next()
  bar.finish()
  log.info("Retrieved company news for %d stocks", len(news))
  return news


def get_industry_news(profiles: dict) -> dict:
  """
  Returns a dictionary of a company name to a list of news objects.

  Parameters:
  profiles: dictionary of profiles
  """
  industries = set()
  for p in profiles:
    industries.add(str(profiles[p]["industry"]).lower())
  i_news = {}
  bar = Bar('Retrieving Industry News', max=len(industries))
  for i in industries:
    i_news[i] = news_api.get_top_headlines_by_category(i)
    bar.next()
  bar.finish()
  log.info("Retrieved industry news for %d industries", len(industries))
  return i_news


def create_historical_price_charts(stocks: List[str], temp_dir: str) -> None:
  """
  Creates line charts of historical prices for the following historical durations 3months,1month,1week

  Parameters:
  stocks: list of stock symbols
  temp_dir: path to the location where the images will be saved to
  """
  for s in stocks:
    yfinance_api.get_historical_prices(s, temp_dir)


def get_stock_quotes(stocks: List[str]) -> dict:
  """
  Returns a dictionary of stock name to stock quote map

  Parameters:
  stocks: list of stock symbols
  """
  quotes = {}
  for stock in stocks:
    quotes[stock] = finnhub_api.get_stock_quote(stock)
  return quotes
  

def __get_article_texts(company_news: dict) -> dict:
  """
  Returns a dictionary of company name to list of texts

  Parameters:
  company_news: dictionary of company name to list of news article objects
  """
  texts = {}
  for c in company_news:
    texts[c] = []
    for n in company_news[c]:
      texts[c].append(n["summary"])
      texts[c].append(n["headline"])
  return texts


def get_sentiment_scores(company_news: dict) -> dict:
  """
  Returns the sentiment score for each company based on the news for that company

  Parameters:
  company_news: dictionary of company to list of news articles
  """
  company_texts = __get_article_texts(company_news)

  scores = {}
  log.info("Getting sentiment scores for %d companies.", len(company_texts))
  for company in company_texts:
    log.debug("Getting sentiment score for %s", company)
    total_score = 0
    if len(company_texts[company]) == 0:
      scores[company] = "N/A"
      continue
    for text in company_texts[company]:
      temp_score = sentiment_analysis.get_sentiment(text)
      total_score += temp_score
    if len(company_texts[company]) > 0:
      score = total_score / len(company_texts[company])
      scores[company] = float("{0:.2f}".format(score))
  return scores
