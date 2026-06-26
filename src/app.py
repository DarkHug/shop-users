from fastapi import FastAPI
import src.routes as routes

app = FastAPI()

for router in routes.routers:
    app.include_router(router)


@app.get("/ping")
def ping():
    return {"message": "pong"}
