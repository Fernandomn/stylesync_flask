from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.models.user import LoginPayload

main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/login", methods=["POST"])
def login():
    try:
        raw_data = request.get_json()
        user_data = LoginPayload(**raw_data)

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    except Exception as e:
        return jsonify({"error": "Erro durante a requisição do dado"}), 500

    if user_data.username == "admin" and user_data.password == "123":        
        return jsonify({"message": f"Login bem sucedido!"}), 200
    else:
        return jsonify({"message": f"Credenciais invalidas"}), 200
        # return jsonify({"message": f"Realizar login do usuário {user_data.model_dump_json()}."}), 200


@main_bp.route("/")
def index():
    return jsonify({"message": "Bem vindo ao StyleSync!"})


@main_bp.route("/products", methods=["GET"])
def get_products():
    return jsonify({"message": "Essa é a rota dos produtos."})


@main_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product_by_id(product_id):
    return jsonify(
        {"message": f"Essa é a rota de visualização do produto com ID {product_id}."}
    )


@main_bp.route("/products", methods=["POST"])
def create_product():
    return jsonify({"message": "Essa é a rota de criação do produto."})


@main_bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    return jsonify(
        {"message": f"Essa é a rota de atualização do produto com ID {product_id}."}
    )


@main_bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    return jsonify(
        {"message": f"Essa é a rota de exclusão do produto com ID {product_id}."}
    )


@main_bp.route("/sales/upload", methods=["POST"])
def upload_sales():
    return jsonify({"message": f"Essa é a rota do upload do arquivo de vendas."})
