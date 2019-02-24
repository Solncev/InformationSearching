import psycopg2 as psycopg2
from lxml import html
import requests

PATH_TO_TITLE='//span[@class="post__title-text"]/text()'
PATH_TO_TAGS='//dd[@class="post__tags-list"]//li/a/text()'
PATH_TO_CONTENT="//div[@class='post__text post__text-html js-mediator-article']"

conn = psycopg2.connect(database='searching', user='postgres', password='postgres')
cur = conn.cursor()

cur.execute("INSERT INTO students (name, surname, mygroup) VALUES (%s, %s, %s) RETURNING id",
            ("Солнцев", "Марат", "11-501"))
student_id = cur.fetchone()[0]

pages = ['https://habr.com/ru/users/sound_cult/posts/', 'https://habr.com/ru/users/ragequit/posts/page2/']
posts = []

for link in pages:
    page = requests.get(link)
    tree = html.fromstring(page.content)
    posts.extend(tree.xpath('//a[@class="post__title_link"]/@href'))

for post in posts[:30]:
    page = requests.get(post)
    tree = html.fromstring(page.content)

    title = tree.xpath(PATH_TO_TITLE)[0]
    print(title)

    tags = tree.xpath(PATH_TO_TAGS)
    tags = '; '.join(tags)
    print(tags)

    content = tree.xpath(PATH_TO_CONTENT)[0].text_content().strip()
    print(content[:50] + '\n\n')

    cur.execute("INSERT INTO articles (title, keywords, content, url, student_id) VALUES (%s, %s, %s, %s, %s)",
                (title, tags, content, post, student_id))

conn.commit()
cur.close()
conn.close()