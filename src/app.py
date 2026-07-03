from http import HTTPStatus

from fastapi import FastAPI
import src.routes as routes


def create_app() -> FastAPI:
    app = FastAPI()

    for router in routes.routers:
        app.include_router(router)

    @app.get("/health-check", status_code=HTTPStatus.NO_CONTENT)
    def health_check():
        pass

    return app
