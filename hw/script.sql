CREATE EXTENSION "uuid-ossp";

CREATE TABLE students
(
  id      uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name    VARCHAR(32),
  surname VARCHAR(32),
  mygroup VARCHAR(32)
);

CREATE TABLE articles
(
  id         uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  title      VARCHAR(256),
  keywords   VARCHAR(256),
  content    TEXT,
  url        VARCHAR(128),
  student_id uuid REFERENCES students (id)
);

create table words_porter
(
  id         uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  term       varchar(64),
  article_id uuid REFERENCES articles (id)
);

create table words_mystem
(
  id         uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  term       varchar(64),
  article_id uuid REFERENCES articles (id)
);

