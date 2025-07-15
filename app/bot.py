import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from app import create_app, db
from app.models import User, Task
from flask_sqlalchemy import SQLAlchemy

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
print(TOKEN)
ALLOWED_ID = int(os.getenv('ALLOWED_CHAT_IDS'))

# Initialize Flask app
flask_app = create_app()

# Initialize Telegram bot
app = ApplicationBuilder().token(TOKEN).build()

EMAIL, PASSWORD = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with flask_app.app_context():
        user = User.query.filter_by(telegram_id=update.effective_user.id).first()
        if user:
            await update.message.reply_text("Ви вже зареєстровані! Використовуйте /tasks для перегляду завдань.")
            return ConversationHandler.END
        else:
            await update.message.reply_text("Вітаю! Введіть свій email для реєстрації:")
            return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Дякую! Тепер введіть пароль:")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with flask_app.app_context():
        email = context.user_data['email']
        password = update.message.text
        telegram_id = update.effective_user.id
        username = update.effective_user.username or f"user_{telegram_id}"

        new_user = User(username=username, email=email, password_hash=password, telegram_id=telegram_id)
        db.session.add(new_user)
        db.session.commit()

        await update.message.reply_text("Реєстрація успішна! 🎉 Використовуйте /tasks для перегляду завдань.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Реєстрацію скасовано.')
    return ConversationHandler.END

async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with flask_app.app_context():
        user = User.query.filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please register first.")
            return

        tasks = Task.query.filter_by(user_id=user.id).order_by(Task.id).all()
        if not tasks:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No tasks found.")
            return

        message_lines = ["🗒 Your tasks:"]
        for t in tasks:
            status = "✅" if t.is_done else "❌"
            deadline = f" ({t.deadline.strftime('%Y-%m-%d %H:%M')})" if t.deadline else ""
            message_lines.append(f"#{t.id}: {t.title}{deadline} - {status}")

        await context.bot.send_message(chat_id=update.effective_chat.id, text="\n".join(message_lines))

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with flask_app.app_context():
        user = User.query.filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please register first.")
            return
        task_title = " ".join(context.args)
        if not task_title:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a task title.")
            return
        new_task = Task(title=task_title, user_id=user.id)
        db.session.add(new_task)
        db.session.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Task '{task_title}' added successfully!")

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with flask_app.app_context():
        user = User.query.filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please register first.")
            return
        try:
            task_id = int(context.args[0])
        except (ValueError, IndexError):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a valid task ID.")
            return
        task = Task.query.get(task_id)
        if not task or task.user_id != user.id:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Task not found or you don't have permission to delete it.")
            return
        db.session.delete(task)
        db.session.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Task '{task.title}' deleted successfully!")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with flask_app.app_context():
        user = User.query.filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please register first.")
            return
        try:
            task_id = int(context.args[0])
        except (ValueError, IndexError):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a valid task ID.")
            return
        task = Task.query.get(task_id)
        if not task or task.user_id != user.id:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Task not found or you don't have permission to mark it as done.")
            return
        task.is_done = True
        db.session.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Task '{task.title}' marked as done!")


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

app.add_handler(conv_handler)
app.add_handler(CommandHandler("tasks", tasks))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("delete", delete))
app.add_handler(CommandHandler("done", done))

if __name__ == "__main__":
    print("Starting Telegram bot...")
    app.run_polling()

