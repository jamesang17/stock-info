from textblob import TextBlob
from typing import List
import logging as log


def get_sentiment(text: str) -> float:
  """
  Gets the sentiment polarity score of text

  Parameters:
  text: string to be analyzed
  """
  analysis = TextBlob(text)
  return analysis.sentiment.polarity
