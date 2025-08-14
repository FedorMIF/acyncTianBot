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
import key

bot = Bot(key.key)  # основа
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
                 '-/playfive - игра 5 букв', '- /mystats - моя статистика в игре 5 букв', '- /gametop - топ игроков в чате',
                 '- /profile - мой профиль и достижения', '- /achievements - все мои достижения',
                 '- /sendmailtoandmin - отправить сообщение админу', '- Попроси "мем" для расслабона и чилла',
                 '-/cormypic - мини фотошоп (beta)',
                 #'- напиши "Поздравление" если хочешь получить новогоднюю картинку'
                 ]
list_commands_adm = [ '- /help - Список всех комманд',
                     #'- /addnote - добавить заметку', '- /showallnotes - посмотреть все текущие заметки',
                     #'- /dellnote - удалить заметку', 
                     '- /showusersname - посомтреть всех юзеров с их id',
                     '- /sendmess - отослать всем сообщение', '- /sendmesstouser - отдельному челу',
                     '- /getlog - получить логфайл', '- /mystats - моя статистика в игре 5 букв', '- /gametop - топ игроков',
                     '- /profile - мой профиль и достижения', '- /achievements - все мои достижения',
                     '- /addachievement - добавить новое достижение', '- /listachievements - список всех достижений',
                     '- Попроси "мем" для расслабона и чилла', '- /tospecial - бро/кис'
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
        # Отслеживаем использование команды
        from datetime import datetime
        current_hour = datetime.now().hour
        is_night = 23 <= current_hour or current_hour <= 6
        await track_activity(mess.from_user.id, "command", 1, 
                           mess.chat.type in ['group', 'supergroup'], is_night)
        
        if mess.from_user.id == key.admin_id:
            await mess.answer(await printlist(list_commands_adm), reply_markup=types.ReplyKeyboardRemove())
        else:
            await mess.answer(await printlist(list_commands), reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['playfive'])
async def send_hi(mess: types.Message, state: FSMContext):
    await check(mess)
    try:
        # Инициализируем таблицу статистики если её нет
        await bd.create_game_stats_table()
        
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
            # Записываем статистику как незавершенную игру
            await bd.update_game_stats(mess.from_user.id, is_completed=False)
            
            # Сбрасываем серию побед
            await track_activity(mess.from_user.id, "win_streak", 0)
            
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
                # Записываем статистику как завершенную игру
                await bd.update_game_stats(mess.from_user.id, is_completed=True)
                
                # Увеличиваем серию побед
                user_stats = await bd.get_or_create_user_stats(mess.from_user.id)
                if user_stats:
                    current_streak = user_stats[12] + 1  # win_streak
                    await track_activity(mess.from_user.id, "win_streak", current_streak)
                
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

@dp.message_handler(content_types=['photo', 'video', 'video_note'])
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

        # Отслеживаем редактирование фото
        await track_activity(message.from_user.id, "photo_edit")

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
        if mess.from_user.id == key.admin_id:
            names = ''
            for user_name in await bd.get_list_users("name"):
                names += user_name + '\n'
            await bot.send_message(mess.chat.id, names)
        else:
            await bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань админом, а потом поговорим')

    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['sendmess'])
async def send_mess(mess: types.Message, state: FSMContext):
    try:
        if mess.from_user.id == key.admin_id:
            await bot.send_message(mess.chat.id, 'Хозяин, что вы хотите отправить всем нашим рабам?')
            await SendMessToAllUsers.text.set()
        else:
            await bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань админом, а потом поговорим')

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
        if mess.from_user.id == key.admin_id:
            await bot.send_message(mess.chat.id, 'Напиши id')
            await SendMessToUser.user_id.set()
        else:
            await bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань админом, а потом поговорим')

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
        await bot.send_message(mess.chat.id, 'Хозяин, вы точно хотите это отправить?')
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
            await bot.send_message(mess.chat.id, f'Хорошо, это останется между нами)')
        

        await state.finish()

    except Exception as e:
        await state.finish()
        await err('die', mess, e)

