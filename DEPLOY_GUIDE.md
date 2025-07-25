# 📦 Инструкция по деплою на хостинг

## 🎯 Что подготовлено для деплоя:

- ✅ `wsgi.py` - точка входа для Flask
- ✅ `run_bot_only.py` - запуск только бота
- ✅ `Procfile` - для автоматического деплоя
- ✅ `requirements.txt` - обновлен с gunicorn и python-dotenv

## 🚀 Шаги деплоя:

### 1. Настройте .env на сервере
```env
# Telegram Bot Configuration
BOT_TOKEN=8327372098:AAFA2Z4zvhGA11qQv9D4SH46HstUv-H3MhY

# AI Provider Configuration
OPENROUTER_API_KEY=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
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# WebApp URL - ЗАМЕНИТЕ НА ВАШ ДОМЕН!
WEBAPP_URL=https://yourdomain.com

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=5nd7CzR3jC_uef0qg4aQ7TU3kZ5kGZTxb-0N7canUrw
```

### 2. Загрузите файлы на хостинг
Скопируйте всю папку проекта на сервер.

### 3. Установите зависимости
```bash
pip install -r requirements.txt
```

### 4. Инициализируйте базу данных
```bash
python src/init_data.py
```

### 5. Варианты запуска:

#### A) Только Flask (WebApp):
```bash
gunicorn wsgi:application --bind 0.0.0.0:8000
```

#### B) Только бот:
```bash
python run_bot_only.py
```

#### C) Оба сервиса:
```bash
python src/bot_runner.py
```

## 🌐 Популярные хостинги:

### Railway / Render:
1. Подключите GitHub репозиторий
2. Установите переменные окружения в панели
3. Деплой произойдет автоматически

### Heroku:
```bash
heroku create your-app-name
heroku config:set BOT_TOKEN=your_token
heroku config:set OPENROUTER_API_KEY=your_key
heroku config:set WEBAPP_URL=https://your-app-name.herokuapp.com
git push heroku main
```

### VPS (Ubuntu):
```bash
# Установка
sudo apt update
sudo apt install python3 python3-pip nginx
pip3 install -r requirements.txt

# Запуск с systemd
sudo systemctl enable your-bot.service
sudo systemctl start your-bot.service
```

## ⚠️ Важные моменты:

1. **WEBAPP_URL** должен быть HTTPS (обязательно для Telegram WebApp)
2. **Telegram бот** нужно настроить в @BotFather:
   - `/setmenubutton` - добавить кнопку "Каталог"
   - URL: `https://yourdomain.com`
3. **База данных** инициализируется автоматически при первом запуске
4. **AI провайдер** можно переключать в .env файле

## 🔧 Тестирование после деплоя:

1. Откройте `https://yourdomain.com` - должен показаться каталог
2. В Telegram найдите вашего бота - должно работать меню
3. Нажмите "Каталог" - должен открыться WebApp
4. Напишите боту сообщение - должен ответить AI

## 📱 Настройка BotFather:

После деплоя выполните в @BotFather:
```
/setmenubutton
@your_bot_name
Каталог
https://yourdomain.com
```