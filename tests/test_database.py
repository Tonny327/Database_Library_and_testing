# /tests/test_database.py
import pytest
from sqlalchemy import inspect
from src.database import create_connection, create_database, Book, User, BorrowedBook
import datetime
from src.library import Library

def test_create_connection():
    engine, Session = create_connection(':memory:')
    assert engine
    assert Session

def test_create_database():
    # Вызываем функцию create_database перед запуском теста
    create_database('library.db')

    engine, _ = create_connection('library.db')
    inspector = inspect(engine)
    assert 'Books' in inspector.get_table_names()
    assert 'Users' in inspector.get_table_names()
    assert 'BorrowedBooks' in inspector.get_table_names()

@pytest.mark.parametrize("isbn, title, author, copies, expected_result", [
    (123456789, "Test Book1", "Test Author1", 3, "ID: 123456789, Название: Test Book1, Автор: Test Author1, Количество копий: 3"),
    (987654321, "Test Book2", "Test Author2", 5, "ID: 987654321, Название: Test Book2, Автор: Test Author2, Количество копий: 5"),
    (456789123, "Test Book3", "Test Author3", 10, "ID: 456789123, Название: Test Book3, Автор: Test Author3, Количество копий: 10"),

])
def test_book_model(isbn, title, author, copies, expected_result):
    book = Book(isbn=isbn, title=title, author=author, copies=copies)
    assert str(book) == expected_result

@pytest.mark.parametrize("user_id, name, penalty, reputation, max_books, return_days, expected_name, expected_penalty, expected_reputation, expected_max_books, expected_return_days ", [
    (1, "Test User1", 0.0, 100, 10, 14, "Test User1",0.0, 100, 10, 14),
    (2, "Test User2", 5.0, 70, 5, 7, "Test User2",5.0, 70, 5, 7),
    (2, "Test User3", 10.5, 20, 2, 3, "Test User3",10.5, 20, 2, 3),
])
def test_user_model(user_id, name, penalty, reputation, max_books, return_days, expected_name,expected_penalty, expected_reputation, expected_max_books, expected_return_days):
    user = User(user_id=user_id, name=name, penalty=penalty, reputation=reputation, max_books=max_books, return_days=return_days)
    assert user.name == expected_name
    assert user.penalty == expected_penalty
    assert user.reputation == expected_reputation
    assert user.max_books == expected_max_books
    assert user.return_days == expected_return_days


@pytest.mark.parametrize(
    "borrow_id, user_id, isbn, borrow_date, due_date, return_date, penalty, expected_user_id, expected_isbn, expected_penalty, expected_borrow_date, expected_due_date, expected_return_date, reputation",
    [
        (1, 1, 123456789, None, None, None, 0.0, 1, 123456789, 0.0, None, None, None, 90),  # Высокая репутация
        (2, 2, 987654321, datetime.date(2024, 1, 1), datetime.date(2024, 1, 15), datetime.date(2024, 1, 5), 0.0, 2,
         987654321, 0.0, datetime.date(2024, 1, 1), datetime.date(2024, 1, 15), datetime.date(2024, 1, 5), 90),
        # Высокая репутация
        (3, 3, 112233445, datetime.date(2024, 2, 1), datetime.date(2024, 2, 8), datetime.date(2024, 2, 15), 5.0, 3,
         112233445, 5.0, datetime.date(2024, 2, 1), datetime.date(2024, 2, 8), datetime.date(2024, 2, 15), 65),
        # Средняя репутация
        (4, 4, 556677889, datetime.date(2024, 3, 1), datetime.date(2024, 3, 4), datetime.date(2024, 3, 10), 0.0, 4,
         556677889, 0.0, datetime.date(2024, 3, 1), datetime.date(2024, 3, 4), datetime.date(2024, 3, 10), 40),
        # Низкая репутация
    ]
)
def test_borrowed_book_model(borrow_id, user_id, isbn, borrow_date, due_date, return_date, penalty, expected_user_id,
                             expected_isbn, expected_penalty, expected_borrow_date, expected_due_date,
                             expected_return_date, reputation):
    borrowed_book = BorrowedBook(
        borrow_id=borrow_id, user_id=user_id, isbn=isbn,
        borrow_date=borrow_date, due_date=due_date,
        return_date=return_date, penalty=penalty
    )

    assert borrowed_book.user_id == expected_user_id
    assert borrowed_book.isbn == expected_isbn
    assert borrowed_book.penalty == expected_penalty
    assert borrowed_book.borrow_date == expected_borrow_date
    assert borrowed_book.due_date == expected_due_date
    assert borrowed_book.return_date == expected_return_date

    # Проверка сроков возврата в зависимости от репутации, если даты заданы
    if borrow_date and due_date:
        if reputation >= 80:
            assert (due_date - borrow_date).days == Library.HIGH_REPUTATION_RETURN_DAYS
        elif 50 <= reputation < 80:
            assert (due_date - borrow_date).days == Library.MIDDLE_REPUTATION_RETURN_DAYS
        else:
            assert (due_date - borrow_date).days == Library.LOW_REPUTATION_RETURN_DAYS


