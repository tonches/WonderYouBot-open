import telebot
import config
import hardsql
import dbworker
import logging
import time
import json
import os.path
import hashlib
import requests
from pathlib import Path
import sys

bot = telebot.TeleBot(config.token)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def isstas(groupid):
    if groupid == -1001156429380:
        return True
    else:
        return False


def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None

# Начало диалога
@bot.message_handler(commands=["start"])
def cmd_start(message):
    if message.text != '/start':
        unique_code = extract_unique_code(message.text)
    else:
        unique_code = extract_unique_code("/start none")

    if hashlib.md5(unique_code.encode()).hexdigest() == '6050ce63e4bce6764cb34cac51fb44d1':
        state = dbworker.get_current_state(message.from_user.id)
        logger.warning('Command from:  "%s"', message.from_user.id)
        logger.warning('Command from chat:  "%s"', message.chat.id)
        logger.warning('Name of chat:  "%s"', message.chat.title)
        statuses = ['creator', 'administrator', 'member']
        status = bot.get_chat_member(message.chat.id, message.from_user.id).status
        if any(st == status for st in statuses):
            bot.send_message(message.chat.id, "Подписка подтверждена!")
        else:
            bot.send_message(message.chat.id, "Кажется вы не подписались!")
        

        if state == config.States.S_ENTER_NAME.value:
            bot.send_message(message.chat.id, "Кажется, кто-то обещал отправить своё имя, но так и не сделал этого :( Жду...")
        elif state == config.States.S_ENTER_EGO.value:
            bot.send_message(message.chat.id, "Кажется, кто-то обещал отправить свой псевдоним, но так и не сделал этого :( Жду...")
        elif state == config.States.S_SEND_EMO.value:
            bot.send_message(message.chat.id, "Кажется, кто-то обещал отправить свой эмодзи, но так и не сделал этого :( Жду...")
        else:  # Под "остальным" понимаем состояние "0" - начало диалога
            if hardsql.check_name("names", str(message.from_user.id)) != True:
                logger.warning('Id:  "%s", in db: "%s"', message.from_user.id, hardsql.check_name("names", str(message.from_user.id)))
                bot.send_message(message.chat.id, "Привет! Как я могу к тебе обращаться?")
                dbworker.set_state(message.from_user.id, config.States.S_ENTER_NAME.value)
            else:
                bot.send_message(message.chat.id, "Привет! Я тебя знаю - если прочитал Библию, то напиши мне /read. Read за вчера - /yesterday. Остальные немаловажные команды - /help")
    else:
        bot.send_message(message.chat.id, "Ты просишь меня об услуге, но делаешь это без уважения...")


# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Как тебя зовут?")
    dbworker.set_state(message.from_user.id, config.States.S_ENTER_NAME.value)

