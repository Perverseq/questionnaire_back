from pydantic import BaseModel


# логин
class UserLoginForm(BaseModel):
    email: str
    password: str


class SaveAnswer(BaseModel):
    respondent_id: int
    user_id: int
    questionnaire_id: int
    answer: list
