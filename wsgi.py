#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI файл для запуска на хостинге
"""
import os
import sys
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app

# Это нужно для большинства хостингов
application = app

if __name__ == "__main__":
    app.run()