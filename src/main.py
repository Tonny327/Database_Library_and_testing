from library import Library
import sys
def print_menu():
    print(f"{'Управление книгами':<40}|{'Управление пользователями':<40}|{'Получение и возврат книг':<40}|{'Функционал поиска':<40}", file=sys.stdout)
    print('-' * 143, file=sys.stdout)
    print(f"{'1. Добавить новую книгу в библиотеку':<40}|{'5. Регистрация нового пользователя':<40}|{'9. Взять книгу':<40}|{'12. Поиск книг по названию, автору или':<40}", file=sys.stdout)
    print(f"{'2. Просмотреть информацию о книге':<40}|{'6. Просмотреть сведения о пользователе':<40}|{'10. Вернуть книгу':<40}|{'   ID книги':<40}", file=sys.stdout)
    print(f"{'3. Обновить информацию о книге':<40}|{'7. Обновить информацию о пользователе':<40}|{'11. Просмотреть все взятые книги ':<40}|{'13. Поиск пользователей по имени или ':<40}", file=sys.stdout)
    print(f"{'4. Удалить книгу':<40}|{'8. Удалить пользователя':<40}|{'   пользователя':<40}|{'   ID пользователя ':<40}", file=sys.stdout)
    print(f"{' ':<40}|{' ':<40}|{' ':<40}|{'14. Выход':<40}", file=sys.stdout)
    print('-' * 143, file=sys.stdout)

def main():
    try:
        library = Library()

        while True:
            print_menu()
            choice = input("Введите номер действия: ")

            if choice == "1":
                try:
                    isbn = input("Введите ISBN книги: ")
                    title = input("Введите название книги: ")
                    author = input("Введите автора книги: ")
                    copies = int(input("Введите количество копий книги: "))
                    library.add_book(isbn, title, author, copies)
                    print("Книга успешно добавлена.")
                except ValueError:
                    print("Ошибка: Введите корректное значение для количества копий.")
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "2":
                try:
                    isbn = input("Введите ISBN книги: ")
                    book = library.view_book(isbn)
                    if book:
                        print(book)
                    else:
                        print("Книга не найдена.")
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "3":
                try:
                    isbn = input("Введите ISBN книги: ")
                    title = input("Введите новое название книги (оставьте пустым, чтобы не изменять): ")
                    author = input("Введите нового автора книги (оставьте пустым, чтобы не изменять): ")
                    copies = input("Введите новое количество копий книги (оставьте пустым, чтобы не изменять): ")

                    copies = int(copies) if copies else None
                    library.update_book(isbn, title or None, author or None, copies)
                except ValueError:
                    print("Ошибка: Введите корректное значение для количества копий.")
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "4":
                try:
                    isbn = input("Введите ISBN книги: ")
                    library.delete_book(isbn)
                    print("Книга успешно удалена.")
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "5":
                try:
                    user_id = input("Введите ID пользователя: ")
                    name = input("Введите имя пользователя: ")
                    library.register_user(user_id, name)
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "6":
                try:
                    user_id = input("Введите ID пользователя: ")
                    user = library.view_user(user_id)
                    if user:
                        print(f"ID: {user.user_id}, Имя: {user.name}, Штраф: {user.penalty},Репутация: {user.reputation}\nЛимит книг:{user.max_books}, Срок аренды: {user.return_days}")
                                

                    else:
                        print("Пользователь не найден.")
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "7":
                try:
                    user_id = input("Введите ID пользователя: ")
                    name = input("Введите новое имя пользователя: ")
                    library.update_user(user_id, name)
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "8":
                try:
                    user_id = input("Введите ID пользователя: ")
                    library.delete_user(user_id)
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "9":
                try:
                    user_id = input("Введите ID пользователя: ")
                    isbn = input("Введите ISBN книги: ")
                    library.borrow_book(user_id, isbn)
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "10":
                try:
                    user_id = input("Введите ID пользователя: ")
                    isbn = input("Введите ISBN книги: ")
                    library.return_book(user_id, isbn)
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "11":
                try:
                    user_id = input("Введите ID пользователя: ")
                    borrowed_books, count = library.view_borrowed_books(user_id)
                    if borrowed_books:
                        print(f"Количество взятых книг пользователем: {count}")
                        for borrowed_book in borrowed_books:
                            borrow_date = borrowed_book.borrow_date.strftime("%d-%m-%Y")
                            due_date = borrowed_book.due_date.strftime("%d-%m-%Y")
                            return_date = borrowed_book.return_date.strftime(
                                "%d-%m-%Y") if borrowed_book.return_date else "Не возвращена"
                            print(f"ID заема: {borrowed_book.id}, ISBN книги: {borrowed_book.isbn}")
                            print(f"Дата взятия: {borrow_date}, Дата возврата: {return_date}, Срок возврата: {due_date}")
                    else:
                        print("Пользователь не имеет взятых книг.")
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "12":
                try:
                    title = input("Введите название книги (оставьте пустым, чтобы не использовать): ")
                    author = input("Введите автора книги (оставьте пустым, чтобы не использовать): ")
                    isbn = input("Введите ISBN книги (оставьте пустым, чтобы не использовать): ")

                    isbn = int(isbn) if isbn else None
                    books = library.search_books(title or None, author or None, isbn)
                    if books:
                        for book in books:
                            print(book)
                    else:
                        print("Книги не найдены.")
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "13":
                try:
                    name = input("Введите имя пользователя (оставьте пустым, чтобы не использовать): ")
                    user_id = input("Введите ID пользователя (оставьте пустым, чтобы не использовать): ")

                    user_id = int(user_id) if user_id else None
                    users = library.search_users(name or None, user_id)
                    if users:
                        for user in users:
                            print(f"ID: {user.user_id}, Имя: {user.name}, Штраф: {user.penalty}")
                    else:
                        print("Пользователь не найден.")
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "14":
                library.close_connection()
                print("До свидания!")
                break

            else:
                print("Неверный выбор. Попробуйте еще раз.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
