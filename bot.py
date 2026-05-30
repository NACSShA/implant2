import telebot
import sqlite3
import random
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8802894093:AAEOUqe9KyQr--Y06MZouvAMv5lReqbLBB8"
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

EPOCH_START = datetime(2026, 5, 29)

def get_imperial_date(real_date):
    days_passed = (real_date - EPOCH_START).days
    year = 10548
    day = 1
    while days_passed > 0:
        days_in_year = 3 if year % 8 == 0 else 4
        if days_passed >= days_in_year:
            days_passed -= days_in_year
            year += 1
        else:
            day = days_passed + 1
            break
    return year, day

def get_generation_letter():
    days_since_epoch = (datetime.now() - EPOCH_START).days
    generation_index = days_since_epoch // 190
    return chr(ord('A') + generation_index)

def format_imperial_date(year, day):
    return f"{day} день {year} Имперского года"

conn = sqlite3.connect('imperia.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY,
        code TEXT UNIQUE,
        name TEXT,
        gender TEXT,
        registered_at TEXT,
        imperial_year INTEGER
    )
''')
conn.commit()

def generate_code():
    current_gen = get_generation_letter()
    cursor.execute('SELECT COUNT(*) FROM players WHERE code LIKE ?', (f"{current_gen}%",))
    count_in_gen = cursor.fetchone()[0]
    return f"{current_gen}{count_in_gen + 1}"

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
    if cursor.fetchone():
        bot.reply_to(message, "<pre>Вы уже зарегистрированы. Используйте /me</pre>")
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("М", callback_data="male"),
        InlineKeyboardButton("Ж", callback_data="female")
    )
    
    bot.send_message(
        message.chat.id,
        "<pre>⭐ Добро пожаловать в зону заботы Империи!\n\nЧтобы продолжить, требуется зарегистрироваться. Укажите свой пол с помощью инлайн-кнопок.</pre>",
        reply_markup=markup
    )

male_names = ["Айрон", "Блейз", "Вант", "Вектор", "Вольф", "Грейв", "Грим", "Дарроу", "Дрейк", "Зейн", "Корд", "Кроу", "Марк", "Морроу", "Нокс", "Рейз", "Роан", "Сейдж", "Солан", "Спарк", "Стикс", "Стоун", "Трэвис", "Уэйд", "Фенн", "Хейл", "Хьюго", "Шейд", "Эш", "Юджин"]
female_names = ["Астра", "Бри", "Векса", "Вера", "Грета", "Джин", "Зара", "Зоя", "Иви", "Ида", "Клара", "Лин", "Лорна", "Люкс", "Ника", "Нова", "Рен", "Риган", "Роан", "Скарлет", "Сигур", "Сэйдж", "Тесса", "Фара", "Хейз", "Шивон", "Эмбер", "Эра", "Юна", "Яра"]

@bot.callback_query_handler(func=lambda call: call.data in ['male', 'female'])
def handle_gender(call):
    user_id = call.from_user.id
    gender = call.data
    
    name = random.choice(male_names if gender == 'male' else female_names)
    code = generate_code()
    registered_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    imperial_year, _ = get_imperial_date(datetime.now())
    
    cursor.execute('''
        INSERT INTO players (user_id, code, name, gender, registered_at, imperial_year)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, code, name, gender, registered_at, imperial_year))
    conn.commit()
    
    gender_text = "Мужской" if gender == 'male' else "Женский"
    
    bot.edit_message_text(
        f"<pre>Базовая регистрация завершена!\n\nВАШИ ДАННЫЕ\nИмя: {name}\nПол: {gender_text}\nКод: {code}\nГод регистрации: {imperial_year}</pre>",
        call.message.chat.id,
        call.message.message_id
    )

@bot.message_handler(commands=['me'])
def show_profile(message):
    user_id = message.from_user.id
    cursor.execute('SELECT code, name, gender, imperial_year FROM players WHERE user_id = ?', (user_id,))
    player = cursor.fetchone()
    if not player:
        bot.reply_to(message, "<pre>Вы не зарегистрированы. Напишите /start</pre>")
        return
    
    code, name, gender, year = player
    gender_text = "Мужской" if gender == 'male' else "Женский"
    
    bot.reply_to(
        message,
        f"<pre>ВАШ ПРОФИЛЬ\n\nИмя: {name}\nПол: {gender_text}\nКод: {code}\nГод регистрации: {year}</pre>"
    )

