from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app import db
from app.decorators import token_required
from app.models.user import UserCreate, UserResponse

user_bp = Blueprint("user", __name__, url_prefix="/users")


@user_bp.route("/", methods=["GET"], strict_slashes=False)
@token_required
def get_users(token_payload):
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
def create_user(token_payload):

    try:
        user_data = UserCreate(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    result = db.users.insert_one(user_data.model_dump(by_alias=True, exclude_none=True))

    return (
        jsonify(
            {
                "message": "O usuário foi criado corretamente!",
                "id": str(result.inserted_id),
            }
        ),
        201,
    )


@user_bp.route("/<string:user_id>", methods=["DELETE"], strict_slashes=False)
@token_required
def delete_user(token_payload, user_id):
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        return jsonify({"error": f"ID de usuário inválido: {user_id}"}), 400

    deleted_user = db.users.delete_one({"_id": oid})

    if deleted_user.deleted_count == 0:
        return jsonify({"error": "Not Found"}), 404

    return (
        jsonify({"message": f"Usuário excluido com sucesso: {user_id}"}),
        200,
    )
