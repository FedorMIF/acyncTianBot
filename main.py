import random
import telebot
from telebot import TeleBot, types
import bd
import log
import fiveword
import img_from_site

bot = TeleBot('1661866696:AAFi8P_OLIstQ2RGmoZFBkXVSZivYMoJIzk')  # основа
#10 str #bot = TeleBot('5207851764:AAGIWwh7EX5t-nJX6xjoT41vuaRH-gkw-Lg')  # тест бот

yn_but = ['Да', 'Нет']

keyboard_menu = types.ReplyKeyboardMarkup(row_width=2).add('Изменить свое имя', 'Добавить заметку', 'Пока ничего')
keyboard_yn = types.ReplyKeyboardMarkup(row_width=2).add('Да', 'Нет')
rem = types.ReplyKeyboardRemove

list_commands = ['- Напиши "привет", для того что бы познакомиться', '- /help - Список всех комманд',
                 '- /addnote - добавить заметку', '- /showallnotes - посмотреть все текущие заметки',
                 '- /dellnote - удалить заметку', '- /menu - открыть меню', '-/playfive - игра 5 букв',
                 '- /sendmailtoandmin - отправить сообщение админу', '- Попроси "мем" для расслабона и чилла',
                 '- напиши "Поздравление" если хочешь получить новогоднюю картинку']
list_commands_adm = ['- Напиши "привет", для того что бы познакомиться', '- /help - Список всех комманд',
                     '- /addnote - добавить заметку', '- /showallnotes - посмотреть все текущие заметки',
                     '- /dellnote - удалить заметку', '- /showusersname - посомтреть всех юзеров с их id',
                     '- /sendmess - отослать всем сообщение', '- /sendmesstouser - отдельному челу',
                     '- /getlog - получить логфайл', '- Попроси "мем" для расслабона и чилла', '- /tospecial - бро/кис'
                                                                                               '- напиши "Поздравление" если хочешь получить новогоднюю картинку']
what_yn_com = 0


def printlist(commands):
    string = ''
    for i in commands:
        string += i + '\n'
    return string


def check(mess):
    try:
        if mess.chat.id not in bd.get_list_users(id):
            if str(mess.chat.type) == 'private':
                nameUser = mess.chat.username
            elif str(mess.chat.type) == 'supergroup' or str(mess.chat.type) == 'group':
                nameUser = mess.chat.title
            else:
                nameUser = 'None'
            bd.add_new_user(mess.chat.id, nameUser)
        if mess.from_user.id not in bd.get_list_users(id):
            bd.add_new_user(mess.from_user.id, mess.from_user.first_name)

    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['start'])
def start(mess):
    try:
        bd.add_new_user(mess.from_user.id, mess.from_user.first_name)
        bd.give_user_name(mess.from_user.id)
        bot.reply_to(mess,
                     f'Привет, {bd.give_user_name(mess.from_user.id)}, я твой помощник в делах насущных, напиши /help для '
                     f'того что бы увидеть все комманды, '
                     f'а так же можешь попросить мем, что бы поржать)')
    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['addnote'])
def add_notification(mess):
    check(mess)
    try:
        if bd.create_new_bdrasp(mess.from_user.id):
            mes = bot.send_message(mess.chat.id, 'Напиши что тебе напомнить')
            bot.register_next_step_handler(mes, note_resiver1)
        else:
            mes = bot.send_message(mess.chat.id, 'У тебя уже есть несколько напоминаний, хочешь добавить еще одно?',
                                   reply_markup=keyboard_yn)
            bot.register_next_step_handler(mes, yn_resiver1)
    except Exception as e:
        err('die', mess, e)


def yn_resiver1(mess):
    try:
        if mess.text.lower() == 'да':
            mes = bot.send_message(mess.from_user.id, 'Напиши что тебе напомнить',
                                   reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(mes, note_resiver1)
        elif mess.text.lower() == 'нет':
            bot.send_message(mess.chat.id, 'Ладно, нет так нет', reply_markup=types.ReplyKeyboardRemove())

    except Exception as e:
        err('die', mess, e)


def note_resiver1(mess):
    try:
        if bd.add_new_rasp(mess.from_user.id, log.time(), mess.text):
            bot.send_message(mess.chat.id, 'Я добавила заметку:\n' + mess.text)
        else:
            bot.send_message(mess.chat.id, 'У меня не получилось, попробуй еще раз')

    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['dellnote'])
