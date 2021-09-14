from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
from datetime import datetime, timedelta
from lxml import html
import html5lib
import time
import sqlite3

cookies = { 'afisha.sid':'s%3AqVKZb4OPJbvtQoIV9ccvZ0UnRO9i8ZTg.Es7iWs0rP2cIgTA3HtNVH8Lkwgau80w%2BDBK6QsaCZ7U',
               '_csrf': 'OeFTDT_63OhBsFubnyT68S3H' }

user_agent  = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 YaBrowser/19.9.3.314 Yowser/2.5 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3',
        'Accept-Encoding': 'deflate',
        'Accept-Charset': 'windows-1251,utf-8;q=0.7,*;q=0.7',
        'Keep-Alive': '300',
        'Connection': 'keep-alive'
        }

results = []
data = []

month = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}

table_name = 'lifehacker'

def clear_db():
    con = sqlite3.connect('NewsDB.db')
    cur = con.cursor()
    cur.execute('DELETE FROM ' + table_name)
    con.commit()

def creat_db():
    con = sqlite3.connect('NewsDB.db')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS ' + table_name + '(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, title STRING, url VARCHAR UNIQUE, img STRING, short_text STRING, content VARCHAR, genre STRING, author STRING, date STRING, source INTEGER)')
    con.commit()

def sql_insert(entities):
    con = sqlite3.connect('NewsDB.db')
    cur = con.cursor()
    cur.execute('INSERT INTO ' + table_name + '(title, url, img, genre, author, short_text, content, date, source) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', entities)
    con.commit()


def get_html(url):
     r = requests.get(url, headers=user_agent,  cookies= cookies).text #Попробовать затолкать сюда BeautifulSoup
     return r

def find_elements_on_page(r):
    sitepage = BeautifulSoup(r, 'html5lib')
    pool = sitepage.find('div', class_='row display-flex')
    links = pool.find_all('div', class_='flow-post')
    return links

def convert(date_time):

    format = '%d:%m:%Y'
    datetime_str = datetime.datetime.strptime(date_time, format)

    return datetime_str

def get_page_data(links):
    con = sqlite3.connect('NewsDB.db')
    cur = con.cursor()

    for link in links:
        g = link.find('a').get('href')
        #last = cur.execute('SELECT * FROM ' + table_name + ' WHERE url = ' + g)
        #if (last):
        news(get_html(g), g)
        #else:
            #print('Статья' + g + ' уже есть')

    con.commit()


def news(ns, url):
    source = 1;
    static = 'https://lifehacker.ru/'
    info = BeautifulSoup(ns, 'lxml')
    try:
        title = info.find('h1', class_='single__title').string
        print(title)

        img = info.find('img', {'id': 'single-post-header-pattern-image'}).get('src')
        genre = info.find('div', class_='meta-info__tax meta-info__item').text

        try:
            author = info.find('div', class_='meta-info__author meta-info__item').text
        except AttributeError:
            author = ''
            print('Нет автора')

        data_t = datetime.datetime.today()
        print =
        date = info.find('div', class_='social-and-date__date').text

        try:
            short_text = info.find('div', class_='single__excerpt').text
        except:
            short_text = info.find('div', class_='lh-cards__excerpt').text

        #name_content = url.replace(static,'')
        #name_content = name_content.replace('/','')

        content = info.find('div', class_='post-content').text

        #with open("html/" + name_content + ".txt","w") as file:
            #file.write(content)

        entities = (title, url, img, genre, author, short_text, content, date, source)
        sql_insert(entities)

    except:
        print('Партнёрка или сторонний ресурс')




def main():
    creat_db()
    #clear_db()
    page = 1
    while True:

        url = 'https://lifehacker.ru/list/page/{}'.format(str(page))

        element = find_elements_on_page(get_html(url))
        if element:
            get_page_data(element)
            page = page + 1
        else:
            break

main()
