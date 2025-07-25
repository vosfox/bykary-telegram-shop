# Демо-магазин одежды ByKary.ru в Telegram

Telegram-бот с мини-приложением (WebApp) для демонстрации интернет-магазина женской одежды бренда ByKary.ru.

## Функционал

### 🛒 Каталог товаров (WebApp)
- Просмотр товаров с фотографиями, названиями и ценами
- Навигация по категориям (Новинки, Платья, Юбки, Костюмы, Аксессуары)
- Выбор размера (XS, S, M, L)
- Добавление товаров в корзину

### 🧺 Корзина и заказы
- Просмотр добавленных товаров
- Изменение количества и размера
- Удаление товаров из корзины
- Оформление заказа с формой (имя, телефон, город, комментарий)

### 🤖 AI-ассистент
- Ответы на вопросы о товарах, размерах, доставке
- Интеграция с OpenAI API
- Fallback ответы при недоступности AI

### 📱 Telegram-бот
- Главное меню с кнопками
- Команды: /start, /help, /catalog
- Интеграция с WebApp
- Обработка данных от мини-приложения

## Технологии

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript, Telegram WebApp API
- **AI**: OpenAI API (GPT-3.5-turbo)
- **База данных**: SQLite
- **Telegram**: python-telegram-bot

## Установка и запуск

### 1. Клонирование и установка зависимостей

```bash
cd bykary_telegram_shop
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
```

Отредактируйте `.env`:
```
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
WEBAPP_URL=https://your-deployed-app-url.com
```

### 3. Инициализация данных

```bash
python src/init_data.py
```

### 4. Запуск приложения

#### Локальный запуск (для разработки):

```bash
# Запуск Flask сервера
python src/main.py

# В другом терминале - запуск бота
python src/telegram_bot.py
```

#### Запуск всех сервисов одной командой:

```bash
python src/bot_runner.py
```

## Создание Telegram бота

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте `/newbot`
3. Выберите имя и username для бота
4. Получите токен и добавьте в `.env`
5. Настройте WebApp через BotFather:
   - `/setmenubutton`
   - Выберите вашего бота
   - Введите текст кнопки: "Каталог"
   - Введите URL WebApp

## Структура проекта

```
bykary_telegram_shop/
├── src/
│   ├── models/          # Модели базы данных
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   └── order.py
│   ├── routes/          # API маршруты
│   │   ├── products.py
│   │   ├── cart.py
│   │   └── orders.py
│   ├── static/          # WebApp файлы
│   │   ├── index.html
│   │   ├── styles.css
│   │   ├── app.js
│   │   └── images/
│   ├── database/        # База данных
│   │   └── app.db
│   ├── main.py          # Flask приложение
│   ├── telegram_bot.py  # Telegram бот
│   ├── bot_runner.py    # Запуск всех сервисов
│   └── init_data.py     # Инициализация данных
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

- `GET /api/products` - Получить все товары
- `GET /api/products?category=<category>` - Товары по категории
- `GET /api/cart/<user_id>` - Корзина пользователя
- `POST /api/cart` - Добавить в корзину
- `PUT /api/cart/<item_id>` - Обновить товар в корзине
- `DELETE /api/cart/<item_id>` - Удалить из корзины
- `POST /api/orders` - Создать заказ

## Товары в каталоге

1. Футболка с монограммой черная - 5900₽
2. Футболка с монограммой белая - 5900₽
3. Костюм-полоска Аладдин rosy - 15900₽
4. Костюм-полоска Аладдин blue - 15900₽
5. Футболка-платье Mama needs champagne розовая - 6900₽
6. Футболка-платье Mama needs champagne бежевая - 6900₽
7. Футболка-поло в полоску - 6900₽
8. Джинсовая куртка-косуха молочная - 12900₽

## Развертывание

Для развертывания на хостинге:

1. Обновите `WEBAPP_URL` в `.env`
2. Настройте webhook для бота (опционально)
3. Убедитесь, что все зависимости установлены
4. Запустите `python src/bot_runner.py`

## Примечания

- Это демо-версия для демонстрации возможностей
- Все заказы носят демонстрационный характер
- Для реальных покупок пользователи направляются на bykary.ru
- AI-ассистент работает с fallback ответами при отсутствии OpenAI API

## Лицензия

Демонстрационный проект для бренда ByKary.ru