def dell_notification(mess):
    check(mess)
    try:
        if bd.create_new_bdrasp(mess.from_user.id):
            bot.send_message(mess.chat.id, 'У тебя нет еще заметок')
        else:
            mes = bot.send_message(mess.chat.id, 'Ты хочешь удалить одну из своих заметок?',
                                   reply_markup=keyboard_yn)
            bot.register_next_step_handler(mes, yn_resiver2)

    except Exception as e:
        err('die', mess, e)


def yn_resiver2(mess):
    try:
        if mess.text.lower() == 'да':
            mes = bot.send_message(mess.chat.id, 'Напиши порядковый номер заметки \n'
                                                 'Ты можешь посомтреть список всех твоих заметок с помошью команды '
                                                 '/showallnotes', reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(mes, note_resiver2)
        elif mess.text.lower() == 'нет':
            bot.send_message(mess.chat.id, 'Ладно, нет так нет', reply_markup=types.ReplyKeyboardRemove())

    except Exception as e:
        err('die', mess, e)


def note_resiver2(mess):
    try:

        if bd.dell_user_rasp(mess.from_user.id, int(mess.text)):
            bot.send_message(mess.chat.id, 'Я удалила заметку :)')
        else:
            bot.send_message(mess.chat.id, 'Я не нашла заметку с таким номером')

    except Exception as e:
        err('die', mess, e)

@bot.message_handler(commands=['showallnotes'])
def show_notes(mess):
    try:
        notes = 'У тебя нет заметок'
        if not bd.create_new_bdrasp(mess.from_user.id):
            for user_id in bd.give_user_notes(mess.from_user.id):
                notes += user_id + "\n"
        bot.send_message(mess.chat.id, 'Твои заметки')
        bot.send_message(mess.chat.id, notes)

    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['showusersname'])
def show_names(mess):
    try:
        if mess.from_user.id == 339512152:
            names = ''
            for user_name in bd.get_list_users("name"):
                names += user_name + '\n'
            bot.send_message(mess.chat.id, names)
        else:
            bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань адином, а потом поговорим')

    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['help'])
def help(mess):
    check(mess)
    try:
        if mess.from_user.id == 339512152:
            bot.reply_to(mess, printlist(list_commands_adm), reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.reply_to(mess, printlist(list_commands), reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['menu'])
def get_menu(mess):
    check(mess)
    try:
        bot.reply_to(mess, 'Выбери что ты хочешь', reply_markup=keyboard_menu)

    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['sendmess'])
def send_mess(mess):
    try:
        if mess.from_user.id == 339512152:
            mes = bot.send_message(mess.chat.id, 'Хозяин, что вы хотите отправить всем нашим рабам?')
            bot.register_next_step_handler(mes, get_text_for_mess)
        else:
            bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань адином, а потом поговорим')

    except Exception as e:
        err('die', mess, e)


def get_text_for_mess(mess):
    try:
        txt = mess.text
        mes = bot.send_message(mess.chat.id, 'Хозяин, вы точно хотите это отвправить?')
        bot.register_next_step_handler(mes, send_mess_to_all, txt)

    except Exception as e:
        err('die', mess, e)


def send_mess_to_all(mess, txt):
    try:
        if mess.text.lower() == "да":
            for user_id in bd.get_list_users('id'):
                try:
                    bot.send_message(user_id, str(txt))
                except:
                    log.add(user_id + ': эта крыса меня забанила')
        else:
            bot.send_message(mess.chat.id, 'Хорошо, это останеться между нами)')

    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['sendmesstouser'])
def send_mess_to_user(mess):
    try:
        if mess.from_user.id == 339512152:
            mes = bot.send_message(mess.chat.id, 'Напиши id')
            bot.register_next_step_handler(mes, get_id_for_mess)
        else:
            bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань адином, а потом поговорим')

    except Exception as e:
        err('die', mess, e)


def get_id_for_mess(mess):
    try:
        txt_id = mess.text
        mes = bot.send_message(mess.chat.id, 'Напиши сообщение')
        bot.register_next_step_handler(mes, get_text2_for_mess, txt_id)

    except Exception as e:
        err('die', mess, e)