@dp.message_handler(commands=['getlog'])
async def send_log_file(mess: types.Message):
    try:
        if mess.from_user.id == key.admin_id:
            await bot.send_document(mess.chat.id, await log.get_file())
        else:
            await bot.send_message(mess.chat.id, 'Не твоего поля ягодка, дорогуша. Стань админом, а потом поговорим')

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
        await bot.send_message(key.admin_id,
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

        await track_activity(mess.from_user.id, "meme")

    except Exception as e:
        await bot.send_message(mess.chat.id, f'Сегодня без мемов, {name} 😭')
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

@dp.message_handler(commands=['mystats'])
async def show_my_stats(mess: types.Message):
    """Показать мою статистику в игре 5 букв"""
    await check(mess)
    try:
        await bd.create_game_stats_table()
        stats = await bd.get_user_game_stats(mess.from_user.id)
        name = await bd.give_user_name(mess.from_user.id)
        
        if not stats:
            await bot.send_message(mess.chat.id, f'{name}, ты еще не играл в игру "5 букв"! Попробуй команду /playfive')
            return
        
        total_games = stats[1] + stats[2]  # всего игр
        total_success_rate = (stats[1] / total_games * 100) if total_games > 0 else 0
        
        monthly_games = stats[4] + stats[5]  # игр за месяц
        monthly_success_rate = (stats[4] / monthly_games * 100) if monthly_games > 0 else 0
        
        stats_text = f"""📊 *Статистика игрока {name}*

🎯 *За все время:*
• Всего игр: {total_games}
• Угадано: {stats[1]}
• Не доиграно: {stats[2]}
• Процент успеха: {total_success_rate:.1f}%

📅 *За текущий месяц:*
• Всего игр: {monthly_games}
• Угадано: {stats[4]}
• Не доиграно: {stats[5]}
• Процент успеха: {monthly_success_rate:.1f}%

🗓 Первая игра: {stats[3]}"""
        
        await bot.send_message(mess.chat.id, stats_text, parse_mode="Markdown")
        
    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['gametop'])
async def show_game_top(mess: types.Message):
    """Показать топ игроков в группе"""
    await check(mess)
    try:
        await bd.create_game_stats_table()
        
        # Проверяем является ли это групповым чатом
        if mess.chat.type in ['group', 'supergroup']:
            # Получаем статистику всех игроков
            all_stats = await bd.get_group_members_stats(mess.chat.id)
            
            if not all_stats:
                await bot.send_message(mess.chat.id, f"Пока никто не играл в игру '5 букв'!\nНачните играть командой /playfive")
                return
            
            # Фильтруем только участников этой группы и тех, кто играл
            group_playing_stats = []
            for stat in all_stats:
                user_id = stat[0]
                total_games = stat[2] + stat[3]
                
                # Проверяем только тех, кто хотя бы раз играл
                if total_games > 0:
                    try:
                        # Проверяем является ли пользователь участником этой группы
                        member = await bot.get_chat_member(mess.chat.id, user_id)
                        # Участник группы если статус не 'left' и не 'kicked'
                        if member.status not in ['left', 'kicked']:
                            group_playing_stats.append(stat)
                    except Exception as e:
                        # Если не удалось проверить пользователя, пропускаем его
                        await log.add(f": Error checking user {user_id} in chat {mess.chat.id}: {e}")
                        continue
            
            if not group_playing_stats:
                await bot.send_message(mess.chat.id, f"Пока никто из участников чата '{mess.chat.title}' не играл в игру '5 букв'!\nНачните играть командой /playfive")
                return
            
            # Формируем топ-лист
            top_text = f"🏆 *Топ игроков в игру '5 букв'*\nВ чате: {mess.chat.title}\n\n"
            
            for i, stat in enumerate(group_playing_stats[:10], 1):
                name = stat[1] if stat[1] else f"Игрок {stat[0]}"
                won = stat[2]
                total = stat[2] + stat[3]
                rate = (won / total * 100) if total > 0 else 0
                monthly_won = stat[4]
                monthly_quit = stat[5]
                
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                top_text += f"{emoji} *{name}*\n"
                top_text += f"   За все время: {won} из {total} ({rate:.1f}%)\n"
                top_text += f"   За месяц: {monthly_won} угадано, {monthly_quit} прекращено\n\n"
            
            if len(group_playing_stats) > 10:
                top_text += f"... и еще {len(group_playing_stats) - 10} игроков"
            
        else:
            # Если это личная переписка, показываем общий топ
            all_stats = await bd.get_group_members_stats(0)
            
            if not all_stats:
                await bot.send_message(mess.chat.id, "Пока никто не играл в игру '5 букв'!\nНачните играть командой /playfive")
                return
            
            # Фильтруем только тех, кто хотя бы раз играл
            playing_stats = [stat for stat in all_stats if (stat[2] + stat[3]) > 0]
            
            if not playing_stats:
                await bot.send_message(mess.chat.id, "Пока никто не играл в игру '5 букв'!\nНачните играть командой /playfive")
                return
            
            top_text = f"🏆 *Общий топ игроков в игру '5 букв'*\n\n"
            
            for i, stat in enumerate(playing_stats[:10], 1):
                name = stat[1] if stat[1] else f"Игрок {stat[0]}"
                won = stat[2]
                total = stat[2] + stat[3]
                rate = (won / total * 100) if total > 0 else 0
                monthly_won = stat[4]
                monthly_quit = stat[5]
                
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                top_text += f"{emoji} *{name}*\n"
                top_text += f"   За все время: {won} из {total} ({rate:.1f}%)\n"
                top_text += f"   За месяц: {monthly_won} угадано, {monthly_quit} прекращено\n\n"
        
        await bot.send_message(mess.chat.id, top_text, parse_mode="Markdown")
        
    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['profile'])
