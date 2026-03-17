from fastapi import FastAPI
from database.connection import Base, engine
import models

from routers.auth import router as auth_router
from routers.categories import router as categories_router
from routers.services import router as services_router
from routers.reviews import router as reviews_router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Service Review API")

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(services_router)
app.include_router(reviews_router)

@app.get("/")
def root():
    return {"message": "Service API radi"}

