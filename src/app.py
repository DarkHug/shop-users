from http import HTTPStatus

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

import src.routes as routes
from src.providers import AppProvider, DatabaseProvider, PasswordProvider, ServiceProvider, RepoProvider
from src.settings import Settings


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI()

    for router in routes.routers:
        app.include_router(router)

    container = make_async_container(
        AppProvider(settings),
        DatabaseProvider(),
        PasswordProvider(),
        RepoProvider(),
        ServiceProvider(),
    )
    setup_dishka(container=container, app=app)

    @app.get("/health-check", status_code=HTTPStatus.NO_CONTENT)
    def health_check():
        pass

    return app
