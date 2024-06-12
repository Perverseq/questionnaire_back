import psycopg2

from app.forms import SaveAnswer


# Коннект к бд
def connect_to_database():
    connect = psycopg2.connect(
        host="localhost",
        port="5432",
        database="questionnaire",
        user="postgres",
        password="new_password")
    return connect


# Проверка на логин пароль в бд
def return_login(email: str, password: str):
    connect = connect_to_database()

    cursor = connect.cursor()

    cursor.execute('SELECT * FROM users where email = %s and password = %s', (email, password))

    user = cursor.fetchall()

    connect.close()
    cursor.close()

    if user:
        return user[0]
    else:
        return False


# Добавление вопросов в таблицу
def add_questions(question: str):
    connect = connect_to_database()
    connect.autocommit = True

    cursor = connect.cursor()

    cursor.execute(f'insert into questions (question) values ("{question}")')

    connect.close()
    cursor.close()

    return {"result": "OK"}


# Поиск id опросов по id  юзера
def found_id_questionnaires(user_id: int):
    connect = connect_to_database()

    cursor = connect.cursor()

    cursor.execute(f'SELECT id_questionnaire FROM questionnaires_for_respondent where id_user = {user_id}')

    questionnaires_id = cursor.fetchall()
    connect.close()
    cursor.close()

    return questionnaires_id


# Поиск данных по опросам
def found_description(user_id: int):
    questionnaires_id = found_id_questionnaires(user_id)

    # Если анкет нет, возвращается questionnaires_id со значением []
    if not questionnaires_id:
        return questionnaires_id

    descriptions = []

    connect = connect_to_database()
    cursor = connect.cursor()

    # Парсим данные анкет и записываем в массив descriptions
    for item in questionnaires_id:
        cursor.execute(f'SELECT id, title, body, date_create, end_date FROM questionnaire where id = {item[0]} and is_active = true')
        questionnaires_description = cursor.fetchall()

        # Если в анкете есть данные, они добавляются в массив descriptions
        if len(questionnaires_description):
            descriptions.append(questionnaires_description[0])

    connect.close()
    cursor.close()

    # Окончательный косметический шаг, приводящий данные к формату json
    questionnaires = []
    for item in descriptions:
        json_list = {
            "id": item[0],
            "title": item[1],
            "body": item[2],
            "date_create": str(item[3]),
            "end_date": str(item[4])
        }
        questionnaires.append(json_list)

    return questionnaires


# Получение id связи между анкетой и респондентом
def qet_id_questionnaire_for_user(user_id: int, questionnaire_id: int):
    connect = connect_to_database()
    cursor = connect.cursor()

    cursor.execute(f'select id from questionnaires_for_respondent where id_user = {user_id} and id_questionnaire = {questionnaire_id}')

    result = cursor.fetchall()
    connect.close()
    cursor.close()
    if len(result):
        return result[0]
    else:
        return False


# Получение людей, по которым нужно ответить в анкете
def get_people(id_questionnaires_for_respondent: int):
    connect = connect_to_database()
    cursor = connect.cursor()

    cursor.execute(
        f'select id_user from users_in_questionnaire where id_questionnaires_for_respondent = {id_questionnaires_for_respondent[0]}\
         and is_active = true')
    users_id = cursor.fetchall()

    if len(users_id):
        users = []

        for item in users_id:
            cursor.execute(f'select id, full_name from users where id = {item[0]}')
            results = cursor.fetchone()
            users.append(results)
        array_users = []
        for item in users:
            json_list = {
                "id": item[0],
                "user_name": item[1]
            }
            array_users.append(json_list)
        connect.close()
        cursor.close()

        return array_users
    else:
        return False


# Получение вопросов по анкете
def get_questions(questionnaire_id: int):
    connect = connect_to_database()
    cursor = connect.cursor()

    cursor.execute(
        f'select id_question from questions_in_questionnaire where id_questionnaire = {questionnaire_id}')

    questions_id = cursor.fetchall()
    questions = []
    for item in questions_id:
        cursor.execute(f'select id, question from questions where id = {item[0]}')
        question = cursor.fetchall()
        if len(question):
            questions.append(question[0])
    result = []
    for item in questions:
        json_list = {
            "id": item[0],
            "question": item[1]
        }
        result.append(json_list)
    connect.close()
    cursor.close()
    return result

