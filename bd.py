import re
import aiosqlite
import log
from sqlite3 import Error
import json
import key

path_to_bd = key.path_to_bd

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
        #await log.add(f": The error create_new_bdrasp '{e}' occur")
        pass
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

async def create_game_stats_table():
    """Создание таблицы статистики игр"""
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    try:
        await cur.execute("""
            CREATE TABLE IF NOT EXISTS game_stats (
                user_id INTEGER PRIMARY KEY,
                total_games_played INTEGER DEFAULT 0,
                total_games_quit INTEGER DEFAULT 0,
                first_game_date TEXT,
                monthly_games_played INTEGER DEFAULT 0,
                monthly_games_quit INTEGER DEFAULT 0,
                monthly_reset_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        await connection.commit()
        await log.add(": Created game_stats table successfully")
    except Error as e:
        await log.add(f": The error creating game_stats table '{e}' occur")
    await connection.close()

async def get_or_create_game_stats(user_id):
    """Получить или создать статистику игрока"""
    from datetime import datetime
    
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Проверяем существует ли запись
        await cur.execute("SELECT * FROM game_stats WHERE user_id = ?", (user_id,))
        stats = await cur.fetchone()
        
        if not stats:
            # Создаем новую запись
            await cur.execute("""
                INSERT INTO game_stats 
                (user_id, first_game_date, monthly_reset_date) 
                VALUES (?, ?, ?)
            """, (user_id, current_date, current_date))
            await connection.commit()
            
            # Получаем созданную запись
            await cur.execute("SELECT * FROM game_stats WHERE user_id = ?", (user_id,))
            stats = await cur.fetchone()
        
        await connection.close()
        return stats
    except Error as e:
        await connection.close()
        await log.add(f": The error get_or_create_game_stats '{e}' occur")
        return None

async def update_game_stats(user_id, is_completed):
    """Обновить статистику игрока"""
    from datetime import datetime
    
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    current_date = datetime.now()
    current_month = current_date.strftime('%Y-%m')
    
    try:
        # Получаем текущую статистику
        stats = await get_or_create_game_stats(user_id)
        if not stats:
            await connection.close()
            return False
        
        # Проверяем нужно ли сбросить месячные счетчики
        monthly_reset_date = datetime.strptime(stats[6], '%Y-%m-%d') if stats[6] else current_date
        stats_month = monthly_reset_date.strftime('%Y-%m')
        
        if current_month != stats_month:
            # Сбрасываем месячные счетчики
            await cur.execute("""
                UPDATE game_stats 
                SET monthly_games_played = 0, 
                    monthly_games_quit = 0, 
                    monthly_reset_date = ?
                WHERE user_id = ?
            """, (current_date.strftime('%Y-%m-%d'), user_id))
        
        # Обновляем статистику
        if is_completed:
            await cur.execute("""
                UPDATE game_stats 
                SET total_games_played = total_games_played + 1,
                    monthly_games_played = monthly_games_played + 1
                WHERE user_id = ?
            """, (user_id,))
        else:
            await cur.execute("""
                UPDATE game_stats 
                SET total_games_quit = total_games_quit + 1,
                    monthly_games_quit = monthly_games_quit + 1
                WHERE user_id = ?
            """, (user_id,))
        
        await connection.commit()
        await connection.close()
        return True
    except Error as e:
        await connection.close()
        await log.add(f": The error update_game_stats '{e}' occur")
        return False

async def get_user_game_stats(user_id):
    """Получить статистику конкретного игрока"""
    from datetime import datetime
    
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    
    try:
        await cur.execute("SELECT * FROM game_stats WHERE user_id = ?", (user_id,))
        stats = await cur.fetchone()
        
        if stats:
            # Проверяем актуальность месячной статистики
            current_month = datetime.now().strftime('%Y-%m')
            reset_date = datetime.strptime(stats[6], '%Y-%m-%d') if stats[6] else datetime.now()
            stats_month = reset_date.strftime('%Y-%m')
            
            if current_month != stats_month:
                # Сбрасываем месячные счетчики
                await cur.execute("""
                    UPDATE game_stats 
                    SET monthly_games_played = 0, 
                        monthly_games_quit = 0, 
                        monthly_reset_date = ?
                    WHERE user_id = ?
                """, (datetime.now().strftime('%Y-%m-%d'), user_id))
                await connection.commit()
                
                # Получаем обновленную статистику
                await cur.execute("SELECT * FROM game_stats WHERE user_id = ?", (user_id,))
                stats = await cur.fetchone()
        
        await connection.close()
        return stats
    except Error as e:
        await connection.close()
        await log.add(f": The error get_user_game_stats '{e}' occur")
        return None

async def get_group_members_stats(group_id):
    """Получить статистику всех участников группы"""
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    
    try:
        # Получаем список всех пользователей которые есть в базе
        await cur.execute("""
            SELECT u.id, u.name, 
                   COALESCE(gs.total_games_played, 0) as total_played,
                   COALESCE(gs.total_games_quit, 0) as total_quit,
                   COALESCE(gs.monthly_games_played, 0) as monthly_played,
                   COALESCE(gs.monthly_games_quit, 0) as monthly_quit
            FROM users u
            LEFT JOIN game_stats gs ON u.id = gs.user_id
            WHERE u.id > 0
            ORDER BY total_played DESC, monthly_played DESC
        """)
        
        results = await cur.fetchall()
        await connection.close()
        return results
    except Error as e:
        await connection.close()
        await log.add(f": The error get_group_members_stats '{e}' occur")
        return []

# ===== СИСТЕМА ДОСТИЖЕНИЙ =====

async def create_achievements_tables():
    """Создание таблиц для системы достижений"""
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    try:
        # Таблица статистики пользователей
        await cur.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                total_messages INTEGER DEFAULT 0,
                group_messages INTEGER DEFAULT 0,
                night_messages INTEGER DEFAULT 0,
                max_message_length INTEGER DEFAULT 0,
                profanity_warnings INTEGER DEFAULT 0,
                commands_used INTEGER DEFAULT 0,
                memes_requested INTEGER DEFAULT 0,
                photos_edited INTEGER DEFAULT 0,
                first_activity_date TEXT,
                last_activity_date TEXT,
                active_days INTEGER DEFAULT 0,
                win_streak INTEGER DEFAULT 0,
                max_win_streak INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Таблица достижений пользователей
        await cur.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                achievement_id TEXT,
                earned_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, achievement_id)
            )
        """)
        
        await connection.commit()
        await log.add(": Created achievements tables successfully")
    except Error as e:
        await log.add(f": The error creating achievements tables '{e}' occur")
    await connection.close()

