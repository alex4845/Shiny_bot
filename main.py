
import time
import telebot
from telebot import types
import sqlite3
from datetime import date



bot = telebot.TeleBot('5921930950:AAFDGklrmWGIyrQyzywlcZKCQ2jV5DVolmw')
user_states = {}

def write_credit(credit, dat):
    conn = sqlite3.connect('MAX_bot_table.db')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS list_1
               (number INTEGER PRIMARY KEY, credit INTEGER (10), date TEXT (20), raschet TEXT (10))""")
    cursor.execute('INSERT INTO list_1 (credit, date) VALUES (?,?)',
                   (credit, dat))
    conn.commit()

def write_debet(debet, dat):
    conn = sqlite3.connect('MAX_bot_table.db')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS list_2
               (number INTEGER PRIMARY KEY, debet INTEGER (10), date TEXT (20), raschet TEXT (10))""")
    cursor.execute('INSERT INTO list_2 (debet, date) VALUES (?,?)',
                   (debet, dat))
    conn.commit()

@bot.message_handler(content_types=['text', 'photo'])
def get_text_messages(message):
    if message.text == None:
        a = str(message.caption)
    else:
        a = str(message.text)
    st, s, stt = "Р", "", "П"
    dat = date.today().strftime("%Y-%m-%d")
    if st in a:
        for el in a[a.index(st):]:
            if el.isdigit():
                s = s + el
            elif el == " " or el == "Р": continue
            else: break
        if s != "":
            credit = int(s)
            bot.send_message(message.from_user.id, "Записано в расходы")
            write_credit(credit, dat)
    elif stt in a:
        for el in a[a.index(stt):]:
            if el.isdigit():
                s = s + el
            elif el == " " or el == "П": continue
            else: break
        if s != "":
            debet = int(s)
            bot.send_message(message.from_user.id, "Продажа записана")
            write_debet(debet, dat)
    elif a == "Итого" or a == "итого":
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        key_yes = types.InlineKeyboardButton(text='По интервалу', callback_data='interval')
        key_no = types.InlineKeyboardButton(text='По расчету', callback_data='raschet')
        keyboard.add(key_yes, key_no)
        question = "Как показывать?"
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    elif a == "Расчет" or a == "расчет":
        conn = sqlite3.connect('MAX_bot_table.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO list_1 (raschet) VALUES ('расчет')")
        cursor.execute("INSERT INTO list_2 (raschet) VALUES ('расчет')")
        conn.commit()
        bot.send_message(message.from_user.id, "Расчет записан")

    chat_id = message.from_user.id
    if user_states.get(chat_id) == "interval_start":
        global date1
        date_0 = str(message.text).split('-')
        date1 = str(date_0[2]) + "-" + str(date_0[1]) + "-" + str(date_0[0])
        bot.send_message(message.from_user.id, "По какую дату? (чис-мес-год)")
        bot.register_next_step_handler(message, get_date2)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    chat_id = call.from_user.id
    if call.data == "interval":
        user_states[chat_id] = "interval_start"
        bot.send_message(chat_id, "С какой даты? (чис-мес-год)")

    elif call.data == "raschet":
        conn = sqlite3.connect('MAX_bot_table.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT SUM(debet) FROM list_2 WHERE number >= (SELECT MAX(number) FROM list_2 WHERE raschet IS NOT NULL)")
        res = str(cursor.fetchall())
        doh = res[2:-3]
        cursor.execute(
            "SELECT SUM(credit) FROM list_1 WHERE number >= (SELECT MAX(number) FROM list_1 WHERE raschet IS NOT NULL)")
        res1 = str(cursor.fetchall())
        ras = res1[2:-3]
        bot.send_message(call.message.chat.id, f'Сумма продаж с последнего расчета:  {doh} руб')
        bot.send_message(call.message.chat.id, f'Сумма расходов с последнего расчета:  {ras} руб')
        res2 = int(doh) - int(ras)
        bot.send_message(call.message.chat.id, f'Прибыль: {res2} руб')

def get_date2(message):
    global date2
    date_0 = str(message.text).split('-')
    date2 = str(date_0[2]) + "-" + str(date_0[1]) + "-" + str(date_0[0])
    conn = sqlite3.connect('MAX_bot_table.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(credit) FROM list_1 WHERE date>=? AND date<=?", [(date1), (date2)])
    res = str(cursor.fetchall())
    ras = res[2:-3]
    cursor.execute("SELECT SUM(debet) FROM list_2 WHERE date>=? AND date<=?", [(date1), (date2)])
    res1 = str(cursor.fetchall())
    doh = res1[2:-3]
    bot.send_message(message.from_user.id, f'Всего продаж на сумму:  {doh} руб')
    bot.send_message(message.from_user.id, f'Всего расходов:  {ras} руб')
    res2 = int(doh) - int(ras)
    bot.send_message(message.from_user.id, f'Прибыль:  {res2} руб')
    user_states[message.from_user.id] = ""


bot.polling(none_stop=True, interval=0)