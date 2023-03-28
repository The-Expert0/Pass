import sqlite3
import hashlib

from prettytable import PrettyTable
# pip install PrettyTable   -для установки пакета


def sql_commit(query):
    """Функция для записи в БД"""
    try:
        sqlite_connection = sqlite3.connect('sqlite_python.db')
        cursor = sqlite_connection.cursor()
        cursor.execute(query)
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            # print("Соединение с SQLite закрыто")


def sql_fetchall(query):
    """Функция для извлечения из БД"""
    try:
        sqlite_connection = sqlite3.connect('sqlite_python.db')
        cursor = sqlite_connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        if records:
            table = PrettyTable(['id', 'website', 'login', 'password'])
            for row in records:
                table.add_row([row[0], row[1], row[2], row[3]])
            print(table)
            return True
        else:
            print("Пароль с данным id не найден.")
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            # print("Соединение с SQLite закрыто")


def select_all():
    """Вывод вех строк из БД"""
    query = "SELECT * FROM list_passwords;"
    sql_fetchall(query)


def select_id():
    """Вывод строки по id"""
    pass_id = input("Введите id пароля: ")
    query = f"SELECT * FROM list_passwords WHERE id = {pass_id};"
    if sql_fetchall(query):
        return pass_id
    else:
        return False


def select_website():
    """Вывод строки по website"""
    website = input("Введите название сайта: ")
    query = f"SELECT * FROM list_passwords WHERE website LIKE '%{website}%';"
    sql_fetchall(query)


def insert():
    """Функция для добавления пароля"""
    website = input("Введите адрес сайта: ")
    if website:
        login = input("Введите логин: ")
        password = input("Введите пароль: ")
        query = "INSERT INTO list_passwords (website, login, password) " + \
                f"VALUES  ('{website}', '{login}', '{password}');"
        sql_commit(query)
        print("Пароль добавлен.")
    else:
        insert()


def update():
    """Функция для изменения пароля"""
    pass_id = select_id()
    if pass_id:
        field = input("Выберете поле для изменения "
                      "(1 - website, 2 - login, 3 - password): ")
        match field:
            case "1":
                field = "website"
            case "2":
                field = "login"
            case "3":
                field = "password"
            case _:
                print("Поле не найдено.")
                update()
                return 0
        value = input(f"Введите новое значение для поля {field}: ")
        query = "UPDATE list_passwords SET " + \
                f"'{field}' = '{value}' WHERE id = '{pass_id}';"
        sql_commit(query)
        print("Пароль изменен.")
    else:
        update()


def delete():
    """Функция для удаления пароля"""
    pass_id = select_id()
    if pass_id:
        cmd = input("Вы действительно хотите удалить данный пароль?(У/N) ")
        if cmd.upper() == "Y" or cmd.upper() == "YES":
            query = f"DELETE FROM list_passwords WHERE id = '{pass_id}'"
            sql_commit(query)
            print("Пароль удален.")
        else:
            print("Отмена удаления.")
    else:
        delete()


def create_db():
    """Функция для создания БД"""
    """Используется один раз при создании БД и таблицы"""
    try:
        sqlite_connection = sqlite3.connect('sqlite_python.db')
        sqlite_create_table_query = '''CREATE TABLE list_passwords (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    website TEXT NOT NULL,
                                    login TEXT NOT NULL,
                                    password TEXT NOT NULL);'''
        cursor = sqlite_connection.cursor()
        cursor.execute(sqlite_create_table_query)
        sqlite_connection.commit()
        print("Таблица SQLite создана")
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            # print("Соединение с SQLite закрыто")


def drop_table():
    """Функция для сброса таблицы."""
    print("Таблица очищена.")
    query = "DROP TABLE list_passwords;"
    sql_commit(query)


# create_db() # Создание БД и таблицы
def main():
    """Основная функция"""
    while True:
        cmd = input(f"\n{'-' * 40}\n"
                    f"Выберете пункт меню введя цифру:\n"
                    f"1) Вывести все пароли;\n"
                    f"2) Вывести пароль по id;\n"
                    f"3) Поиск пароля по названию сайта;\n"
                    f"4) Добавить пароль;\n"
                    f"5) Изменить пароль;\n"
                    f"6) Удалить пароль;\n"
                    f"7) Закрыть программу.\n")
        match cmd:
            case "1":
                select_all()
            case "2":
                select_id()
            case "3":
                select_website()
            case "4":
                insert()
            case "5":
                update()
            case "6":
                delete()
            case "7":
                print("Завершение работы.")
                break
            case _:
                print("Неверная команда.")


def verify():
    """Функция ввода пароля при запуске программы"""
    file_name = "pass.txt"
    try:
        file_ = open(file_name, 'r')
        password = file_.read()    # Пароль - pass
        file_.close()
        pass_ = input(
            "Введите пароль для доступа к программе: ").encode('utf-8')
        if hashlib.sha224(pass_).hexdigest() == password:
            print("Верный пароль.")
            main()
        else:
            cmd = input("Неверный пароль. (1 - Попробовать еще раз, "
                        "2 - Сбросить пароль и очистить БД) ")
            match cmd:
                case "1":
                    print("*Пароль указан в функции verify*")
                    verify()
                case "2":
                    new_pass = input("Введите новый пароль: ").encode('utf-8')
                    file_ = open(file_name, 'w')
                    file_.seek(0)
                    file_.write(hashlib.sha224(new_pass).hexdigest())
                    file_.close()
                    drop_table()
                    create_db()
                    verify()
    except FileNotFoundError:
        print("Файл с паролем не был найден и был создан.")
        file_ = open(file_name, 'w')
        file_.close()


verify()
