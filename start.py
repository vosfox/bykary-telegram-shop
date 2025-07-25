#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой запуск для Railway
"""
import os
from dotenv import load_dotenv

# Загружаем переменные из переменных окружения Railway
load_dotenv()

from src.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)