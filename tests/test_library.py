# /tests/test_library.py
import pytest
from src.library import Library, Book, User, BorrowedBook
from datetime import datetime, timedelta
@pytest.fixture
def library():
    return Library(':memory:')
@pytest.mark.parametrize("user_id, user_name, isbn, title, author, copies, max_books, reputation, expected_exception", [
    # Тест попытки взять книгу, у которой нет доступных копий
    (1, "Test User", 123456789, "Test Book", "Test Author", 0, 10, 100, ValueError("Нет доступных копий книги.")),
    # Тест успешного взятия книги
    (1, "Test User", 123456789, "Test Book", "Test Author", 1, 10, 100, None),
    # Тест попытки взять книгу для несуществующего пользователя
    (2, "Test User", 123456789, "Test Book", "Test Author", 1, 10, 100, ValueError(f"Пользователь с ID 2 не найден.")),
    # Тест попытки взять несуществующую книгу
    (1, "Test User", 987654321, "Test Book", "Test Author", 1, 10, 100, ValueError(f"Книга с ID 987654321 не найдена.")),
    # Тест попытки взять книгу, когда достигнуто максимальное количество книг для пользователя
    (1, "Test User", 123456789, "Test Book", "Test Author", 1, 1, 100, ValueError(f"Достигнуто максимальное количество книг для пользователя с ID 1.")),
    # Тест расчета срока возврата книги
    (1, "Test User", 123456789, "Test Book", "Test Author", 1, 10, 20, None),
])
def test_borrow_book(library, user_id, user_name, isbn, title, author, copies, max_books, reputation, expected_exception):
    # Создаем пользователя и добавляем книгу в библиотеку
    library.register_user(user_id, user_name)
    library.add_book(isbn, title, author, copies)
    library.update_user(user_id, name=user_name, max_books=max_books, reputation=reputation)

    # Пытаемся взять книгу пользователем
    try:
        library.borrow_book(user_id, isbn)
        # Если исключение не возникло, проверяем, что книга добавлена в список взятых книг пользователя
        if expected_exception is None:
            borrowed_books, _ = library.view_borrowed_books(user_id)
            assert borrowed_books[0].isbn == isbn
    except ValueError as e:
        # Если ожидается исключение, убеждаемся, что оно сгенерировано с правильным сообщением
        assert str(e) == str(expected_exception)
        return

@pytest.mark.parametrize("isbn, title, author, copies", [
    (123456789, "Test Book1", "Test Author1", 3),
    (987654321, "Test Book2", "Test Author2", 5),
    (456789123, "Test Book3", "Test Author3", 10),
])
def test_add_book(library, isbn, title, author, copies):
    library.add_book(isbn, title, author, copies)
    book = library.view_book(isbn)
    assert book.isbn == isbn
    assert book.title == title
    assert book.author == author
    assert book.copies == copies

@pytest.mark.parametrize("isbn, title, author, copies, new_title, new_author, new_copies", [
    (123456789, "Test Book1", "Test Author1", 3, "New Title", None, None),
    (987654321, "Test Book2", "Test Author2", 5, None, "New Author", None),
    (456789123, "Test Book3", "Test Author3", 10, None, None, 15),
])
def test_update_book(library, isbn, title, author, copies, new_title, new_author, new_copies):
    library.add_book(isbn, title, author, copies)
    library.update_book(isbn, new_title, new_author, new_copies)
    book = library.view_book(isbn)
    if new_title is not None:
        assert book.title == new_title
    if new_author is not None:
        assert book.author == new_author
    if new_copies is not None:
        assert book.copies == new_copies

@pytest.mark.parametrize("isbn, title, author, copies", [
    (123456789, "Test Book1", "Test Author1", 3),
    (987654321, "Test Book2", "Test Author2", 5),
    (456789123, "Test Book3", "Test Author3", 10),
])
def test_delete_book(library, isbn, title, author, copies):
    library.add_book(isbn, title, author, copies)
    library.delete_book(isbn)
    assert library.view_book(isbn) is None

@pytest.mark.parametrize("user_id, name", [
    (1, "Test User1"),
    (2, "Test User2"),
    (3, "Test User3"),
])
def test_register_user(library, user_id, name):
    library.register_user(user_id, name)
    user = library.view_user(user_id)
    assert user.user_id == user_id
    assert user.name == name

@pytest.mark.parametrize("user_id, name, new_name", [
    (1, "Test User1", "New Name1"),
    (2, "Test User2", "New Name2"),
    (3, "Test User3", "New Name3"),
])
def test_update_user(library, user_id, name, new_name):
    library.register_user(user_id, name)
    library.update_user(user_id, new_name)
    user = library.view_user(user_id)
    assert user.name == new_name

@pytest.mark.parametrize("user_id, name", [
    (1, "Test User1"),
    (2, "Test User2"),
    (3, "Test User3"),
])
def test_delete_user(library, user_id, name):
    library.register_user(user_id, name)
    library.delete_user(user_id)
    assert library.view_user(user_id) is None

