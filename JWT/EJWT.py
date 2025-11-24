from app import jwt
from flask import flash, redirect, url_for
from JWT.JWT import verificar_y_renovar_token

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Cuando el access token expira"""
    flash('Tu sesión ha expirado. Renovando...', 'info')
    return redirect(url_for('refresh'))
    

@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Token inválido"""
    flash('Sesión inválida', 'error')
    return redirect(url_for('login'))

@jwt.unauthorized_loader
def missing_token_callback(error):
    """Sin token"""
    flash('Debes iniciar sesión', 'info')
    return redirect(url_for('login'))