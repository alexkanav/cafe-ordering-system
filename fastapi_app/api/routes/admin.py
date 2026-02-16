from anyio import from_thread
from fastapi import APIRouter, Depends, status, HTTPException, Response, Query, UploadFile, File
from fastapi_cache import FastAPICache
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

from domain.core.constants import CacheNamespace
from domain.core.errors import NotFoundError, ConflictError, DomainValidationError, DomainError
from fastapi_app.dependencies.db import get_db
from domain import services
from fastapi_app.auth.jwt import create_access_token
from fastapi_app.dependencies.auth import has_required_role, require_active_staff
from fastapi_app.auth.cookies import set_auth_cookie, clear_auth_cookie
from domain import schemas
from utils.enums import UserRole
from utils.images import process_image_upload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/me", response_model=schemas.CurrentUserSchema)
def get_me(
        current_user: schemas.CurrentUserSchema = Depends(require_active_staff),
):
    return current_user


@router.post('/auth/register', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponseSchema)
def register_endpoint(
        auth_data: schemas.RegisterRequestSchema,
        response: Response,
        db: Session = Depends(get_db),
):
    try:
        user_id = services.register_staff(db, auth_data)
        db.commit()
        logger.info(f"registered_user user={user_id} email={auth_data.email}")
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email {auth_data.email} вже використана"
        )
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed_to_register_user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не вдалося зареєструвати користувача"
        )

    access_token = create_access_token(subject=str(user_id), role=UserRole.staff)
    set_auth_cookie(response, access_token)

    return {"user_id": user_id}


@router.post("/auth/login", response_model=schemas.UserResponseSchema)
def login_endpoint(
        auth_data: schemas.LoginRequestSchema,
        response: Response,
        db: Session = Depends(get_db),
):
    user = services.authenticate_staff(db, auth_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Відмова: Email та пароль не збігаються"
        )

    access_token = create_access_token(
        subject=str(user.id),
        role=UserRole.staff
    )

    set_auth_cookie(response, access_token)

    return {"user_id": user.id}


@router.post('/auth/logout', response_model=schemas.MessageResponseSchema)
def logout_endpoint(response: Response):
    clear_auth_cookie(response)
    return {"message": "Ви вийшли з системи"}


@router.get('/menu', response_model=schemas.StaffMenuResponseSchema)
def get_menu_endpoint(
        _: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
        db: Session = Depends(get_db),
):
    return services.build_staff_menu(db)


@router.patch('/categories', response_model=schemas.MessageResponseSchema)
def update_categories_endpoint(
        data: schemas.CategoryNamesSchema,
        _: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
        db: Session = Depends(get_db),
):
    try:
        services.update_categories(db, data.category_names)
        db.commit()
        logger.info("Categories_updated")
    except Exception:
        db.rollback()
        logger.exception("Failed_to_update_categories")
        raise

    from_thread.run(FastAPICache.clear, CacheNamespace.MENU)

    return {"message": "Категорії оновлено"}


@router.post('/dishes', response_model=schemas.MessageResponseSchema)
def create_or_update_dish_endpoint(
        data: schemas.DishUpdateSchema,
        _: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
        db: Session = Depends(get_db),
):
    try:
        services.create_or_update_dish(db, data)
        db.commit()
        logger.info("Dish_updated")
    except Exception:
        db.rollback()
        logger.exception("Failed_to_update_dish")
        raise

    from_thread.run(FastAPICache.clear, CacheNamespace.MENU)

    return {"message": f"Страву {data.code} оновлено"}


@router.get('/notifications', response_model=list[schemas.NotificationSchema])
def get_notifications_endpoint(
        only_unread: bool = Query(False),
        _: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
        db: Session = Depends(get_db)
):
    return services.get_notifications(only_unread, db)