# Поиск информации по активной анкете: людей и вопросов
def get_details_active_questionnaire(user_id: int, questionnaire_id: int):
    # С помощью двух методов осуществляется получение данных о пользователях, по которым нужно ответить в анкете
    id_questionnaires_for_respondent = qet_id_questionnaire_for_user(user_id, questionnaire_id)

    if id_questionnaires_for_respondent is False:
        return id_questionnaires_for_respondent

    users = get_people(id_questionnaires_for_respondent)

    if users is False:
        return users
    # Получение вопросов по анкете
    questions = get_questions(questionnaire_id)

    result = dict()
    result["users"] = users
    result["questions"] = questions

    return result


# Сохранение ответов по анкете
# TODO: поправить сохранение ответов здесь и в бд
def save_answer(answer: SaveAnswer):
    connect = connect_to_database()
    connect.autocommit = True
    cursor = connect.cursor()

    for item in answer.answer:
        cursor.execute(
            'insert into answers (id_respondent, id_user, id_questionnaire, id_question, comment, point) values (%s, %s, %s, %s, %s, %s) returning id',
            (answer.respondent_id, answer.user_id, answer.questionnaire_id, item["id_question"], item["comment"], item["point"]))

    connect.close()
    cursor.close()

    return True


# Изменение статуса анкеты
def change_state_questionnaire(questionnaire_id: int):
    connect = connect_to_database()
    cursor = connect.cursor()
    connect.autocommit = True

    cursor.execute(f'select status from questionnaire where id = {questionnaire_id}')

    if cursor.fetchone()[0] == 'active':
        cursor.execute('update questionnaire set status = %s where id = %s', ("closed", questionnaire_id))

        cursor.execute(
            f'select DISTINCT ON (id_respondent) id_respondent from answers where id_questionnaire = {questionnaire_id}')

        id_respondents = cursor.fetchall()

        for item in id_respondents:
            average_calculation(item[0], questionnaire_id)

        connect.close()
        cursor.close()

        return {"result": "successful"}
    else:
        connect.close()
        cursor.close()

        return {"result": "questionnaire is already closed"}


# Вычисление средней оценки по опросу
def average_calculation(respondent_id: int, questionnaire_id: int):
    connect = connect_to_database()
    cursor = connect.cursor()
    connect.autocommit = True

    cursor.execute(
        f'select id_respondent, id_user, id_question, comment, point from answers where id_respondent = {respondent_id}'
        f' and id_questionnaire = {questionnaire_id} and id_user != {respondent_id} order by id_question')

    answers = cursor.fetchall()
    print(answers)

    id_question = 0

    average_point = 0
    count = 0
    all_comment = []

    for item in answers:
        if id_question != item[2]:
            if id_question != 0:
                average_point = average_point/count
                cursor.execute(f'insert into final_comment (id_respondent, id_questionnaire, id_question, all_comment, average_point)'
                               f' values (%s, %s, %s, %s, %s)', (respondent_id, questionnaire_id, id_question, all_comment, average_point))
            average_point = 0
            count = 0
            all_comment = []

            id_question = item[2]
            average_point += item[4]
            count += 1
            all_comment.append(item[3])
        else:
            average_point += item[4]
            count += 1
            all_comment.append(item[3])

    average_point = average_point/count
    cursor.execute(
        f'insert into final_comment (id_respondent, id_questionnaire, id_question, all_comment, average_point)'
        f' values (%s, %s, %s, %s, %s)', (respondent_id, questionnaire_id, id_question, all_comment, average_point))

    connect.close()
    cursor.close()
    return {"result": "successful"}


# Получение деталей закрытой анкеты
def get_detail_closed_questionnaire(user_id: int, questionnaire_id: int):
    connect = connect_to_database()
    cursor = connect.cursor()

    cursor.execute(
        f'select id_question, comment, point from answers where id_respondent = {user_id} and id_user = {user_id} and id_questionnaire = {questionnaire_id}')

    myself = cursor.fetchall()

    about_myself = []

    for item in myself:
        json_list = {
            "question_id": item[0],
            "comment": item[1],
            "point": item[2]
        }
        about_myself.append(json_list)

    cursor.execute(
        f'select id_question, all_comment, average_point from final_comment where id_respondent = {user_id} and id_questionnaire = {questionnaire_id}')

    comments = cursor.fetchall()

    final_comments = []

    for item in comments:
        json_list = {
            "question_id": item[0],
            "all_comments": item[1],
            "average_point": item[2]
        }
        final_comments.append(json_list)

    result = dict()

    result["myself"] = about_myself
    result["other"] = final_comments

    connect.close()
    cursor.close()
    return result


# Получение статуса анкеты
def get_status_questionnaire(questionnaire_id: int):
    connect = connect_to_database()
    cursor = connect.cursor()

    cursor.execute(f'select status from questionnaire where id = {questionnaire_id}')

    status = cursor.fetchall()
    connect.close()
    cursor.close()
    return status
