#tests/test_main.py
from src.main import *

def test_print_menu(capsys):
    print_menu()
    captured = capsys.readouterr()
    assert "Управление книгами" in captured.out
    assert "Управление пользователями" in captured.out
    assert "Получение и возврат книг" in captured.out
    assert "Функционал поиска" in captured.out
    assert "-" in captured.out

def test_main(monkeypatch, capsys):
    # Мокаем пользовательский ввод
    user_input = iter(["1", "1234567890", "Test Book", "Test Author", "5", "0", "1", "2", "1234567890", "4", "1234567890", "14"])
    monkeypatch.setattr('builtins.input', lambda prompt: next(user_input))

    # Тестирование основного сценария
    main()

    # Проверка сообщений вывода
    captured = capsys.readouterr()
    assert "Книга успешно добавлена." in captured.out
    assert "Test Book" in captured.out
    assert "Книга не найдена." in captured.out
    assert "Книга успешно удалена." in captured.out
    assert "До свидания!" in captured.out