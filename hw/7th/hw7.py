import math
import operator
from collections import defaultdict

import numpy as np
import psycopg2
from scipy.linalg import svd
from sklearn.feature_extraction.text import CountVectorizer

from hw.third.hw3 import filter_sentence

RANK = 5
conn = psycopg2.connect(database='searching', user='postgres', password='postgres')
cur = conn.cursor()


def calc_cos_m(vec1, vec2):
    pairs = zip(vec1, vec2)
    num = sum(pair[0] * pair[1] for pair in pairs)
    den = math.sqrt(sum(el * el for el in vec1)) * math.sqrt(sum(el * el for el in vec2))
    return num / den if den != 0 else 0


def get_matrix(docs, query):
    cv = CountVectorizer(tokenizer=lambda doc: doc, lowercase=False)
    words_in_docs = []
    for doc in docs:
        cur.execute('select term from words_porter where article_id = %s', (doc,))
        words = [word[0] for word in cur.fetchall()]
        words_in_docs.append(words)
    tdm = cv.fit_transform(words_in_docs).toarray().transpose()
    q_t = cv.transform([query]).toarray()
    return tdm, q_t


def get_rank_docs(query, vector, docs):
    result = defaultdict(float)
    query = np.diagonal(query)
    for i, doc in enumerate(docs):
        cur.execute('select url from articles where id = %s', (doc,))
        url = cur.fetchone()[0]
        similarity = calc_cos_m(query, vector[i])
        result[url] = similarity
    return result


def calculate_lsi(query, docs):
    a_matrix, query_vector = get_matrix(docs, query)
    u, s, vt = svd(a_matrix, full_matrices=False)
    u_k = u[:, :RANK]
    s_k = np.diag(s[:RANK, ])
    v_k = vt.transpose()[:, :RANK]
    m1 = np.matmul(query_vector, u_k)
    q = m1 * np.linalg.inv(s_k)
    doc_ranks = get_rank_docs(q, v_k, documents)
    doc_ranks = sorted(doc_ranks.items(), key=operator.itemgetter(1), reverse=True)
    return doc_ranks


if __name__ == '__main__':
    sentence = 'продолжаем рассказывать о советских портативных кассетных магнитофонах'
    cur.execute('select id from articles')
    documents = [doc[0] for doc in cur.fetchall()]
    query = filter_sentence(sentence)
    result = calculate_lsi(query, documents)

    print(result[:10])
