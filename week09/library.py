from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
Base = declarative_base()


class Book(Base):

    __tablename__ = 'BOOK'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    year = Column(String)
    genre = Column(String)


class Library(object):

    def create_table(self):

        engine = create_engine('sqlite:///library.db')
        Base.metadata.create_all(engine)

    def insert_book(self, id, title, author, year, genre):
        engine = create_engine('sqlite:///library.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        book = Book(id = id, title = title, author = author, year = year, genre = genre)
        session.add(book)
        session.commit()
        session.close()

    def search_book(self, title):
        print("\nSearch for book: " + title + "...")
        engine = create_engine('sqlite:///library.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker()
        DBSession.bind = engine
        session = DBSession()
        books = session.query(Book).filter(Book.title == title)
        for book in books:
            print(book.id, book.title, book.author, book.year, book.genre)
        session.close()

    def search_author(self, author):
        print("\nSearch for author: " + author + "...")
        engine = create_engine('sqlite:///library.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker()
        DBSession.bind = engine
        session = DBSession()
        books = session.query(Book).filter(Book.author == author)
        for book in books:
            print(book.id, book.title, book.author, book.year, book.genre)
        session.close()


library = Library()
try:
    library.create_table()

except:
    print("Table already there!")

try:
    library.insert_book('001', 'Agile Design', 'Tom', '1997', 'textbook')
    library.insert_book('002', 'Cooking', 'Jack', '1998', 'cookbook')
    library.insert_book('003', 'Solid Principle', 'Tom', '2002', 'cookbook')
except:
    print("Books already there!")

library.search_book('Agile Design')
library.search_author('Tom')