async def show_profile(mess: types.Message):
    """Показать полный профиль пользователя"""
    await check(mess)
    try:
        await bd.create_achievements_tables()
        
        profile = await bd.get_user_profile(mess.from_user.id)
        if not profile:
            await bot.send_message(mess.chat.id, "Не удалось загрузить ваш профиль. Попробуйте позже.")
            return
        
        user_info = profile['user_info']
        user_stats = profile['user_stats']
        game_stats = profile['game_stats']
        achievements = profile['achievements']
        
        name = user_info[0] if user_info else f"Пользователь {mess.from_user.id}"
        
        # Формируем профиль
        profile_text = f"👤 *Профиль {name}*\n\n"
        
        if user_stats:
            # Проверяем ночные сообщения
            from datetime import datetime
            current_hour = datetime.now().hour
            is_night = 23 <= current_hour or current_hour <= 6
            
            profile_text += f"📊 *Статистика активности:*\n"
            profile_text += f"💬 Всего сообщений: {user_stats[1]}\n"
            profile_text += f"👥 В группах: {user_stats[2]}\n"
            profile_text += f"🦉 Ночных: {user_stats[3]}\n"
            profile_text += f"📝 Самое длинное: {user_stats[4]} символов\n"
            profile_text += f"😈 Замечаний за мат: {user_stats[5]}\n"
            profile_text += f"⚡ Команд использовано: {user_stats[6]}\n"
            profile_text += f"😂 Мемов запрошено: {user_stats[7]}\n"
            profile_text += f"🎨 Фото отредактировано: {user_stats[8]}\n"
            profile_text += f"📅 Активных дней: {user_stats[11]}\n"
            
            # Отслеживаем активность просмотра профиля
            await track_activity(mess.from_user.id, "command", 1, 
                               mess.chat.type in ['group', 'supergroup'], is_night)
        else:
            profile_text += "📊 Статистика активности пока не собирается.\n"
        
        if game_stats:
            total_games = game_stats[1] + game_stats[2]
            win_rate = (game_stats[1] / total_games * 100) if total_games > 0 else 0
            
            profile_text += f"\n🎮 *Игровая статистика:*\n"
            profile_text += f"🏆 Всего игр: {total_games}\n"
            profile_text += f"✅ Угадано: {game_stats[1]}\n"
            profile_text += f"❌ Не доиграно: {game_stats[2]}\n"
            profile_text += f"📈 Процент побед: {win_rate:.1f}%\n"
            
            if user_stats:
                profile_text += f"🔥 Лучшая серия: {user_stats[13]} побед\n"
                profile_text += f"⚡ Текущая серия: {user_stats[12]} побед\n"
        else:
            profile_text += f"\n🎮 *Игровая статистика:*\nЕще не играли в '5 букв'\n"
        
        # Последние достижения
        if achievements:
            profile_text += f"\n🏅 *Последние достижения:*\n"
            for achievement_id, earned_date in achievements[:3]:
                achievement = bd.ACHIEVEMENTS.get(achievement_id)
                if achievement:
                    profile_text += f"{achievement['icon']} {achievement['name']}\n"
            
            if len(achievements) > 3:
                profile_text += f"... и еще {len(achievements) - 3} достижений\n"
            
            total_achievements = len(bd.get_achievements())
            profile_text += f"\nВсего достижений: {len(achievements)}/{total_achievements}\n"
        else:
            profile_text += f"\n🏅 *Достижения:* Пока нет\n"
        
        profile_text += f"\n💡 Используйте /achievements для просмотра всех достижений"
        
        await bot.send_message(mess.chat.id, profile_text, parse_mode="Markdown")
        
    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['achievements'])
