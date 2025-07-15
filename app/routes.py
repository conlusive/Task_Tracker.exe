from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from flask_login import logout_user


from app import db
from app.forms import TaskForm
from app.models import Task, User

tasks = Blueprint('tasks', __name__)
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


admin = Blueprint('admin', __name__)

@admin.route('/admin', methods=['GET'])
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.all()
    return render_template('admin_panel.html', title='Admin Panel', users=users)

@admin.route('/admin/make-admin/<int:user_id>', methods=['GET'])
@login_required
def make_admin(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash(f'{user.username} is already an admin.', 'info')
    else:
        user.is_admin = True
        db.session.commit()
        flash(f'{user.username} is now an admin.', 'success')

    return redirect(url_for('admin.admin_panel'))



@main.route('/link-telegram', methods=['POST'])
@login_required
def link_telegram():
    telegram_id = request.form.get('telegram_id')
    if telegram_id:
        current_user.telegram_id = telegram_id
        db.session.commit()
        flash('Telegram ID tied successfully!', 'success')
    else:
        flash('Please enter the correct Telegram ID.', 'danger')
    return redirect(url_for('main.index'))




@tasks.route('/tasks')
@login_required
def tasks_list():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', tasks=tasks)



@tasks.route('/tasks/add', methods=['GET', 'POST'], endpoint='create')
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, is_done=form.is_done.data, user_id=current_user.id, deadline=form.deadline.data)
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks.tasks_list'))
    return render_template('task_form.html', form=form)



@tasks.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to edit this task.', 'danger')
        return redirect(url_for('tasks.tasks_list'))

    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.is_done = form.is_done.data
        task.deadline = form.deadline.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.tasks_list'))
    return render_template('task_form.html', form=form)


@tasks.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('tasks.tasks_list'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks.tasks_list'))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('auth.login'))



