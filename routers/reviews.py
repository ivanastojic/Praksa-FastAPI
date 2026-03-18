from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from models.review import Review
from models.service import Service
from models.user import User
from schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from routers.auth import get_current_user, require_permission

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("create_review"))
):
    service = db.query(Service).filter(Service.id == review_data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if service.provider_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot review your own service")

    existing_review = db.query(Review).filter(
        Review.service_id == review_data.service_id,
        Review.user_id == current_user.id
    ).first()

    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this service")

    review = Review(
        service_id=review_data.service_id,
        user_id=current_user.id,
        rating=review_data.rating,
        comment=review_data.comment
    )

    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    updated_review: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("update_review"))
):
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != current_user.id and current_user.role_name != "admin":
        raise HTTPException(status_code=403, detail="You can only update your own review unless you are admin")

    review.rating = updated_review.rating
    review.comment = updated_review.comment

    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("delete_review"))
):
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != current_user.id and current_user.role_name != "admin":
        raise HTTPException(status_code=403, detail="You can only delete your own review unless you are admin")

    db.delete(review)
    db.commit()

    return {"message": "Review deleted successfully"}

@router.get("/service/{service_id}", response_model=list[ReviewResponse])
def get_reviews_by_service(service_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.service_id == service_id).all()