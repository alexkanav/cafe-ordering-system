from datetime import datetime
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
import logging

from flask_app.extensions import cache
from flask_app.security import role_required, require_active_staff
from utils.images import process_image_upload
from domain.core.constants import CacheNamespace
from domain.core.errors import NotFoundError, ConflictError, DomainError, DomainValidationError
from domain import services
from domain import schemas
from utils.enums import UserRole

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = require_active_staff(g.db)
    return jsonify(id=user_id, role=UserRole.staff.value), 200


@admin_bp.route("/auth/register", methods=["POST"])
def register_endpoint():
    data = request.get_json(silent=True)
    if not data:
        return jsonify(detail="Invalid JSON"), 400

    name = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify(detail="Заповніть всі поля."), 400

    try:
        auth_data = schemas.RegisterRequestSchema.model_validate({
            "username": name,
            "email": email,
            "password": password,
        })

        user_id = services.register_staff(g.db, auth_data)
        logger.info(f"registered_user user={user_id} email={email}")

    except IntegrityError:
        g.db.rollback_needed = True
        return jsonify(detail=f"Email {email} вже використана"), 409

    except SQLAlchemyError:
        g.db.rollback_needed = True
        logger.exception(f"Failed_to_register_user")
        return jsonify(detail="Не вдалося зареєструвати користувача"), 500

    except ValidationError as e:
        return jsonify(detail=str(e)), 422

    access_token = create_access_token(
        identity=str(user_id),
        additional_claims={"role": UserRole.staff.value}
    )
    response = jsonify(user_id=user_id)
    set_access_cookies(response, access_token)
    return response, 201


@admin_bp.route('/auth/login', methods=['POST'])
def login_endpoint():
    data = request.get_json(silent=True)
    if not data:
        return jsonify(detail="Invalid JSON"), 400

    email = data.get('email')
    password = data.get('password')

    try:
        auth_data = schemas.LoginRequestSchema.model_validate({
            "email": email,
            "password": password,
        })
    except ValidationError as e:
        return jsonify(detail=str(e)), 422

    user = services.authenticate_staff(g.db, auth_data)
    if not user:
        return jsonify(detail="Відмова: Email та пароль не збігаються"), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": UserRole.staff.value}
    )
    response = jsonify(user_id=user.id)
    set_access_cookies(response, access_token)
    return response, 200


@admin_bp.route('/auth/logout', methods=['POST'])
def logout_endpoint():
    response = jsonify(message='Ви вийшли з системи')
    unset_jwt_cookies(response)
    return response, 200


@admin_bp.route('/orders', methods=['GET'])
@role_required(UserRole.staff)
def get_orders_endpoint():
    only_uncompleted = request.args.get(
        'only_uncompleted',
        default='true'
    ).lower() == 'true'

    orders = services.get_orders(g.db, only_uncompleted)
    orders_data = [o.model_dump() for o in orders]

    return jsonify(orders=orders_data, orders_count=len(orders)), 200


@admin_bp.route('/orders/count', methods=['GET'])
def get_orders_count_endpoint():
    count = services.count(g.db)
    return jsonify(count=count), 200


@admin_bp.route('/orders/<int:order_id>/complete', methods=['PATCH'])
@role_required(UserRole.staff)
def complete_order_endpoint(order_id, user_id):
    try:
        services.complete_order(g.db, order_id, user_id)
    except NotFoundError as e:
        g.db.rollback_needed = True
        return jsonify(detail=str(e)), 404
    except ConflictError as e:
        g.db.rollback_needed = True
        return jsonify(detail=str(e)), 409

    return jsonify(message=f"Замовлення:{order_id} виконано."), 200


@admin_bp.route("/statistics", methods=["GET"])
@role_required(UserRole.staff)
def statistics_endpoint():
    start_raw = request.args.get("startDate")
    end_raw = request.args.get("endDate")

    if not start_raw or not end_raw:
        return jsonify(detail="startDate and endDate are required"), 400

    try:
        start_date = datetime.strptime(start_raw, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_raw, "%Y-%m-%d").date()

        if start_date > end_date:
            return jsonify(detail="startDate must be before endDate"), 400

        sales_summary = services.get_sales_summary(g.db, start_date, end_date)

        dish_order_stats = services.get_dish_order_stats(g.db)

    except ValueError:
        return jsonify(detail="Invalid date format. Use YYYY-MM-DD"), 400

    return {
        "sales_summary": sales_summary.model_dump(),
        "dish_order_stats": dish_order_stats.model_dump(),
    }, 200


@admin_bp.route('/menu', methods=['GET'])
@role_required(UserRole.staff)
def get_menu_endpoint():
    menu = services.build_staff_menu(g.db)
    return jsonify(menu.model_dump()), 200


