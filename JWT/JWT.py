from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, verify_jwt_in_request, get_jwt_identity,
    unset_jwt_cookies, unset_refresh_cookies, set_access_cookies
)
from datetime import timedelta
import logging
from functools import wraps
from flask import flash, redirect, url_for, make_response

def crear_access_token(id_usuario : int):
    logging.info(f"Creando token para el usuario {id_usuario}")
    try:
        logging.info(f"Token creado para el usuario {id_usuario}")
        id_str = str(id_usuario)
        access_token = create_access_token(identity=id_str, expires_delta=timedelta(hours=1))
        return access_token
    except Exception as e:
        logging.error(f"Error al crear token para el usuario {id_usuario}: {str(e)}")
        return None
    
def crear_refresh_token(id_usuario : int):
    logging.info(f"Creando token para el usuario {id_usuario}")
    try:
        logging.info(f"Token creado para el usuario {id_usuario}")
        id_str = str(id_usuario)
        refresh_token = create_refresh_token(identity=id_str)
        return refresh_token
    except Exception as e:
        logging.error(f"Error al crear token para el usuario {id_usuario}: {str(e)}")
        return None

def eliminar_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        unset_jwt_cookies(response)
        unset_refresh_cookies(response)
        flash('Sesión cerrada exitosamente', 'info')
        return response
    return decorated_function


def verificar_y_renovar_token(f):
    """
    Decorador que verifica el token y lo renueva automáticamente si es necesario
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Intentar verificar el token actual
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            logging.info(f"Token válido para usuario: {user_id}")
            
            # Token válido, continuar
            return f(*args, **kwargs)
            
        except Exception as e:
            error_msg = str(e)
            logging.warning(f"Token inválido/expirado: {error_msg}")
            
            # Si el token expiró, intentar renovarlo
            if 'expired' in error_msg.lower():
                try:
                    # Verificar el refresh token
                    verify_jwt_in_request(refresh=True)
                    user_id = get_jwt_identity()
                    
                    # Crear nuevo access token
                    new_access_token = create_access_token(identity=user_id)
                    
                    # Establecer nueva cookie y continuar
                    response = make_response(f(*args, **kwargs))
                    set_access_cookies(response, new_access_token)
                    
                    logging.info(f"Token renovado automáticamente para: {user_id}")
                    return response
                    
                except Exception as refresh_error:
                    # El refresh token también expiró o es inválido
                    logging.error(f"Refresh token inválido: {refresh_error}")
                    flash('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.', 'warning')
                    return redirect(url_for('login'))
            else:
                # Otro tipo de error (token inválido, no refresh token, etc.)
                flash('Sesión inválida. Por favor, inicia sesión.', 'error')
                return redirect(url_for('login'))
    
    return decorated_function