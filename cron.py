# import sys
# sys.path.append('/opt/anaconda3/lib/python3.7/site-packages')
# import requests
# from bs4 import BeautifulSoup
# res = requests.get('https://ubot-110.herokuapp.com/')
# soup = BeautifulSoup(res.text, 'lxml')
# print(soup.getText())

from apscheduler.schedulers.blocking import BlockingScheduler
import urllib.request

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour='9-20',minute='*/5')
def scheduled_job():
    url = "https://ubot-110.herokuapp.com/"
    conn = urllib.request.urlopen(url)
        
    for key, value in conn.getheaders():
        print(key, value)

sched.start()