import csv
import io
from datetime import datetime, timedelta, timezone

import jwt
from bson import ObjectId
from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError

from app import db
from app.decorators import token_required
from app.models.products import Product, ProductDBModel, UpdateProduct
from app.models.sale import Sale
from app.models.user import LoginPayload

main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/login", methods=["POST"], strict_slashes=False)
def login():
    try:
        raw_data = request.get_json()
        user_data = LoginPayload(**raw_data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        return (
            jsonify({"error": f"Corpo da requisição inválido, ou não é um JSON: {e}"}),
            500,
        )

    if user_data.username == "admin" and user_data.password == "123":
        token = jwt.encode(
            {
                "user_id": user_data.username,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

        print(token)

        return jsonify({"access_token": token}), 200

    return jsonify({"message": f"Credenciais invalidas"}), 401


@main_bp.route("/")
def index():
    return jsonify({"message": "Bem vindo ao StyleSync!"})


@main_bp.route("/products", methods=["GET"], strict_slashes=False)
def get_products():
    products_cursor = db.products.find({})
    products_list = [
        ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True)
        for product in products_cursor
    ]

    return jsonify(products_list)


@main_bp.route("/products/<string:product_id>", methods=["GET"])
def get_product_by_id(product_id):

    try:
        oid = ObjectId(str(product_id))
    except Exception as ex:
        return jsonify(
            {"error": f"Erro ao transformar {product_id} em ObjectId: {ex}."}
        )

    product = db.products.find_one({"_id": oid})
    if product:
        product_model = ProductDBModel(**product).model_dump(
            by_alias=True, exclude_none=True
        )

        return jsonify(product_model)
    else:
        return jsonify({"error": f"Erro: Produto {product_id} não encontrado"})


@main_bp.route("/products", methods=["POST"], strict_slashes=False)
@token_required
def create_product(token):
    try:
        product = Product(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    result = db.products.insert_one(product.model_dump())
    return (
        jsonify(
            {
                "message": f"O produto foi criado corretamente!",
                "id": str(result.inserted_id),
            }
        ),
        201,
    )


@main_bp.route("/products/<string:product_id>", methods=["PUT"])
@token_required
def update_product(token, product_id):
    try:
        oid = ObjectId(product_id)
        update_data = UpdateProduct(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()})

    update_result = db.products.update_one(
        {"_id": oid}, {"$set": update_data.model_dump(exclude_unset=True)}
    )

    if update_result.matched_count == 0:
        return jsonify({"error": "Produto não encontrado"}), 404

    updated_product = db.products.find_one({"_id": oid})

    return jsonify(
        ProductDBModel(**updated_product).model_dump(by_alias=True, exclude=None)
    )


@main_bp.route("/products/<string:product_id>", methods=["DELETE"])
@token_required
def delete_product(token, product_id):

    try:
        oid = ObjectId(product_id)
    except ValidationError as e:
        return jsonify({"error": f"ID do produto inválido: {e.errors()}"}), 400

    delete_result = db.products.delete_one({"_id": oid})

    if delete_result.deleted_count == 0:
        return jsonify({"error": "Produto não encontrado"}), 404

    return "", 204


@main_bp.route("/sales/upload", methods=["POST"])
@token_required
def upload_sales(token):
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo foi enviado"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    if file and file.filename.endswith(".csv"):
        csv_stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        csv_reader = csv.DictReader(csv_stream)

        sales_to_insert = []
        errors = []

        for row_num, row in enumerate(csv_reader, 1):
            try:
                sale_data = Sale(**row)

                sales_to_insert.append(sale_data.model_dump())
            except ValidationError as e:
                errors.append(f"Linha {row_num} com dados inválidos")
            except Exception:
                errors.append(f"Linha {row_num} com erro inesperado nos dados")

        if sales_to_insert:
            try:
                db.sales.insert_many(sales_to_insert)
            except Exception as e:
                return jsonify({"error": f"{e}"}), 500
            return (
                jsonify(
                    {
                        "message": "Upload realizado com sucesso",
                        "vendas_importadas": len(sales_to_insert),
                        "erros_encontrados": errors,
                    }
                ),
                200,
            )

    return jsonify({"message": f"Essa é a rota do upload do arquivo de vendas."})
