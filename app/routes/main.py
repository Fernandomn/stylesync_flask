from flask import Blueprint, jsonify

main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/login", methods=["POST"])
def login():
    return jsonify({"message": "Login."})


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
