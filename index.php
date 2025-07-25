<?php
// Редирект на Python приложение
// Поскольку на shared хостинге Python может быть ограничен,
// создаем простую заглушку с информацией
?>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ByKary Demo Shop</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
        .container { max-width: 600px; margin: 0 auto; }
        .error { color: #e74c3c; margin: 20px 0; }
        .info { color: #2c3e50; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛒 ByKary Demo Shop</h1>
        <div class="error">
            <h3>⚠️ Python приложение требует настройки</h3>
            <p>Этот проект создан на Python Flask и требует:</p>
            <ul style="text-align: left;">
                <li>Поддержку Python 3.11+ на хостинге</li>
                <li>Возможность запуска Flask приложений</li>
                <li>Установку зависимостей из requirements.txt</li>
            </ul>
        </div>
        
        <div class="info">
            <h3>📞 Что делать:</h3>
            <p>1. Свяжитесь с поддержкой REG.RU</p>
            <p>2. Уточните поддержку Python Flask</p>
            <p>3. Или рассмотрите VPS хостинг</p>
        </div>
        
        <div class="info">
            <h3>🚀 Альтернатива - бесплатные PaaS:</h3>
            <p><a href="https://railway.app">Railway</a> | <a href="https://render.com">Render</a> | <a href="https://vercel.com">Vercel</a></p>
        </div>
    </div>
</body>
</html>