import logging
from telegram import Update, ChatMember
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота и канал
BOT_TOKEN = "7926003917:AAFlhESCGH96FV6Fw3PRx_F5Ekwmab0ba0E"
CHANNEL_USERNAME = "@Minvy52"  # Юзернейм канала без @

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Проверяет, подписан ли пользователь на канал"""
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")
        return False

async def send_subscription_required(update: Update):
    """Отправляет сообщение о необходимости подписки"""
    await update.message.reply_html(
        "❌ <b>Для использования бота необходимо подписаться на канал!</b>\n\n"
        f"Подпишись: {CHANNEL_USERNAME}\n\n"
        "После подписки используй команду снова."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Проверяем подписку
    if not await check_subscription(user.id, context):
        await send_subscription_required(update)
        return
    
    await update.message.reply_html(
        f"✅ <b>Привет, {user.mention_html()}!</b>\n\n"
        f"Твой ID: <code>{user.id}</code>\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - начать работу\n"
        "/myid - показать твой ID\n"
        "/getid @username - получить ID Канала/Группы по юзернейму"
    )

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать ID пользователя"""
    user = update.effective_user
    
    # Проверяем подписку
    if not await check_subscription(user.id, context):
        await send_subscription_required(update)
        return
    
    await update.message.reply_html(
        f"🆔 <b>Твой ID:</b> <code>{user.id}</code>"
    )

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить ID пользователя по юзернейму"""
    user = update.effective_user
    
    # Проверяем подписку
    if not await check_subscription(user.id, context):
        await send_subscription_required(update)
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 <b>Используй:</b> /getid @username\n"
            "<b>Например:</b> /getid @durov",
            parse_mode='HTML'
        )
        return

    username = context.args[0]
    
    # Убираем @ если пользователь его указал
    if username.startswith('@'):
        username = username[1:]
    
    try:
        # Получаем информацию о пользователе
        target_user = await context.bot.get_chat(f"@{username}")
        await update.message.reply_html(
            f"👤 <b>Канал/Группа:</b> @{username}\n"
            f"🆔 <b>ID:</b> <code>{target_user.id}</code>"
        )
    except Exception as e:
        logging.error(f"Ошибка при получении ID: {e}")
        await update.message.reply_text(
            f"❌ <b>Не удалось найти канал</b> @{username}\n"
            "Убедись, что юзернейм правильный и канал существует.",
            parse_mode='HTML'
        )

async def check_subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для проверки подписки"""
    user = update.effective_user
    is_subscribed = await check_subscription(user.id, context)
    
    if is_subscribed:
        await update.message.reply_html(
            "✅ <b>Отлично! Ты подписан на канал.</b>\n\n"
            "Теперь ты можешь использовать все команды бота."
        )
    else:
        await send_subscription_required(update)

def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("myid", myid))
    application.add_handler(CommandHandler("getid", getid))
    application.add_handler(CommandHandler("check", check_subscription_command))

    # Запускаем бота
    print("Бот запущен...")
    print(f"Проверка подписки на канал: {CHANNEL_USERNAME}")
    application.run_polling()

if __name__ == "__main__":
    main()
