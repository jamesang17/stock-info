from .. import settings
import requests
import logging as log
import datetime
import urllib.parse

NEWS_URL = "https://newsapi.org/v2"

def __submit_request(url):
  url += ("&apiKey=" + settings.NEWS_KEY)
  r = requests.get(url)
  if r.status_code == 200:
    return r
  log.error("Request %s failed with status %s and message %s",
            url, str(r.status_code), r.text)


def __validate_date(date):
    try:
      datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
      raise ValueError("Incorrect date format, should be YYYY-MM-DD")


def get_top_headlines_by_category(category: str) -> [dict]:
  """
  Returns top 20 headlines around a specified category

  Parameters:
  category: either one of the following valid values ["business","entertainment","general","health","science","sports","technology"] 
  """
  categories = ["business","entertainment","general","health","science","sports","technology"]
  category = category.lower()
  if category in categories:
    log.debug("Getting top headlines for category %s", category)
    url = NEWS_URL + "/top-headlines?country=us&category=" + category
    r = __submit_request(url)
    return r.json()
  log.debug("%s category not found. Defaulting to query search")
  return get_top_headlines_by_query(category)


def get_top_headlines_by_query(query: str) -> [dict]:
  """
  Returns top 20 headlines around a specified topic

  Parameters:
  query: topic to get articles about as str
  """
  log.debug("Getting top headlines for %s", query)
  url = NEWS_URL + "/top-headlines?country=us&q=" + urllib.parse.quote(query)
  r = __submit_request(url)
  return r.json()