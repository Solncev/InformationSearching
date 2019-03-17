import math

import psycopg2

from hw.third.hw3 import filter_sentence

articles_count = 30
conn = psycopg2.connect(database='searching', user='postgres', password='postgres')
cur = conn.cursor()


def count_idf(word):
    cur.execute(
        "select count(a.article_id) from article_term a where a.term_id ="
        " (select term_id from terms_list where term_text=%s)", (word,))
    x = cur.fetchone()[0]
    idf = 0 if x == 0 else math.log10(articles_count / x)
    return idf


def search(query):
    print(query)
    words = filter_sentence(query)
    query_vector = list(map(count_idf, words))
    query_ids = []

    article_ids = set()
    for word in words:
        cur.execute("select term_id from terms_list where term_text=%s", (word,))
        word_id = cur.fetchone()
        query_ids.append(word_id)
        cur.execute('select a.article_id from article_term a where a.term_id = %s', (word_id,))
        rows = cur.fetchall()
        for row in rows:
            article_ids.add(row[0])

    articles_idf = {}
    for article in article_ids:
        vector = []
        for w_id in query_ids:
            cur.execute('select a.tf_idf from article_term a where a.article_id = %s and a.term_id=%s', (article, w_id))
            row = cur.fetchone()
            if row:
                vector.append(row[0])
            else:
                vector.append(0)
        articles_idf[article] = vector

    cos_values = {}
    for art in articles_idf.keys():
        doc_vector = articles_idf[art]
        cos = sum([a * b for a, b in zip(query_vector, doc_vector)]) \
              / (math.sqrt(sum(a * a for a in query_vector)) * math.sqrt(sum(b * b for b in doc_vector)))
        cos_values[art] = cos

    sorted_by_cos = sorted(cos_values.items(), key=lambda kv: kv[1], reverse=True)
    for i in range(len(sorted_by_cos) if len(sorted_by_cos) < 10 else 10):
        id = sorted_by_cos[i][0]
        cos = sorted_by_cos[i][1]
        cur.execute('select a.url from articles a where a.id = %s', (id,))
        url = cur.fetchone()[0]
        print(url + ' ' + str(cos))


if __name__ == '__main__':
    search('собственно в 2019 я сломал систему слов в актуальных и переменно переходящих в забытые соцсетях google')
