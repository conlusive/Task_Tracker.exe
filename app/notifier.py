import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from telegram import Bot
from app import create_app, db
from app.models import Task, User

load_dotenv()
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
flask_app = create_app()

def check_deadlines():
    with flask_app.app_context():
        now = datetime.now()
        soon = now + timedelta(hours=24)

        tasks = Task.query.filter(
            Task.deadline != None,
            Task.deadline <= soon,
            Task.is_done == False,
            Task.is_notified == False
        ).all()

        user_tasks = {}
        for task in tasks:
            user = db.session.get(User, task.user_id)
            if not user or not user.telegram_id:
                continue
            if user.id not in user_tasks:
                user_tasks[user.id] = {
                    "user": user,
                    "tasks": []
                }
            user_tasks[user.id]["tasks"].append(task)

        for data in user_tasks.values():
            user = data["user"]
            tasks_list = data["tasks"]

            message_lines = ["🔔 Your tasks for the next 24h:"]
            for task in tasks_list:
                status = "✅" if task.is_done else "❌"
                message_lines.append(f"#{task.id}: {task.title} — {task.deadline.strftime('%Y-%m-%d %H:%M')} {status}")
                task.is_notified = True

            message = "\n".join(message_lines)

            try:
                bot.send_message(chat_id=user.telegram_id, text=message)
                db.session.commit()
            except Exception as e:
                print(f"Failed to notify user {user.id}: {e}")
                db.session.rollback()


scheduler = BackgroundScheduler()
scheduler.add_job(check_deadlines, 'interval', hours=1)
scheduler.start()

if __name__ == "__main__":
    pass
