
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.database import return_login, add_questions, found_description, get_details_active_questionnaire, save_answer, \
    get_status_questionnaire, get_detail_closed_questionnaire
from app.forms import UserLoginForm, SaveAnswer

router = APIRouter()
templates = Jinja2Templates(directory="templates/")


# Проверка соответствия логина и пароля бд
@router.post('/login')
def login(userLoginForm: UserLoginForm):
    user = return_login(userLoginForm.email, userLoginForm.password)

    if user:
        result = {
            "id": user[0],
            "full_name": user[3]
        }
        return JSONResponse(content=result)
    else:
        return JSONResponse(content={"result": "fail", "error": "Email/password invalid"})


#Добавление новых вопросов в бд
@router.post('/question/add')
def add_question(question: str):
    result = add_questions(question)
    return JSONResponse(content=result)


#Возвращение всей информации по опросу
@router.get('/get_questionnaires')
def get_questionnaires(user_id: int):
    questionnaires_list = found_description(user_id)
# Если анкет нет, возвращается not found
    if not questionnaires_list:
        return JSONResponse(content={"result": "Not found"})
# Если анкеты есть, возвращаются данные по этой анкете
    result = dict()
    result["questionnaires"] = questionnaires_list
    return JSONResponse(content=result)


# Метод, возвращающий людей, по которым нужно ответить в опросе и список вопросов
@router.get('/get_detail_questionnaire')
def get_detail_questionnaire(user_id: int, questionnaire_id: int):
    status = get_status_questionnaire(questionnaire_id)
    if not status:
        return JSONResponse(content={"result": "Not found"})
    print(status)

    if status[0][0] == 'active':
        result = get_details_active_questionnaire(user_id, questionnaire_id)
        if result is False:
            return JSONResponse(content={"result": "Not found"})
        else:
            return JSONResponse(content=result)
    else:
        result = get_detail_closed_questionnaire(user_id, questionnaire_id)
        return JSONResponse(content=result)


# Метод сохранения ответов по анкете
@router.post('/save_answers')
def save_answers(answer: SaveAnswer):
    if save_answer(answer):
        return JSONResponse(content={"result": "saved successfully"})
    else:
        return JSONResponse(content={"result": "save failed"})


# Изменение статуса анкеты
# @router.get('/change_state')
# def change_state(id_questionnaire: int):
#     return change_state_questionnaire(id_questionnaire)
