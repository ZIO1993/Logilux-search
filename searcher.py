#!/usr/bin/env python3.7

import time
import requests
from bs4 import BeautifulSoup
import json
import os.path
import time
import telegram_send
from webbot import Browser
import urllib.request

#Var global
delay=1
minuti = 10
queries = dict()
url_offerte = "https://www.logilux.it/offerte-di-lavoro"
url_login = "https://www.logilux.it/browse/login.php"
email=''
password=''
regioni_cercate = ["italia", "lazio"]

#File global
telegram_conf="telegram-send.conf"
account_config="config.json"
dbFile = "db.json"

def loadAccount():
    global email
    global password
    if not os.path.isfile(account_config):
        raise Exception("File config.json not found!!")
    with open(account_config) as file:
        temp = json.load(file)
        email=temp['email']
        password=temp['password']

def print_time():
    ora = time.strftime("%H:%M:%S")
    data = time.strftime("%d/%m/%Y")
    print(ora+" - "+data)

def save(fileName):
    with open(fileName, 'w') as file:
        file.write(json.dumps(queries))

def load_from_file(fileName):
    global queries
    if not os.path.isfile(fileName):
        return

    with open(fileName) as file:
        queries = json.load(file)

def getPage():
    global queries
    global soup

    print("Scarico la pagina")
    web = Browser()
    web.go_to(url_login)
    web.type(email , into='E-mail')
    web.type(password , into='Password')
    web.click('ACCEDI', classname='submit_access')
    time.sleep(delay)
    web.click('OFFERTE DI LAVORO')
    time.sleep(delay)
    page = web.get_page_source()
    web.close_current_tab()
    
    soup = BeautifulSoup(str(page), 'html.parser')
    
    print("Cerco il box degli annunci")
    soup = soup.find("div", id="js-grid-blog-posts")

    print("Inzio a filtrare i risultati per regione")
    global regioni_cercate
    for reg in regioni_cercate:
        print("Filtro per: "+reg)
        filter(soup, reg)
    print("Ho concluso l'esecuzione")

def filter(soup, regione):
    global dbFile
    global queries

    items = soup.find_all(class_="cbp-offerta cbp-item cbp-item-fix "+regione)
    for item in items:
        desc = item
        luogo_data = item
        ruolo = item
        link = item
        photo = item
        
        luogo_data = luogo_data.find(class_="coll-prov2-mod")
        luogo_data = str(luogo_data.get_text())
        ruolo = ruolo.find(class_="cbp-l-grid-blog-title grid-blog-title-fix")
        ruolo = str(ruolo.get_text())
        desc = desc.find(class_="cbp-l-grid-blog-desc text-subofferte")
        desc = str(desc.select('p')[0].get_text())
        link = link.find('a').get('href')
        photo = photo.find('img').get('src')

        if not queries.get(luogo_data):
            print("HO TROVATO UN NUOVO EVENTO!")
            queries[luogo_data] = {regione: {ruolo: {"desc": desc, "link": link, "photo": photo}}}
            tmp = "Nuovo Evento trovato per "+regione.upper()+"\n"+ruolo+"\nLuogo e Data: "+luogo_data+"\n\n Descrizione:\n"+desc+"\n\n "+link
            queries[luogo_data][regione][ruolo] = {"desc": desc, "link":link, "photo": photo}
            urllib.request.urlretrieve(photo, "local-image.jpg")
            with open("local-image.jpg", "rb") as f:
                telegram_send.send(images=[f], captions=[tmp], conf=telegram_conf, disable_web_page_preview=False, parse_mode="markdown")
            
            print(tmp)
        save(dbFile)

if __name__ == '__main__':
    loadAccount()
    while True:
        print_time()
        load_from_file(dbFile)
        getPage()
        save(dbFile)
        print_time()
        time.sleep(minuti * 60)
