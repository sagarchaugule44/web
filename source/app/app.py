import feedparser
import json
import urllib
import urllib3
import datetime
from flask import Flask, render_template, request, make_response

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
'cnn': 'http://rss.cnn.com/rss/edition.rss',
'fox': 'http://feeds.foxnews.com/foxnews/latest',
'iol': 'http://www.iol.co.za/cmlink/1.640',
'toi': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms'}

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=1dcda65920ce05c4b10a28b88bb11593"
CURRENCY_URL ="https://openexchangerates.org//api/latest.json?app_id=72b57144d25d499fac42047d5d1c2bcf"

DEFAULTS = {'publication':'toi',
			'city': 'mumbai,in',
			'currency_from':'USD',
			'currency_to':'INR'}

@app.route("/", methods=['GET','POST'])
def home():
	# get customised headlines, based on user input or default
	publication_keys = []
	for k, v in RSS_FEEDS.items():
		publication_keys.append(k)
	publication = get_value_with_fallback("publication")
	articles = get_news(publication)
	# get customised weather based on user input or default
	city = get_value_with_fallback("city")
	weather = get_weather (city)
	# get customised currency based on user input or default
	currency_from = get_value_with_fallback("currency_from")
	currency_to = get_value_with_fallback("currency_to")
	rate, currencies = get_rate(currency_from, currency_to)
	# save cookies and return template
	
	response = make_response(render_template("index.html",publications_keys=publication_keys, publication=publication, articles=articles,weather=weather, currency_from=currency_from,currency_to=currency_to, rate=rate,currencies=sorted(currencies)))
	expires = datetime.datetime.now() + datetime.timedelta(days=365)
	response.set_cookie("publication", publication,expires=expires)
	response.set_cookie("city", city, expires=expires)
	response.set_cookie("currency_from",currency_from, expires=expires)
	response.set_cookie("currency_to",
	currency_to, expires=expires)
	return response

def get_value_with_fallback(key):
	if request.args.get(key):
		return request.args.get(key)
	if request.cookies.get(key):
		return request.cookies.get(key)
	return DEFAULTS[key]
	
def get_news(query):
	# query = request.args.get("publication")
	if not query or query.lower() not in RSS_FEEDS:
		publication = DEFAULTS['publication']
	else:
		publication = query.lower()
	
	feed = feedparser.parse(RSS_FEEDS[publication])
	articles = feed['entries']
	return articles
	# weather = get_weather("London,UK")
	# return render_template("index.html",articals=articals,weather=weather)

def get_weather(query):
	query = urllib.parse.quote(query)
	url = WEATHER_URL.format(query)
	data = urllib.request.urlopen(url).read()
	parsed = json.loads(data)
	print (parsed)
	weather = None
	if parsed.get("weather"):
		weather = {"description":
		parsed["weather"][0]["description"],
		"temperature":parsed["main"]["temp"],
		"min":parsed["main"]["temp_min"],
		"max":parsed["main"]["temp_max"],
		"humidity":parsed["main"]["humidity"],
		"icon":parsed["weather"][0]["icon"],
		"city":parsed["name"],
		"country": parsed['sys']['country']}
	return weather

def get_rate(frm, to):
	all_currency = urllib.request.urlopen(CURRENCY_URL).read()
	parsed = json.loads(all_currency).get('rates')
	frm_rate = parsed.get(frm.upper())
	to_rate = parsed.get(to.upper())
	return (to_rate / frm_rate, parsed.keys())

if __name__ == "__main__":
	app.run(debug=True)