async def show_achievements(mess: types.Message):
    """Показать все достижения пользователя"""
    await check(mess)
    try:
        await bd.create_achievements_tables()
        
        achievements = await bd.get_user_achievements(mess.from_user.id)
        name = await bd.give_user_name(mess.from_user.id)
        
        # Отслеживаем активность
        from datetime import datetime
        current_hour = datetime.now().hour
        is_night = 23 <= current_hour or current_hour <= 6
        await track_activity(mess.from_user.id, "command", 1, 
                           mess.chat.type in ['group', 'supergroup'], is_night)
        
        achievements_text = f"🏆 *Достижения {name}*\n\n"
        
        if achievements:
            earned_ids = {achievement[0] for achievement in achievements}
            
            # Получаем достижения, сгруппированные по категориям
            categories = bd.get_achievements_by_category()
            all_achievements = bd.get_achievements()
            
            for category, achievement_ids in categories.items():
                achievements_text += f"*{category}:*\n"
                category_has_achievements = False
                
                for achievement_id in achievement_ids:
                    achievement = all_achievements.get(achievement_id)
                    if achievement:
                        if achievement_id in earned_ids:
                            achievement_text = f"✅ {achievement['icon']} {achievement['name']}"
                            # Находим дату получения
                            for ach_id, date in achievements:
                                if ach_id == achievement_id:
                                    achievement_text += f" _{date[:10]}_"
                                    break
                            achievements_text += f"{achievement_text}\n"
                            category_has_achievements = True
                        else:
                            achievements_text += f"⬜ {achievement['icon']} {achievement['name']} _{achievement['desc']}_\n"
                
                if not category_has_achievements:
                    achievements_text += "_Пока нет достижений в этой категории_\n"
                
                achievements_text += "\n"
            
            total_achievements = len(all_achievements)
            progress = f"{len(achievements)}/{total_achievements}"
            achievements_text += f"📊 *Прогресс:* {progress} ({len(achievements)/total_achievements*100:.1f}%)"
            
        else:
            achievements_text += "У вас пока нет достижений.\n\n"
            achievements_text += "🎯 *Получите первое достижение:*\n"
            achievements_text += "💬 Напишите 100 сообщений - получите *'Болтун'*\n"
            achievements_text += "🎮 Сыграйте в игру /playfive - получите *'Новичок'*\n"
            achievements_text += "😂 Попросите мем - начните путь к *'Мем-мастер'*"
        
        await bot.send_message(mess.chat.id, achievements_text, parse_mode="Markdown")
        
    except Exception as e:
        await err('die', mess, e)

