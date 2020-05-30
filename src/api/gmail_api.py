# Google API required modules
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from .. import settings

import logging as log
# reading report
import os
# for creating emails
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
# time stamp
from datetime import datetime


# Reference for how to setup email message: 
# @SeattleDataGuy
# https: // medium.com/better-programming/how-to-automate-your-emails-with-python-386b4e2d5395 

def __create_email(sender, to, subject, report):
  message = MIMEMultipart('alternative')
  message['from'] = sender
  message['to'] = to
  message['subject'] = subject

  text = "Hi " + to + ",\nPlease find your stock report for " + datetime.today().strftime("%Y-%m-%d") + " below."

  html = ""
  with open(report, 'r') as file:
    html = file.read().replace('\n', '')
  
  part1 = MIMEText(text, 'plain')
  part2 = MIMEText(html, 'html')

  message.attach(part1)
  message.attach(part2)

  # Return message
  raw = base64.urlsafe_b64encode(message.as_bytes())
  raw = raw.decode()
  return {'raw' : raw}


def __send_email(service, sender, message):
  try:
    message = service.users().messages(). \
    send(userId=sender, body=message).execute()
    log.info("Message Id: %s", message['id'])
    return message
  except Exception as e:
    log.error("An error occured when trying to send the email: %s", e)
    return None


def __find_report(client,files):
  lo,hi = 0,len(files)
  m = (lo+hi) // 2
  while lo < hi:
    fname = files[m].split("_report")[0]
    if fname == client:
      return files[m]
    elif fname < client:
      lo = m+1
    else:
      hi = m-1
  return None


def __get_credentials():
  # Credit: SeattleDataGuy - https://medium.com/better-programming/how-to-automate-your-emails-with-python-386b4e2d5395

  creds = None 
  # The file token.pickle stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.

  # if os.path.exists('token.pickle'):
  #     with open('token.pickle', 'rb') as token:
  #       creds = pickle.load(token)
  # # If there are no (valid) credentials available, let the user log in.
  # if not creds or not creds.valid:
  #   if creds and creds.expired and creds.refresh_token:
  #     creds.refresh(Request())
  #   else:
  #     flow = InstalledAppFlow.from_client_secrets_file(
  #       settings.GOOGLE_APP_CREDS, SCOPES)
  #     creds = flow.run_local_server(port=0)
  #   # Save the credentials for the next run
  #   with open('token.pickle', 'wb') as token:
  #     pickle.dump(creds, token)

  SCOPES = ['https://mail.google.com']
  SERVICE_ACCOUNT_FILE = settings.GOOGLE_APP_CREDS

  creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

  return creds


def email_report(sender, client, reports_dir):
  subject = "Stock Report for " + datetime.today().strftime("%Y-%m-%d")

  files = os.listdir(reports_dir)
  files = sorted(files)
  report = __find_report(client, files)
  report_path = os.path.join(reports_dir,report)

  message = __create_email(sender, client, subject, report_path)

  creds = __get_credentials()

  service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
  #__send_email(service, sender, message)
  print(message)

  log.info("Message sent to %s", client)