@pytest.mark.parametrize("return_date, due_date, expected_penalty, expected_reputation", [
    # Возврат книги в срок
    (datetime.now(), datetime.now() + timedelta(days=7), 0, 100),
    # Возврат книги с просрочкой на 1 день
    (datetime.now() + timedelta(days=1), datetime.now(), 5, 95),
    # Возврат книги с просрочкой на 3 дня
    (datetime.now() + timedelta(days=3), datetime.now(), 15, 85),
    # Возврат книги с просрочкой на 5 дней
    (datetime.now() + timedelta(days=5), datetime.now(), 25, 75),
    # Проверка того что значение репутации не может опускаться ниже 0
    (datetime.now() + timedelta(days=25), datetime.now(), 125, 0),

])
def test_return_book(library, return_date, due_date, expected_penalty, expected_reputation):
    user_id = 1
    isbn = 123456789

    # Создаем пользователя и добавляем взятую книгу
    library.register_user(user_id, "Test User")
    library.add_book(isbn, "Test Book", "Test Author", 1)
    library.borrow_book(user_id, isbn)
    borrowed_book = library.session.query(BorrowedBook).filter_by(user_id=user_id, isbn=isbn).first()
    borrowed_book.due_date = due_date
    library.session.commit()

    # Устанавливаем дату возврата и возвращаем книгу
    library.set_return_date(user_id, isbn, return_date)
    library.return_book(user_id, isbn)

    # Проверяем штраф и репутацию пользователя
    user = library.session.query(User).filter_by(user_id=user_id).first()
    assert user.penalty == expected_penalty
    assert user.reputation == expected_reputation

@pytest.mark.parametrize("user_id, book_count", [
    (1, 0),  # Нет взятых книг
    (2, 2),  # Две взятые книги
    (3, 5),  # Пять взятых книг
])
def test_get_borrowed_books_count(library, user_id, book_count):
    # Добавляем пользователя и взятые книги
    library.register_user(user_id, f"Test User {user_id}")
    for i in range(book_count):
        library.add_book(1000000000 + i, f"Test Book {i+1}", "Test Author", 1)
        library.borrow_book(user_id, 1000000000 + i)

    # Проверяем количество взятых книг
    count = library.get_borrowed_books_count(user_id)
    assert count == book_count

@pytest.mark.parametrize("user_id, book_count", [
    (1, 0),  # Нет взятых книг
    (2, 2),  # Две взятые книги
    (3, 5),  # Пять взятых книг
])
def test_view_borrowed_books(library, user_id, book_count):
    # Добавляем пользователя и взятые книги
    library.register_user(user_id, f"Test User {user_id}")
    for i in range(book_count):
        library.add_book(2000000000 + i, f"Test Book {i+1}", "Test Author", 1)
        library.borrow_book(user_id, 2000000000 + i)

    # Просматриваем взятые книги пользователя
    borrowed_books, count = library.view_borrowed_books(user_id)

    # Проверяем, что список не пустой и количество книг соответствует ожидаемому
    assert borrowed_books is not None
    assert len(borrowed_books) == count == book_count
@pytest.mark.parametrize("name, user_id", [
    ("Test User 1", None),  # Поиск по имени
    (None, 1),  # Поиск по ID пользователя
])
def test_search_users(library, name, user_id):
    # Добавляем несколько пользователей в библиотеку
    library.register_user(1, "Test User 1")
    library.register_user(2, "Test User 2")

    # Поиск пользователей
    users = library.search_users(name=name, user_id=user_id)

    # Проверяем, что пользователи найдены и соответствуют ожидаемому
    if name:
        assert len(users) == 1
        assert users[0].name == name
    elif user_id:
        assert len(users) == 1
        assert users[0].user_id == user_id

def test_search_books(library):
    # Добавляем несколько книг в библиотеку
    library.add_book(123456789, "Test Book 1", "Test Author 1", 1)
    library.add_book(987654321, "Test Book 2", "Test Author 2", 1)

    # Поиск книг по названию и автору
    books_by_title = library.search_books(title="Test Book 1")
    books_by_author = library.search_books(author="Test Author 2")

    # Проверяем, что книги найдены и соответствуют ожидаемому
    assert len(books_by_title) == 1
    assert books_by_title[0].title == "Test Book 1"
    assert len(books_by_author) == 1
    assert books_by_author[0].author == "Test Author 2"

def test_search_books_by_isbn(library):
    # Добавляем книги с нужными ISBN в библиотеку
    library.add_book(123456789, "Test Book 1", "Test Author 1", 1)
    library.add_book(987654321, "Test Book 2", "Test Author 2", 1)

    # Поиск книг по ISBN
    book_by_isbn = library.search_books(isbn=123456789)

    # Проверяем, что книга найдена и соответствует ожидаемому
    assert len(book_by_isbn) == 1
    assert book_by_isbn[0].isbn == 123456789
if __name__ == "__main__":
    pytest.main()
