import tweepy
import csv
import datetime
import requests


response = requests.get('https://raw.githubusercontent.com/ccodwg/Covid19Canada/master/timeseries_prov/vaccine_administration_timeseries_prov.csv', stream=True)

response.raise_for_status()

with open("vaccine_administration_timeseries_prov.csv", 'wb') as handle:
    for block in response.iter_content(1024):
        handle.write(block)

with open("twitterkeys.txt") as f:
    lines = f.readlines()
    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET = [l.strip() for l in lines]
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


with open("lasttweet.txt") as f:
    lasttweet = f.readlines()[0]

pop = 14570000
ontario = []
with open("vaccine_administration_timeseries_prov.csv") as csvfile:
    spamreader = csv.reader(csvfile)
    for row in spamreader:
        if row[0] == "Ontario":
            date = datetime.datetime.strptime(row[1], "%d-%m-%Y")
            ontario.append([date,int(row[2]),int(row[3])])
ontario.sort()           
recent = ontario[-1]
daysleft = (2*pop- recent[2])/ (recent[1])
end_date = recent[0] + datetime.timedelta(days=daysleft)
if recent[0].strftime("%Y-%m-%d") != lasttweet:
    text = "#Ontario administered %d #COVID19 #Vaccine doses on %s. The total number of administered doses is %d. At this rate, it will take until %s to administer two doses to every person in Ontario. Data from https://opencovid.ca." %(recent[1],recent[0].strftime("%A %-d %B %Y"),recent[2],end_date.strftime("%-d %B %Y"))
    print(text)
    with open("lasttweet.txt","w") as f:
        f.write(recent[0].strftime("%Y-%m-%d"))
    api.update_status(text)
    