@bot.message_handler(commands=['time'])
def show_time(message):
    now = datetime.now()
    year, day = get_imperial_date(now)
    generation = get_generation_letter()
    imperial_str = format_imperial_date(year, day)
    
    bot.reply_to(
        message,
        f"<pre>Дата: {now.strftime('%d.%m.%Y')}\nИмперская дата: {imperial_str}\nПоколение: {generation}</pre>"
    )

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()

# ========== ГЕНЕРАТОР КОДА ==========
def generate_code():
    current_gen = get_generation_letter()
    cursor.execute('SELECT COUNT(*) FROM players WHERE code LIKE ?', (f"{current_gen}%",))
    count_in_gen = cursor.fetchone()[0]
    return f"{current_gen}{count_in_gen + 1}"

# ========== КОМАНДА /START ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
    if cursor.fetchone():
        bot.reply_to(message, "<pre>Вы уже зарегистрированы. Используйте /me</pre>")
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("М", callback_data="male"),
        InlineKeyboardButton("Ж", callback_data="female")
    )
    
    bot.send_message(
        message.chat.id,
        "<pre>⭐ Добро пожаловать в зону заботы Империи!\n\nЧтобы продолжить, требуется зарегистрироваться. Укажите свой пол с помощью инлайн-кнопок.</pre>",
        reply_markup=markup
    )

# ========== ОБРАБОТЧИК ВЫБОРА ПОЛА ==========
male_names = ["Айрон", "Блейз", "Вант", "Вектор", "Вольф", "Грейв", "Грим", "Дарроу", "Дрейк", "Зейн", "Корд", "Кроу", "Марк", "Морроу", "Нокс", "Рейз", "Роан", "Сейдж", "Солан", "Спарк", "Стикс", "Стоун", "Трэвис", "Уэйд", "Фенн", "Хейл", "Хьюго", "Шейд", "Эш", "Юджин"]
female_names = ["Астра", "Бри", "Векса", "Вера", "Грета", "Джин", "Зара", "Зоя", "Иви", "Ида", "Клара", "Лин", "Лорна", "Люкс", "Ника", "Нова", "Рен", "Риган", "Роан", "Скарлет", "Сигур", "Сэйдж", "Тесса", "Фара", "Хейз", "Шивон", "Эмбер", "Эра", "Юна", "Яра"]

@bot.callback_query_handler(func=lambda call: call.data in ['male', 'female'])
def handle_gender(call):
    user_id = call.from_user.id
    gender = call.data
    
    name = random.choice(male_names if gender == 'male' else female_names)
    code = generate_code()
    registered_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    imperial_year, _ = get_imperial_date(datetime.now())
    
    cursor.execute('''
        INSERT INTO players (user_id, code, name, gender, registered_at, imperial_year)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, code, name, gender, registered_at, imperial_year))
    conn.commit()
    
    gender_text = "Мужской" if gender == 'male' else "Женский"
    
    bot.edit_message_text(
        f"<pre>Базовая регистрация завершена!\n\nВАШИ ДАННЫЕ\nИмя: {name}\nПол: {gender_text}\nКод: {code}\nГод регистрации: {imperial_year}</pre>",
        call.message.chat.id,
        call.message.message_id
    )

# ========== КОМАНДА /ME ==========
@bot.message_handler(commands=['me'])
def show_profile(message):
    user_id = message.from_user.id
    cursor.execute('SELECT code, name, gender, imperial_year FROM players WHERE user_id = ?', (user_id,))
    player = cursor.fetchone()
    if not player:
        bot.reply_to(message, "<pre>Вы не зарегистрированы. Напишите /start</pre>")
        return
    
    code, name, gender, year = player
    gender_text = "Мужской" if gender == 'male' else "Женский"
    
    bot.reply_to(
        message,
        f"<pre>ВАШ ПРОФИЛЬ\n\nИмя: {name}\nПол: {gender_text}\nКод: {code}\nГод регистрации: {year}</pre>"
    )

# ========== КОМАНДА /TIME ==========
@bot.message_handler(commands=['time'])
def show_time(message):
    now = datetime.now()
    year, day = get_imperial_date(now)
    generation = get_generation_letter()
    imperial_str = format_imperial_date(year, day)
    
    bot.reply_to(
        message,
        f"<pre>Дата: {now.strftime('%d.%m.%Y')}\nИмперская дата: {imperial_str}\nПоколение: {generation}</pre>"
    )

# ========== ЗАПУСК БОТА ==========
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()