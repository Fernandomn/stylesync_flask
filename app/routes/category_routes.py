from flask import Blueprint, jsonify

category_bp = Blueprint("category", __name__, url_prefix="/categories")


@category_bp.route("/", methods=["GET"])
def get_categories():
    return jsonify({"message": "rota de recuperação de todas as categorias"})


@category_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    return jsonify(
        {"message": f"rota de recuperação da categoria com ID {category_id}"}
    )


@category_bp.route("/", methods=["POST"])
def create_category():
    return jsonify({"message": "rota de criação de uma nova categoria"})


@category_bp.route("/<int:category_id>", methods=["PUT"])
def edit_category(category_id):
    return jsonify({"message": f"rota de edição da categoria {category_id}"})


@category_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    return jsonify({"message": f"rota de exclusão da categoria {category_id}"})
