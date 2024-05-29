# /src/library.py
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import logging

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    penalty = Column(Float, default=0.0)
    reputation = Column(Integer, default=100)
    max_books = Column(Integer, default=10)
    return_days = Column(Integer, default=14)
class Book(Base):
    __tablename__ = 'books'

    isbn = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    copies = Column(Integer)

    def __str__(self):
        return f"ID: {self.isbn}, Название: {self.title}, Автор: {self.author}, Количество копий: {self.copies}"

class BorrowedBook(Base):
    __tablename__ = 'borrowed_books'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    isbn = Column(Integer, ForeignKey('books.isbn'))
    borrow_date = Column(DateTime, default=datetime.now)
    return_date = Column(DateTime)
    due_date = Column(DateTime)


    user = relationship("User")
    book = relationship("Book")

    def set_due_date(self):
        self.due_date = datetime.now() + timedelta(days=14)

class Library:
    HIGH_REPUTATION_LIMIT = 10  # Максимальное количество книг для пользователей с высокой репутацией
    MIDDLE_REPUTATION_LIMIT = 5  # Максимальное количество книг для пользователей со средней репутацией
    LOW_REPUTATION_LIMIT = 2   # Максимальное количество книг для пользователей с низкой репутацией
    HIGH_REPUTATION_RETURN_DAYS = 14  # Срок возврата для пользователей с высокой репутацией (в днях)
    MIDDLE_REPUTATION_RETURN_DAYS = 7  # Срок возврата для пользователей со средней репутацией (в днях)
    LOW_REPUTATION_RETURN_DAYS = 3    # Срок возврата для пользователей с низкой репутацией (в днях)

    def __init__(self, db_file='library.db'):
        self.engine = create_engine(f'sqlite:///{db_file}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def add_book(self, isbn, title, author, copies):
        new_book = Book(isbn=isbn, title=title, author=author, copies=copies)
        self.session.add(new_book)
        self.session.commit()

    def update_book(self, isbn, title=None, author=None, copies=None):
        book = self.session.query(Book).filter_by(isbn=isbn).first()
        if book:
            if title is not None:
                book.title = title
            if author is not None:
                book.author = author
            if copies is not None:
                book.copies = copies
            self.session.commit()
        else:
            raise ValueError("Книга с указанным ID не найдена.")

    def delete_book(self, isbn):
        book = self.session.query(Book).filter_by(isbn=isbn).first()
        if book:
            self.session.delete(book)
            self.session.commit()
        else:
            raise ValueError("Книга с указанным ID не найдена.")

    def view_book(self, isbn):
        book = self.session.query(Book).filter_by(isbn=isbn).first()
        return book

    def book_exists(self, isbn):
        book = self.session.query(Book).filter_by(isbn=isbn).first()
        return book is not None

    def register_user(self, user_id, name):
        new_user = User(user_id=user_id, name=name, reputation=100)  # Устанавливаем репутацию по умолчанию
        self.session.add(new_user)
        self.session.commit()

    def user_exists(self, user_id):
        user = self.session.query(User).filter_by(user_id=user_id).first()
        return user is not None

    def close_connection(self):
        self.session.close()
        self.session = None


    def view_user(self, user_id):
        user = self.session.query(User).filter_by(user_id=user_id).first()
        return user

    def update_user(self, user_id, name, max_books=None, reputation=None):
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user:
            user.name = name
            if max_books is not None:
                user.max_books = max_books
            if reputation is not None:
                user.reputation = reputation
            self.session.commit()
        else:
            raise ValueError("Пользователь с указанным ID не найден.")

    def delete_user(self, user_id):
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user:
            self.session.delete(user)
            self.session.commit()
        else:
            raise ValueError("Пользователь с указанным ID не найден.")

    def borrow_book(self, user_id, isbn):
        try:
            user = self.session.query(User).filter_by(user_id=user_id).first()
            book = self.session.query(Book).filter_by(isbn=isbn).first()

            if user is None:
                raise ValueError(f"Пользователь с ID {user_id} не найден.")
            if book is None:
                raise ValueError(f"Книга с ID {isbn} не найдена.")
            if book.copies == 0:
                raise ValueError("Нет доступных копий книги.")

            # Определение максимального количества книг и срока возврата в зависимости от репутации пользователя
            if user.reputation >= 80:
                max_copies = self.HIGH_REPUTATION_LIMIT
                return_days = self.HIGH_REPUTATION_RETURN_DAYS
            elif 50 <= user.reputation < 80:
                max_copies = self.MIDDLE_REPUTATION_LIMIT
                return_days = self.MIDDLE_REPUTATION_RETURN_DAYS
            else:
                max_copies = self.LOW_REPUTATION_LIMIT
                return_days = self.LOW_REPUTATION_RETURN_DAYS

            # Проверяем, сколько книг уже взял пользователь
            borrowed_books_count = self.session.query(BorrowedBook).filter_by(user_id=user_id).count()

            if borrowed_books_count >= max_copies:
                raise ValueError(f"Достигнуто максимальное количество книг для пользователя с ID {user_id}.")

            # Уменьшаем количество доступных копий книги
            book.copies -= 1

            # Устанавливаем дату взятия и срок возврата
            borrow_date = datetime.now()
            due_date = borrow_date + timedelta(days=return_days)

            # Создаем новую запись о взятой книге
            new_borrowed_book = BorrowedBook(user_id=user_id, isbn=isbn, borrow_date=borrow_date, due_date=due_date)

            # Сохраняем изменения
            self.session.add(new_borrowed_book)
            self.session.commit()
        except Exception as e:
            self.logger.error(f"Ошибка при взятии книги: {e}")
            self.session.rollback()

    def return_book(self, user_id, isbn):
        try:
            # Получаем пользователя из базы данных
            user = self.session.query(User).filter_by(user_id=user_id).first()

            # Получаем информацию о взятой книге из базы данных
            borrowed_book = self.session.query(BorrowedBook).filter_by(user_id=user_id, isbn=isbn).first()

            if borrowed_book is None:
                raise ValueError("Для пользователя нет взятой книги.")

            # Удаляем запись о взятой книге
            self.session.delete(borrowed_book)
            self.session.commit()

            # Увеличиваем количество доступных копий книги
            book = self.session.query(Book).filter_by(isbn=isbn).first()
            if book is not None:
                book.copies += 1

                # Проверяем, была ли книга возвращена в срок, и начисляем штраф при необходимости
                if borrowed_book.return_date and borrowed_book.return_date > borrowed_book.due_date:
                    overdue_days = (borrowed_book.return_date - borrowed_book.due_date).days
                    overdue_penalty = overdue_days * 5
                    user.penalty += overdue_penalty
                    user.reputation -= user.penalty
                else:
                    # Если книга была возвращена в срок, увеличиваем репутацию пользователя
                    user.reputation += 5

                # Проверка и корректировка репутации пользователя
                user.reputation = min(max(user.reputation, 0), 100)
                self.session.commit()
        except Exception as e:
            self.logger.error(f"Ошибка при возврате книги: {e}")
            self.session.rollback()

    def set_return_date(self, user_id, isbn, return_date):
        try:
            borrowed_book = self.session.query(BorrowedBook).filter_by(user_id=user_id, isbn=isbn).first()

            if borrowed_book is not None:
                borrowed_book.return_date = return_date
                self.session.commit()
            else:
                raise ValueError("Для данного пользователя нет взятой книги с указанным ISBN.")
        except Exception as e:
            self.logger.error(f"Ошибка при установке даты возврата книги: {e}")
            self.session.rollback()

    def get_borrowed_books_count(self, user_id):
        try:
            count = self.session.query(BorrowedBook).filter_by(user_id=user_id).count()
            return count
        except Exception as e:
            self.logger.error(f"Ошибка при получении количества взятых книг: {e}")
            return None

    def view_borrowed_books(self, user_id):
        try:
            borrowed_books = self.session.query(BorrowedBook).filter_by(user_id=user_id).all()
            count = self.get_borrowed_books_count(user_id)
            return borrowed_books, count
        except Exception as e:
            self.logger.error(f"Ошибка при просмотре взятых книг: {e}")
            return None, None

    def search_books(self, title=None, author=None, isbn=None):
        try:
            query = self.session.query(Book)
            if title:
                query = query.filter(Book.title.like(f'%{title}%'))
            if author:
                query = query.filter(Book.author.like(f'%{author}%'))
            if isbn:
                query = query.filter_by(isbn=isbn)
            return query.all()
        except Exception as e:
            self.logger.error(f"Ошибка при поиске книг: {e}")
            return None

    def search_users(self, name=None, user_id=None):
        try:
            query = self.session.query(User)
            if name:
                query = query.filter(User.name.like(f'%{name}%'))
            if user_id:
                query = query.filter_by(user_id=user_id)
            return query.all()
        except Exception as e:
            self.logger.error(f"Ошибка при поиске пользователей: {e}")
            return None
