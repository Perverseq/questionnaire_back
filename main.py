from fastapi import FastAPI, APIRouter
from app.handlers import router
from fastapi.middleware.cors import CORSMiddleware


def get_application() -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    return application


app = get_application()

app.add_middleware(
    CORSMiddleware,
    allow_origins='http://127.0.0.1:5500',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
