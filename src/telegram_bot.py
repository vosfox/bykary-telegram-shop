import os
import sys
import json
import logging
from typing import Optional
import asyncio
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from openai import OpenAI

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://your-app-url.com')

# AI Provider Configuration
OPENPROXY_API_KEY = os.getenv('OPENPROXY_API_KEY')
OPENPROXY_BASE_URL = os.getenv('OPENPROXY_BASE_URL', 'https://api.openproxy.com/v1')

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Определяем активный провайдер (логика переключения через комментирование)
ai_client = None
current_provider = None

if OPENPROXY_API_KEY:
    ai_client = OpenAI(api_key=OPENPROXY_API_KEY, base_url=OPENPROXY_BASE_URL)
    current_provider = "OpenProxy"
elif OPENROUTER_API_KEY:
    ai_client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
    current_provider = "OpenRouter"
elif OPENAI_API_KEY:
    ai_client = OpenAI(api_key=OPENAI_API_KEY)
    current_provider = "OpenAI"
else:
    # Если все закомментированы, выходим с ошибкой
    logger.error("❌ Ни один AI провайдер не настроен! Раскомментируйте провайдера в .env файле")
    sys.exit(1)

logger.info(f"✅ AI Provider: {current_provider}")

class ByKaryBot:
    def __init__(self):
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start"""
        user = update.effective_user
        
        welcome_text = f"""
Привет, {user.first_name}! Это демо-магазин By Kary 👗

— Посмотри каталог
— Добавь в корзину  
— Задай вопрос ассистенту
— Оформи заказ прямо тут

(Это демо. Реальные покупки — на bykary.ru)
        """
        
        keyboard = [
            [InlineKeyboardButton("🛒 Каталог", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton("🧺 Корзина", callback_data="show_cart")],
            [InlineKeyboardButton("💬 Помощь AI", callback_data="ai_help")],
            [InlineKeyboardButton("📦 Мои заказы", callback_data="my_orders")],
            [InlineKeyboardButton("🔗 Сайт", url="https://bykary.ru")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help"""
        help_text = """
<b>Команды бота:</b>

/start - Главное меню
/help - Справка
/catalog - Открыть каталог
/cart - Показать корзину
/orders - Мои заказы

<b>AI-ассистент:</b>
Просто напишите мне любой вопрос о товарах, доставке или размерах!

<b>Примеры вопросов:</b>
• "Какие платья у вас есть?"
• "У меня размер между S и M, что выбрать?"
• "Как доставляете?"
• "Есть ли скидки?"
• "Можно ли примерить?"
        """
        
        await update.message.reply_text(help_text, parse_mode='HTML')
    
    async def catalog_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /catalog"""
        keyboard = [[InlineKeyboardButton("🛒 Открыть каталог", web_app=WebAppInfo(url=WEBAPP_URL))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Откройте каталог товаров By Kary:",
            reply_markup=reply_markup
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "show_cart":
            keyboard = [[InlineKeyboardButton("🛒 Открыть корзину", web_app=WebAppInfo(url=f"{WEBAPP_URL}#cart"))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "Откройте корзину для просмотра добавленных товаров:",
                reply_markup=reply_markup
            )
            
        elif query.data == "ai_help":
            await query.edit_message_text(
                "💬 <b>AI-ассистент готов помочь!</b>\n\n"
                "Задайте любой вопрос о товарах, размерах, доставке или бренде By Kary.\n\n"
                "<i>Просто напишите ваш вопрос в чат...</i>",
                parse_mode='HTML'
            )
            
        elif query.data == "my_orders":
            await query.edit_message_text(
                "📦 <b>Ваши заказы</b>\n\n"
                "Это демо-версия магазина. Все заказы носят демонстрационный характер.\n\n"
                "Для реальных покупок посетите bykary.ru",
                parse_mode='HTML'
            )
    
    async def ai_assistant(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """AI-ассистент для ответов на вопросы"""
        user_message = update.message.text
        user_name = update.effective_user.first_name
        
        # Показываем, что бот печатает
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
        try:
            # Системный промпт для AI-ассистента
            system_prompt = """
Ты - AI-ассистент интернет-магазина женской одежды By Kary (bykary.ru). 

О бренде:
- BY KARY создает стильную одежду для повседневной жизни
- Бренд воспевает женственность, нежность и элегантность
- Каждое изделие имеет особую нашивку с посланием "к себе нужно нежно"
- Основатель - Кэри

Товары в каталоге:
- Футболки с монограммой (черная, белая) - 5900₽
- Костюмы-полоска Аладдин (розовый, голубой) - 15900₽  
- Платья-футболки "Mama needs champagne" (розовое, бежевое) - 6900₽
- Футболка-поло в полоску - 6900₽
- Джинсовая куртка-косуха молочная - 12900₽

Размеры: XS, S, M, L

Отвечай дружелюбно, по-русски, кратко и полезно. Если не знаешь точной информации - честно скажи об этом и предложи обратиться на сайт bykary.ru.
            """
            
            # Определяем модель в зависимости от провайдера
            model = "gpt-3.5-turbo"
            if current_provider == "OpenRouter":
                model = OPENROUTER_MODEL  # Используем модель из .env
            elif current_provider == "OpenProxy":
                model = "gpt-3.5-turbo"  # OpenProxy format
            
            # Запрос к AI провайдеру
            response = ai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Добавляем кнопки для быстрых действий
            keyboard = [
                [InlineKeyboardButton("🛒 Каталог", web_app=WebAppInfo(url=WEBAPP_URL))],
                [InlineKeyboardButton("🔗 Сайт bykary.ru", url="https://bykary.ru")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"💬 [{current_provider}] {ai_response}",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in AI assistant: {e}")
            
            # При ошибке показываем сообщение об ошибке
            keyboard = [
                [InlineKeyboardButton("🛒 Каталог", web_app=WebAppInfo(url=WEBAPP_URL))],
                [InlineKeyboardButton("🔗 Сайт bykary.ru", url="https://bykary.ru")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"⚠️ Ошибка AI-ассистента. Попробуйте позже или посетите наш сайт bykary.ru",
                reply_markup=reply_markup
            )
    
    async def web_app_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик данных от WebApp"""
        try:
            data = json.loads(update.effective_message.web_app_data.data)
            
            if data.get('type') == 'order_completed':
                order_id = data.get('order_id')
                total_amount = data.get('total_amount')
                
                success_message = f"""
✅ <b>Заказ #{order_id} оформлен!</b>

Сумма: {total_amount}₽

<i>Это демо-версия магазина. Для реальных покупок переходите на bykary.ru</i>

Спасибо за интерес к бренду By Kary! 💕
                """
                
                keyboard = [[InlineKeyboardButton("🔗 Перейти на bykary.ru", url="https://bykary.ru")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    success_message,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"Error processing WebApp data: {e}")
    
    def run(self):
        """Запуск бота"""
        if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
            logger.error("BOT_TOKEN не установлен!")
            return
            
        # Создаем приложение
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("catalog", self.catalog_command))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        self.application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.web_app_data))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.ai_assistant))
        
        # Запускаем бота
        logger.info("Запуск бота...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = ByKaryBot()
    bot.run()

