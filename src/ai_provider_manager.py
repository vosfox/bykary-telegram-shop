import os
import json
import logging
import subprocess
import sys
from typing import Optional, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIProviderManager:
    """Менеджер для управления AI провайдерами с fallback системой"""
    
    def __init__(self):
        self.providers = self._init_providers()
        self.current_provider = None
        self.client = None
        self._init_primary_provider()
    
    def _init_providers(self) -> Dict[str, Dict[str, Any]]:
        """Инициализация конфигурации провайдеров"""
        return {
            'puter': {
                'enabled': os.getenv('USE_PUTER', 'true').lower() == 'true',
                'priority': 1,
                'fallback_on_error': True
            },
            'openproxy': {
                'api_key': os.getenv('OPENPROXY_API_KEY'),
                'base_url': os.getenv('OPENPROXY_BASE_URL', 'https://api.openproxy.com/v1'),
                'enabled': bool(os.getenv('OPENPROXY_API_KEY')),
                'priority': 2
            },
            'openrouter': {
                'api_key': os.getenv('OPENROUTER_API_KEY'),
                'base_url': os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'),
                'model': os.getenv('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo'),
                'enabled': bool(os.getenv('OPENROUTER_API_KEY')),
                'priority': 3
            },
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'enabled': bool(os.getenv('OPENAI_API_KEY')),
                'priority': 4
            }
        }
    
    def _init_primary_provider(self):
        """Инициализация основного провайдера по приоритету"""
        # Сортируем провайдеров по приоритету
        sorted_providers = sorted(
            [(name, config) for name, config in self.providers.items() if config.get('enabled')],
            key=lambda x: x[1].get('priority', 999)
        )
        
        logger.info(f"🔍 Доступные провайдеры: {[name for name, _ in sorted_providers]}")
        
        for provider_name, config in sorted_providers:
            logger.info(f"🔄 Пытаюсь инициализировать: {provider_name}")
            if self._try_init_provider(provider_name):
                break
        
        if not self.current_provider:
            logger.error("❌ Ни один AI провайдер не доступен!")
            logger.error(f"Проверьте переменные: USE_PUTER={os.getenv('USE_PUTER')}, OPENAI_API_KEY={'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
            raise Exception("Ни один AI провайдер не доступен!")
    
    def _try_init_provider(self, provider_name: str) -> bool:
        """Попытка инициализации конкретного провайдера"""
        try:
            config = self.providers[provider_name]
            
            if provider_name == 'puter':
                return self._init_puter()
            elif provider_name in ['openproxy', 'openrouter']:
                self.client = OpenAI(
                    api_key=config['api_key'],
                    base_url=config['base_url']
                )
            elif provider_name == 'openai':
                self.client = OpenAI(api_key=config['api_key'])
            
            self.current_provider = provider_name
            logger.info(f"✅ AI Provider активирован: {provider_name}")
            return True
            
        except Exception as e:
            logger.warning(f"❌ Не удалось инициализировать {provider_name}: {e}")
            return False
    
    def _init_puter(self) -> bool:
        """Инициализация Puter.js через Node.js"""
        try:
            # Проверяем наличие Node.js
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            self.current_provider = 'puter'
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("❌ Node.js не найден для Puter.js")
            return False
    
    def _call_puter_api(self, messages: list, model: str = "gpt-4o", **kwargs) -> str:
        """Вызов Puter.js API через Node.js скрипт"""
        try:
            # Подготавливаем данные для Node.js скрипта
            request_data = {
                'messages': messages,
                'model': model,
                'max_tokens': kwargs.get('max_tokens', 500),
                'temperature': kwargs.get('temperature', 0.7)
            }
            
            # Вызываем Node.js скрипт
            script_path = os.path.join(os.path.dirname(__file__), 'puter_client.js')
            result = subprocess.run(
                ['node', script_path, json.dumps(request_data)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                return response.get('content', 'Ошибка получения ответа')
            else:
                raise Exception(f"Puter API error: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Ошибка Puter API: {e}")
            raise
    
    def chat_completion(self, messages: list, model: str = None, **kwargs) -> str:
        """Основной метод для получения ответа от AI с fallback"""
        max_retries = 3
        last_error = None
        
        # Получаем список провайдеров для попыток (текущий + fallback)
        providers_to_try = [self.current_provider]
        
        # Добавляем fallback провайдеров если текущий поддерживает fallback
        if self.providers[self.current_provider].get('fallback_on_error'):
            other_providers = [
                name for name, config in sorted(
                    self.providers.items(),
                    key=lambda x: x[1].get('priority', 999)
                ) if name != self.current_provider and config.get('enabled')
            ]
            providers_to_try.extend(other_providers)
        
        for provider_name in providers_to_try:
            for attempt in range(max_retries if provider_name == self.current_provider else 1):
                try:
                    return self._make_request(provider_name, messages, model, **kwargs)
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"Ошибка {provider_name} (попытка {attempt + 1}): {e}")
                    
                    if attempt < max_retries - 1 and provider_name == self.current_provider:
                        continue  # Повторяем с тем же провайдером
                    else:
                        break  # Переходим к следующему провайдеру
        
        # Если все провайдеры не сработали
        raise Exception(f"Все AI провайдеры недоступны. Последняя ошибка: {last_error}")
    
    def _make_request(self, provider_name: str, messages: list, model: str = None, **kwargs) -> str:
        """Выполнение запроса к конкретному провайдеру"""
        if provider_name == 'puter':
            return self._call_puter_api(messages, model or "gpt-4o", **kwargs)
        
        # Для OpenAI-совместимых провайдеров
        if provider_name != self.current_provider:
            # Временно переключаемся на fallback провайдера
            old_client = self.client
            old_provider = self.current_provider
            
            if not self._try_init_provider(provider_name):
                raise Exception(f"Не удалось инициализировать fallback провайдер {provider_name}")
        
        try:
            # Определяем модель
            if model is None:
                if provider_name == 'openrouter':
                    model = self.providers['openrouter']['model']
                else:
                    model = "gpt-3.5-turbo"
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            
            return response.choices[0].message.content.strip()
            
        finally:
            # Восстанавливаем исходного провайдера если переключались
            if provider_name != self.current_provider:
                self.client = old_client
                self.current_provider = old_provider
    
    def get_current_provider(self) -> str:
        """Получить название текущего активного провайдера"""
        return self.current_provider
    
    def get_stylists_name(self) -> str:
        """Получить имя стилиста в зависимости от провайдера"""
        stylists = {
            'puter': 'Аня',
            'openproxy': 'Ксения', 
            'openrouter': 'Ксения',
            'openai': 'Ксения'
        }
        return stylists.get(self.current_provider, 'Ксения')
    
    def is_fallback_enabled(self) -> bool:
        """Проверить включен ли fallback для текущего провайдера"""
        return self.providers[self.current_provider].get('fallback_on_error', False)

# Глобальный экземпляр менеджера
ai_manager = AIProviderManager()