# Загрузка конфигурации достижений
_achievements_config = None

def load_achievements_config():
    """Загрузить конфигурацию достижений из файла"""
    global _achievements_config
    if _achievements_config is None:
        try:
            import json
            import os
            
            config_path = os.path.join(os.path.dirname(__file__), 'achievements.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                _achievements_config = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки конфигурации достижений: {e}")
            _achievements_config = {"categories": {}, "achievements": {}}
    
    return _achievements_config

def get_achievements():
    """Получить все активные достижения"""
    config = load_achievements_config()
    achievements = {}
    
    for achievement_id, achievement_data in config.get('achievements', {}).items():
        if achievement_data.get('enabled', True):
            # Преобразуем формат для совместимости
            achievements[achievement_id] = {
                "name": achievement_data.get('name', ''),
                "desc": achievement_data.get('description', ''),
                "icon": achievement_data.get('icon', ''),
                "threshold": achievement_data.get('threshold', 0),
                "stat": achievement_data.get('stat', ''),
                "category": achievement_data.get('category', ''),
                "special_condition": achievement_data.get('special_condition', None)
            }
    
    return achievements

def get_achievements_by_category():
    """Получить достижения, сгруппированные по категориям"""
    config = load_achievements_config()
    categories = config.get('categories', {})
    achievements = get_achievements()
    
    result = {}
    for category_id, category_data in categories.items():
        category_achievements = []
        for achievement_id, achievement_data in achievements.items():
            if achievement_data.get('category') == category_id:
                category_achievements.append(achievement_id)
        
        if category_achievements:  # Только категории с достижениями
            result[category_data['name']] = category_achievements
    
    return result

def add_achievement(achievement_id, name, description, icon, category, threshold, stat, enabled=True, special_condition=None):
    """Добавить новое достижение в конфигурацию"""
    import json
    import os
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'achievements.json')
        config = load_achievements_config()
        
        # Добавляем новое достижение
        config['achievements'][achievement_id] = {
            "name": name,
            "description": description,
            "icon": icon,
            "category": category,
            "threshold": threshold,
            "stat": stat,
            "enabled": enabled
        }
        
        if special_condition:
            config['achievements'][achievement_id]['special_condition'] = special_condition
        
        # Сохраняем обратно в файл
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # Сбрасываем кэш
        global _achievements_config
        _achievements_config = None
        
        return True
    except Exception as e:
        print(f"Ошибка добавления достижения: {e}")
        return False

