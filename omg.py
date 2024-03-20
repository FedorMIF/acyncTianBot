import asyncio
import json
import aiosqlite

async def add_value_to_grups(path_to_bd, user_id, new_value):
    async with aiosqlite.connect(path_to_bd) as connection:
        cur = await connection.cursor()
        # Получаем текущее значение grups
        await cur.execute("SELECT grups FROM users WHERE id = ?", (user_id,))
        row = await cur.fetchone()
        if row:
            # Десериализуем строку обратно в список
            current_grups = json.loads(row[0]) if row[0] else []
            
        await cur.close()
        print(current_grups)

# Пример использования функции
path_to_bd = 'user_data.sqlite'
user_id = '339512152'
new_value = 'new_group_name2'

# Запускаем асинхронную функцию
asyncio.run(add_value_to_grups(path_to_bd, user_id, new_value))
