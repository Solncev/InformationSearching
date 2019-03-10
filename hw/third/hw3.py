import psycopg2
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

conn = psycopg2.connect(database='searching', user='postgres', password='postgres')
cur = conn.cursor()
stop_words = stopwords.words('russian')
stop_words.add(' ')
snowball_stemmer = SnowballStemmer("russian")


def fill_data():
    cur.execute('SELECT term from words_porter')
    words = cur.fetchall()
    words = [word[0] for word in words]
    words = sorted(words)

    for w in words:
        cur.execute("""INSERT into terms_list(term_text) values (%s) ON CONFLICT (term_text)
         DO UPDATE set term_text = %s returning term_id""", (w, w))
        word_id = cur.fetchone()[0]

        cur.execute('SELECT article_id from words_porter WHERE term = %s', (w,))
        articles = cur.fetchall()

        for article in articles:
            cur.execute('INSERT into article_term(article_id, term_id) values (%s, %s) on conflict do nothing ',
                        (article[0], word_id))
        conn.commit()


def filter_sentence(sentence):
    tokenizer = RegexpTokenizer(r'\w+')
    word_tokens = tokenizer.tokenize(sentence)

    filtered_words = [w for w in word_tokens if not w in stop_words]
    snowball_result_set = [snowball_stemmer.stem(word) for word in filtered_words]
    return snowball_result_set


def intersection(lst1, lst2):
    if len(lst1) == 0:
        return lst2
    if len(lst2) == 0:
        return lst1
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def get_article_url_by_id(ids):
    urls = []
    for id in ids:
        cur.execute('select a.url from articles a where a.id = %s', (id,))
        rows = cur.fetchall()
        for row in rows:
            urls.append(row[0])
    urls = set(urls)
    return urls


def inverted_index_search(sentence):
    words = filter_sentence(sentence)
    articles = dict()
    for word in words:
        cur.execute("""SELECT article_id from article_term as a inner join terms_list as t 
        on a.term_id = t.term_id where t.term_text = %s""", (word,))
        ids = cur.fetchall()
        result_ids = []
        for id in ids:
            result_ids.append(id[0])
        articles[word] = result_ids
    sorted_words = sorted(articles.items(), key=lambda kv: len(kv[1]), reverse=True)
    result = []
    for word, articles in sorted_words:
        if len(articles) > 0:
            result = intersection(result, articles)
    urls = get_article_url_by_id(result)
    return urls


if __name__ == '__main__':
    # needed only once
    fill_data()
    print(inverted_index_search("я сломал систему слов"))
