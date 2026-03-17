from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from models.service import Service
from models.category import Category
from models.user import User
from schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from routers.auth import get_current_user

router = APIRouter(prefix="/services", tags=["Services"])


@router.post("/", response_model=ServiceResponse)
def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(Category.id == service_data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    service = Service(
        title=service_data.title,
        description=service_data.description,
        price=service_data.price,
        category_id=service_data.category_id,
        provider_id=current_user.id
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("/", response_model=list[ServiceResponse])
def get_services(db: Session = Depends(get_db)):
    return db.query(Service).all()


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    updated_service: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if service.provider_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own service")

    category = db.query(Category).filter(Category.id == updated_service.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    service.title = updated_service.title
    service.description = updated_service.description
    service.price = updated_service.price
    service.category_id = updated_service.category_id

    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if service.provider_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own service")

    db.delete(service)
    db.commit()

    return {"message": "Service deleted successfully"}

@router.get("/category/{category_id}", response_model=list[ServiceResponse])
def get_services_by_category(category_id: int, db: Session = Depends(get_db)):
    return db.query(Service).filter(Service.category_id == category_id).all()


@router.get("/my/list", response_model=list[ServiceResponse])
def get_my_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Service).filter(Service.provider_id == current_user.id).all()