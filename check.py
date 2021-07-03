import tweepy
import csv
import datetime
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter




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
    x = [r[0] for r in ontario[-7:]]
    y = [r[1] for r in ontario[-7:]]
    weekavg = sum(y)/7.

    text = "#Ontario administered %d #COVID19 #Vaccine doses on %s. The 7-day average is %d. The total number of administered doses is now %d (%.2f%% of the population). Data from https://opencovid.ca." %(recent[1],recent[0].strftime("%A %-d %B %Y"),weekavg,recent[2],recent[2]*100./pop)
    print(text)
    with open("lasttweet.txt","w") as f:
        f.write(recent[0].strftime("%Y-%m-%d"))
    fig, ax = plt.subplots(1,1,figsize=(6,4))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d/%-m'))

    x = [r[0] for r in ontario[-14:]]
    y = [r[1] for r in ontario[-14:]]
    ax.set_xlim([x[0]-datetime.timedelta(days=0.6),x[-1]+datetime.timedelta(days=0.6)])
    ax.axhline(weekavg,color="black",ls="--")
    ax.annotate('7-day average: %.0f doses/day'%(weekavg), xy=(x[0]-datetime.timedelta(days=0.2), 1.03*weekavg))
    ax.set_ylabel("Administered doses")
    rects = ax.bar(x,y,color=(1,0.4,0.4))
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{} doses'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, 1000),
                    xytext=(0, 3), 
                    textcoords="offset points",
                    ha='center', va='bottom', rotation=90)

    fig.savefig("7day.png", transparent=False)
    api.update_with_media("7day.png", text)

    fig, ax = plt.subplots(1,1,figsize=(6,4),tight_layout=True)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d/%-m/%Y'))
    x = [r[0] for r in ontario]
    y = [r[2] for r in ontario]

    daysleft = (2.*pop-y[-1])/weekavg
    dateoneshot = x[-1] + datetime.timedelta(days=daysleft)

    daysleft = (pop*0.7*2-y[-1])/weekavg
    date70 = x[-1] + datetime.timedelta(days=daysleft)



    rhs = date70 + datetime.timedelta(days=100)
    ax.set_ylim([0,1.3*pop*2])
    ax.plot((x[0],rhs), (2.*pop,2.*pop),color="black",ls="--")
    ax.annotate("2x population of Ontario", xy=(x[3],2.*pop+4e5))

    ax.plot((x[0],rhs), (pop*2*0.7,pop*2*0.7),color="black",ls="--")
    ax.annotate("70% of the population receives 2 vaccine doses", xy=(x[3],pop*2*0.7+4e5))


    ax.plot(x,y,label="Total doses administered",color="red", lw=2)
    ax.plot((x[-1],date70),(y[-1],pop*2*0.7),color="red",ls=":",label="Projection based on \n7-day average")




    ax.legend(loc="lower right")
    def millions(x, pos):
        return '%1.1f million' % (x * 1e-6)

    formatter = FuncFormatter(millions)
    ax.yaxis.set_major_formatter(formatter)


    ax.annotate(date70.strftime("%-d %B %Y"), xy=(date70, pop*2*0.7),  xycoords='data',
                xytext=(0.78, 0.8), textcoords='axes fraction',
                arrowprops=dict(facecolor='black', arrowstyle="->"))

    ax.annotate(dateoneshot.strftime("%-d %B %Y"), xy=(dateoneshot, pop),  xycoords='data',
                xytext=(0.6, 0.5), textcoords='axes fraction',
                arrowprops=dict(facecolor='black', arrowstyle="->"))

    ax.annotate("today", xy=(x[-1], y[-1]),  xycoords='data',
                xytext=(0.1, 0.2), textcoords='axes fraction',
                arrowprops=dict(facecolor='black', arrowstyle="->"))

    text2 = "Based on the 7-day average rate of daily #COVID19 #vaccine doses administered, everyone in #Ontario can receive two doses by %s. 70%% of the population can receive two doses by %s. Data from https://opencovid.ca."%(dateoneshot.strftime("%-d %B %Y"),date70.strftime("%-d %B %Y"))

    fig.savefig("predict.png", transparent=False)
    api.update_with_media("predict.png", text2)
    print(text2)

     