def get_text2_for_mess(mess, txt_id):
    try:
        txt = mess.text
        mes = bot.send_message(mess.chat.id, 'Хозяин, вы точно хотите это отвправить?')
        bot.register_next_step_handler(mes, send_mess2_to_all, txt_id, txt)

    except Exception as e:
        err('die', mess, e)


def send_mess2_to_all(mess, txt_id, txt):
    try:
        if mess.text.lower() == "да":
            bot.send_message(int(txt_id), str(txt))
        else:
            bot.send_message(mess.chat.id, 'Хорошо, это останеться между нами)')

    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['getlog'])
def send_log_file(mess):
    try:
        if mess.from_user.id == 339512152:
            bot.send_document(mess.chat.id, log.get_file())
        else:
            bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань адином, а потом поговорим')

    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['sendmailtoandmin'])
def send_mail(mess):
    check(mess)
    try:
        mes = bot.send_message(mess.chat.id, 'Напиши сообщение админу)')
        bot.register_next_step_handler(mes, send_mail_to_admin)

    except Exception as e:
        err('die', mess, e)


def send_mail_to_admin(mess):
    try:
        bot.send_message(339512152,
                         'Cообщениение Админу:\n' + str(mess.text) + '\n от: ' + str(mess.from_user.first_name) +
                         ' ' + str(mess.from_user.id))
        bot.send_message(mess.chat.id, 'Сообщение отпралено, я тебе передам ответ (если он будет)')

    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['sendmem'])
def mem(mess):
    check(mess)
    try:
        name = bd.give_user_name(mess.from_user.id)
        if name == '':
            name = mess.from_user.first_name
        if mess.from_user.id in log.bro_list():
            bot.send_photo(mess.chat.id, photo=img_from_site.get_pic(), caption='Держи, Братан, мем')
        elif mess.from_user.id in log.kis_list():
            bot.send_photo(mess.chat.id, photo=img_from_site.get_pic(), caption='Держи, Киса, мем')
        else:
            bot.send_photo(mess.chat.id, photo=img_from_site.get_pic(), caption=f'Держи, {name}, мем')

    except Exception as e:
        err('die', mess, e)


def NY(mess):
    check(mess)
    try:
        name = bd.give_user_name(mess.from_user.id)
        if name == '':
            name = mess.from_user.first_name
        if mess.from_user.id in log.bro_list():
            bot.send_photo(mess.chat.id, photo=img_from_site.get_NY_pic(), caption='Поздравляю тебя, Братан, '
                                                                                   'с наступающим новым годом!!!')
        elif mess.from_user.id in log.kis_list():
            bot.send_photo(mess.chat.id, photo=img_from_site.get_NY_pic(), caption='Поздравляю тебя, Киса, '
                                                                                   'с наступающим новым годом!!!')
        else:
            bot.send_photo(mess.chat.id, photo=img_from_site.get_NY_pic(), caption=f'Поздравляю тебя, {name}, '
                                                                                   f'с наступающим новым годом!!!')

    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['tospecial'])
def get_id_bro(mess):
    try:
        if mess.from_user.id == 339512152:
            mes = bot.send_message(mess.chat.id, 'Напиши id')
            bot.register_next_step_handler(mes, get_bro_or_kiss)
        else:
            bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань адином, а потом поговорим')
    except Exception as e:
        err('die', mess, e)


def get_bro_or_kiss(mess):
    try:
        global bro_id
        bro_id = mess.text
        mes = bot.send_message(mess.chat.id, 'бро или кис')
        bot.register_next_step_handler(mes, get_to_bro)
    except Exception as e:
        err('die', mess, e)


def get_to_bro(mess):
    try:
        global bro_id
        if 'бро' in mess.text.lower():
            log.to_bro_list(bro_id)
        elif 'кис' in mess.text.lower():
            log.to_kis_list(bro_id)
        else:
            bot.send_message(mess.chat.id, 'Нет такого списка, давай все заново')
    except Exception as e:
        err('die', mess, e)


