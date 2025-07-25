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

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, LabeledPrice
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, PreCheckoutQueryHandler
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
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN', 'YOUR_PAYMENT_TOKEN_HERE')

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
        self.user_main_messages = {}  # Хранение ID главных сообщений
        
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
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])
        await update.message.reply_text(help_text, reply_markup=keyboard, parse_mode='HTML')
    
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
    
    async def clear_cart(self, user_id: str):
        """Очистить корзину пользователя"""
        try:
            # Формируем URL для очистки корзины
            api_url = WEBAPP_URL.replace('/static', '') if '/static' in WEBAPP_URL else WEBAPP_URL
            clear_url = f"{api_url}/api/cart/{user_id}/clear"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.delete(clear_url) as response:
                    if response.status == 200:
                        logger.info(f"Cart cleared for user {user_id}")
                        return True
                    else:
                        logger.error(f"Error clearing cart: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error clearing cart: {e}")
            return False
    
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
            [InlineKeyboardButton("💳 Оплатить заказ", callback_data="pay_cart")],
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
            await self.show_coffee_menu(query)
            
        elif query.data.startswith("coffee_"):
            await self.process_coffee_payment(query)
            
        elif query.data == "pay_cart":
            await self.process_cart_payment(query)
    
    async def ai_assistant(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """AI-ассистент для ответов на вопросы"""
        user_message = update.message.text
        user_name = update.effective_user.first_name
        
        # Показываем, что бот печатает
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
        try:
            # Системный промпт для AI-ассистента
            system_prompt = f"""
Ты - кокетливая продавщица-консультант бутика BY KARY! 💕

ТВОЯ ЛИЧНОСТЬ:
- Романтичная, кокетливая, иногда игривая 😉
- Знаешь ВСЁ о товарах и влюблена в бренд
- Умеешь мягко закрывать продажи
- Используешь эмодзи, но не перебарщиваешь
- Обращаешься к клиенткам нежно: "красотка", "милая", "дорогая"

ТОВАРЫ В БОТЕ (знай назубок!):
🔥 ОДЕЖДА:
- Футболки с монограммой BY KARY (черная/белая) - 5,900₽
- Костюмы-полоска "Аладдин" (розовый rosy/голубой blue) - 15,900₽  
- Платья-футболки "Mama needs champagne" (розовое/бежевое) - 6,900₽
- Футболка-поло в полоску - 6,900₽
- Джинсовая куртка-косуха молочная - 12,900₽

☕ КОФЕ МЕНЮ (для поддержки):
- Bubble tea - 350₽
- Coffee классический - 250₽  
- Matcha японский - 300₽
- Дубайский шоколад премиум - 450₽

РАЗМЕРЫ: XS, S, M, L (все идеально сидят!)

ФИЛОСОФИЯ БРЕНДА:
"к себе нужно нежно" - это про заботу о себе любимой 💕

ТВОЯ ЗАДАЧА:
1. Влюбить в товары ✨
2. Помочь с выбором размера/цвета 💭  
3. Мягко закрывать продажи 💳
4. Быть немного кокетливой и романтичной 😘
5. Предлагать кофе для поддержки бренда ☕

ПРИМЕРЫ СТИЛЯ:
"Ой, милая, эта футболка будет на тебе просто божественно! 💕"
"Красотка, а ты знаешь что этот костюм делает талию еще тоньше? 😉"
"Дорогая, размер S тебе точно подойдет, не переживай! ✨"

Отвечай по-русски, кокетливо, но профессионально. Закрывай продажи мягко!
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
    
    async def show_coffee_menu(self, query):
        """Показать меню кофе BY KARY"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🧋 Bubble tea - 350₽", callback_data="coffee_bubble_tea")],
            [InlineKeyboardButton("☕ Coffee - 250₽", callback_data="coffee_regular")],
            [InlineKeyboardButton("🍵 Matcha - 300₽", callback_data="coffee_matcha")],
            [InlineKeyboardButton("🍫 Дубайский шоколад - 450₽", callback_data="coffee_dubai_chocolate")],
            [InlineKeyboardButton("🔄 Назад в меню", callback_data="main_menu")]
        ])
        await query.edit_message_text(
            "☕ <b>Кофейное меню BY KARY</b>\n\n"
            "🧋 <b>Bubble tea</b> - 350₽\n"
            "Освежающий чай с жемчужинами тапиоки\n\n"
            "☕ <b>Coffee</b> - 250₽\n"
            "Классический ароматный кофе\n\n"
            "🍵 <b>Matcha</b> - 300₽\n"
            "Японский зеленый чай матча\n\n"
            "🍫 <b>Дубайский шоколад</b> - 450₽\n"
            "Премиальный шоколад с фисташкой\n\n"
            "<i>💕 Поддержите создателей бренда BY KARY!</i>",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def process_coffee_payment(self, query):
        """Обработка оплаты кофе"""
        coffee_type = query.data.replace("coffee_", "")
        
        # Определяем цену и название
        coffee_menu = {
            "bubble_tea": {"name": "🧋 Bubble tea", "price": 35000},  # в копейках
            "regular": {"name": "☕ Coffee", "price": 25000},
            "matcha": {"name": "🍵 Matcha", "price": 30000},
            "dubai_chocolate": {"name": "🍫 Дубайский шоколад", "price": 45000}
        }
        
        if coffee_type not in coffee_menu:
            return
            
        item = coffee_menu[coffee_type]
        
        try:
            # Создаем счет для оплаты
            await query.message.reply_invoice(
                title=f"BY KARY - {item['name']}",
                description=f"Поддержите создателей бренда BY KARY! 💕",
                payload=f"coffee_{coffee_type}_{query.from_user.id}",
                provider_token=PAYMENT_PROVIDER_TOKEN,
                currency="RUB",
                prices=[LabeledPrice(item['name'], item['price'])],
                start_parameter="coffee_payment",
                photo_url="https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400",
                photo_width=400,
                photo_height=300,
                need_name=False,
                need_phone_number=False,
                need_email=False,
                need_shipping_address=False,
                send_phone_number_to_provider=False,
                send_email_to_provider=False,
                is_flexible=False
            )
            
            await query.answer("💳 Счет создан! Выберите способ оплаты")
            
            # Возвращаем меню обратно
            await self.show_coffee_menu(query)
            
        except Exception as e:
            logger.error(f"Ошибка создания счета: {e}")
            await query.answer("❌ Ошибка создания счета", show_alert=True)
    
    async def process_cart_payment(self, query):
        """Обработка оплаты корзины"""
        user_id = str(query.from_user.id)
        cart_items = await self.get_cart_data(user_id)
        
        if not cart_items:
            await query.answer("❌ Корзина пуста", show_alert=True)
            return
        
        # Считаем общую сумму
        total_amount = 0
        items_description = []
        
        for item in cart_items:
            product = item.get('product', {})
            name = product.get('name', 'Товар')
            price = product.get('price', 0)
            quantity = item.get('quantity', 1)
            
            item_total = price * quantity
            total_amount += item_total
            items_description.append(f"{name} x{quantity}")
        
        if total_amount <= 0:
            await query.answer("❌ Некорректная сумма заказа", show_alert=True)
            return
        
        try:
            # Создаем счет для оплаты корзины
            await query.message.reply_invoice(
                title="BY KARY - Оплата заказа",
                description=f"Заказ: {', '.join(items_description[:3])}" + ("..." if len(items_description) > 3 else ""),
                payload=f"cart_{user_id}_{len(cart_items)}",
                provider_token=PAYMENT_PROVIDER_TOKEN,
                currency="RUB",
                prices=[LabeledPrice("Заказ BY KARY", int(total_amount * 100))],  # в копейках
                start_parameter="cart_payment",
                need_name=True,
                need_phone_number=True,
                need_email=False,
                need_shipping_address=True,
                send_phone_number_to_provider=False,
                send_email_to_provider=False,
                is_flexible=False
            )
            
            await query.answer("💳 Счет создан! Заполните данные для доставки")
            
            # Возвращаем корзину обратно
            await self.show_cart_info(query)
            
        except Exception as e:
            logger.error(f"Ошибка создания счета для корзины: {e}")
            await query.answer("❌ Ошибка создания счета", show_alert=True)
    
    async def pre_checkout_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка предварительной проверки платежа"""
        query = update.pre_checkout_query
        
        # Всегда подтверждаем (в реальном приложении здесь проверки)
        await query.answer(ok=True)
    
    async def successful_payment_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка успешного платежа"""
        payment = update.message.successful_payment
        payload = payment.invoice_payload
        
        if payload.startswith("coffee_"):
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Открыть каталог", web_app=WebAppInfo(url=WEBAPP_URL))],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            await update.message.reply_text(
                "🎉 <b>Спасибо за поддержку!</b>\n\n"
                "☕ Ваш кофе оплачен! \n"
                "💕 Это вдохновляет нас создавать новые коллекции BY KARY\n\n"
                "<i>✨ Следите за новинками в нашем каталоге!</i>",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        elif payload.startswith("cart_"):
            user_id = str(update.effective_user.id)
            
            # Очищаем корзину после успешной оплаты
            await self.clear_cart(user_id)
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Открыть каталог", web_app=WebAppInfo(url=WEBAPP_URL))],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            await update.message.reply_text(
                "🎉 <b>Заказ оплачен!</b>\n\n"
                "📦 Ваш заказ принят в обработку\n"
                "📞 Мы свяжемся с вами для уточнения деталей доставки\n\n"
                f"💰 Сумма: {payment.total_amount // 100}₽\n\n"
                "🛒 <i>Корзина очищена для новых покупок</i>\n\n"
                "<i>✨ Спасибо за покупку в BY KARY!</i>",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
    
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
        
        # Обработчики платежей
        self.application.add_handler(PreCheckoutQueryHandler(self.pre_checkout_callback))
        self.application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, self.successful_payment_callback))
        
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

