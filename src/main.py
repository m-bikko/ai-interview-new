from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('catalog.index'))