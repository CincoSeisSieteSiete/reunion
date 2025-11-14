from functools import wraps
from flask import session, redirect, url_for, flash
from typing import Callable, Any


def requiere_login(f: Callable) -> Callable:
    """Decorador que requiere que el usuario esté logueado"""
    @wraps(f)
    def decorador_login(*args, **kwargs) -> Any:
        if 'user_id' not in session:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorador_login


def requiere_admin(f: Callable) -> Callable:
    """Decorador que requiere que el usuario sea admin"""
    @wraps(f)
    def decorador_admin(*args, **kwargs) -> Any:
        if 'user_rol' not in session or session['user_rol'] != 'admin':
            flash('No tienes permisos de administrador', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorador_admin


def requiere_lider(f: Callable) -> Callable:
    """Decorador que requiere que el usuario sea líder o admin"""
    @wraps(f)
    def decorador_lider(*args, **kwargs) -> Any:
        if 'user_rol' not in session or session['user_rol'] not in ['lider', 'admin']:
            flash('No tienes permisos de líder', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorador_lider
