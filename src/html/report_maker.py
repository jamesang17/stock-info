import time
import datetime
import os
import pathlib
from .. import settings
from progress.bar import Bar
from google.cloud import storage


def __add_opening_tags(f, output_dir):
  path = os.path.join(str(pathlib.Path(__file__).parent.absolute()), "template.css")
  with open(path, 'r') as file:
    css_data = file.read().replace('\n', '')
  file.close()
  html = [
      """<!DOCTYPE html><head>""",
      "<style>"
  ]
  html.append(css_data)
  html.append("""</style></head><body><div>""")
  f.write(''.join(html))


def __add_closing_tags(f):
  html = """</div></body></html>"""
  f.write(html)


def __add_section_break(f):
  html = """<div class="Line-break"></div>"""
  f.write(html)


def __add_header(f, client):
  html = [
    """<div class="Header">""","""<p class="Name">""",
    "Report for " + client, "</p></div>"
  ]
  f.write(''.join(html))


def __add_intro(f, stock, name, quote, sentiment):
  sent_style = "Pos-sentiment-value"
  if sentiment == "N/A":
    sent_style = "Def-sentiment-value"
  elif sentiment < 0:
    sent_style = "Neg-sentiment-value"
  html = [
      """<div class="Intro-container">""",
      """<h2 class="Stock-name">""",
      stock + "(" + name + ")",
      "</h2>",
      """<div class="Quote-info-container">""",
      """<p class="Quote-info">""", "Open: " + str(quote["o"]), "</p>",
      """<p class="Quote-info">""", "Close: " + str(quote["c"]), "</p>",
      """<p class="Quote-info">""", "High: " + str(quote["h"]), "</p>"
      """<p class="Quote-info">""", "Low: " + str(quote["l"]), "</p>",
      """</div>""",
      """<p class="Sentiment">""","Sentiment: ",
      """<span class=""", '"' + sent_style + '">', 
      str(sentiment), "</span></p></div>"
  ]
  f.write(''.join(html))


def __add_news(f, news):
  html = [
    """<div class="News-container">""",
    """<h2 class="Company-news-header">Company News</h2>""",
    """<div class="News-article-1">"""    
  ]
  i = 0
  while i < 5 and i < len(news): 
    if i == 0:
      html.extend([
          "<a href=",'"' + news[i]["url"] + '"', """ target="_blank" rel="noopener noreferrer">""",
          """<img src=""", '"' + news[i]["image"] + '"', """ class="Article-img">""",
          """<div class="Article-description">""",
          """<p class="Headline">""", news[i]["headline"], "</p>",
          """<p class="Source">""", news[i]["source"], "</p>",
          """<p class="Publish-time">""", time.strftime('%m-%d-%Y', time.localtime(news[i]["datetime"])), "</p>",
          """</div></a></div><div class="Sub-news-articles">"""
      ])
    else:
      if i % 2 != 0:
        html.extend([
          """<div class="Sub-article-group">""",
         """<div class="Sub-article">""",
          "<a href=", '"' + news[i]["url"] + '"', """ target="_blank" rel="noopener noreferrer">""",
          """<img src=""", '"' + news[i]["image"] + '"', """ class="Article-img">""",
          """<div class="Article-description">""",
          """<p class="Sub-Headline">""", news[i]["headline"], "</p>",
          """<p class="Sub-Source">""", news[i]["source"], "</p>",
          """<p class="Sub-publish-time">""", time.strftime('%m-%d-%Y', time.localtime(news[i]["datetime"])), "</p>",
          "</div></a></div>"
        ])
      else:
        html.extend([
            """<div class="Sub-article">""",
            "<a href=", '"' + news[i]["url"] + '"', """ target="_blank" rel="noopener noreferrer">""",
            """<img src=""", '"' + news[i]["image"] + '"', """ class="Article-img">""",
            """<div class="Article-description">""",
            """<p class="Sub-Headline">""", news[i]["headline"], "</p>",
            """<p class="Sub-Source">""", news[i]["source"], "</p>",
            """<p class="Sub-publish-time">""", time.strftime('%m-%d-%Y', time.localtime(news[i]["datetime"])), "</p>",
            "</div></a></div></div>"
      ])
    i+=1
  if i < 6 and (len(news)-1) % 2 != 0:
    html.append("</div>")
  html.append("""</div></div>""")
  f.write(''.join(html))


def __add_graphs(f, stock, gcp_path):
  date = datetime.datetime.today().strftime("%Y%m%d")
  storage_client = storage.Client()
  bucket = storage_client.bucket(settings.GCP_BUCKET)

  html = [
      """<div class="Graph-container">""",
      """<img src=""", '"' + bucket.blob(date + "/" + stock+"_3mo.png").public_url + '"', """ class="Primary-line-graph" />""",
      """<div class="Sub-graph-container">""",
      """<img src=""", '"' + bucket.blob(date + "/" + stock+"_1mo.png").public_url + '"', """ class="Line-graph" />""",
      """<img src=""", '"' + bucket.blob(date + "/" + stock+"_1wk.png").public_url + '"', """ class="Line-graph" />""",
      "</div></div>"
  ]
  f.write(''.join(html))
  

def create_report(stocks, output_dir, client, profiles, news, quotes, sentiment_scores) -> None:
  file = os.path.join(output_dir,"reports",client + "_report.html")
  f = open(file, 'w')
  __add_opening_tags(f, output_dir)
  __add_header(f, client)
  
  for stock in stocks:
    profile = profiles[stock]
    quote = quotes[stock]
    sentiment = sentiment_scores[stock]
    company_news = news[stock]
    gcp_path = ''.join(["https://storage.cloud.google.com/",settings.GCP_BUCKET,"/",time.strftime("%Y%m%d"),"/"])
    __add_intro(f, stock, profile["name"], quote, sentiment)
    __add_news(f, company_news)
    __add_graphs(f, stock, gcp_path)
    __add_section_break(f)
  __add_closing_tags(f)
  f.close()
