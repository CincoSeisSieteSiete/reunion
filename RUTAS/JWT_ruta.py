from flask import jsonify
from JWT.JWT import renovar_token_logica

def refresh_ruta():
    """
    Ruta para renovar el access token usando el refresh token.
    Solo accesible con un refresh token válido.
    """
    return renovar_token_logica()