@router.patch('/notifications/{notification_id}', response_model=schemas.MessageResponseSchema)
def mark_notification_as_read_endpoint(
        notification_id: int,
        current_user: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
        db: Session = Depends(get_db)
):
    try:
        services.mark_notification_as_read(db, notification_id, current_user.id)
        db.commit()
        logger.info(f"notification_marked_read notification_id={notification_id} user_id={current_user.id}")
    except NotFoundError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception:
        db.rollback()
        logger.exception("Unexpected_error")
        raise

    return {"message": f"Сповіщення:{notification_id} помічене як прочитане"}


@router.get("/notifications/unread/count", response_model=schemas.NotificationCountResponseSchema)
def get_unread_notification_count_endpoint(
        _: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
        db: Session = Depends(get_db),
):
    unread_notifications_count = services.count_unread_notifications(db)
    return {"unread_notif_count": unread_notifications_count}


@router.get('/statistics', response_model=schemas.StatisticsResponseSchema)
def statistics_endpoint(
        params: schemas.StatisticsQuerySchema = Depends(),
        _: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
        db: Session = Depends(get_db)
):
    if params.start_date > params.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date"
        )
    sales_summary = services.get_sales_summary(db, params.start_date, params.end_date)
    dish_order_stats = services.get_dish_order_stats(db)
    return {"sales_summary": sales_summary, "dish_order_stats": dish_order_stats}


@router.get('/coupons', response_model=list[schemas.CouponSchema])
def get_coupons_endpoint(
        _: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
        db: Session = Depends(get_db)
):
    return services.get_coupons(db)


@router.post('/coupons', status_code=status.HTTP_201_CREATED, response_model=schemas.MessageResponseSchema)
def create_coupon_endpoint(
        coupon_data: schemas.CouponCreateSchema,
        _: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
        db: Session = Depends(get_db)
):
    try:
        coupon_id = services.create_coupon(db, coupon_data)
        db.commit()
        logger.info(f"Coupon_added id={coupon_id}")

    except ConflictError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception:
        db.rollback()
        logger.exception("Unexpected_error")
        raise

    return {"message": f'Додано купон id:{coupon_id}'}


@router.patch("/coupons/{coupon_id}/deactivate", response_model=schemas.MessageResponseSchema)
def deactivate_coupon_endpoint(
        coupon_id: int,
        _: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
        db: Session = Depends(get_db),
):
    try:
        services.deactivate_coupon(db, coupon_id)
        db.commit()
        logger.info(f"Coupon_deactivated id={coupon_id}")
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
    except Exception:
        db.rollback()
        logger.exception("Unexpected_error")
        raise

    return {"message": f"Купон id:{coupon_id} деактивовано"}


@router.get('/orders', response_model=schemas.OrderResponseSchema)
def get_orders_endpoint(
        only_uncompleted: bool = Query(True),
        _: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
        db: Session = Depends(get_db),
):
    orders = services.get_orders(db, only_uncompleted)

    return {"orders": orders, "orders_count": len(orders)}


@router.get('/orders/count', response_model=schemas.OrderCountResponseSchema)
def get_orders_count_endpoint(db: Session = Depends(get_db)):
    count = services.count(db)
    return {"count": count}


@router.patch('/orders/{order_id}/complete', response_model=schemas.MessageResponseSchema)
def complete_order_endpoint(
        order_id: int,
        current_user: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
        db: Session = Depends(get_db),
):
    try:
        services.complete_order(db, order_id, current_user.id)
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
    except Exception:
        db.rollback()
        logger.exception("Unexpected_error")
        raise

    return {"message": f"Замовлення:{order_id} виконано."}


@router.post("/images", status_code=status.HTTP_201_CREATED, response_model=schemas.ImageResponseSchema)
def upload_image(
        image: UploadFile = File(...),
        current_user: schemas.CurrentUserSchema = Depends(has_required_role(UserRole.staff)),
):
    try:
        filename = process_image_upload(image, current_user.id)
    except (ConflictError, DomainValidationError, DomainError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return {"filename": filename}
