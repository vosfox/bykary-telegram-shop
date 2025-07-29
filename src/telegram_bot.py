import os
import sys
import json
import logging
from typing import Optional
import asyncio
import aiohttp
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
✨ <b>Добро пожаловать в мир BY KARY</b> ✨

Привет, {user.first_name}! 💕

<i>Здесь каждое изделие создано с любовью
"к себе нужно нежно" — наше кредо</i>

🛍 <b>Что тебя ждет:</b>
• Эксклюзивная женская одежда
• Стильные образы на каждый день
• Персональный AI-стилист
• Удобное оформление заказов

<i>💎 Это демо-версия магазина
Полный ассортимент на bykary.ru</i>
        """
        
        keyboard = [
            [InlineKeyboardButton("✨ КАТАЛОГ", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton("🛍 Корзина", callback_data="show_cart"), 
             InlineKeyboardButton("💬 Стилист", callback_data="ai_help")],
            [InlineKeyboardButton("📦 Заказы", callback_data="my_orders"),
             InlineKeyboardButton("🌸 Сайт", url="https://bykary.ru")],
            [InlineKeyboardButton("☕ Купить кофе BY KARY", callback_data="buy_coffee")],
            [InlineKeyboardButton("🔄 Меню", callback_data="main_menu")]
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
    
    async def cart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /cart"""
        user_id = str(update.effective_user.id)
        cart_items = await self.get_cart_data(user_id)
        
        if not cart_items:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Открыть каталог", web_app=WebAppInfo(url=WEBAPP_URL))],
                [InlineKeyboardButton("🔄 Меню", callback_data="main_menu")]
            ])
            
            await update.message.reply_text(
                "🛍 <b>Ваша корзина пуста</b>\n\n"
                "💫 Добавьте товары из каталога, чтобы они появились здесь\n\n"
                "<i>✨ Откройте каталог и выберите что-то прекрасное!</i>",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            return
        
        # Формируем сообщение с товарами из корзины
        cart_text = "🛍 <b>Ваша корзина</b>\n\n"
        total_amount = 0
        
        for item in cart_items:
            product = item.get('product', {})
            name = product.get('name', 'Товар')
            price = product.get('price', 0)
            quantity = item.get('quantity', 1)
            size = item.get('size', 'не указан')
            
            item_total = price * quantity
            total_amount += item_total
            
            cart_text += f"📦 <b>{name}</b>\n"
            cart_text += f"   Размер: {size}\n"
            cart_text += f"   Количество: {quantity} шт.\n"
            cart_text += f"   Цена: {price:,}₽ × {quantity} = {item_total:,}₽\n\n"
        
        cart_text += f"💰 <b>Итого: {total_amount:,}₽</b>\n\n"
        cart_text += "<i>💫 Корзина синхронизируется между ботом и веб-каталогом</i>"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍 Открыть корзину", web_app=WebAppInfo(url=f"{WEBAPP_URL}#cart"))],
            [InlineKeyboardButton("✨ Каталог", web_app=WebAppInfo(url=WEBAPP_URL)),
             InlineKeyboardButton("🔄 Обновить", callback_data="show_cart")],
            [InlineKeyboardButton("🔄 Меню", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(
            cart_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    def get_main_menu_keyboard(self):
        """Возвращает клавиатуру главного меню"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ КАТАЛОГ", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton("🛍 Корзина", callback_data="show_cart"), 
             InlineKeyboardButton("💬 Стилист", callback_data="ai_help")],
            [InlineKeyboardButton("📦 Заказы", callback_data="my_orders"),
             InlineKeyboardButton("🌸 Сайт", url="https://bykary.ru")],
            [InlineKeyboardButton("☕ Купить кофе BY KARY", callback_data="buy_coffee")],
            [InlineKeyboardButton("🔄 Меню", callback_data="main_menu")]
        ])
    
    async def get_cart_data(self, user_id: str):
        """Получить данные корзины через API"""
        try:
            # Формируем URL для запроса корзины
            api_url = WEBAPP_URL.replace('/static', '') if '/static' in WEBAPP_URL else WEBAPP_URL
            cart_url = f"{api_url}/api/cart/{user_id}"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(cart_url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Error fetching cart: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error getting cart data: {e}")
            return []
    
    async def show_cart_info(self, query):
        """Показать информацию о корзине пользователя"""
        user_id = str(query.from_user.id)
        cart_items = await self.get_cart_data(user_id)
        
        if not cart_items:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Открыть каталог", web_app=WebAppInfo(url=WEBAPP_URL))],
                [InlineKeyboardButton("🔄 Назад в меню", callback_data="main_menu")]
            ])
            
            await query.edit_message_text(
                "🛍 <b>Ваша корзина пуста</b>\n\n"
                "💫 Добавьте товары из каталога, чтобы они появились здесь\n\n"
                "<i>✨ Откройте каталог и выберите что-то прекрасное!</i>",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            return
        
        # Формируем сообщение с товарами из корзины
        cart_text = "🛍 <b>Ваша корзина</b>\n\n"
        total_amount = 0
        
        for item in cart_items:
            product = item.get('product', {})
            name = product.get('name', 'Товар')
            price = product.get('price', 0)
            quantity = item.get('quantity', 1)
            size = item.get('size', 'не указан')
            
            item_total = price * quantity
            total_amount += item_total
            
            cart_text += f"📦 <b>{name}</b>\n"
            cart_text += f"   Размер: {size}\n"
            cart_text += f"   Количество: {quantity} шт.\n"
            cart_text += f"   Цена: {price:,}₽ × {quantity} = {item_total:,}₽\n\n"
        
        cart_text += f"💰 <b>Итого: {total_amount:,}₽</b>\n\n"
        cart_text += "<i>💫 Корзина синхронизируется между ботом и веб-каталогом</i>"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍 Открыть корзину", web_app=WebAppInfo(url=f"{WEBAPP_URL}#cart"))],
            [InlineKeyboardButton("✨ Каталог", web_app=WebAppInfo(url=WEBAPP_URL)),
             InlineKeyboardButton("🔄 Обновить", callback_data="show_cart")],
            [InlineKeyboardButton("🔄 Назад в меню", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(
            cart_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "main_menu":
            welcome_text = f"""
✨ <b>Добро пожаловать в мир BY KARY</b> ✨

<i>Здесь каждое изделие создано с любовью
"к себе нужно нежно" — наше кредо</i>

🛍 <b>Выберите действие:</b>
            """
            await query.edit_message_text(
                welcome_text,
                reply_markup=self.get_main_menu_keyboard(),
                parse_mode='HTML'
            )
            
        elif query.data == "show_cart":
            await self.show_cart_info(query)
            
        elif query.data == "ai_help":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Назад в меню", callback_data="main_menu")]
            ])
            await query.edit_message_text(
                "💬 <b>Персональный стилист BY KARY</b> ✨\n\n"
                "Привет! Я помогу тебе с выбором:\n"
                "• Подберу размер\n"
                "• Расскажу о тканях и уходе\n"
                "• Посоветую образы\n"
                "• Отвечу на любые вопросы\n\n"
                "<i>Просто напиши мне что хочешь узнать 💕</i>",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        elif query.data == "my_orders":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Назад в меню", callback_data="main_menu")]
            ])
            await query.edit_message_text(
                "📦 <b>История заказов</b>\n\n"
                "💎 Это демо-версия магазина\n"
                "Все заказы носят демонстрационный характер\n\n"
                "🌸 Для реальных покупок:\n"
                "• Посетите bykary.ru\n"
                "• Или свяжитесь с нами напрямую\n\n"
                "<i>Спасибо за интерес к бренду BY KARY! 💕</i>",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        elif query.data == "buy_coffee":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Оплатить кофе", url="https://payment-url-placeholder.com")],
                [InlineKeyboardButton("🔄 Назад в меню", callback_data="main_menu")]
            ])
            await query.edit_message_text(
                "☕ <b>Угостить кофе BY KARY</b>\n\n"
                "💕 Поддержите создателей бренда BY KARY!\n\n"
                "🎯 <b>Варианты поддержки:</b>\n"
                "• ☕ Один кофе - 150₽\n"
                "• ☕☕ Два кофе - 300₽\n"
                "• 🍰 Кофе с десертом - 500₽\n\n"
                "<i>Каждая чашечка кофе вдохновляет нас создавать новые коллекции! 💫</i>",
                reply_markup=keyboard,
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
                [InlineKeyboardButton("✨ Каталог", web_app=WebAppInfo(url=WEBAPP_URL)),
                 InlineKeyboardButton("🛍 Корзина", callback_data="show_cart")],
                [InlineKeyboardButton("🔄 Меню", callback_data="main_menu"),
                 InlineKeyboardButton("🌸 Сайт", url="https://bykary.ru")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"💬 <b>Стилист BY KARY:</b>\n\n{ai_response}\n\n<i>Еще вопросы? Пишите! 💕</i>",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error in AI assistant: {e}")
            
            # При ошибке показываем красивое сообщение
            keyboard = [
                [InlineKeyboardButton("✨ Каталог", web_app=WebAppInfo(url=WEBAPP_URL)),
                 InlineKeyboardButton("🛍 Корзина", callback_data="show_cart")],
                [InlineKeyboardButton("🔄 Меню", callback_data="main_menu"),
                 InlineKeyboardButton("🌸 Сайт", url="https://bykary.ru")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "💫 <b>Стилист временно недоступен</b>\n\n"
                "Попробуйте чуть позже или посетите наш сайт bykary.ru\n\n"
                "<i>Мы всегда рады помочь! 💕</i>",
                reply_markup=reply_markup,
                parse_mode='HTML'
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
    
    async def setup_bot_menu(self):
        """Настройка постоянного меню бота"""
        try:
            from telegram import BotCommand, MenuButtonWebApp
            
            # Устанавливаем список команд
            commands = [
                BotCommand("start", "🏠 Главное меню"),
                BotCommand("catalog", "✨ Открыть каталог"),
                BotCommand("cart", "🛍 Моя корзина"),  
                BotCommand("help", "❓ Помощь")
            ]
            
            await self.application.bot.set_my_commands(commands)
            
            # Устанавливаем кнопку меню как WebApp
            menu_button = MenuButtonWebApp(
                text="✨ КАТАЛОГ",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
            await self.application.bot.set_chat_menu_button(menu_button=menu_button)
            
            logger.info("✅ Bot menu настроено успешно")
            
        except Exception as e:
            logger.error(f"Ошибка настройки меню бота: {e}")
    
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
        self.application.add_handler(CommandHandler("cart", self.cart_command))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        self.application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.web_app_data))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.ai_assistant))
        
        # Настраиваем меню при запуске
        async def post_init(application):
            await self.setup_bot_menu()
        
        self.application.post_init = post_init
        
        # Запускаем бота
        logger.info("Запуск бота...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = ByKaryBot()
    bot.run()

