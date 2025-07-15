from flask import Blueprint, render_template
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        return "Access denied", 403

    from app.models import Task, User
    tasks = Task.query.all()
    users = User.query.all()
    return render_template('admin/dashboard.html', tasks=tasks, users=users)


