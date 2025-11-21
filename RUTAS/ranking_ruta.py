from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from QUERYS.querysRaking import get_50_posiciones_raking


def ranking_global_rutas():
    ranking = get_50_posiciones_raking()            
    return render_template('user_view/ranking.html', ranking=ranking)
