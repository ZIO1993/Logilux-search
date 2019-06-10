#!/usr/bin/env python3.7

import argparse
import requests
from bs4 import BeautifulSoup
import json
import os.path
#import telegram_send

"""
parser = argparse.ArgumentParser()
parser.add_argument("--name", "--add", dest='name', help="name of new tracking to be added")
parser.add_argument("--url", help="url for your new tracking's search query")
parser.add_argument("--delete", help="name of the search you want to delete")
parser.add_argument('--refresh', dest='refresh', action='store_true', help="refresh search results")
parser.set_defaults(refresh=False)
parser.add_argument('--list', dest='list', action='store_true', help="print a list of current trackings")
parser.set_defaults(list=False)

args = parser.parse_args()
"""

queries = dict()
dbFile = "searches.tracked"
url = "https://www.logilux.it/offerte-di-lavoro"

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

    filter(soup, "italia")

def filter(soup, string):
    item = soup.find_all(class_=string, recursive=False)
    counter=1
    for iter in item:
        desc = iter
        luogo_data = iter
        ruolo = iter
        
        luogo_data = luogo_data.find(class_="coll-prov2-mod")
        luogo_data = luogo_data.get_text()
        ruolo = ruolo.find(class_="cbp-l-grid-blog-title grid-blog-title-fix")
        ruolo = ruolo.get_text()
        desc = desc.find(class_="cbp-l-grid-blog-desc text-subofferte")
        desc = desc.select('p')[0].get_text()
        print()
        print("______________Annuncio "+str(counter)+"____________________")
        print("Luogo e Data: "+str(luogo_data))
        print(str(ruolo))
        print("Descrizione: "+str(desc))

        counter+=1


if __name__ == '__main__':
    getContainerClass()

"""
# load from file
def load_from_file(fileName):
    global queries
    if not os.path.isfile(fileName):
        return

    with open(fileName) as file:
        queries = json.load(file)


def print_queries():
    global queries
    #print(queries, "\n\n")
    for search in queries.items():
        print("\nsearch: ", search[0])
        for query_url in search[1]:
            print("query url:", query_url)
            for url in search[1].items():
                for result in url[1].items():
                    print("\n", result[1].get('title'), ":", result[1].get('price'), "-->", result[1].get('location'))
                    print(" ", result[0])


def refresh():
    global queries
    for search in queries.items():
        for query_url in search[1]:
            run_query(query_url, search[0])


def delete(toDelete):
    global queries
    queries.pop(toDelete)


def run_query(url, name):
    print("running query ", name, url)
    global queries
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    products_list = soup.find(class_='items_listing')
    product_list_items = products_list.find_all(class_='item_list_inner')
    msg = []

    for product in product_list_items:
        desc = product.find(class_='item_description')
        title = desc.find('a').contents[0]
        if(desc.find(class_='item_price') is not None):
            price = desc.find(class_='item_price').contents[0]
        else:
            price = "Unknown price"
        link = desc.find('a').get('href')
        location = desc.find(class_="item_location").contents[0]

        if not queries.get(name):   # insert the new search
            queries[name] = {url: {link: {'title': title, 'price': price, 'location': location}}}
            print("\nNew search added:", name)
            print("Adding result:", title, "-", price, "-", location)
        else:   # add search results to dictionary
            if not queries.get(name).get(url).get(link):   # found a new element
                tmp = "New element found for "+name+": "+title+" @ "+price+" - "+location+" --> "+link
                msg.append(tmp)
                queries[name][url][link] = {'title': title, 'price': price, 'location': location}

    if len(msg) > 0:
        telegram_send.send(messages=msg)
        print("\n".join(msg))
        save(dbFile)
    # print("queries file saved: ", queries)


def save(fileName):
    with open(fileName, 'w') as file:
        file.write(json.dumps(queries))


if __name__ == '__main__':

    load_from_file(dbFile)
    
    if args.list:
        print("printing current status...")
        print_queries()

    if args.url is not None and args.name is not None:
        run_query(args.url, args.name)

    if args.refresh:
        refresh()

    if args.delete is not None:
        delete(args.delete)

    print()
    save(dbFile)
"""