# Для обратной совместимости (используйте get_achievements() для получения актуальных данных)
ACHIEVEMENTS = {}

async def get_or_create_user_stats(user_id):
    """Получить или создать статистику пользователя"""
    from datetime import datetime
    
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        await cur.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
        stats = await cur.fetchone()
        
        if not stats:
            await cur.execute("""
                INSERT INTO user_stats 
                (user_id, first_activity_date, last_activity_date) 
                VALUES (?, ?, ?)
            """, (user_id, current_date, current_date))
            await connection.commit()
            
            await cur.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
            stats = await cur.fetchone()
        
        await connection.close()
        return stats
    except Error as e:
        await connection.close()
        await log.add(f": The error get_or_create_user_stats '{e}' occur")
        return None

async def update_user_activity(user_id, activity_type, value=1, is_group=False, is_night=False):
    """Обновить активность пользователя"""
    from datetime import datetime
    
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Получаем текущую статистику
        stats = await get_or_create_user_stats(user_id)
        if not stats:
            await connection.close()
            return []
        
        # Проверяем, нужно ли увеличить счетчик активных дней
        last_activity = stats[10]  # last_activity_date
        active_days = stats[11]  # active_days
        if last_activity != current_date:
            active_days += 1
            await cur.execute("""
                UPDATE user_stats 
                SET active_days = ?, last_activity_date = ?
                WHERE user_id = ?
            """, (active_days, current_date, user_id))
        
        # Обновляем статистику в зависимости от типа активности
        updates = []
        new_achievements = []
        
        if activity_type == "message":
            await cur.execute("""
                UPDATE user_stats 
                SET total_messages = total_messages + 1,
                    group_messages = group_messages + ?,
                    night_messages = night_messages + ?,
                    max_message_length = MAX(max_message_length, ?)
                WHERE user_id = ?
            """, (1 if is_group else 0, 1 if is_night else 0, value, user_id))
            
        elif activity_type == "profanity":
            await cur.execute("""
                UPDATE user_stats 
                SET profanity_warnings = profanity_warnings + 1
                WHERE user_id = ?
            """, (user_id,))
            
        elif activity_type == "command":
            await cur.execute("""
                UPDATE user_stats 
                SET commands_used = commands_used + 1
                WHERE user_id = ?
            """, (user_id,))
            
        elif activity_type == "meme":
            await cur.execute("""
                UPDATE user_stats 
                SET memes_requested = memes_requested + 1
                WHERE user_id = ?
            """, (user_id,))
            
        elif activity_type == "photo_edit":
            await cur.execute("""
                UPDATE user_stats 
                SET photos_edited = photos_edited + 1
                WHERE user_id = ?
            """, (user_id,))
            
        elif activity_type == "win_streak":
            await cur.execute("""
                UPDATE user_stats 
                SET win_streak = ?,
                    max_win_streak = MAX(max_win_streak, ?)
                WHERE user_id = ?
            """, (value, value, user_id))
            
        await connection.commit()
        
        # Проверяем новые достижения
        new_achievements = await check_achievements(user_id)
        
        await connection.close()
        return new_achievements
        
    except Error as e:
        await connection.close()
        await log.add(f": The error update_user_activity '{e}' occur")
        return []

