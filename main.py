import datetime
import telebot
from telebot import types
import sqlite3
from datetime import date

bot = telebot.TeleBot('5921930950:AAFDGklrmWGIyrQyzywlcZKCQ2jV5DVolmw')

def write_credit(credit, dat):
    conn = sqlite3.connect('MAX_bot_table.db')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS list_1
               (number INTEGER PRIMARY KEY, credit INTEGER (10), date TEXT (20))""")
    cursor.execute('INSERT INTO list_1 (credit, date) VALUES (?,?)',
                   (credit, dat))
    conn.commit()
    cursor.execute("SELECT * FROM list_1")
    res = list(cursor.fetchall())
    print("Добавлено в расход", res[-1])


def write_debet(debet, dat):
    conn = sqlite3.connect('MAX_bot_table.db')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS list_2
               (number INTEGER PRIMARY KEY, debet INTEGER (10), date TEXT (20))""")
    cursor.execute('INSERT INTO list_2 (debet, date) VALUES (?,?)',
                   (debet, dat))
    conn.commit()
    cursor.execute("SELECT * FROM list_2")
    res = list(cursor.fetchall())
    print("Добавлено в доход", res[-1])

@bot.message_handler(content_types=['text', 'photo'])
def get_text_messages(message):
    if message.text == None:
        a = str(message.caption)
    else:
        a = str(message.text)
    st, s, stt = "Р", "", "П"
    dat = date.today().strftime("%d-%m-%Y")
    if st in a:
        for el in a[a.index(st):]:
            if el.isdigit():
                s = s + el
            elif el == " " or el == "Р": continue
            else: break
        if s != "":
            credit = int(s)
            write_credit(credit, dat)
    elif stt in a:
        for el in a[a.index(stt):]:
            if el.isdigit():
                s = s + el
            elif el == " " or el == "П": continue
            else: break
        if s != "":
            debet = int(s)
            write_debet(debet, dat)
    elif a == "Итого" or a == "итого":
        bot.send_message(message.from_user.id, "С какой даты? (чис-мес-год)")
        bot.register_next_step_handler(message, get_date1)

def get_date1(message):
    global date1
    date1 = str(message.text)
    bot.send_message(message.from_user.id, "По какую дату? (чис-мес-год)")
    bot.register_next_step_handler(message, get_date2)

def get_date2(message):
    global date2
    date2 = str(message.text)
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

bot.polling(none_stop=True, interval=0)