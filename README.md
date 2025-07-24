# Телеграм бот для учёта смен и зарплаты

## Как запустить

1. Создай бота в Telegram через @BotFather и получи токен.
2. Установи Python 3.8+ и зависимости:
   ```
   pip install python-telegram-bot==13.7
   ```
3. Экспортируй токен в переменную окружения:
   - Windows (cmd):
     ```
     set TELEGRAM_BOT_TOKEN=твой_токен_бота
     ```
   - Linux/macOS:
     ```
     export TELEGRAM_BOT_TOKEN=твой_токен_бота
     ```
4. Запусти бота:
   ```
   python bot.py
   ```

## Команды бота

- /start — приветствие
- /startshift — начать смену
- /endshift — закончить смену и получить расчёт
- /report — получить отчёт по всем сменам