@dp.message_handler()
async def echo(mess: types.Message):
    # Отслеживаем активность для всех сообщений
    from datetime import datetime
    current_hour = datetime.now().hour
    is_night = 23 <= current_hour or current_hour <= 6
    is_group = mess.chat.type in ['group', 'supergroup']
    message_length = len(mess.text) if mess.text else 0
    
    if any(item in mess.text.lower() for item in ['хуй', 'хер', 'блядь', 'fuck', 'shit', 'dick']):
        try:
            name = await bd.give_user_name(mess.from_user.id)
        except:
            name = 'дорогуша'
        
        # Отслеживаем сообщение и серьезное предупреждение за мат
        await track_activity(mess.from_user.id, "message", message_length, is_group, is_night)
        await track_activity(mess.from_user.id, "profanity")
        
        await bot.send_message(mess.chat.id, f'Фу, {name}, как тебе не стыдно!', reply_to_message_id=mess.message_id)
        
    elif any(item in mess.text.lower() for item in ['блин', 'бля', 'блять', 'пизд']):
        try:
            name = await bd.give_user_name(mess.from_user.id)
        except:
            name = 'дорогуша'
        
        # Отслеживаем сообщение и легкое предупреждение за мат
        await track_activity(mess.from_user.id, "message", message_length, is_group, is_night)
        await track_activity(mess.from_user.id, "profanity")
        
        await bot.send_message(mess.chat.id, f'Не выражайся, {name}!', reply_to_message_id=mess.message_id)
        
    elif 'сук' in mess.text.lower():
        try:
            name = await bd.give_user_name(mess.from_user.id)
        except:
            name = 'дорогуша'
        
        # Отслеживаем сообщение и предупреждение
        await track_activity(mess.from_user.id, "message", message_length, is_group, is_night)
        await track_activity(mess.from_user.id, "profanity")
        
        await bot.send_message(mess.chat.id, f'Не переживай так сильно, {name}!', reply_to_message_id=mess.message_id)
        
    elif 'спасибо' in mess.text.lower():
        try:
            name = await bd.give_user_name(mess.from_user.id)
        except:
            name = "дорогуша"
        
        # Отслеживаем вежливое сообщение
        await track_activity(mess.from_user.id, "message", message_length, is_group, is_night)
        
        await bot.send_message(mess.chat.id, f'Пожалуйста, {name}!', reply_to_message_id=mess.message_id)
        
    elif "мем" in mess.text.lower():
        # Отслеживаем сообщение и запрос мема
        await track_activity(mess.from_user.id, "message", message_length, is_group, is_night)
        await track_activity(mess.from_user.id, "meme")
        await mem(mess)
        
    else:
        # Отслеживаем обычное сообщение
        await track_activity(mess.from_user.id, "message", message_length, is_group, is_night)
        await err('wtf', mess)

@dp.message_handler(commands=['addachievement'])
async def add_achievement_command(mess: types.Message):
    """Добавить новое достижение (только для админа)"""
    await check(mess)
    try:
        if mess.from_user.id != 339512152:  # Только для админа
            await bot.send_message(mess.chat.id, "❌ Эта команда доступна только администратору")
            return
        
        # Показываем справку по использованию команды
        help_text = """🔧 *Добавление нового достижения*

Формат команды:
`/addachievement ID|Название|Описание|Эмодзи|Категория|Порог|Статистика`

*Параметры:*
• ID - уникальный идентификатор (например: super_user_1)
• Название - название достижения
• Описание - подробное описание
• Эмодзи - иконка достижения
• Категория - communication/gaming/behavior/group
• Порог - число для достижения
• Статистика - поле статистики (total_messages, games_played и т.д.)

*Пример:*
`/addachievement super_user_1|Супер пользователь|Отправить 10000 сообщений|⭐|communication|10000|total_messages`

*Доступные категории:*
• communication - За общение
• gaming - За игры  
• behavior - За поведение
• group - Групповые

*Доступные поля статистики:*
• total_messages, group_messages, night_messages
• profanity_warnings, commands_used, memes_requested
• photos_edited, active_days, max_win_streak
• games_played, games_quit, win_rate_percentage"""
        
        await bot.send_message(mess.chat.id, help_text, parse_mode="Markdown")
        
    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(lambda message: message.text and message.text.startswith('/addachievement '))
