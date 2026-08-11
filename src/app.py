from http import HTTPStatus

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

import src.routes as routes
from src.providers.password import PasswordProvider
from src.providers.uow import UoWProvider
from src.providers.user import UserProvider
from src.providers.database import DatabaseProvider


def create_app() -> FastAPI:
    app = FastAPI()

    for router in routes.routers:
        app.include_router(router)

    container = make_async_container(
        DatabaseProvider(),
        PasswordProvider(),
        UserProvider(),
        UoWProvider()
    )
    setup_dishka(container=container, app=app)

    @app.get("/health-check", status_code=HTTPStatus.NO_CONTENT)
    def health_check():
        pass

    return app
