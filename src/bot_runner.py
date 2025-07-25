import os
import sys
import threading
import time
from multiprocessing import Process
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Устанавливаем кодировку для Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def run_flask_app():
    """Запуск Flask приложения"""
    from src.main import app
    app.run(host='0.0.0.0', port=5000, debug=False)

def run_telegram_bot():
    """Запуск Telegram бота"""
    # Ждем немного, чтобы Flask успел запуститься
    time.sleep(3)
    
    from src.telegram_bot import ByKaryBot
    bot = ByKaryBot()
    bot.run()

def main():
    """Главная функция для запуска обоих сервисов"""
    print("Запуск демо-магазина ByKary.ru...")
    
    # Проверяем переменные окружения
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token or bot_token == 'your_bot_token_here':
        print("⚠️  BOT_TOKEN не установлен!")
        print("Установите переменную окружения BOT_TOKEN с токеном вашего бота")
        print("Пример: export BOT_TOKEN='your_bot_token_here'")
        return
    
    # Проверяем AI провайдеры
    openproxy_key = os.getenv('OPENPROXY_API_KEY')
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if openproxy_key:
        print("✅ AI Provider: OpenProxy")
    elif openrouter_key:
        print("✅ AI Provider: OpenRouter")
    elif openai_key:
        print("✅ AI Provider: OpenAI")
    else:
        print("❌ AI Provider: НЕ НАСТРОЕН!")
        print("Раскомментируйте один из провайдеров в .env файле")
        return
    
    try:
        # Запускаем Flask в отдельном процессе
        flask_process = Process(target=run_flask_app)
        flask_process.start()
        
        print("✅ Flask сервер запущен на http://0.0.0.0:5000")
        
        # Запускаем Telegram бота в основном процессе
        print("🤖 Запуск Telegram бота...")
        run_telegram_bot()
        
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервисов...")
        flask_process.terminate()
        flask_process.join()
        print("✅ Сервисы остановлены")

if __name__ == '__main__':
    main()

