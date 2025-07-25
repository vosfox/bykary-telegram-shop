#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI файл для Railway
"""
import os
import sys
from dotenv import load_dotenv

# Загружаем переменные из переменных окружения Railway
load_dotenv()

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app

# Railway ожидает переменную application
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)