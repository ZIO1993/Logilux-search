#!/usr/bin/env python3.7

import requests
from bs4 import BeautifulSoup
import json
import os.path
import time
import telegram_send

#Variabili globali
minuti = 0
queries = dict()
dbFile = "db.json"
url = "https://www.logilux.it/offerte-di-lavoro"
regioni_cercate = ["italia", "lazio"]

def save(fileName):
    with open(fileName, 'w') as file:
        file.write(json.dumps(queries))

def load_from_file(fileName):
    global queries
    if not os.path.isfile(fileName):
        return

    with open(fileName) as file:
        queries = json.load(file)


def getContainerClass():
    global queries

    print("Scarico la pagina")
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')


    print("Pulisco i risultati da Register e Login")
    for div in soup.find_all('div', class_="RegLog"):
        div.decompose()
    
    print("Cerco il box degli annunci")
    soup = soup.find(id="js-grid-blog-posts")

    print("Inzio a filtrare i risultati per regione")
    global regioni_cercate
    for reg in regioni_cercate:
        print("Filtro per: "+reg)
        filter(soup, reg)
    print("Ho concluso l'esecuzione")

def filter(soup, regione):
    global dbFile
    global queries
    #msg=[]

    item = soup.find_all(class_=regione, recursive=False)
    #counter=1
    for iter in item:
        desc = iter
        luogo_data = iter
        ruolo = iter
        
        luogo_data = luogo_data.find(class_="coll-prov2-mod")
        luogo_data = str(luogo_data.get_text())
        ruolo = ruolo.find(class_="cbp-l-grid-blog-title grid-blog-title-fix")
        ruolo = str(ruolo.get_text())
        desc = desc.find(class_="cbp-l-grid-blog-desc text-subofferte")
        desc = str(desc.select('p')[0].get_text())

        if not queries.get(luogo_data):   # insert the new search
            queries[luogo_data] = {regione: {ruolo: {"desc": desc}}}
            tmp = "Nuovo Evento trovato per "+regione+"\n"+ruolo+"\nLuogo e Data: "+luogo_data+"\n\n Descrizione:"+desc
                #msg.append(tmp)
            queries[luogo_data][regione][ruolo] = {"desc": desc}
            telegram_send.send(messages=[tmp])
            print(tmp)
        save(dbFile)

if __name__ == '__main__':
    while True:
        load_from_file(dbFile)
        getContainerClass()
        save(dbFile)
        time.sleep(minuti * 60)