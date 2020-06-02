# Stock Report Generator
Python script that gets information on a certain financial products for various users and emails the reports.

### Setup:

#### GCP Project:
- GCP Project Access

#### API Keys:
- Get an api key from [Finnhub](https://finnhub.io/)

#### Python Virtual Environment:
Steps are taken from here: [Setting up a Python development environment](https://cloud.google.com/python/setup)

Create a python virtual environment so dependencies can be managed strictly within this project
_note: requires python version > 3_
```
python -m venv venv
source venv/bin/activate
```

To deactivate <br/>
`deactivate`

#### Packages to install:
- Dotenv - to keep all api keys and other configs private
- Google libaries
- oauth2client - for authentication with google api via google credentials object
- Progress - nice user feedback on progress of tasks 
- PyYaml - for parsing the input yaml file with clients and stocks
- Textblob - for performing sentiment analysis on news articles
- Yfinance - for historical stock prices
- matplotlib - for creating stock price graphs

```
pip install python-dotenv \ 
  google-api-python-client google-auth-oauthlib google-cloud-storage \
  oauth2client \
  progress \
  PyYaml \
  textblob \
  yfinance \
  matplotlib
```


### Configuration:
Create a yaml file with the following strcuture

```yaml
sender: "test-sender@test.com"
mappings:
  - email: "test@test.com"
    stocks:
      - "AMZN"
  - email: "tester2@test.com"
    stocks:
      - "GOOGL"
      - "AAPL"
```


### Running:
If using a virtual environment don't forget to use that version of python 
`${your virtual environment name}/bin/python`

Run the script with the following command <br/>
`python stock_info_runner.py ${YOUR CONFIG FILE}`

Run in test mode <br/>
`python stock_info_runner.py ${YOUR CONFIG FILE} --test`

Run with increased logging <br/>
`python stock_info_runner.py ${YOUR CONFIG FILE} --log DEBUG`


### TO DO:
- [X] API to get stock information
- [X] get information of multiple stocks
- [X] API to get news on stock (use news api)
- [X] plot last week, month, 3 months performance for product
- [X] get sentiment analysis of product/industry based on twitter and news
- [X] write results to static html page
- [X] store graph data on some bucket (GCP Bucket)
- [X] images should be pulled from this bucket
- [X] send results via email
