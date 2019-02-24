import psycopg2 as psycopg2
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from pymystem3 import Mystem

conn = psycopg2.connect(database='searching', user='postgres', password='postgres')
cur = conn.cursor()

cur.execute("select * from articles")
result_set = cur.fetchall()
stop_words = set(stopwords.words('russian'))
snowball_stemmer = SnowballStemmer("russian")
m = Mystem()

for row in result_set:
    article_id = row[0]
    sentence = row[1].lower()

    tokenizer = RegexpTokenizer(r'\w+')
    word_tokens = tokenizer.tokenize(sentence)
    filtered_words = [w for w in word_tokens if not w in stop_words]
    snowball_result_set = [snowball_stemmer.stem(word) for word in filtered_words]

    print(snowball_result_set)

    lemmas = m.lemmatize(sentence)
    print(lemmas)

cur.close()
conn.close()
