from flask_jwt_extended import create_access_token, set_access_cookies
from flask import Blueprint, request, jsonify, g
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
import logging

from flask_app.extensions import cache, limiter
from domain import services
from utils.discounts import calculate_discount
from domain import schemas
from domain.core.errors import NotFoundError, ConflictError, DomainValidationError
from domain.core.constants import CacheNamespace
from flask_app.security import role_required
from utils.enums import UserRole

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('/me', methods=['GET'])
@role_required()
def get_me(user_id: int):
    return jsonify(id=user_id, role=UserRole.client.value), 200


@users_bp.route('/', methods=['POST'])
@limiter.limit("10 per hour")
def create_user_endpoint():
    user_id = services.create_user(g.db)

    access_token = create_access_token(
        identity=str(user_id),
        additional_claims={"role": UserRole.client.value}
    )

    response = jsonify(user_id=user_id)
    set_access_cookies(response, access_token)
    return response, 201


@users_bp.route('/comments', methods=['GET'])
@cache.cached(timeout=3600, key_prefix=CacheNamespace.COMMENTS)
def get_comments_endpoint():
    comments = services.get_comments(g.db, 10)

    return jsonify(comments=[c.model_dump() for c in comments]), 200


@users_bp.route('/comments', methods=['POST'])
@role_required()
@limiter.limit("2 per hour")
def add_comment_endpoint(user_id: int):
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify(detail="No comment data received"), 400

    try:
        comment = schemas.CommentCreateSchema.model_validate(json_data)
    except ValidationError as e:
        return jsonify(detail=str(e)), 422

    services.add_comment(g.db, user_id, comment)

    return jsonify(message="Ваш коментар надіслано на модерацію"), 201


@users_bp.route('/menu', methods=['GET'])
@cache.cached(timeout=3600, key_prefix=CacheNamespace.MENU)
def get_user_menu():
    menu = services.build_user_menu(g.db)
    return jsonify(menu.model_dump()), 200


@users_bp.route('/discount', methods=['GET'])
@role_required()
def get_discount_endpoint(user_id: int):
    user_total_amount = services.total_amount(g.db, user_id)
    discount = calculate_discount(user_total_amount)
    return jsonify(discount=discount), 200


@users_bp.route('/order', methods=['POST'])
@role_required()
def place_order_endpoint(user_id: int):
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify(detail="No order data received"), 400

    try:
        order_data = schemas.OrderCreateSchema.model_validate(json_data)

    except ValidationError as e:
        return jsonify(detail=str(e)), 422

    order = services.create_order(g.db, order_data, user_id)
    return jsonify(order.model_dump()), 201


@users_bp.route('/dishes/<dish_code>/like', methods=['POST'])
@role_required()
def like_dish_endpoint(dish_code: str, user_id: int):
    try:
        services.add_dish_like(g.db, user_id, dish_code)
        logger.info(f"User_liked_dish user={user_id} dish={dish_code}")

    except NotFoundError as e:
        g.db.rollback_needed = True
        return jsonify(detail=str(e)), 404

    except IntegrityError:
        # duplicate like or constraint violation
        g.db.rollback_needed = True
        return jsonify(detail="Ви вже оцінювали цей продукт"), 409

    return jsonify(message="Вподобання додано"), 200


@users_bp.route('/coupon/<coupon_code>', methods=['POST'])
@role_required()
def check_coupon_endpoint(coupon_code: str, user_id: int):
    try:
        discount = services.check_coupon(g.db, coupon_code, user_id)
    except NotFoundError as e:
        g.db.rollback_needed = True
        return jsonify(detail=str(e)), 404

    except ConflictError as e:
        g.db.rollback_needed = True
        return jsonify(detail=str(e)), 409

    except DomainValidationError as e:
        g.db.rollback_needed = True
        return jsonify(detail=str(e)), 400

    return jsonify(discount=discount), 200
