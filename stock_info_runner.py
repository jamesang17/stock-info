import logging as log
from progress.bar import Bar
import os
import pathlib
import shutil

# for parsing the input yaml file
import yaml
import argparse
import io

# helper functions
from src import util_functions
from src.html import report_maker
from src.api import gmail_api


log.basicConfig(
    format='%(asctime)s - [%(levelname)s] %(message)s', level=log.INFO)


def __setup() -> None:
  path = os.path.join(str(pathlib.Path(__file__).parent.absolute()),"tmp")
  if os.path.exists(path):
    log.info("tmp directory already exists. Removing.")
    shutil.rmtree(path)
  os.mkdir(path)
  log.info("Created temporary directory at: %s", str(path))
  return path


def __cleanup(path) -> None:
  log.info("Removing temporary directory: %s", path)
  shutil.rmtree(path)
  

def __generate_reports(output_dir, clients, profiles, news, quotes, sentiment_scores) -> None:
  reports_path = os.path.join(output_dir, "reports")
  os.mkdir(reports_path)
  bar = Bar('Client Reports Created', max=len(clients))
  for client in clients:
    print('\n')
    log.info("Generating report for %s", client)
    stocks = clients[client]
    report_maker.create_report(stocks, output_dir, client, profiles, news, quotes, sentiment_scores)
    bar.next()
  bar.finish()


def __email_reports(reports_dir, clients, sender) -> None:
  bar = Bar('Emailing Reports', max=len(clients))
  for client in clients:
    gmail_api.email_report(sender, client, reports_dir)
    bar.next()
  bar.finish()


def main():
  parser = argparse.ArgumentParser(description="Retrieve stock information and desired stocks and email results")
  parser.add_argument('stockconfig', help='yaml file with email to stock symbol list mapping')
  parser.add_argument('--test', action='store_true', help='Run in test mode where tmp directory will not be removed.') 
  parser.add_argument('--loglevel', help='set logging level [INFO, DEBUG, WARN]. default is INFO')

  args = parser.parse_args()
  config = args.stockconfig
  testMode = args.test
  loglevel = log.INFO

  if str(args.loglevel).upper() == "DEBUG":
    loglevel = log.DEBUG
  elif str(args.loglevel).upper() == "WARN":
    loglevel = log.WARN
  
  log.getLogger().setLevel(loglevel)
  log.info("Running using args: [ Config File: %s, Test Mode: %s, Log Level: %s ]", 
    config, str(testMode), str(loglevel))

  if testMode: 
    log.info("Test mode is enabled. Temporary directory will not be removed.")

  temp_dir = __setup()

  log.info("Parsing config file %s", config)
  with io.open(config, 'r') as stream:
    data = yaml.safe_load(stream)

  stocks = set()
  clients = {}
  people = data["mappings"]
  sender = data["sender"]
  for p in people:
    clients[p["email"]] = p["stocks"]
    stocks.update(p["stocks"])

  log.info("Identified the following clients: " + ','.join(clients.keys()))
  log.info("Getting information on the following stocks: " + ','.join(stocks))

  profiles = util_functions.get_company_profiles(stocks)
  news = util_functions.get_company_news(stocks)
  quotes = util_functions.get_stock_quotes(stocks)
  #industry_news = util_functions.get_industry_news(profiles)
  util_functions.create_historical_price_charts(stocks, temp_dir)
  sentiment_scores = util_functions.get_sentiment_scores(news)
  
  __generate_reports(temp_dir, clients, profiles, news, quotes, sentiment_scores)

  if not testMode:
    __email_reports(os.path.join(temp_dir,"reports"), clients, sender)
    __cleanup(temp_dir)

  log.info("DONE.")


main()
