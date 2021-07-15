import requests
import pymysql

r = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
data = r.json().get('Valute')
app_id = 'f9fff33
if data:
    con = pymysql.connect(host='localhost', db='vista', user='root', password='1')
    cur = con.cursor()
    cur.execute('update rates set value = %s, previous = %s, last_update = now() '
                'where currency = %s', (data['EUR']['Value'], data['EUR']['Previous'], 'VISTA EUR'))
    cur.execute('update rates set value = %s, previous = %s, last_update = now() '
                'where currency = %s', (data['USD']['Value'], data['USD']['Previous'], 'VISTA USD'))
    cur.execute('update rates set value = %s, previous = %s, last_update = now() '
                'where currency = %s', (data['BYN']['Value'], data['BYN']['Previous'], 'BYN'))
    con.commit()
    con.close()

    r = requests.post(url=f'https://openexchangerates.org/api/latest.json'
                          f'?app_id={app_id}'
                          f'&symbols=THB,RUB')
    data = r.json()
    usd_rub = data.get('rates').get('RUB')
    usd_thb = data.get('rates').get('THB')

    if all([usd_rub, usd_thb]):
        rub_thb = round(usd_rub / usd_thb, 4)

        con = pymysql.connect(host='localhost', db='vista', user='root', password='1')
        cur = con.cursor()
        cur.execute('update rates set previous = value, value = %s, last_update = now() '
                    'where currency = %s', (rub_thb, 'THB'))
        con.commit()
        con.close()
