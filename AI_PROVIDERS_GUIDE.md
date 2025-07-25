# 🤖 Руководство по настройке AI провайдеров

## Система переключения провайдеров

Проект поддерживает 3 AI провайдера с простой системой переключения через комментирование в `.env` файле.

### Приоритет провайдеров:
1. **OpenProxy** (наивысший приоритет)
2. **OpenRouter** 
3. **OpenAI**

### 🔧 Как переключать провайдеры

В файле `.env` раскомментируйте **СТРОГО ОДИН** провайдер:

#### Вариант 1: Использовать OpenProxy
```env
# Option 1: OpenProxy
OPENPROXY_API_KEY=your_openproxy_api_key_here
OPENPROXY_BASE_URL=https://api.openproxy.com/v1

# Option 2: OpenRouter  
#OPENROUTER_API_KEY=your_openrouter_api_key_here
#OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Option 3: OpenAI
#OPENAI_API_KEY=your_openai_api_key_here
```

#### Вариант 2: Использовать OpenRouter
```env
# Option 1: OpenProxy
#OPENPROXY_API_KEY=your_openproxy_api_key_here
#OPENPROXY_BASE_URL=https://api.openproxy.com/v1

# Option 2: OpenRouter  
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Option 3: OpenAI
#OPENAI_API_KEY=your_openai_api_key_here
```

#### Вариант 3: Использовать OpenAI
```env
# Option 1: OpenProxy
#OPENPROXY_API_KEY=your_openproxy_api_key_here
#OPENPROXY_BASE_URL=https://api.openproxy.com/v1

# Option 2: OpenRouter  
#OPENROUTER_API_KEY=your_openrouter_api_key_here
#OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Option 3: OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

### 📋 Индикаторы в сообщениях

Бот показывает, какой провайдер используется:

- `💬 [OpenProxy] Ответ...` - используется OpenProxy
- `💬 [OpenRouter] Ответ...` - используется OpenRouter  
- `💬 [OpenAI] Ответ...` - используется OpenAI

### 🚀 При запуске

При запуске `python src/bot_runner.py` вы увидите:

```
Запуск демо-магазина ByKary.ru...
✅ AI Provider: OpenRouter
✅ Flask сервер запущен на http://0.0.0.0:5000
🤖 Запуск Telegram бота...
```

Если ни один провайдер не настроен:
```
❌ AI Provider: НЕ НАСТРОЕН!
Раскомментируйте один из провайдеров в .env файле
```

### 🛠 Модели по провайдерам

- **OpenProxy**: `gpt-3.5-turbo`
- **OpenRouter**: `openai/gpt-3.5-turbo` 
- **OpenAI**: `gpt-3.5-turbo`

### ⚠️ Важно

1. Раскомментируйте **СТРОГО ОДИН** провайдер
2. Убедитесь, что API ключ действительный  
3. Если ни один провайдер не настроен - приложение не запустится
4. При ошибках AI показывается сообщение об ошибке