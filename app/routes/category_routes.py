from flask import Blueprint, jsonify


category_bp = Blueprint("category", __name__, url_prefix="/categories")

@category_bp.route('/', methods=['GET'])
def get_categories():
    return jsonify({'message': 'rota de recuperação de todas as categorias'})

