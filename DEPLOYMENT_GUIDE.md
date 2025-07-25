# Руководство по развертыванию демо-магазина ByKary.ru

## 🚀 Быстрый старт

Ваш демо-магазин уже развернут и доступен по адресу:
**https://zmhqivcvj15p.manus.space**

## 📱 Настройка Telegram бота

### 1. Создание бота

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Введите имя бота: `ByKary Demo Shop`
4. Введите username: `bykary_demo_shop_bot` (или любой доступный)
5. Получите токен бота и сохраните его

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here

# OpenAI Configuration (опционально)
OPENAI_API_KEY=your_openai_api_key_here

# WebApp URL
WEBAPP_URL=https://zmhqivcvj15p.manus.space

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
```

### 3. Настройка WebApp в BotFather

1. Отправьте `/setmenubutton` в [@BotFather](https://t.me/botfather)
2. Выберите вашего бота
3. Введите текст кнопки: `🛒 Каталог`
4. Введите URL: `https://zmhqivcvj15p.manus.space`

### 4. Настройка команд бота

Отправьте `/setcommands` в [@BotFather](https://t.me/botfather) и добавьте:

```
start - Главное меню
help - Справка
catalog - Открыть каталог
```

## 🛠️ Локальный запуск

### Установка зависимостей

```bash
cd bykary_telegram_shop
source venv/bin/activate
pip install -r requirements.txt
```

### Инициализация данных

```bash
python src/init_data.py
```

### Запуск приложения

```bash
# Запуск всех сервисов
python src/bot_runner.py

# Или раздельно:
# Flask сервер
python src/main.py

# Telegram бот (в другом терминале)
python src/telegram_bot.py
```

## 🌐 Развертывание на хостинге

### Heroku

1. Создайте приложение на Heroku
2. Добавьте переменные окружения в настройках
3. Подключите GitHub репозиторий
4. Разверните приложение

### VPS/Dedicated Server

1. Установите Python 3.11+
2. Клонируйте репозиторий
3. Установите зависимости
4. Настройте systemd сервисы
5. Настройте nginx (опционально)

## 🔧 Конфигурация

### Добавление товаров

Отредактируйте файл `src/init_data.py` и добавьте новые товары:

```python
products = [
    {
        'name': 'Новый товар',
        'price': 7900,
        'category': 'Платья',
        'sizes': ['XS', 'S', 'M', 'L'],
        'image_url': 'https://example.com/image.jpg'
    }
]
```

### Настройка AI-ассистента

В файле `src/telegram_bot.py` отредактируйте `system_prompt` для изменения поведения AI:

```python
system_prompt = """
Ты - AI-ассистент интернет-магазина женской одежды By Kary.
[Ваши настройки...]
"""
```

## 📊 Мониторинг

### Логи

Логи приложения сохраняются в консоль. Для продакшена настройте:

```python
import logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### База данных

SQLite база данных находится в `src/database/app.db`. Для продакшена рекомендуется PostgreSQL.

## 🔒 Безопасность

1. **Никогда не коммитьте токены** в Git
2. Используйте переменные окружения
3. Настройте HTTPS для WebApp
4. Ограничьте доступ к базе данных
5. Регулярно обновляйте зависимости

## 🐛 Устранение неполадок

### Бот не отвечает

1. Проверьте токен бота
2. Убедитесь, что сервер запущен
3. Проверьте логи на ошибки

### WebApp не загружается

1. Проверьте URL в настройках бота
2. Убедитесь, что Flask сервер доступен
3. Проверьте CORS настройки

### AI-ассистент не работает

1. Проверьте OPENAI_API_KEY
2. Убедитесь в наличии средств на аккаунте OpenAI
3. Проверьте лимиты API

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи приложения
2. Убедитесь в правильности конфигурации
3. Проверьте статус внешних сервисов (Telegram API, OpenAI API)

## 📝 Лицензия

Демонстрационный проект для бренда ByKary.ru

