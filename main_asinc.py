from aiogram import Bot, types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove
import os

import random

import bd
import log
import fiveword
import img_from_site
import piccor as pc

bot = Bot('1661866696:AAFi8P_OLIstQ2RGmoZFBkXVSZivYMoJIzk')  # основа
#bot = Bot('5207851764:AAGIWwh7EX5t-nJX6xjoT41vuaRH-gkw-Lg')  # тест бот

addToSell = -1002109739402

dp = Dispatcher(bot, storage=MemoryStorage())

yn_but = ['Да', 'Нет']

kb = ('Изменить', 'yes')

row_bt = InlineKeyboardButton(kb[0], callback_data=kb[1])

menu1 = InlineKeyboardMarkup(row_width=1)
menu1.row(row_bt)

#keyboard_menu = types.ReplyKeyboardMarkup(row_width=2).add('Изменить свое имя', 'Добавить заметку', 'Пока ничего')
#keyboard_yn = types.ReplyKeyboardMarkup(row_width=2).add('Да', 'Нет')
#rem = types.ReplyKeyboardRemove

list_commands = ['- Напиши "привет", для того что бы познакомиться', '- /help - Список всех комманд',
                 #'- /addnote - добавить заметку', '- /showallnotes - посмотреть все текущие заметки',
                 #'- /dellnote - удалить заметку', '- /menu - открыть меню', 
                 '-/playfive - игра 5 букв', '- /sendmailtoandmin - отправить сообщение админу', '- Попроси "мем" для расслабона и чилла',
                 '-/cormypic - мини фотошоп (beta)',
                 #'- напиши "Поздравление" если хочешь получить новогоднюю картинку'
                 ]
list_commands_adm = [ '- /help - Список всех комманд',
                     #'- /addnote - добавить заметку', '- /showallnotes - посмотреть все текущие заметки',
                     #'- /dellnote - удалить заметку', 
                     '- /showusersname - посомтреть всех юзеров с их id',
                     '- /sendmess - отослать всем сообщение', '- /sendmesstouser - отдельному челу',
                     '- /getlog - получить логфайл', '- Попроси "мем" для расслабона и чилла', '- /tospecial - бро/кис'
                    #'- напиши "Поздравление" если хочешь получить новогоднюю картинку'
                    ]
what_yn_com = 0

class GameStates(StatesGroup):
    waiting_for_word = State()

class SendMessToAllUsers(StatesGroup):
    text = State()
    confing = State() 

class SendMessToUser(StatesGroup):
    text = State()
    user_id = State()
    confing = State()

class SendMessToAdmin(StatesGroup):
    text = State()

class ChName(StatesGroup):
    name = State()

class Form(StatesGroup):
    mode = State()
    name = State()
    enhancement = State()

class Meme(StatesGroup):
    text = State()
    photo = State()    

class GroupeRoad(StatesGroup):
    text = State()
    newGroupe = State()
    editАnswers = State()
    addAnswers = State()
    dellAnswers = State()

async def printlist(commands):
    string = ''
    for i in commands:
        string += i + '\n'
    return string


async def check(mess: types.Message):
    try:
        if mess.forward_from_chat:
            channel_info = mess.forward_from_chat
            channel_id = channel_info.id
            channel_name = channel_info.title  # Имя канала
            await bd.add_new_user(channel_id, channel_name)
        elif mess.chat.id not in await bd.get_list_users(id):
            if str(mess.chat.type) == 'private':
                nameUser = mess.chat.username
            elif str(mess.chat.type) == 'supergroup' or str(mess.chat.type) == 'group':
                nameUser = mess.chat.title
            await bd.add_new_user(mess.chat.id, nameUser)

    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['start'])
async def start(mess: types.Message):
    try:
        await check(mess)
        await bd.give_user_name(mess.from_user.id)
        await mess.answer(
                     f'Привет, {await bd.give_user_name(mess.from_user.id)}, я твой помощник в делах насущных, напиши /help для '
                     f'того что бы увидеть все комманды, '
                     f'а так же можешь попросить мем, что бы поржать)')
    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['help'])
