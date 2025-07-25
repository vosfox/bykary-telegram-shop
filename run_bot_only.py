#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск только Telegram бота (без Flask)
Для использования когда Flask уже развернут на хостинге
"""
import os
import sys
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from src.telegram_bot import ByKaryBot

if __name__ == "__main__":
    print("🤖 Запуск Telegram бота (только бот)...")
    bot = ByKaryBot()
    bot.run()