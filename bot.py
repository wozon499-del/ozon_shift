import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

RATE_PER_HOUR = 141
shifts = {}      # user_id -> {'start': datetime, 'end': datetime or None, 'object': str}
employees = {}

SELECT_OBJECT = 0

OBJECTS = ['новогодняя', 'ватутина', 'серафимовича', 'станиславского']

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'Привет! Используй команды:\n'
        '/register — зарегистрироваться\n'
        '/startshift — начать смену\n'
        '/endshift — закончить смену\n'
        '/report — отчёт'
    )

def register(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in employees:
        update.message.reply_text('Ты уже зарегистрирован.')
        return
    name = update.message.from_user.full_name or update.message.from_user.username or "Без имени"
    employees[user_id] = name
    update.message.reply_text(f'Регистрация прошла успешно, {name}!')

def start_shift(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    if user_id not in employees:
        update.message.reply_text('Сначала зарегистрируйся командой /register')
        return ConversationHandler.END
    if user_id in shifts and 'start' in shifts[user_id] and shifts[user_id]['end'] is None:
        update.message.reply_text('Смена уже начата. Отправь /endshift, чтобы её закончить.')
        return ConversationHandler.END

    keyboard = [[obj] for obj in OBJECTS]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Выбери объект для смены:', reply_markup=reply_markup)
    return SELECT_OBJECT

def select_object(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    obj = update.message.text.strip().lower()
    if obj not in OBJECTS:
        update.message.reply_text('Пожалуйста, выбери объект из списка, используя кнопки.')
        return SELECT_OBJECT
    shifts[user_id] = {'start': update.message.date, 'end': None, 'object': obj}
    update.message.reply_text(f'Смена начата на объекте "{obj}".', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def end_shift(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in employees:
        update.message.reply_text('Сначала зарегистрируйся командой /register')
        return
    if user_id not in shifts or 'start' not in shifts[user_id] or shifts[user_id]['end'] is not None:
        update.message.reply_text('Ты ещё не начал смену. Отправь /startshift для начала.')
        return
    shifts[user_id]['end'] = update.message.date
    start_time = shifts[user_id]['start']
    end_time = shifts[user_id]['end']
    delta = end_time - start_time
    hours = delta.total_seconds() / 3600
    pay = round(hours * RATE_PER_HOUR, 2)
    obj = shifts[user_id].get('object', 'Не указан')
    update.message.reply_text(
        f'Смена на объекте "{obj}" закончена.\n'
        f'Продолжительность: {hours:.2f} часов.\n'
        f'Зарплата: {pay}₽'
    )

def report(update: Update, context: CallbackContext) -> None:
    if not shifts:
        update.message.reply_text('Нет данных о сменах.')
        return
    report_lines = []
    for user_id, times in shifts.items():
        if (
            user_id in employees
            and 'start' in times
            and 'end' in times
            and times['end'] is not None
        ):
            hours = (times['end'] - times['start']).total_seconds() / 3600
            pay = round(hours * RATE_PER_HOUR, 2)
            name = employees.get(user_id, 'Unknown')
            obj = times.get('object', 'Не указан')
            report_lines.append(f'{name} ({obj}): {hours:.2f} ч, зарплата {pay}₽')
    if not report_lines:
        update.message.reply_text('Нет завершённых смен для отчёта.')
        return
    update.message.reply_text('\n'.join(report_lines))

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Действие отменено.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    TOKEN = "8117669546:AAEY-L7XEfsMK0aJL96t31eyxZznZMHKUD4"

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('startshift', start_shift)],
        states={
            SELECT_OBJECT: [MessageHandler(Filters.text & ~Filters.command, select_object)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("endshift", end_shift))
    dispatcher.add_handler(CommandHandler("report", report))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
