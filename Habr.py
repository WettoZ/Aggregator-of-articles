from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
from datetime import datetime, timedelta
from lxml import html
import time
import sqlite3

cookies = { 'afisha.sid':'s%3AqVKZb4OPJbvtQoIV9ccvZ0UnRO9i8ZTg.Es7iWs0rP2cIgTA3HtNVH8Lkwgau80w%2BDBK6QsaCZ7U',
               '_csrf': 'OeFTDT_63OhBsFubnyT68S3H'
         }
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

table_name = 'habr'

def clear_db():
    con = sqlite3.connect('NewsDB.db')
    cur = con.cursor()
    cur.execute('DELETE FROM ' + table_name)
    con.commit()

def creat_db():
    con = sqlite3.connect('NewsDB.db')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS ' + table_name + '(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, title STRING, url VARCHAR UNIQUE, img STRING, short_text STRING, content VARCHAR, genre STRING, author, date STRING)')
    con.commit()

def sql_insert(entities):
    con = sqlite3.connect('NewsDB.db')
    cur = con.cursor()
    cur.execute('INSERT INTO ' + table_name + '(title, url, img, genre, author, short_text, content, date) VALUES(?, ?, ?, ?, ?, ?, ?, ?)', entities)
    con.commit()


def get_html(url):
     r = requests.get(url, headers=user_agent,  cookies= cookies).text #Попробовать затолкать сюда BeautifulSoup
     return r

def find_elements_on_page(r):
    sitepage = BeautifulSoup(r, 'lxml')
    pool = sitepage.find('div', class_='posts_list')
    links = pool.find_all('li', class_='content-list__item_post')
    return links

def get_page_data(links):

    for link in links:
        try:
            g = link.find('a', class_='post__title_link').get('href')
            news(get_html(g), g)
        except:
            print('Рекомендации')


def news(ns, url):
    info = BeautifulSoup(ns, 'lxml')
    title = info.find('h1', class_='post__title').text
    print(title)

    try:
        img = info.find('img', {'alt': 'image'}).get('src')
    except:
        img = ''

    poolgenre = info.find('ul', class_='post__hubs')
    poolgenre = poolgenre.find_all('li', class_='inline-list__item inline-list__item_hub')
    date = info.find('span', class_='post__time').text
    date = date.replace('сегодня в', datetime.now().strftime("%d/%m/%Y") )
    genre = 'IT '
    for post in poolgenre:
        genre += post.text + ' '
    author = info.find('span', class_='user-info__nickname user-info__nickname_small').text
    short_text = info.find('div', class_='post__text').text
    content = info.find('div', class_='post__text').text

    entities = (title, url, img, genre, author, short_text, content, date)
    sql_insert(entities)


def main():
    creat_db()
    clear_db()
    page = 1
    while True:

        url = 'https://habr.com/ru/all/page{}/'.format(str(page))

        element = find_elements_on_page(get_html(url))
        if element:
            get_page_data(element)
            page = page + 1
        else:
            break

main()