async def help(mess: types.Message):
    await check(mess)
    try:
        if mess.from_user.id == 339512152:
            await mess.answer(await printlist(list_commands_adm), reply_markup=types.ReplyKeyboardRemove())
        else:
            await mess.answer(await printlist(list_commands), reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['playfive'])
async def send_hi(mess: types.Message, state: FSMContext):
    await check(mess)
    try:
        async with state.proxy() as data:
            data['word'] = await fiveword.genword()
        await bot.send_message(mess.chat.id, f"Давай поиграем в игру _5 Букв_\n"
                                             f"У нее очень простые правила:\n"
                                             f"Тебе надо угадать слово из 5 букв\n"
                                             f"для начала напиши любое слово из 5 букв\n"
                                             f"я тебе отвечу:\n"
                                             f"какие буквы стоят на *правильном месте*\n"
                                             f"а какие просто _есть в этом слове_\n"
                                             f"Если устанешь играть, напиши слово 'Стоп'", parse_mode="Markdown")  
        await GameStates.waiting_for_word.set()
    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(state=GameStates.waiting_for_word, content_types=types.ContentTypes.TEXT)
async def compration_word(mess: types.Message, state: FSMContext):
    try:

        async with state.proxy() as data:
            word = data['word'].lower()

        userword = mess.text.lower()

        if userword == 'стоп':
            await bot.send_message(mess.chat.id, f'Жаль, что не доиграли, слово было: {word}')
            await state.finish()

        elif len(mess.text) == 5:
            llb = ''
            lb = []
            li = []

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
                    await bot.send_message(mess.chat.id, f'Ни одна буква не совпала(((')
                else:
                    await bot.send_message(mess.chat.id, f'Правильная позиция: *{llb}*\n'
                                                         f'Неправильная позиця: _{",".join(li)}_',
                                           parse_mode="Markdown")
            else:
                await bot.send_message(mess.chat.id, f'Молодец, это было слово: {word}')
                await state.finish()

        else:
            await bot.send_message(mess.chat.id, 'Надо написать слово из 5 букв, попробуй еще раз!')

    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(commands=['userinfo'])
async def user_info(mess: types.Message):
    name = await bd.give_user_name(mess.from_user.id)
    user_id = mess.from_user.id
    await bot.send_message(mess.chat.id, f'Имя: {name}\nid: {user_id}\nХотите изменить имя?', reply_markup=menu1)

@dp.callback_query_handler(text = 'yes')
async def callback_inline(query: types.CallbackQuery, state: FSMContext):
    if query.data == 'yes':
        await bot.edit_message_text("Введи новое имя", query.message.chat.id, query.message.message_id)
        await ChName.name.set()
        await state.update_data(queryUid=query.from_user.id)
        await state.update_data(queryMid=query.message.message_id)

@dp.message_handler(state=ChName.name, content_types=types.ContentTypes.TEXT)
async def chName(mess: types.Message, state: FSMContext):
    name = mess.text
    answers = await state.get_data()
    try:
        if await bd.edit_user_name(mess.from_user.id, name):
            await bot.edit_message_text("Изменено!", answers['queryUid'], answers['queryMid'])
        else:
            await bot.edit_message_text("Что то пошло не так!", answers['queryUid'], answers['queryMid'])
    
        await state.finish()

    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(mess: types.Message):
    await check(mess)
    try:
        chat_id = mess.chat.id 
        groups_id = tuple([name[1] for name in await bd.get_list_groups()])
        answList = ['Потрясающая картинка, присылай еще))', 'Наверное это не в моем вкусе(']
        
        if chat_id in groups_id:
            nts = await bd.give_user_notes(chat_id)
            answList = [n[0] for n in nts]
            if answList[0] == 'Специальных ответов для группы нет':
                answList = ['Потрясающая картинка, присылай еще))', 'Наверное это не в моем вкусе(']

        await bot.send_message(chat_id, random.choice(answList), reply_to_message_id=mess.message_id)
        
        try:
            nameChat = mess.chat.title
            if not nameChat:
                nameChat = await bd.give_user_name(mess.from_user.id)
        except:
            nameChat = 'Имя не получено'
        
        if mess.forward_from_chat:
            if mess.forward_from_chat.id != addToSell:
                await bot.send_message(addToSell, f'{str(mess.from_user.id)}, {str(chat_id)}, {nameChat}, {mess.chat.type}')
                await bot.forward_message(addToSell, chat_id, message_id=mess.message_id)
        else:
            await bot.send_message(addToSell, f'{str(mess.from_user.id)}, {str(chat_id)}, {nameChat}, {mess.chat.type}')
            await bot.forward_message(addToSell, chat_id, message_id=mess.message_id)


    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['cormypic'])