@bot.message_handler(commands=["cool"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Спасибо, стараюсь)")

@bot.message_handler(commands=["crazy"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Есть немного)")


@bot.message_handler(commands=["help"])
def cmd_help(message):
    if hardsql.check_name("names", str(message.from_user.id)) != True:
        logger.warning('Id:  "%s", in db: "%s"', message.from_user.id, hardsql.check_name("names", str(message.from_user.id)))
        bot.send_message(message.chat.id, "Привет! Как я могу к тебе обращаться?")
        dbworker.set_state(message.from_user.id, config.States.S_ENTER_NAME.value)
    else:
        bot.send_message(message.chat.id, "Йоу 🐳, справка по моим кнопочкам: \n\n📖 записаться в табличку по чтению Библии -  /read \n😴 read за вчера - /yesterday. \n✍🏻 поменять имя в таблице - /change \n❔ твое имя сейчас - /name \n📊 получить свою статистику за месяц: /report \n🗓 заказать новую табличку за месяц: /tablenew \n🔦 просто получить табличку: /table")



# По команде /read будем фиксировать прочтение Библии
@bot.message_handler(commands=["read"])
def cmd_read(message):
    if hardsql.check_name("names", str(message.from_user.id)) != True:
        bot.send_message(message.chat.id, "Привет, скажи сначала как тебя зовут?")
        dbworker.set_state(message.from_user.id, config.States.S_ENTER_NAME.value)
    else:
        if message.chat.id == -1001156429380: #hardcode for experienced tourists 
            groupid = 0
        else:
            groupid = message.chat.id
        logger.warning('Command from chat:  "%s"', groupid)
        if hardsql.check_column(str(message.from_user.id)) != True:
            hardsql.add_column(str(message.from_user.id))    #добавляем столбец пользователя

            if hardsql.in_group(message.from_user.id, groupid) != True:
                hardsql.attend_to_group(message.from_user.id, groupid)

            bot.send_message(message.chat.id, "Супер, записываю!")
            hardsql.add_new_row(int(message.from_user.id), 0)
        else:

            if hardsql.in_group(message.from_user.id, groupid) != True:
                logger.warning('Not in group')
                hardsql.attend_to_group(message.from_user.id, groupid)
            else:
                logger.warning('in group')
            bot.send_message(message.chat.id, "Супер, записываю!")
            hardsql.add_new_row(int(message.from_user.id), 0)

@bot.message_handler(commands=["yesterday"])
def cmd_yesterday(message):
    if hardsql.check_name("names", str(message.from_user.id)) != True:
        bot.send_message(message.chat.id, "Привет, скажи сначала как тебя зовут?")
        dbworker.set_state(message.from_user.id, config.States.S_ENTER_NAME.value)
    else: 
        if hardsql.check_column(str(message.from_user.id)) != True:
            hardsql.add_column(str(message.from_user.id))    #добавляем столбец пользователя

            if hardsql.in_group(message.from_user.id, message.chat.id) != True:
                hardsql.attend_to_group(message.from_user.id, message.chat.id)

            bot.send_message(message.chat.id, "Супер, записываю вчерашним числом!")
            hardsql.add_new_row(int(message.from_user.id), 24)
        else:
            if hardsql.in_group(message.from_user.id, message.chat.id) != True:
                logger.warning('Not in group')
                hardsql.attend_to_group(message.from_user.id, message.chat.id)
            else:
                logger.warning('in group')
            bot.send_message(message.chat.id, "Супер, записываю вчерашним числом!")
            hardsql.add_new_row(int(message.from_user.id), 24)

@bot.message_handler(commands=["change"])
def cmd_change(message):
    if hardsql.check_name("names", str(message.from_user.id)) != True:
        bot.send_message(message.chat.id, "Привет, напиши твое имя!")
        dbworker.set_state(message.from_user.id, config.States.S_ENTER_NAME.value)
    else:
        bot.send_message(message.chat.id, "Привет, напиши новое имя!")
        dbworker.set_state(message.from_user.id, config.States.S_CHANGE_NAME.value)

@bot.message_handler(commands=["name"])
def get_name(message):
    if hardsql.check_name("names", str(message.from_user.id)) != True:
        bot.send_message(message.chat.id, "Привет, ты новенький. Напиши своё имя!")
        dbworker.set_state(message.from_user.id, config.States.S_ENTER_NAME.value)
    else:
        myname = hardsql.get_name(message.from_user.id)
        bot.send_message(message.chat.id, "Ты записан как: " + myname)

@bot.message_handler(commands=["report"])
def get_report(message):
    if hardsql.check_name("names", str(message.from_user.id)) != True:
        bot.send_message(message.chat.id, "Привет, напиши твое имя!")
        dbworker.set_state(message.from_user.id, config.States.S_ENTER_NAME.value)
    else:
        rep = hardsql.get_report(message.from_user.id, 'personal')
        bot.send_message(message.chat.id, 'В этом месяце ты в Слове на ' + str(rep) + '%')

@bot.message_handler(commands=["table"])
def get_greport(message):
    if hardsql.check_name("names", str(message.from_user.id)) != True:
        bot.send_message(message.chat.id, "Привет, напиши твое имя!")
        dbworker.set_state(message.from_user.id, config.States.S_ENTER_NAME.value)
    else:
        if message.chat.id == -1001156429380: #hardcode for experienced tourists 
            groupid = 0
        else:
            groupid = message.chat.id

        if hardsql.check_id(groupid) != True:
            bot.send_message(message.chat.id, "Сначала закажи табличку: /tablenew")
        else:
            cid = hardsql.increment_id(groupid, 'get')         
            fullpath = config.out_path + "read_" + str(groupid) + "_" + str(cid - 1) + ".pdf"
            my_file = Path(fullpath)
            if my_file.is_file():
                #bot.send_message(message.chat.id, "А файлик то уже оформлен!")
                doc = open(fullpath, 'rb')
                bot.send_document(message.chat.id, doc)
            else:
                bot.send_message(message.chat.id, "Пока не готово...")
            #doc = open('/tmp/file.txt', 'rb')


@bot.message_handler(commands=["tablenew"])
def get_nreport(message):
    if hardsql.check_name("names", str(message.from_user.id)) != True:
        bot.send_message(message.chat.id, "Привет, напиши твое имя!")
        dbworker.set_state(message.from_user.id, config.States.S_ENTER_NAME.value)
    else:
        if message.chat.id == -1001156429380: #hardcode for experienced tourists 
            groupid = 0
        else:
            groupid = message.chat.id
        
        logger.warning('tablenew from chat:  "%s"', groupid)
        logger.warning('tablenew groupid type:  "%s"', type(groupid))

        if hardsql.check_id(groupid) != True: #add groupid to ids if not exists
            hardsql.add_id(groupid)
        

        cid = hardsql.increment_id(groupid, 'get')
        names = []
        content = []
        times = hardsql.get_times('series')
        ids = hardsql.get_names()
        grouphash = hardsql.get_groups()



        for _id in ids:
            if grouphash[_id] is not None:
                if groupid in grouphash[_id]: #check if user is related to group
                    names.append({"name": hardsql.get_name(_id)})
                    rep = hardsql.get_report(_id, 'global')
                    content.append({"content": rep})       
        _json = {"id": cid, "gid": groupid, "period": 1, "wgroup": message.chat.title, "title": times, "names": names, "content": content}
        logger.warning(_json)


        filename = config.report + str(groupid) + '.json'
        fnamerep = "reads_data" + str(groupid) + '.json'
        
        with open(filename, 'w') as outfile: #create separate file for each chat
            json.dump(_json, outfile)


        try:
            r = requests.get("http://report:3000/generate-report?filename=" + fnamerep)
        except requests.exceptions.RequestException as e:
            print(f"\nOOOPS! It seems something went wrong...\n{e}")
            return
        if r.status_code == 200:
            hardsql.increment_id(groupid, 'add')       
            bot.send_message(message.chat.id, "Готовлю отчет за месяц. Приходи через минуту за новой табличкой: /table")
        else:
            bot.send_message(message.chat.id, "Что-то не так с нашим писателем отчетов, но с секретарем все хорошо")
            print(f"\nUnexpected response: {str(r.status_code)} {r.text}")
            return


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.from_user.id) == config.States.S_ENTER_NAME.value)
def user_entering_name(message):
    #bot.send_message(message.chat.id, "Отличное имя, запомню! Теперь укажи, пожалуйста, свой псевдоним.")
    #dbworker.set_state(message.from_user.id, config.States.S_ENTER_EGO.value)
    logger.warning('Id:  "%s", name: "%s"', message.from_user.id, message.text)
    if len(message.text) > 10:
        bot.send_message(message.chat.id, "Давай покороче, максимум 10 символов")
    else:
        hardsql.insert_name(message.from_user.id, message.text)
        if hardsql.check_column(str(message.from_user.id)) != True:
            hardsql.add_column(str(message.from_user.id))
        bot.send_message(message.chat.id, "Отлично, теперь ты записан! Больше от тебя ничего не требуется. Теперь можешь отправить свой /read. Остальные немаловажные команды - /help")
        dbworker.set_state(message.from_user.id, config.States.S_START.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.from_user.id) == config.States.S_CHANGE_NAME.value)
def user_changing_name(message):
    logger.warning('Id:  "%s", name: "%s"', message.from_user.id, message.text)
    if len(message.text) > 10:
        bot.send_message(message.chat.id, "Давай покороче, максимум 10 символов")
    else:
        if hardsql.check_same(message.text) != True:
            hardsql.change_name(message.from_user.id, message.text)
            bot.send_message(message.chat.id, "Отлично, имя я поменял! Теперь у тебя новое имя в табличке)")
            dbworker.set_state(message.from_user.id, config.States.S_START.value)
        else:
            bot.send_message(message.chat.id, "Кто-то уже занял это имя... Возможно \"кто-то\" это ты :) Попробуй другое")


if __name__ == "__main__":
    bot.infinity_polling()