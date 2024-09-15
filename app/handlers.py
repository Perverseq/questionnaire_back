from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.database import user_with_login
from app.models import User

router = APIRouter()


# Проверка соответствия логина и пароля бд
@router.post('/user/login')
def login(u: User) -> JSONResponse:
    """
    Метод для авторизации пользователя.

    :param u: email и password с помощью модели.
    :return: ID пользователя и ФИО.
    """
    user = user_with_login(u.email, u.password)

    if user is not None:
        result = {
            "id": user[0],
            "full_name": user[1]
        }
        return JSONResponse(content=result)
    else:
        return JSONResponse(content={"result": "fail", "error": "Email/password invalid"})


@router.get('/list/questionnaires')
def get_questionnaires(user_id: int, type: bool = None, max: int = 20) -> JSONResponse:
    """
    Метод для получения списка анкет с процентом завершенности

    :param user_id: ID пользователя, для которого запрашивается список анкет.
    :param type: Тип анкеты. С полученным ответом или нет.
    :param max: Максимальное количество получаемых в ответе анкет.
    :return: JSON с анкетами.
    """
    if type is None:
        # Вернуть все анкеты
        pass
        return JSONResponse
    elif type is True:
        # Вернуть анкеты, по которым получен ответ
        pass
        return JSONResponse
    elif type is False:
        # Вернуть анкеты, по которым не получен ответ
        pass
        return JSONResponse
    else:
        # Вернуть ошибку
        pass
        return JSONResponse


@router.get('/questionnaire/details')
def get_questionnaire_details(questionnaire_id: int, user_id: int) -> JSONResponse:
    """
    Метод для получения анкеты для ответа. Список респондентов и вопросы.

    :param questionnaire_id: ID анкеты.
    :param user_id: ID пользователя.
    :return: JSON со списком респондентом и списком вопросов.
    """
    # Вернуть список респондентов и список вопросов
    pass
    return JSONResponse


@router.get('/questionnaire/results')
def get_questionnaire_results(questionnaire_id: int, user_id: int) -> JSONResponse:
    """
    Метод для получения результатов по анкете.

    :param questionnaire_id: ID анкеты.
    :param user_id: ID ползователя.
    :return: JSON со списком вопросов, своими оценками на вопросы,
    усредненными оценками других отвечающих, комментариями.
    """
    # Вернуть JSON
    pass
    return JSONResponse


@router.post('questionnaire/save_answer')
def post_questionnaire_save_answer(questionnaire_id: int, user_id: int, respondent_id: int, answers: dict) -> str:
    """
    Метод для сохранения ответа по анкете.

    :param questionnaire_id: ID анкеты.
    :param user_id: ID авторизованного пользователя.
    :param respondent_id: ID респондента.
    :param answers: Словарь с ответами и комментариями. {ID вопроса: [Оценка, Комментарий], ..}
    :return: Статус успешно или нет.
    """
    pass
    return ''