async def cmd_start(message: types.Message):
    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton("ЧБ", callback_data='bw:ЧБ'),
        InlineKeyboardButton("Сепия", callback_data='sepia:сепия')
    )    
    markup.add(
        InlineKeyboardButton("Изменить насыщенность", callback_data='enhance:насыщенности'),
        InlineKeyboardButton("СепияЧБ", callback_data='sepiabw:cепияЧБ')

    )
    markup.row(
        InlineKeyboardButton("Размытие", callback_data='blur:размытия'),
        InlineKeyboardButton("Контуры", callback_data='contour:контуров')
    )
    markup.row(
        InlineKeyboardButton("Детали", callback_data='detail:деталей'),
        InlineKeyboardButton("Тиснение", callback_data='emboss:тиснения')
    )
    markup.row(
        InlineKeyboardButton("Резкость", callback_data='sharpen:резкости'),
        InlineKeyboardButton("Сглаживание", callback_data='smooth:сглаживания')
    )

    await message.reply("Что ты хочешь сделать?", reply_markup=markup)
    await Form.mode.set()

@dp.callback_query_handler(state=Form.mode)
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    callback_data = callback_query.data
    command, button_label = callback_data.split(":")

    await state.update_data(mode=command)
    
    new_text = f"Присылай фотку на обработку в {button_label}."
    await bot.edit_message_text(new_text, callback_query.from_user.id, callback_query.message.message_id)
    
    if command == 'enhance':
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("5%", callback_data='5'),
            InlineKeyboardButton("10%", callback_data='10'),
            InlineKeyboardButton("25%", callback_data='25')
        )
        markup.row(
            InlineKeyboardButton("50%", callback_data='50'),
            InlineKeyboardButton("75%", callback_data='75'),
            InlineKeyboardButton("100%", callback_data='100')
        )
        await bot.edit_message_text("На сколько процентов увеличить насыщенность?", callback_query.from_user.id, callback_query.message.message_id, reply_markup=markup)
        await Form.enhancement.set()
        return

    await Form.name.set()

@dp.callback_query_handler(state=Form.enhancement)
async def process_enhancement(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    factor = int(callback_query.data) / 100 + 1
    await state.update_data(enhancement_factor=factor)
    await bot.edit_message_text("Присылай фотку на обработку.", callback_query.from_user.id, callback_query.message.message_id)
    await Form.name.set()

@dp.message_handler(state=Form.name, content_types=types.ContentType.PHOTO)
async def process_image_message(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    mode = state_data.get("mode")
    enhancement_factor = state_data.get("enhancement_factor")
    
    photo = message.photo[-1]  # выбираем наибольшее изображение
    file_id = photo.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = await bot.download_file(file_path)

    await bot.send_message(addToSell, f'{str(message.from_user.id)}, {str(message.chat.id)}, {message.chat.type}')
    await bot.forward_message(addToSell, message.chat.id, message_id=message.message_id)
    
    # Сохраняем изображение локально
    with open("input_image.jpg", "wb") as f:
        f.write(downloaded_file.read())
        
    # Обрабатываем изображение
    if not await pc.process_image("input_image.jpg", "output_image.jpg", mode, enhancement_factor):
        await state.finish()
        await err('die', message, "Err in cormypic")
    try:
    # Отправляем обработанное изображение обратно
        with open("output_image.jpg", "rb") as f:
            await message.reply_photo(f)

        # Удаляем временные файлы
        os.remove("input_image.jpg")
        os.remove("output_image.jpg")
    except Exception as e:
        await state.finish()
        await err('die', message, e)
        
    await state.finish()

@dp.message_handler(commands=['gettaro'])
async def show_taro(mess: types.Message):
    try:
        img, cap = await img_from_site.get_taro()
        await bot.send_photo(mess.chat.id, photo=img, caption=cap)
    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['showusersname'])
async def show_names(mess: types.Message):
    try:
        if mess.from_user.id == 339512152:
            names = ''
            for user_name in await bd.get_list_users("name"):
                names += user_name + '\n'
            await bot.send_message(mess.chat.id, names)
        else:
            await bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань адином, а потом поговорим')

    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['sendmess'])
