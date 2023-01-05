from bs4 import BeautifulSoup
import requests
import pandas as pd
from config import credentials, keywords, time_range
from pymongo import MongoClient

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

url = "https://news.google.com/rss/search"

fetcher_config = {
    'target_collection': 'google_news',
}

mongo_client = MongoClient(credentials).get_database('DATABASE')
target_collection = mongo_client.get_collection(fetcher_config['target_collection'])


def write_to_mongo(df):
    data_dict = df.to_dict("records")
    target_collection.insert_many(data_dict)
    return data_dict


def getContentFromURI(uri):
    content = ""
    html_data = requests.get(uri, headers=headers)
    soup = BeautifulSoup(html_data.content, 'html5lib')
    content = ""
    if soup.find('div', {"class": "entry-content"}):
        print("Entry-Content")
        el = soup.findAll('div', {"class": "entry-content"})
        for e in el:
            elts = e.findAll('p')
            for p in elts:
                content += p.text
    elif soup.find('div', {"class": "main-content"}):
        print("Main-Content")
        el = soup.findAll('div', {"class": "main-content"})
        for e in el:
            elts = e.findAll('p')
            for p in elts:
                content += p.text
    elif soup.find('div', {"class": "post-content"}):
        print("POST-Content")
        el = soup.findAll('div', {"class": "post-content"})
        for e in el:
            elts = e.findAll('p')
            for p in elts:
                content += p.text
    elif soup.find('div', {"class": "content"}):
        print("Content")
        el = soup.findAll('div', {"class": "content"})
        for e in el:
            elts = e.findAll('p')
            for p in elts:
                content += p.text
    elif soup.find('article'):
        print("ARTICLE")
        elts = soup.find('article').findAll('p')
        for p in elts:
            content += p.text
    elif soup.find('article'):
        print("Story-body")
        elts = soup.find("div", {"id": "story-body"}).findAll('p')
        for p in elts:
            content += p.text
    else:
        print("NONE")
        print(uri)
    return content


def gnews(words):
    df = pd.DataFrame(columns=['created_at', 'title', 'text', 'source', 'url', 'keyword'])
    for keyword in words:
        our_url = url + "?q=" + keyword
        if time_range:
            our_url = our_url + "%20when%3A" + time_range
        xml_data = requests.get(our_url, headers=headers)
        soup = BeautifulSoup(xml_data.content, 'xml')
        articles = soup.findAll('item')
        if len(articles) > 0:
            for article in articles:
                row = {
                    'created_at': article.pubDate.string,
                    'title': article.title.string,
                    'text': getContentFromURI(article.link.string),
                    'source': article.source.string,
                    'url': article.link.string,
                    'keyword': keyword
                }
                new_df = pd.DataFrame([row])
                df = pd.concat([df, new_df], axis=0, ignore_index=True)
    return df


if __name__ == '__main__':
    print("--START--")
    data = (gnews(keywords))
    if data.empty:
        print("empty")
    else:
        print("not empty")
        #print(data)
        # NEED TO BATCH !
        write_to_mongo(data) # not working