async def check_achievements(user_id):
    """Проверить и выдать новые достижения"""
    from datetime import datetime
    
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    new_achievements = []
    
    try:
        # Получаем текущую статистику
        await cur.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
        stats = await cur.fetchone()
        if not stats:
            await connection.close()
            return []
        
        # Получаем игровую статистику
        await cur.execute("""
            SELECT total_games_played + total_games_quit as total_games,
                   total_games_played,
                   total_games_quit,
                   ROUND(CAST(total_games_played AS FLOAT) / 
                         CAST(total_games_played + total_games_quit AS FLOAT) * 100, 1) as win_rate
            FROM game_stats WHERE user_id = ?
        """, (user_id,))
        game_stats = await cur.fetchone()
        
        # Создаем словарь статистики для проверки
        user_stats_dict = {
            "total_messages": stats[1],
            "group_messages": stats[2],
            "night_messages": stats[3],
            "max_message_length": stats[4],
            "profanity_warnings": stats[5],
            "commands_used": stats[6],
            "memes_requested": stats[7],
            "photos_edited": stats[8],
            "active_days": stats[11],
            "max_win_streak": stats[13],
            "games_played": game_stats[0] if game_stats else 0,
            "games_quit": game_stats[2] if game_stats else 0,
            "win_rate_percentage": game_stats[3] if game_stats else 0
        }
        
        # Получаем уже полученные достижения
        await cur.execute("SELECT achievement_id FROM user_achievements WHERE user_id = ?", (user_id,))
        earned_achievements = {row[0] for row in await cur.fetchall()}
        
        # Получаем актуальные достижения из конфигурации
        achievements = get_achievements()
        
        # Проверяем каждое достижение
        for achievement_id, achievement in achievements.items():
            if achievement_id not in earned_achievements:
                stat_value = user_stats_dict.get(achievement["stat"], 0)
                
                # Проверяем специальные условия
                meets_special_condition = True
                if achievement.get("special_condition"):
                    if achievement["special_condition"] == "min_games_20":
                        meets_special_condition = user_stats_dict.get("games_played", 0) >= 20
                
                if stat_value >= achievement["threshold"] and meets_special_condition:
                    # Выдаем достижение
                    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    await cur.execute("""
                        INSERT INTO user_achievements (user_id, achievement_id, earned_date)
                        VALUES (?, ?, ?)
                    """, (user_id, achievement_id, current_date))
                    new_achievements.append(achievement_id)
        
        await connection.commit()
        await connection.close()
        return new_achievements
        
    except Error as e:
        await connection.close()
        await log.add(f": The error check_achievements '{e}' occur")
        return []

async def get_user_achievements(user_id):
    """Получить все достижения пользователя"""
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    
    try:
        await cur.execute("""
            SELECT achievement_id, earned_date 
            FROM user_achievements 
            WHERE user_id = ? 
            ORDER BY earned_date DESC
        """, (user_id,))
        
        results = await cur.fetchall()
        await connection.close()
        return results
    except Error as e:
        await connection.close()
        await log.add(f": The error get_user_achievements '{e}' occur")
        return []

async def get_user_profile(user_id):
    """Получить полный профиль пользователя"""
    connection = await create_connection(path_to_bd)
    cur = await connection.cursor()
    
    try:
        # Основная информация о пользователе
        await cur.execute("SELECT name FROM users WHERE id = ?", (user_id,))
        user_info = await cur.fetchone()
        
        # Статистика активности
        await cur.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
        user_stats = await cur.fetchone()
        
        # Игровая статистика
        await cur.execute("SELECT * FROM game_stats WHERE user_id = ?", (user_id,))
        game_stats = await cur.fetchone()
        
        # Достижения
        await cur.execute("""
            SELECT achievement_id, earned_date 
            FROM user_achievements 
            WHERE user_id = ? 
            ORDER BY earned_date DESC
        """, (user_id,))
        achievements = await cur.fetchall()
        
        await connection.close()
        return {
            "user_info": user_info,
            "user_stats": user_stats,
            "game_stats": game_stats,
            "achievements": achievements
        }
    except Error as e:
        await connection.close()
        await log.add(f": The error get_user_profile '{e}' occur")
        return None