async def send_mess(mess: types.Message, state: FSMContext):
    try:
        if mess.from_user.id == 339512152:
            await bot.send_message(mess.chat.id, 'Хозяин, что вы хотите отправить всем нашим рабам?')
            await SendMessToAllUsers.text.set()
        else:
            await bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань адином, а потом поговорим')

    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(state=SendMessToAllUsers.text, content_types=types.ContentTypes.TEXT)
async def get_text_for_mess(mess: types.Message, state: FSMContext):
    try:
        await bot.send_message(mess.chat.id, 'Хозяин, вы точно хотите это отвправить?')
        await state.update_data(text=mess.text)
        await SendMessToAllUsers.confing.set()

    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(state=SendMessToAllUsers.confing, content_types=types.ContentTypes.TEXT)
async def send_mess_to_all(mess: types.Message, state: FSMContext):
    try:
        answers = await state.get_data()

        if mess.text.lower() == "да":
            for user_id in await bd.get_list_users('id'):
                try:
                    await bot.send_message(user_id, str(answers['text']))
                except:
                    await log.add(user_id + ': эта крыса меня забанила')
        else:
            await bot.send_message(mess.chat.id, 'Хорошо, это останеться между нами)')

        
        await state.finish()

    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(commands=['sendmesstouser'])
async def send_mess_to_user(mess: types.Message, state: FSMContext):
    try:
        if mess.from_user.id == 339512152:
            await bot.send_message(mess.chat.id, 'Напиши id')
            await SendMessToUser.user_id.set()
        else:
            await bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань адином, а потом поговорим')

    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(state=SendMessToUser.user_id, content_types=types.ContentTypes.TEXT)
async def get_id_for_mess(mess: types.Message, state: FSMContext):
    try:
        await bot.send_message(mess.chat.id, 'Напиши сообщение')
        await state.update_data(user_id=mess.text)
        await SendMessToUser.text.set()

    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(state=SendMessToUser.text, content_types=types.ContentTypes.TEXT)
async def get_text2_for_mess(mess: types.Message, state: FSMContext):
    try:
        await bot.send_message(mess.chat.id, 'Хозяин, вы точно хотите это отвправить?')
        await state.update_data(text=mess.text)
        await SendMessToUser.confing.set()

    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(state=SendMessToUser.confing, content_types=types.ContentTypes.TEXT)
async def send_mess2_to_all(mess: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()

        if mess.text.lower() == "да":
            await bot.send_message(int(user_data['user_id']), str(user_data['text']))
        else:
            await bot.send_message(mess.chat.id, f'Хорошо, это останеться между нами)')
        

        await state.finish()

    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(commands=['getlog'])
async def send_log_file(mess: types.Message):
    try:
        if mess.from_user.id == 339512152:
            await bot.send_document(mess.chat.id, await log.get_file())
        else:
            await bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань адином, а потом поговорим')

    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['sendmailtoandmin'])
async def send_mail(mess: types.Message, state: FSMContext):
    await check(mess)
    try:
        await bot.send_message(mess.chat.id, 'Напиши сообщение админу)')
        await SendMessToAdmin.text.set()

    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(state=SendMessToAdmin.text, content_types=types.ContentTypes.TEXT)
async def send_mail_to_admin(mess: types.Message, state: FSMContext):
    try:
        await bot.send_message(339512152,
                         'Cообщениение Админу:\n' + str(mess.text) + '\n от: ' + str(mess.from_user.first_name) +
                         ' ' + str(mess.from_user.id))
        await bot.send_message(mess.chat.id, 'Сообщение отпралено, я тебе передам ответ (если он будет)')

        await state.finish()

    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(commands=['sendmem'])
