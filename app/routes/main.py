import csv
import io
from datetime import datetime, timedelta, timezone

import jwt
from bson import ObjectId
from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from pydantic import ValidationError

from app import db
from app.decorators import token_required
from app.models.products import Product, ProductDBModel, UpdateProduct
from app.models.sale import Sale
from app.models.user import LoginPayload

main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/")
def index():
    if "jwt_token" not in session:
        return redirect(url_for("main_bp.login"))
    return redirect(url_for("main_bp.dashboard"))


@main_bp.route("/dashboard")
def dashboard():
    if "jwt_token" not in session:
        return redirect(url_for("main_bp.login"))
    return render_template("dashboard.html", title="Dashboard")


@main_bp.route("/login", methods=["GET"], strict_slashes=False)
def render_login():
    return render_template("login.html", title="Login")


@main_bp.route("/login", methods=["POST"], strict_slashes=False)
def login():
    # try:
    # raw_data = request.get_json()
    username = request.form.get("username")
    password = request.form.get("password")
    user_data = LoginPayload(username=username, password=password)

    user_in_db = db.users.find_one({"username": username})

    if user_in_db and user_in_db.get("password") == password:
        token = jwt.encode(
            {
                "user_id": user_data.username,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        session["jwt_token"] = token

        return redirect(url_for("main_bp.dashboard"))
    else:
        flash("Usuário ou senha inválidos", "danger")
        return redirect(url_for("main_bp.login"))
    # except ValidationError as e:
    #     return jsonify({"error": e.errors()}), 400
    # except Exception as e:
    #     return (
    #         jsonify({"error": f"Corpo da requisição inválido, ou não é um JSON: {e}"}),
    #         500,
    #     )

    # if user_data.username == "admin" and user_data.password == "123":
    #     token = jwt.encode(
    #         {
    #             "user_id": user_data.username,
    #             "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    #         },
    #         current_app.config["SECRET_KEY"],
    #         algorithm="HS256",
    #     )

    #     print(token)

    #     return jsonify({"access_token": token}), 200

    # return jsonify({"message": f"Credenciais invalidas"}), 401


# ----------------------PRODUTOS------------------------


@main_bp.route("/products", methods=["GET"], strict_slashes=False)
def get_products():
    if "jwt_token" not in session:
        return redirect(url_for("main_bp.login"))

    products_cursor = db.products.find({})
    # products_list = [
    #     ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True)
    #     for product in products_cursor
    # ]

    # return jsonify(products_list)
    return render_template("products.html", products=products_cursor, title="Produtos")


@main_bp.route("/products/<string:product_id>", methods=["GET"])
def get_product_by_id(product_id):

    try:
        oid = ObjectId(product_id)
    except Exception as ex:
        return jsonify({"error": f"Id do produto inválido"}), 400

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
def create_product(jwt_token):
    try:
        product = Product(**request.get_json())
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
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400


@main_bp.route("/products/<string:product_id>", methods=["PUT"])
@token_required
def update_product(jwt_token, product_id):
    try:
        oid = ObjectId(product_id)
        update_data = UpdateProduct(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

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
    except Exception:
        return jsonify({"error": f"ID do produto inválido"}), 400

    delete_result = db.products.delete_one({"_id": oid})

    if delete_result.deleted_count == 0:
        return jsonify({"error": "Produto não encontrado"}), 404

    return "", 204


# ----------------------VENDAS------------------------


@main_bp.route("/vendas/upload", methods=["GET"])
def upload_sales_page():
    if "jwt_token" not in session:
        return redirect(url_for("main_bp.login"))
    return render_template("upload_sales.html", title="Upload de Vendas")


@main_bp.route("/sales/upload", methods=["POST"])
@token_required
def upload_sales(jwt_token):
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
                errors.append(f"Linha {row_num} com dados inválidos: {e.errors()}")
            except Exception as e:
                errors.append(f"Linha {row_num} com erro inesperado: {str(e)}")

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

    return (
        jsonify(
            {"error": "Formato de arquivo inválido. Por favor, envie um arquivo .csv"}
        ),
        400,
    )
