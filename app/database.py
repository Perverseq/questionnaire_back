import psycopg2


# Коннект к бд
def db_cursor():
    connect = psycopg2.connect(
        host="localhost",
        port="5432",
        database="questionnaire",
        user="postgres",
        password="new_password")
    connect.autocommit = True
    return connect


# Проверка на логин пароль в бд
def user_with_login(email: str, password: str):
    connect = db_cursor()
    cursor = connect.cursor()
    cursor.execute('SELECT id, full_name FROM users where email = %s and password = %s', (email, password))
    user = cursor.fetchall()
    cursor.close()
    connect.close()

    if user:
        return user
    else:
        return False
