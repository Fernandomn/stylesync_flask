from bson import ObjectId
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app import db
from app.decorators import token_required
from app.models.user import UserCreate, UserResponse

user_bp = Blueprint("user", __name__, url_prefix="/users")


@user_bp.route("/", methods=["GET"], strict_slashes=False)
@token_required
def get_users():
    users_cursor = db.users.find({}, {"password": 0})
    users_list = []

    for user in users_cursor:
        user["_id"] = str(user["_id"])
        users_list.append(
            UserResponse(**user).model_dump(by_alias=True, exclude_none=True)
        )

    return jsonify(users_list)


@user_bp.route("/", methods=["POST"], strict_slashes=False)
@token_required
def create_user(token):

    try:
        product = UserCreate(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    result = db.users.insert_one(product.model_dump(by_alias=True, exclude_none=True))

    return (
        jsonify(
            {
                "message": "O usuário foi criado corretamente!",
                "id": str(result.inserted_id),
            }
        ),
        201,
    )


@user_bp.route("/<str:user_id>", methods=["DELETE"], strict_slashes=False)
@token_required
def delete_user(token, user_id):
    try:
        oid = ObjectId(user_id)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    deleted_user = db.users.delete_one({"_id": oid})

    if deleted_user.deleted_count == 0:
        return jsonify({"error": "Not Found"}), 404

    return (
        jsonify({"message": f"Usuário excluido com sucesso: {user_id}"}),
        204,
    )
