import re
import aiosqlite
import log
from sqlite3 import Error
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
            val = [(int(user_id), str(name))]
            await cur.executemany("INSERT INTO users VALUES (?,?)", val)
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
    try:
        await cur.execute(f"CREATE TABLE user{user_id} ( id integer primary key, name text, time text)")
        await connection.commit()
        await log.add(f": Connection to {user_id} DB successful")
        good = True
    except Error as e:
        await log.add(f": The error '{e}' occur")
    await connection.close()
    return good


async def add_new_rasp(user_id, data, note):
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    good = False
    try:
        await cur.execute(f"INSERT INTO user{user_id} (name, time) VALUES ('{note}', '{data}')")
        await connection.commit()
        await log.add(f": Add new rasp to user{user_id}: {note}, {data} successful")
        good = True
    except Error as e:
        await log.add(f": The error '{e}' occur")
    await connection.close()
    return good


async def dell_user_rasp(user_id, note_id):
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    good = False
    try:
        await cur.execute(f"DELETE FROM user{user_id} WHERE id = {note_id}")
        await connection.commit()
        await log.add(f": Dell note by user{user_id} on id={note_id} successful")
        good = True
    except Error as e:
        await log.add(f": The error '{e}' occur")
    await connection.close()
    return good


async def give_user_notes(user_id):
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    list_users_new = ['Ошибка']
    try:
        await cur.execute(f'SELECT id, name, time FROM user{user_id}')
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
