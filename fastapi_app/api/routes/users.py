import logging
from fastapi import APIRouter, Depends, status, Request, HTTPException, Response
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from domain.core.errors import NotFoundError, ConflictError, DomainValidationError
from domain.core.constants import RedisPrefix, CacheNamespace, CacheKey
from fastapi_app.core.limiter import limiter
from fastapi_app.dependencies.db import get_db
from domain import services
from fastapi_app.dependencies.auth import get_current_user
from fastapi_app.auth.jwt import create_access_token
from fastapi_app.auth.cookies import set_auth_cookie
from domain import schemas
from utils.helpers import static_key
from utils.discounts import calculate_discount
from utils.enums import UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.CurrentUserSchema)
def get_me(
        current_user: schemas.CurrentUserSchema = Depends(get_current_user),
):
    return current_user


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponseSchema,
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": schemas.RateLimitErrorSchema},
    },
)
@limiter.limit("10/hour")
def create_user_endpoint(
        response: Response,
        request: Request,
        db: Session = Depends(get_db),
):
    try:
        user_id = services.create_user(db)

        access_token = create_access_token(
            subject=str(user_id),
            role=UserRole.client,
        )
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed_to_create_user")
        raise

    set_auth_cookie(response, access_token)
    return {"user_id": user_id}


@router.get("/comments", response_model=schemas.CommentResponseSchema)
@cache(
    expire=3600,
    key_builder=static_key(f"{RedisPrefix.CACHE}:{CacheNamespace.COMMENTS}:{CacheKey.LIST}")
)
def get_comments_endpoint(db: Session = Depends(get_db)):
    comments = services.get_comments(db, limit=10)
    return {"comments": comments}


@router.post(
    '/comments',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MessageResponseSchema,
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": schemas.RateLimitErrorSchema}
    },
)
@limiter.limit("2/hour")
def add_comment_endpoint(
        request: Request,
        comment_data: schemas.CommentCreateSchema,
        current_user: schemas.CurrentUserSchema = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        services.add_comment(db, current_user.id, comment_data)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed_to_create_comment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не вдалося додати коментар"
        )

    return {"message": "Ваш коментар надіслано на модерацію"}


@router.get("/menu", response_model=schemas.UserMenuResponseSchema)
@cache(
    expire=3600,
    key_builder=static_key(f"{RedisPrefix.CACHE}:{CacheNamespace.MENU}:{CacheKey.DETAIL}")
)
def get_user_menu(db: Session = Depends(get_db)):
    return services.build_user_menu(db)


@router.get("/discount", response_model=schemas.DiscountSchema)
def get_discount_endpoint(
        current_user: schemas.CurrentUserSchema = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user_total_amount = services.total_amount(db, current_user.id)
    discount = calculate_discount(user_total_amount)
    return {"discount": discount}


@router.post("/order", response_model=schemas.OrderOperationResultSchema, status_code=status.HTTP_201_CREATED)
def place_order_endpoint(
        order_data: schemas.OrderCreateSchema,
        current_user: schemas.CurrentUserSchema = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        order = services.create_order(db, order_data, current_user.id)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed_to_create_order")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не вдалося створити замовлення"
        )

    return order


@router.post("/dishes/{dish_code}/like", response_model=schemas.MessageResponseSchema)
def like_dish_endpoint(
        dish_code: str,
        db: Session = Depends(get_db),
        current_user: schemas.CurrentUserSchema = Depends(get_current_user)
):
    try:
        services.add_dish_like(db, current_user.id, dish_code)
        db.commit()
        logger.info(f"User_liked_dish user={current_user.id} dish={dish_code}")
    except NotFoundError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except IntegrityError:
        # duplicate like or constraint violation
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ви вже оцінювали цей продукт",
        )

    return {"message": "Вподобання додано"}


@router.post("/coupon/{coupon_code}", response_model=schemas.DiscountSchema)
def check_coupon_endpoint(
        coupon_code: str,
        db: Session = Depends(get_db),
        current_user: schemas.CurrentUserSchema = Depends(get_current_user)
):
    try:
        discount = services.check_coupon(db, coupon_code, current_user.id)
        db.commit()
    except NotFoundError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ConflictError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except DomainValidationError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return {"discount": discount}
