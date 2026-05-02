from fastapi import FastAPI

from recipeLabs.api.cooks import router as cooks_router
from recipeLabs.api.health import router
from recipeLabs.api.recipes import router as recipes_router

app = FastAPI()
app.include_router(router)
app.include_router(recipes_router)
app.include_router(cooks_router)