async def process_add_achievement(mess: types.Message):
    """Обработать добавление достижения"""
    await check(mess)
    try:
        if mess.from_user.id != 339512152:  # Только для админа
            return
        
        # Парсим параметры
        command_text = mess.text[len('/addachievement '):]
        params = command_text.split('|')
        
        if len(params) != 7:
            await bot.send_message(mess.chat.id, "❌ Неверное количество параметров. Используйте /addachievement для справки.")
            return
        
        achievement_id, name, description, icon, category, threshold_str, stat = [p.strip() for p in params]
        
        try:
            threshold = int(threshold_str)
        except ValueError:
            await bot.send_message(mess.chat.id, "❌ Порог должен быть числом")
            return
        
        # Проверяем корректность категории
        valid_categories = ['communication', 'gaming', 'behavior', 'group']
        if category not in valid_categories:
            await bot.send_message(mess.chat.id, f"❌ Неверная категория. Доступные: {', '.join(valid_categories)}")
            return
        
        # Добавляем достижение
        success = bd.add_achievement(achievement_id, name, description, icon, category, threshold, stat)
        
        if success:
            await bot.send_message(mess.chat.id, f"✅ Достижение '{name}' успешно добавлено!\n\n{icon} *{name}*\n_{description}_\nПорог: {threshold} ({stat})", parse_mode="Markdown")
            await log.add(f": Admin {mess.from_user.id} added achievement {achievement_id}")
        else:
            await bot.send_message(mess.chat.id, "❌ Ошибка при добавлении достижения")
        
    except Exception as e:
        await err('die', mess, e)

@dp.message_handler(commands=['listachievements'])
async def list_achievements_command(mess: types.Message):
    """Показать все достижения из конфигурации (только для админа)"""
    await check(mess)
    try:
        if mess.from_user.id != 339512152:  # Только для админа
            await bot.send_message(mess.chat.id, "❌ Эта команда доступна только администратору")
            return
        
        config = bd.load_achievements_config()
        achievements = config.get('achievements', {})
        
        if not achievements:
            await bot.send_message(mess.chat.id, "📝 Список достижений пуст")
            return
        
        text = "📋 *Все достижения в конфигурации:*\n\n"
        
        # Группируем по категориям
        categories = bd.get_achievements_by_category()
        
        for category_name, achievement_ids in categories.items():
            text += f"*{category_name}:*\n"
            for achievement_id in achievement_ids:
                achievement = achievements.get(achievement_id, {})
                enabled = "✅" if achievement.get('enabled', True) else "❌"
                text += f"{enabled} `{achievement_id}` - {achievement.get('icon', '')} {achievement.get('name', '')}\n"
            text += "\n"
        
        await bot.send_message(mess.chat.id, text, parse_mode="Markdown")
        
    except Exception as e:
        await err('die', mess, e)

# ===== СИСТЕМА ДОСТИЖЕНИЙ =====

async def notify_achievements(user_id, new_achievements):
    """Уведомить пользователя о новых достижениях"""
    if not new_achievements:
        return
    
    achievements_config = bd.get_achievements()
    for achievement_id in new_achievements:
        achievement = achievements_config.get(achievement_id)
        if achievement:
            achievement_text = f"🎉 *Новое достижение!*\n\n{achievement['icon']} *{achievement['name']}*\n_{achievement['desc']}_"
            try:
                await bot.send_message(user_id, achievement_text, parse_mode="Markdown")
            except Exception as e:
                await log.add(f": Error sending achievement notification to {user_id}: {e}")

async def track_activity(user_id, activity_type, value=1, is_group=False, is_night=False):
    """Отследить активность пользователя и проверить достижения"""
    try:
        # Инициализируем таблицы достижений если их нет
        await bd.create_achievements_tables()
        
        # Обновляем статистику и получаем новые достижения
        new_achievements = await bd.update_user_activity(user_id, activity_type, value, is_group, is_night)
        
        # Уведомляем о новых достижениях
        if new_achievements:
            await notify_achievements(user_id, new_achievements)
            
    except Exception as e:
        await log.add(f": Error tracking activity for {user_id}: {e}")

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