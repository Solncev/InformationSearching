import math
import operator
from collections import defaultdict

import psycopg2

from hw.third.hw3 import filter_sentence

conn = psycopg2.connect(database='searching', user='postgres', password='postgres')
cur = conn.cursor()

K1 = 1.2
B = 0.75
articles_count = 30


def get_avg_article_len():
    cur.execute('select id from articles')
    articles = [article[0] for article in cur.fetchall()]
    words_in_articles = 0
    for article in articles:
        cur.execute('select count(1) from words_porter where article_id = %s', (article,))
        words_in_articles += cur.fetchone()[0]
    return words_in_articles / len(articles)


avg_article_len = get_avg_article_len()


def get_score(doc, query):
    result = 0
    cur.execute('select count(1) from words_porter where article_id = %s', (doc,))
    article_len = cur.fetchone()[0]
    for term in query:
        nom = (get_frequency(term, doc) * (K1 + 1))
        den = (get_frequency(term, doc) * K1 * (1 - B + B * article_len / avg_article_len))
        result += get_idf(term) * (nom / den) if den != 0 else 0
    return result


def get_frequency(term, doc):
    cur.execute('select count(1) from words_porter where article_id = %s and term = %s', (doc, term))
    num_of_term_in_doc = cur.fetchone()[0]
    cur.execute('select count(1) from words_porter where article_id = %s', (doc,))
    article_len = cur.fetchone()[0]
    return num_of_term_in_doc / article_len if article_len != 0 else 0


def get_idf(t):
    cur.execute('select count(distinct article_id) from words_porter where term = %s', (t,))
    num_of_docs_with_term = cur.fetchone()[0]
    res = math.log((articles_count - num_of_docs_with_term + 0.5) / (num_of_docs_with_term + 0.5))
    return res if res > 0 else 0


def search(query):
    words = filter_sentence(query)
    cur.execute('select id from articles')
    articles = [article[0] for article in cur.fetchall()]
    result = defaultdict(float)
    for article in articles:
        s = get_score(article, words)
        cur.execute('select url from articles where id = %s', (article,))
        url = cur.fetchone()[0]
        result[url] = s
    result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)
    return result


if __name__ == '__main__':
    results = search(
        'собственно в 2019 я сломал систему слов в актуальных и переменно переходящих в забытые соцсетях google')
    for r in results[:10]:
        print(r)