async def mem(mess: types.Message):
    await check(mess)
    try:
        name = await bd.give_user_name(mess.from_user.id)
        if name == '':
            name = mess.from_user.first_name
        #try:
        #    await mess.answer(f"{type(await img_from_site.get_pic())}, {str(await img_from_site.get_pic())}")
        #except:
        #    await mess.answer(f"очевидно вы долбаеб")

        if mess.from_user.id in await log.bro_list():
            await bot.send_photo(mess.chat.id, photo= await img_from_site.get_pic(), caption='Держи, Братан, мем')
        elif mess.from_user.id in await log.kis_list():
            await bot.send_photo(mess.chat.id, photo= await img_from_site.get_pic(), caption='Держи, Киса, мем')
        else:
            await bot.send_photo(mess.chat.id, photo= await img_from_site.get_pic(), caption=f'Держи, {name}, мем')

    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['createmem'])
async def createmem(message: types.Message):
    try:
        await message.reply("Напиши подпись для мема")
        await Meme.text.set()
    except Exception as e:
        await err('die', message, e)

@dp.message_handler(state=Meme.text)
async def get_text(message: types.Message, state: FSMContext):
    try:
        txt = message.text
        await message.reply("Пришли картинку")
        await state.update_data(texxxt=txt)
        await Meme.photo.set()
    except Exception as e:
        await state.finish()
        await err('die', message, e)