@bot.message_handler(commands=['playfive'])
def send_hi(mess):
    #check(mess)
    try:
        word = fiveword.genword()
        mes = bot.send_message(mess.chat.id, f"Давай поиграем в игру _5 Букв_\n"
                                             f"У нее очень простые правила:\n"
                                             f"Тебе надо угадать слово из 5 букв\n"
                                             f"для начала напиши любое слово из 5 букв\n"
                                             f"я тебе отвечу:\n"
                                             f"какие буквы стоят на *правильном месте*\n"
                                             f"а какие просто _есть в этом слове_\n"
                                             f"Если устанешь играть, напиши слово 'Стоп'", parse_mode="Markdown")
        bot.register_next_step_handler(mes, compration_word, word)
    except Exception as e:
        err('die', mess, e)


def compration_word(mess, word):
    try:

        if mess.text.lower() == 'стоп':
            bot.send_message(mess.chat.id, f'Жаль, что не доиграли, слово было: {word}')

        elif len(mess.text) == 5:
            llb = ''
            lb = []
            li = []

            word = word.lower()
            userword = mess.text.lower()

            if userword != word:
                for letter in range(5):
                    if userword[letter] == word[letter]:
                        llb += userword[letter]
                        lb.append(userword[letter])
                    else:
                        llb += '_'

                    if userword[letter] in word and userword[letter] not in lb and userword[letter] not in li:
                        li.append(userword[letter])

                if not len(lb) and not len(li):
                    mes = bot.send_message(mess.chat.id, f'Ни одна буква не совпала(((')
                    bot.register_next_step_handler(mes, compration_word, word)
                else:
                    mes = bot.send_message(mess.chat.id, f'Правильная позиция: *{llb}*\n'
                                                         f'Неправильная позиця: _{",".join(li)}_',
                                           parse_mode="Markdown")
                    bot.register_next_step_handler(mes, compration_word, word)
            else:
                bot.send_message(mess.chat.id, f'Молодец, это было слово: {word}')

        else:
            mes = bot.send_message(mess.chat.id, 'Надо написать слово из 5 букв, попробуй еще раз!')
            bot.register_next_step_handler(mes, compration_word, word)

    except Exception as e:
        err('die', mess, e)

@bot.message_handler(commands=['getquestion'])
def question(mess):
    bot.send_message(mess.chat.id, f'{fiveword.genquestion()}')

