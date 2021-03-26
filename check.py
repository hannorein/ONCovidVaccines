import tweepy
import csv
import datetime
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker



def forward(x):
    return x/pop*100.




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
    fig, ax = plt.subplots(1,1,figsize=(6,4))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d/%-m'))

    x = [r[0] for r in ontario[-7:]]
    y = [r[1] for r in ontario[-7:]]
    ax.set_xlim([x[0]-datetime.timedelta(days=0.6),x[-1]+datetime.timedelta(days=0.6)])
    ax.axhline(sum(y)/7.,color="black",ls="--")
    ax.annotate('7 day average: %.0f doses/day'%(sum(y)/7.), xy=(x[0]-datetime.timedelta(days=0.2), 1.03*sum(y)/7.))
    ax.set_ylabel("Administered doses")
    rects = ax.bar(x,y,color=(1,0.4,0.4))
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{} doses'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, 1000),
                    xytext=(0, 3), 
                    textcoords="offset points",
                    ha='center', va='bottom', rotation=90)

    rax = ax.twinx()
    rax.set_yticks([forward(x) for x in ax.get_yticks()])
    rax.set_ybound([forward(x) for x in ax.get_ybound()])
    rax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f%%'))
    rax.set_ylabel("Fraction of population")

    fig.savefig("7day.png", transparent=False)

    api.update_with_media("7day.png", text)

    #api.update_status(text)
    
