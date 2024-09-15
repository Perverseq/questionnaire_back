import psycopg2


# Коннект к бд
def decorator_db(func):
    def db_cursor(*args, **kwargs):
        connect = psycopg2.connect(
            host="localhost",
            port="5432",
            database="questionnaire",
            user="postgres",
            password="new_password")
        connect.autocommit = True
        cursor = connect.cursor()

        result = func(*args, sql_cursor=cursor,  **kwargs)

        cursor.close()
        connect.close()
        return result
    return db_cursor


# Проверка на логин пароль в бд
@decorator_db
def user_with_login(email: str, password: str, **kwargs):
    sql_cursor = kwargs.get('sql_cursor')
    sql_cursor.execute('SELECT id, full_name FROM users where email = %s and password = %s', (email, password))
    user = sql_cursor.fetchone()
    if user:
        return user
    else:
        return None