@bot.message_handler(content_types=['text'])
def com_text(mess):
    check(mess)
    try:
        global what_yn_com

        if 'привет' in mess.text.lower():
            name = bd.give_user_name(mess.from_user.id)
            if mess.from_user.id in log.bro_list():
                bot.send_message(mess.chat.id, f'Салам, брату {name} админа')
            else:
                bot.send_message(mess.chat.id, f'Привет, {name}!')

        elif mess.text.lower() == 'изменить свое имя':
            bot.send_message(mess.chat.id, 'Напиши все новое имя')
            bot.register_next_step_handler(mess, get_name)

        elif mess.text.lower() == 'добавить заметку':
            bot.send_message(mess.chat.id, 'Напиши эту команду: /addnote')

        elif mess.text.lower() == 'пока ничего':
            bot.send_message(mess.chat.id, 'Напши как что-то захочешь /menu')

        elif 'мем' in mess.text.lower():
            mem(mess)
        elif 'хуй' in mess.text.lower() or 'хер' in mess.text.lower():
            try:
                name = bd.give_user_name(mess.from_user.id)
            except:
                name = 'дорогуша'
            bot.send_message(mess.chat.id, f'Фу, {name}, как тебе не стыдно!')
        elif 'блин' in mess.text.lower() or 'бля' in mess.text.lower():
            try:
                name = bd.give_user_name(mess.from_user.id)
            except:
                name = 'дорогуша'
            bot.send_message(mess.chat.id, f'Не выражайся, {name}!')
        elif 'сук' in mess.text.lower():
            try:
                name = bd.give_user_name(mess.from_user.id)
            except:
                name = 'дорогуша'
            bot.send_message(mess.chat.id, f'Не переживай так сильно, {name}!')
        elif 'спасибо' in mess.text.lower():
            try:
                name = bd.give_user_name(mess.from_user.id)
            except:
                name = "дорогуша"
            bot.send_message(mess.chat.id, f'Пожалуйста, {name}!')

        elif 'поздравление' in mess.text.lower():
            NY(mess)

        elif mess.text.lower() == 'да':
            if what_yn_com == 0:
                err('wtf', mess)

            elif what_yn_com == 2:
                what_yn_com = 0
                msg = bot.send_message(mess.chat.id, 'Напиши все новое имя', reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(msg, ch_name1)

            elif what_yn_com == 3:
                what_yn_com = 0
                bot.send_message(mess.chat.id, 'Хорошо) Тогда я тебя запомню)',
                                 reply_markup=types.ReplyKeyboardRemove())

        elif mess.text.lower() == 'нет':
            if what_yn_com == 0:
                err('wtf', mess)

            elif what_yn_com == 2:
                what_yn_com = 0
                bot.send_message(mess.chat.id, 'Тогда я тебя запомню таким', reply_markup=types.ReplyKeyboardRemove())

            elif what_yn_com == 3:
                what_yn_com = 0
                bot.send_message(mess.chat.id, 'Как тебя зовут?', reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(mess, get_name)

        else:
            err('wtf', mess)

    except Exception as e:
        err('die', mess, e)

def get_name(mess):
    try:
        ch = bd.add_new_user(mess.from_user.id, mess.text)

        if ch == 'T':
            name = bd.give_user_name(mess.from_user.id)
            if name:
                bot.send_message(mess.chat.id,
                                 'Привет, ' + name + '. Напиши "/menu", что бы ознакомиться с тем, что я могу для '
                                                     'тебя сделать')
            else:
                err('name_err', mess)

        elif ch == "double":
            name = bd.give_user_name(mess.from_user.id)
            if name:
                bot.send_message(mess.chat.id, f'У меня уже есть твое имя, {name}, хочешь выбрать другое?',
                                 reply_markup=keyboard_yn)
                global what_yn_com
                what_yn_com = 2
            else:
                err('name_err', mess)

        else:
            err('err', mess)

    except Exception as e:
        err('die', mess, e)


def ch_name1(mess):
    try:
        ch = bd.edit_user_name(mess.from_user.id, mess.text)
        if ch:
            name = bd.give_user_name(mess.from_user.id)
            bot.send_message(mess.chat.id,
                             'Привет, ' + name + '. Напиши "/menu", что бы ознакомиться с тем, что я могу для тебя '
                                                 'сделать')
        else:
            err('err', mess)
    except Exception as e:
        err('die', mess, e)


def err(v, mess=None, err=None):
    if v == 'err':
        bot.send_message(mess.chat.id, 'Что то пошло не так, попробуй заново')
    elif v == 'name_err':
        bot.send_message(mess.chat.id, 'Не могу получить твое имя, попробуй заново')
    elif v == 'wtf':
        if mess.chat.id > 0:
            bot.send_message(mess.chat.id, 'Я тебя не понимаю( Напиши /help')
            log.add(str(mess.text) + ' ' + str(mess.from_user.id))
    elif v == 'die':
        bot.send_message(mess.chat.id, 'Прости, у меня проблемы(( Возможно меня скоро перезапустят')
        bot.send_message(339512152, 'Произошел взлом жопы, проверь лог')
        log.add('!!!!!Ошибка!!!!!:' + str(err) + ' после сообщения:' + str(mess.text) + ' ' + str(mess.from_user.id))
    elif v == 'pol':
        # bot.send_message(339512152, 'Произошел взлом жопы ПОЛИНГА МАТЬ ЕГО, проверь лог')
        log.add('!!!!!Ошибка POLING!!!!!:' + str(err))


@bot.message_handler(content_types=['photo'])
def handle_docs_photo(mess):
    check(mess)
    try:
        if random.randint(0, 1):
            bot.send_message(mess.chat.id, 'Потрясающая картинка, присылай еще))')
        else:
            bot.send_message(mess.chat.id, 'Фу')

        try:
            nameChat = mess.chat.title
        except:
            nameChat = 'Имя не получено'

        bot.send_message(339512152, f'{str(mess.from_user.id)}, {str(mess.chat.id)}, {nameChat}, {mess.chat.type}')
        bot.forward_message(339512152, mess.chat.id, message_id=mess.message_id)

    except Exception as e:
        err('die', mess, e)

try:
    bot.polling(none_stop=True, interval=0)
except Exception as e:
    err('pol', err=e)
