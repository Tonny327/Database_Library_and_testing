# /src/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class Book(Base):
    __tablename__ = 'Books'

    isbn = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    copies = Column(Integer, default=1)

    def __str__(self):
        return f"ID: {self.isbn}, Название: {self.title}, Автор: {self.author}, Количество копий: {self.copies}"

class User(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    penalty = Column(Float, default=0.0)
    reputation = Column(Integer, default=100)
    max_books = Column(Integer, default=10)
    return_days = Column(Integer, default=14)

class BorrowedBook(Base):
    __tablename__ = 'BorrowedBooks'

    borrow_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    isbn = Column(Integer, ForeignKey('Books.isbn'))
    borrow_date = Column(DateTime)
    due_date = Column(DateTime)
    return_date = Column(DateTime, nullable=True)
    penalty = Column(Float, default=0.0)


    user = relationship("User", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_books")

User.borrowed_books = relationship("BorrowedBook", order_by=BorrowedBook.borrow_id, back_populates="user")
Book.borrowed_books = relationship("BorrowedBook", order_by=BorrowedBook.borrow_id, back_populates="book")

def create_connection(db_file):
    engine = create_engine(f'sqlite:///{db_file}')
    Session = sessionmaker(bind=engine)
    return engine, Session

def create_database(db_file):
    engine, _ = create_connection(db_file)
    Base.metadata.create_all(engine)
    print(f"Database {db_file} created with all tables.")

def main():
    create_database('library.db')


if __name__ == '__main__':
    main()
