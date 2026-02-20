from functools import wraps

import jwt
from flask import current_app, jsonify, request

AUTH_CONST = "Authorization"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if AUTH_CONST in request.headers:
            auth_header = request.headers[AUTH_CONST]

            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"message": "Token Mal formado"})
        if not token:
            return jsonify({"error": "Token não encontrado"}), 401

        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        return f(data, *args, **kwargs)

    return decorated
