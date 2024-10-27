import asyncpg
import asyncio
from decouple import config


# pg_manager = DatabaseManager(db_url=config('PG_LINK'), deletion_password=config('ROOT_PASS'))

async def create_connection():
    conn = await asyncpg.connect(dsn=config('PG_LINK'))
    types = await conn.fetch('SELECT * FROM pg_type')
    # print(type(conn))
    return conn


async def check_user(user_id: str, conn):
    ids = await conn.fetch(f'''
        SELECT user_id FROM users
    ''')
    # print(ids)
    ids = {'user_id': [id_['user_id'] for id_ in ids]}
    if user_id in ids["user_id"]:
        # print('user_id')
        return False
    else:
        return True


async def add_users(user_id: str, conn):
    await conn.execute('''
        INSERT INTO users(user_id)
        VALUES($1)
    ''', user_id, )


async def add_word_from_df(df, conn):
    await conn.copy_records_to_table(
        table_name='words',
        records=df.itertuples(index=False),
        columns=df.columns.to_list())


async def get_words(user_id: str, conn):
    # ids = await conn.fetch(f'''
    #         SELECT user_id FROM users
    #     ''')
    check = await check_user(user_id, conn)
    # print(check)
    if check:
        return False
    words = await conn.fetch(f'''
            SELECT word, translation FROM words WHERE user_id = $1
        ''', user_id, )
    words = [dict(word) for word in words]
    return words


async def add_word_from_text(string: list, user_id: str, conn):
    data = [s.split(';')[0::1] for s in string]
    print(*data)
    await conn.executemany('''
            INSERT INTO words(user_id, word, translation)
            VALUES($1, $2, $3)
        ''', [(user_id, d[0], d[1]) for d in data])


async def update_words(string: list, update_type: str, conn):
    if update_type == 'Translation':
        q = '''
        UPDATE words SET translation = $1 WHERE (user_id == $3) AND (word == $2);
        '''
        await conn.executemany(q, *string)
    elif update_type == 'Word':
        q = '''
                UPDATE words SET word = $1 WHERE (user_id == $3) AND (translation == $2);
                '''
        await conn.executemany(q, *string)
# asyncio.get_event_loop().run_until_complete(create_connection())
