from fastapi import FastAPI
from database.connection import Base, engine
import models

from routers.auth import router as auth_router
from routers.categories import router as categories_router
from routers.services import router as services_router
from routers.reviews import router as reviews_router
from routers.roles import router as roles_router
from routers.permissions import router as permissions_router
from routers.role_permissions import router as role_permissions_router
from routers.users import router as users_router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Service Review API")

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(services_router)
app.include_router(reviews_router)
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(role_permissions_router)
app.include_router(users_router)
@app.get("/")
def root():
    return {"message": "Service API radi"}

