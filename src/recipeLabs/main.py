from fastapi import FastAPI
from recipeLabs.api.health import router

app = FastAPI()
app.include_router(router)
