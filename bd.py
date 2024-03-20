import re
import aiosqlite
import log
from sqlite3 import Error
import json

path_to_bd = 'user_data.sqlite'

async def create_connection(path):
    connection = None
    try:
        connection = await aiosqlite.connect(path)
    except Error as e:
        await log.add(f": The error '{e}' occur")
    return connection

async def add_new_user(user_id, name):
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    good = False
    try:
        if await give_user_name(user_id) == '':
            val = [(int(user_id), str(name), 'yes' if user_id > 0 else 'no', None)]
            await cur.executemany("INSERT INTO users VALUES (?,?,?,?)", val)
            await connection.commit()
            await log.add(f": Add new user{user_id} aka {name} successful")
            good = True
        else:
            await connection.close()
            return "double"
    except Error as e:
        await log.add(f": The error '{e}' occur")
    await connection.close()
    return good

async def edit_user_name(user_id, name):
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    good = False
    try:
        val = [(str(name), int(user_id))]
        await cur.executemany("UPDATE users SET name = ? WHERE id = ?", val)
        await connection.commit()
        await log.add(f": Edit new user{user_id} aka {name} successful")
        #print(f"Edit new user{user_id} aka {name} successful")
        good = True
    except Error as e:
        await log.add(f": The error '{e}' occur")
    await connection.close()
    return good

async def create_new_bdrasp(user_id):
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    good = False
    user_id = str(user_id)[1:]
    try:
        await cur.execute(f"CREATE TABLE groupe{user_id} ( id integer primary key, answers text)")
        await connection.commit()
        good = True
    except Error as e:
        await log.add(f": The error create_new_bdrasp '{e}' occur")
    await connection.close()
    return good

async def add_new_rasp(user_id, data):
    user_id = str(user_id)[1:]
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    good = False
    try:
        for answ in data:
            await cur.execute(f"INSERT INTO groupe{user_id} (answers) VALUES ('{answ}')")
            await connection.commit()
        good = True
    except Error as e:
        await log.add(f": The error add_new_rasp '{e}' occur")
    await connection.close()
    return good

async def dell_user_rasp(user_id, note_id):
    user_id = str(user_id)[1:]
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    good = False
    try:
        await cur.execute(f"DELETE FROM groupe{user_id} WHERE id = {note_id}")
        await connection.commit()
        good = True
    except Error as e:
        await log.add(f": The error dell_user_rasp '{e}' occur")
    await connection.close()
    return good

async def give_user_notes(user_id):
    user_id = str(user_id)[1:]
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    row = [["Специальных ответов для группы нет"]]
    try:
        await cur.execute(f"SELECT answers, id FROM groupe{user_id}")
        row = await cur.fetchall()
        if len(row) == 0:
            row = [["Специальных ответов для группы нет"]]
        await connection.close()
    except Error as e:
        await connection.close()
        await log.add(f": The error give_user_notes '{e}' occur")
    return row

async def give_user_name(user_id):
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    name = 'err'
    try:
        await cur.execute(f"SELECT name FROM users WHERE id = '{user_id}'")
        await connection.commit()
        mess = await cur.fetchall()
        name_row = ''.join(str(x) for x in mess)
        name = ''
        i = 0
        for i in range(0, len(name_row)):
            if name_row[i] == ('('):
                continue
            elif name_row[i] == (','):
                continue
            elif name_row[i] == ("'"):
                continue
            elif name_row[i] == (')'):
                continue
            name += name_row[i]
    except Error as e:
        await log.add(f": The error '{e}' occur")
    await connection.close()
    return name

async def add_groupe(user_id, data):
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    good = False
    print(data)
    try:
        await cur.execute("SELECT grups FROM users WHERE id = ?", (user_id,))
        row = await cur.fetchone()
        if row:
            current_grups = json.loads(row[0]) if row[0] else []
            if data not in current_grups:
                current_grups.append(data)
                updated_grups_str = json.dumps(current_grups)
                print(current_grups, updated_grups_str)
                await cur.execute("UPDATE users SET grups = ? WHERE id = ?", (updated_grups_str, user_id))
                await connection.commit()
        good = True
    except Error as e:
        await log.add(f": The error '{e}' occur")
    await connection.close()
    return good

async def get_groupe(user_id):
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    try:
        await cur.execute("SELECT grups FROM users WHERE id = ?", (user_id,))
        row = await cur.fetchone()
        if row:
            current_grups = json.loads(row[0]) if row[0] else []

        await connection.close()
        return current_grups
    except Error as e:
        await connection.close()
        await log.add(f": The error '{e}' occur")

async def get_list_groups():
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    row = "err"
    try:
        await cur.execute(f'SELECT name, id FROM users WHERE id < 0')
        row = await cur.fetchall()
        await connection.close()
    except Error as e:
        await connection.close()
        await log.add(f": The error '{e}' occur")
    
    return row
   
async def get_list_users(var):
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    list_users_new = ['Ошибка']
    try:
        if var == 'id':
            await cur.execute(f'SELECT {var} FROM users')
        else:
            await cur.execute(f'SELECT name, id FROM users')
        await connection.commit()
        list_users = await cur.fetchall()
        list_users_new.clear()
        for st in list_users:
            st = re.sub(r',', '', str(st))
            st = re.sub(r'\(', '', str(st))
            st = re.sub(r'\)', '', str(st))
            st = re.sub(r"'", '', str(st))
            list_users_new.append(st)
    except Error as e:
        await log.add(f": The error '{e}' occur")
    await connection.close()
    return list_users_new
