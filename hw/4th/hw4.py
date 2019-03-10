import math

import psycopg2 as psycopg2

conn = psycopg2.connect(database='searching', user='postgres', password='postgres')
cur = conn.cursor()


def calculate_tf_idf(article_id, term_id, articles_count):
    cur.execute("select count(*) from article_term where article_id = %s and term_id = %s ;", (article_id, term_id))
    repetition_count = cur.fetchone()[0]
    cur.execute("select count(term_id) from article_term where article_id = %s", (article_id,))
    terms_count = cur.fetchone()[0]
    tf = repetition_count / float(terms_count)
    cur.execute("select count(article_id) from article_term where term_id = %s", (term_id,))
    articles_with_term_count = cur.fetchone()[0]
    idf = math.log((articles_count / float(articles_with_term_count)))
    return tf * idf


def get_articles_ids():
    ids = []
    cur.execute("select distinct article_id from article_term;")
    for id in cur.fetchall():
        ids.append(id[0])
    return ids


def get_terms_ids(article_id):
    ids = []
    cur.execute("select distinct term_id from article_term where article_id = %s", (article_id,))
    for id in cur.fetchall():
        ids.append(id[0])
    return ids


def get_articles_count():
    cur.execute("select count(distinct(article_id)) from article_term")
    count = cur.fetchone()[0]
    return count


if __name__ == '__main__':
    articles_count = get_articles_count()
    art_ids = get_articles_ids()

    for a_id in art_ids:
        terms_ids = get_terms_ids(a_id)
        for t_id in terms_ids:
            tfidf = calculate_tf_idf(a_id, t_id, articles_count)
            print(tfidf)
            cur.execute("update article_term set tf_idf = %s where article_id = %s and term_id = %s",
                        (tfidf, a_id, t_id))
    conn.commit()
