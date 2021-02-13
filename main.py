
import json
import requests
from flask import Flask, request, abort
from bs4 import BeautifulSoup
from datetime import datetime
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)
url = "https://mybank.ubot.com.tw/MyBank/IBKB040101"
line_bot_api = LineBotApi('')
handler = WebhookHandler('ada9716b08814248b6bc2c65cf46d33b')

def update_file(currency,now_price=None,opt=None,line='None'):
    with open(currency+".txt",'r+') as f: 
        price = (f.read()).split(',')
        if opt == 'w':       
            f.seek(0)
            if line == 'no':
                price[0] = now_price
            if line == 'yes':
                price[0] = now_price
                now_price = float(price[1])+0.9999999
            if datetime.now().strftime('%H:%M') != '20:55':
                f.write(str(price[0])+','+str(now_price)) 
                print('update price:',currency,price[0])
            else:
                if currency == 'au':
                    f.write('21.6,100')
                    print('update au_price:','21.6')    
                else:
                    f.write('27.97,100')
                    print('update usd_price:','27.97')
            f.truncate()

    return price

def get_detail(currency,data):
    if currency == 'au':
        index = 3
        price = update_file('au')
    else :
        index = 0
        price = update_file('usd')
    
    time = data['RespCode']['Time']
    now_price = data['RespBody']['RateList'][index]['ImmeSell']
    detail = time+' '+data['RespBody']['RateList'][index]['CurrencyCName']+':'+now_price
    CurrencyCName = data['RespBody']['RateList'][index]['CurrencyCName']
    print(detail)
    return detail,price,now_price,CurrencyCName

@app.route("/", methods=['GET'])
def ubot():
    res = requests.post(url)
    soup = BeautifulSoup(res.text, 'lxml')
    data = json.loads(soup.getText())

    currency_list = ['usd','au']
    detail = ''
    for currency in currency_list:
        all_detail = get_detail(currency,data)
        detail = detail +'</br>'+all_detail[0]
        price = all_detail[1]
        now_price = all_detail[2]
        CurrencyCName = all_detail[3]

        if float(now_price) <= float(price[0]) and float(now_price) != float(price[1]):
            headers = {
                "Authorization": "Bearer " + "0b7JgWLaBQgwE3T3etqWxbzfJMOVQQnFw6lYm2AZdjg",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            params = {"message":CurrencyCName+':'+str(now_price)}
            r = requests.post("https://notify-api.line.me/api/notify",
                            headers=headers, params=params)
            print(r.status_code)
            update_file(currency,now_price,'w','no')
        
        else:
            update_file(currency,now_price,'w')

    return detail 


@app.route("/change_price", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body, "Signature: " + signature)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
       abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    print(msg)
    # msg = msg.encode('utf-8')
    try:
        float(msg)
        try:
            if float(msg) >=25:
                update_file("usd",msg,'w','yes')
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text='美金變更為'+str(msg)))
            else:
                update_file("au",msg,'w','yes')
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text='澳幣變更為'+str(msg)))
        except Exception as e:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=str(e.args)))
    except:
        pass

if __name__ == "__main__":
    app.run(debug=True)

