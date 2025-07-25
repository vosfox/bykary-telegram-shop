# 🚂 Деплой на Railway (РЕКОМЕНДУЕТСЯ)

Railway - бесплатная платформа для Python приложений.

## 🎯 Пошаговая инструкция:

### 1. Подготовка
1. Зарегистрируйтесь на https://railway.app
2. Подключите GitHub аккаунт

### 2. Создание репозитория
1. Создайте репозиторий на GitHub
2. Загрузите туда папку проекта

### 3. Деплой
1. В Railway нажмите "New Project"
2. Выберите "Deploy from GitHub repo"
3. Выберите ваш репозиторий
4. Railway автоматически определит Python проект

### 4. Настройка переменных окружения
В разделе Variables добавьте:
```
BOT_TOKEN=8327372098:AAFA2Z4zvhGA11qQv9D4SH46HstUv-H3MhY
OPENROUTER_API_KEY=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
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
WEBAPP_URL=https://yourdomain.railway.app
SECRET_KEY=5nd7CzR3jC_uef0qg4aQ7TU3kZ5kGZTxb-0N7canUrw
```

### 5. Получение URL
Railway даст вам URL типа: `https://bykary-production.up.railway.app`

### 6. Настройка домена (опционально)
В Railway можно подключить ваш домен chika-food.ru

### 7. Запуск бота
Railway автоматически запустит и Flask и бота по Procfile

## ✅ Преимущества Railway:
- ✅ Бесплатно до 500 часов в месяц
- ✅ Автоматический деплой
- ✅ Поддержка Python из коробки
- ✅ Автоматические SSL сертификаты
- ✅ Можно подключить свой домен