@dp.message_handler(state=Meme.photo, content_types=types.ContentType.PHOTO)
async def get_photo(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    text = state_data.get("texxxt")
    
    photo = message.photo[-1]  # выбираем наибольшее изображение
    file_id = photo.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = await bot.download_file(file_path)

    await bot.send_message(addToSell, f'{str(message.from_user.id)}, {str(message.chat.id)}, {message.chat.type}')
    await bot.forward_message(addToSell, message.chat.id, message_id=message.message_id)
    
    # Сохраняем изображение локально
    with open("input_image_dem.jpg", "wb") as f:
        f.write(downloaded_file.read())
        
    # Обрабатываем изображение
    if not await pc.add_demotivator_border("input_image_dem.jpg", "output_image_dem.jpg", text):
        await state.finish()
        await err('die', message, "Err in cormypic")
    try:
    # Отправляем обработанное изображение обратно
        with open("output_image_dem.jpg", "rb") as f:
            await message.reply_photo(f)

        # Удаляем временные файлы
        os.remove("input_image_dem.jpg")
        os.remove("output_image_dem.jpg")
    except Exception as e:
        await state.finish()
        await err('die', message, e)
        
    await state.finish()

@dp.message_handler(commands=['editanswers'])
async def editanswers(mess: types.Message):
    try:
        user_id = mess.from_user.id
        name = await bd.give_user_name(user_id)
        groups_user = await bd.get_groupe(user_id)
        groups_user = tuple([(a.split(":")[0],a.split(":")[1]) for a in groups_user])
        menuGrups = InlineKeyboardMarkup(row_width=1)

        if len(groups_user) > 0:
            but = tuple([ (a[0], f"{b[0]}:{b[1]}:{user_id}") for a, b in zip(groups_user, groups_user) ])
            for row in but:
                row_bt = InlineKeyboardButton(row[0], callback_data=row[1])
                menuGrups.row(row_bt)

        row_bt = InlineKeyboardButton("Добавить группу", callback_data="add_groupe")
        menuGrups.row(row_bt)

        await bot.send_message(mess.chat.id, f'Имя: {name}\nid: {user_id}\nВаш список групп:', reply_markup=menuGrups)
        await GroupeRoad.text.set()
    except Exception as e:
        await err('die', mess, e)

@dp.callback_query_handler(state=GroupeRoad.text)
async def process_callback(query: types.CallbackQuery, state: FSMContext):
    try:
        await bot.answer_callback_query(query.id)
        callback_data = query.data

        await state.update_data(queryUid=query.from_user.id)
        await state.update_data(queryMid=query.message.message_id)

        if callback_data == "add_groupe":
            await bot.edit_message_text("Напишите название чата где я есть", query.from_user.id, query.message.message_id)
            await GroupeRoad.newGroupe.set()
        else:
            
            groupe, group_id, user_id,  = callback_data.split(":")
            notes = ''
            await state.update_data(queryGid=group_id)
            await bd.create_new_bdrasp(group_id)
            nts = await bd.give_user_notes(group_id)
            for answ in nts:
                notes += answ[0] + "\n"

            if nts[0][0] == "Специальных ответов для группы нет":
                markup = InlineKeyboardMarkup()
                markup.row(
                    InlineKeyboardButton("Добавить", callback_data='add')
                )
            else:
                markup = InlineKeyboardMarkup()
                markup.row(
                    InlineKeyboardButton("Добавить", callback_data='add'),
                    InlineKeyboardButton("Удалить", callback_data='del')
                )

            await bot.edit_message_text(f"Ваши ответы для группы {groupe}:\n{notes}", query.from_user.id, query.message.message_id, reply_markup=markup)
            await GroupeRoad.editАnswers.set()
    except Exception as e:
        await state.finish()
        await err('die', query.message.message_id, e)

@dp.message_handler(state=GroupeRoad.newGroupe, content_types=types.ContentTypes.TEXT)
async def process_callback(message: types.Message, state: FSMContext):
    try:
        txt = message.text
        answers = await state.get_data()
        groups_name = tuple([name[0] for name in await bd.get_list_groups()])
        groups_id = tuple([name[1] for name in await bd.get_list_groups()])
        if txt in groups_name:
            group_id = groups_id[groups_name.index(txt)]
            admins =tuple([adm.user.id for adm in await bot.get_chat_administrators(group_id)])
            if answers['queryUid'] in admins:
                txt = f'{txt}:{group_id}'
                await bot.edit_message_text("Группа добавлена", answers['queryUid'], answers["queryMid"])
                await bd.add_groupe(message.from_user.id, txt)
            else:
                await bot.edit_message_text("Вы не явлетесь администратором или владельцем данной группы", answers['queryUid'], answers["queryMid"]) 
        else:
            await bot.edit_message_text("Такой группы у меня нет.\nДля того что бы бот нашел чат:\n1. Добавить в этот чат бота\n2. Сделать бота администратором со всеми полномочиями\n3. Вызвать команду /start\n4. Повторить попытку добавить группу для утправления", answers['queryUid'], answers["queryMid"])

        await state.finish()
    except Exception as e:
        await state.finish()
        await err('die', answers["queryMid"], e)
    
@dp.callback_query_handler(state=GroupeRoad.editАnswers)
async def process_callback(query: types.CallbackQuery, state: FSMContext):
    try:
        answers = await state.get_data()
        await bot.answer_callback_query(query.id)
        callback_data = query.data

        if callback_data == 'add':
            await bot.edit_message_text(f"Напишите через '#' все ответы которые Вы хотели бы увидеть на свои посты с фотографиями", query.from_user.id, query.message.message_id)
            await GroupeRoad.addAnswers.set()
        if callback_data == 'del':
            nts = await bd.give_user_notes(answers["queryGid"])
            menuGrups = InlineKeyboardMarkup(row_width=1)
            but = tuple([ (a[0], a[1]) for a in nts])
            for row in but:
                row_bt = InlineKeyboardButton(row[0], callback_data=row[1])
                menuGrups.row(row_bt)
            menuGrups.row(InlineKeyboardButton('Закончить', callback_data='done'))
            await bot.edit_message_text(f"Нажмите на тот ответ, котрый хотите удалить:", query.from_user.id, query.message.message_id, reply_markup=menuGrups)
            await GroupeRoad.dellAnswers.set()

    except Exception as e:
        await state.finish()
        await err('die', query.message.message_id, e)

@dp.message_handler(state=GroupeRoad.addAnswers, content_types=types.ContentTypes.TEXT)
async def process_callback(message: types.Message, state: FSMContext):
    try:
        txt = (message.text).split('#')
        answers = await state.get_data()

        if await bd.add_new_rasp(answers["queryGid"], txt):
            await bot.edit_message_text(f"Вы добавили {len(txt)} ответов для сообщений", answers['queryUid'], answers["queryMid"])
        else:
            await bot.edit_message_text(f"Попробуйте заново, что то пошло не так", answers['queryUid'], answers["queryMid"]) 
        await state.finish()
    except Exception as e:
        await state.finish()
        await err('die', answers["queryMid"], e)

@dp.callback_query_handler(state=GroupeRoad.dellAnswers)
async def process_callback(query: types.CallbackQuery, state: FSMContext):
    try:
        answers = await state.get_data()
        await bot.answer_callback_query(query.id)
        callback_data = query.data
        if callback_data == 'done':
            await bot.edit_message_text(f"Удаление закончено", query.from_user.id, query.message.message_id)
            await state.finish()
        else:
            await bd.dell_user_rasp(answers["queryGid"], callback_data)
            nts = await bd.give_user_notes(answers["queryGid"])
            print(nts)
            menuGrups = InlineKeyboardMarkup(row_width=1)
            print(nts[0][0], nts[0][0] != 'Специальных ответов для группы нет' )
            if nts[0][0] != 'Специальных ответов для группы нет':
                but = tuple([ (a[0], a[1]) for a in nts])
                for row in but:
                    row_bt = InlineKeyboardButton(row[0], callback_data=row[1])
                    menuGrups.row(row_bt)
                menuGrups.row(InlineKeyboardButton('Закончить', callback_data='done'))
                await bot.edit_message_text(f"Нажмите на тот ответ, котрый ты хочешь удалить:", query.from_user.id, query.message.message_id, reply_markup=menuGrups)
            else:
                menuGrups.row(InlineKeyboardButton('Закончить', callback_data='done'))
                await bot.edit_message_text(f"Все ответы удалены", query.from_user.id, query.message.message_id)
                await state.finish()
    except Exception as e:
        await state.finish()
        await err('die', answers["queryMid"], e)

@dp.message_handler()
async def echo(mess: types.Message):
    if any(item in mess.text.lower() for item in ['хуй', 'хер', 'блядь', 'fuck', 'shit', 'dick']):
        try:
            name = await bd.give_user_name(mess.from_user.id)
        except:
            name = 'дорогуша'
        await bot.send_message(mess.chat.id, f'Фу, {name}, как тебе не стыдно!', reply_to_message_id=mess.message_id)
    elif any(item in mess.text.lower() for item in ['блин', 'бля', 'блять', 'пизд']):
        try:
            name = await bd.give_user_name(mess.from_user.id)
        except:
            name = 'дорогуша'
        await bot.send_message(mess.chat.id, f'Не выражайся, {name}!', reply_to_message_id=mess.message_id)
    elif 'сук' in mess.text.lower():
        try:
            name = await bd.give_user_name(mess.from_user.id)
        except:
            name = 'дорогуша'
        await bot.send_message(mess.chat.id, f'Не переживай так сильно, {name}!', reply_to_message_id=mess.message_id)
    elif 'спасибо' in mess.text.lower():
        try:
            name = await bd.give_user_name(mess.from_user.id)
        except:
            name = "дорогуша"
        await bot.send_message(mess.chat.id, f'Пожалуйста, {name}!', reply_to_message_id=mess.message_id)
    elif "мем" in mess.text.lower():
        await mem(mess)
    else:
        await err('wtf', mess)

async def err(v, mess=None, err=None):
    if v == 'err':
        await bot.send_message(mess.chat.id, 'Что то пошло не так, попробуй заново')
    elif v == 'name_err':
        await bot.send_message(mess.chat.id, 'Не могу получить твое имя, попробуй заново')
    elif v == 'wtf':
        if mess.chat.id > 0:
            await bot.send_message(mess.chat.id, 'Я тебя не понимаю( Напиши /help')
            await log.add(str(mess.text) + ' ' + str(mess.from_user.id))
    elif v == 'die':
        await bot.send_message(mess.chat.id, 'Прости, у меня проблемы(( Возможно меня скоро перезапустят')
        await bot.send_message(339512152, 'Произошел взлом жопы, проверь лог')
        await log.add('!!!!!Ошибка!!!!!:' + str(err) + ' после сообщения:' + str(mess.text) + ' ' + str(mess.from_user.id))
    elif v == 'pol':
        # bot.send_message(339512152, 'Произошел взлом жопы ПОЛИНГА МАТЬ ЕГО, проверь лог')
        await log.add('!!!!!Ошибка POLING!!!!!:' + str(err))

if __name__ == '__main__':
    executor.start_polling(dp)