@admin_bp.route('/images', methods=['POST'])
@role_required(UserRole.staff)
def upload_image_endpoint(user_id: int):
    if 'image' not in request.files:
        return jsonify(detail='No image uploaded'), 400

    file = request.files['image']
    try:
        filename = process_image_upload(file, user_id)
    except (ConflictError, DomainValidationError, DomainError) as e:
        return jsonify(detail=str(e)), 400
    except NotFoundError as e:
        return jsonify(detail=str(e)), 404

    return jsonify(filename=filename), 201


@admin_bp.route('/categories', methods=['PATCH'])
@role_required(UserRole.staff)
def update_categories_endpoint():
    data = request.get_json(silent=True)
    if not data:
        return jsonify(detail="Invalid JSON"), 400
    print(14, data.get("category_names"), 15, data)
    if not isinstance(data.get("category_names"), list) or \
            not all(isinstance(c, str) for c in data["category_names"]):
        return jsonify(detail="Невірний формат категорій"), 400

    services.update_categories(g.db, data["category_names"])
    logger.info("Categories_updated")

    cache.delete(CacheNamespace.MENU)
    return jsonify(message="Категорії оновлено"), 200


@admin_bp.route('/dishes', methods=['POST'])
@role_required(UserRole.staff)
def create_or_update_dish_endpoint():
    data = request.get_json(silent=True)
    if not data:
        return jsonify(detail="Invalid JSON"), 400

    try:
        dish = schemas.DishUpdateSchema.model_validate(data)
        services.create_or_update_dish(g.db, dish)
        logger.info(f"Dish_saved code={dish.code}")

    except ValidationError as e:
        return jsonify(detail=str(e)), 422

    cache.delete(CacheNamespace.MENU)
    return jsonify(message=f"Страву з кодом {dish.code} збережено"), 200


@admin_bp.route('/notifications', methods=['GET'])
@role_required(UserRole.staff)
def get_notifications_endpoint():
    only_unread = request.args.get(
        'only_unread',
        default='true'
    ).lower() == 'true'

    notifications = services.get_notifications(only_unread, g.db)
    return jsonify([n.model_dump() for n in notifications]), 200


@admin_bp.route('/notifications/unread/count', methods=['GET'])
@role_required(UserRole.staff)
def get_unread_notification_count_endpoint():
    unread_notifications_count = services.count_unread_notifications(g.db)
    return jsonify(unread_notif_count=unread_notifications_count), 200


@admin_bp.route('/notifications/<int:notification_id>', methods=["PATCH"])
@role_required(UserRole.staff)
def mark_notification_read_endpoint(notification_id: int, user_id: int):
    try:
        services.mark_notification_as_read(g.db, notification_id, user_id)
    except NotFoundError as e:
        g.db.rollback_needed = True
        return jsonify(detail=str(e)), 404

    logger.info(f"notification_marked_read notification_id={notification_id} user_id={user_id}")
    return jsonify(
        message=f"Сповіщення:{notification_id} помічене як прочитане"
    ), 200


@admin_bp.route('/coupons', methods=['GET'])
@role_required(UserRole.staff)
def get_coupons_endpoint():
    coupons = services.get_coupons(g.db)
    return jsonify([c.model_dump() for c in coupons]), 200


@admin_bp.route('/coupons', methods=['POST'])
@role_required(UserRole.staff)
def create_coupon_endpoint():
    data = request.get_json(silent=True)
    if not data:
        return jsonify(detail="Invalid JSON"), 400

    try:
        coupon_data = schemas.CouponCreateSchema.model_validate(data)
        coupon_id = services.create_coupon(g.db, coupon_data)
        logger.info(f"Coupon_added id={coupon_id}")

    except ValidationError as e:
        return jsonify(detail=str(e)), 422

    except ConflictError as e:
        g.db.rollback_needed = True
        return jsonify(detail=str(e)), 409

    return jsonify(message=f'Додано купон id={coupon_id}'), 201


@admin_bp.route('/coupons/<int:coupon_id>/deactivate', methods=['PATCH'])
@role_required(UserRole.staff)
def deactivate_coupon_endpoint(coupon_id):
    try:
        services.deactivate_coupon(g.db, coupon_id)
        logger.info(f"Coupon_deactivated id={coupon_id}")
    except NotFoundError as e:
        g.db.rollback_needed = True
        return jsonify(detail=str(e)), 404
    except ConflictError as e:
        g.db.rollback_needed = True
        return jsonify(detail=str(e)), 409

    return jsonify(message=f"Купон id={coupon_id} деактивовано"), 200
