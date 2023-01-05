import time
# import requests

import pandas as pd
from config import credentials, keywords, x_api_key
from pymongo import MongoClient
from newscatcherapi import NewsCatcherApiClient

# Language format
# af,ar,bg,bn,ca,cs,cy,cn,da,de,el,en,es,et,fa,fi,fr,gu,he,hi,hr,hu,id,it,ja,kn,ko,lt,lv,mk,ml,mr,ne,nl,no,pa,pl,pt,ro,ru,sk,sl,so,sq,sv,sw,ta,te,th,tl,tr,tw,uk,ur,vi
# Country format
# https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2

fetcher_config = {
    # 'countries': 'AT,DE,CH',
    'language': 'de,en,fr',
    'target_collection': 'live_articles',
    'batch_size': 20,
}

processed_keywords = []
counter = 0
mongo_client = MongoClient(credentials).get_database('DATABASE')
target_collection = mongo_client.get_collection(fetcher_config['target_collection'])


def prepare_keywords_data(struct):
    for keyword_name in struct:
        if keyword_name == "general_keywords_AND":
            for i in range(len(struct[keyword_name])):
                for j in range(i + 1, len(struct[keyword_name])):
                    processed_keywords.append(struct[keyword_name][i] + " " + struct[keyword_name][j])
        else:
            for kw in struct[keyword_name]:
                if "\"" + kw + "\"" not in processed_keywords:
                    processed_keywords.append("\"" + kw + "\"")


def write_to_mongo(data_df):
    try:
        data_dict = data_df.to_dict("records")
        target_collection.insert_many(data_dict)
        return True
    except Exception as e:
        print("An exception occurred ::", e)
        return False


if __name__ == '__main__':
    print("--START GOOGLENEWS FETCHER--")
    prepare_keywords_data(keywords)
    for k in processed_keywords:
        print(k)

    newscatcherapi = NewsCatcherApiClient(x_api_key=x_api_key)
    df = pd.DataFrame(
        columns=['created_at', 'title', 'text', 'source', 'url', 'country', 'topic', 'language', 'keyword'])
    unique_ids = []

    for keyword in processed_keywords:
        # querystring = {"q": keyword, "lang": "en", "page_size": 100}
        # news_articles = requests.request("GET", url, headers=headers, params=querystring).json()
        # Parametar    from_="2021/12/21"       DEFAULT is 2 weeks
        if 'countries' in fetcher_config.keys() and 'language' in fetcher_config.keys():
            news_articles = newscatcherapi.get_search_all_pages(q=keyword, from_="2022/12/15",
                                                                lang=fetcher_config['language'],
                                                                countries=fetcher_config['countries'],
                                                                page_size=100)
        elif 'countries' in fetcher_config.keys():
            news_articles = newscatcherapi.get_search_all_pages(q=keyword, from_="2022/12/15",
                                                                countries=fetcher_config['countries'],
                                                                page_size=100)
        elif 'language' in fetcher_config.keys():
            news_articles = newscatcherapi.get_search_all_pages(q=keyword, from_="2022/12/15",
                                                                lang=fetcher_config['language'],
                                                                page_size=100)
        else:
            news_articles = newscatcherapi.get_search_all_pages(q=keyword, from_="2022/12/15", page_size=100)
        # print('Total HITS:')
        # print(news_articles['total_hits'])
        # print('Total PAGES')
        # print(news_articles['total_pages'])
        # print('Page SIZE:')
        # print(news_articles['page_size'])
        print(f'KEYWORD: {keyword}')
        print('==============')
        time.sleep(1)
        if news_articles['total_hits'] > 0:
            for article in news_articles['articles']:
                # Deduplicate results
                if article['_id'] not in unique_ids:
                    unique_ids.append(article['_id'])
                    new_row = {
                        '_id': article['_id'],
                        'created_at': article['published_date'],
                        'updated_at': article['published_date'],
                        'title': article['title'],
                        'text': article['summary'],
                        'source': article['clean_url'],
                        'url': article['link'],
                        'country': article['country'],
                        'topic': article['topic'],
                        'is_opinion': article['is_opinion'],
                        'twitter_account': article['twitter_account'],
                        'language': article['language'],
                        'keyword': keyword
                    }
                    new_df = pd.DataFrame([new_row])
                    df = pd.concat([df, new_df], axis=0, ignore_index=True)
                if len(df.index) == fetcher_config['batch_size']:
                    write_to_mongo(df)
                    counter += fetcher_config['batch_size']
                    print("Processed 20")
                    df.drop(df.index, inplace=True)

    if len(df.index) > 0:
        write_to_mongo(df)
        counter += len(df.index)
        print("Processed ", len(df.index))
        df.drop(df.index, inplace=True)

    print("END | Inserted: ", counter)
