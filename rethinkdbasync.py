import asyncio
import logging
from os import environ as env
from rethinkdb import RethinkDB
from rethinkdb.asyncio_net.net_asyncio import AsyncioCursor


class RethinDBWork(object):
    """Класс для работы с данными из RethinDB"""
    def __init__(self):
        self.log = logging
        self.db = RethinkDB()
        self.format = '%(asctime)s.%(msecs)d|\
%(levelname)s|%(module)s.%(funcName)s:%(lineno)d %(message)s'
        self.log.basicConfig(level=logging.INFO,
                             format=self.format,
                             datefmt='%Y-%m-%d %H:%M:%S')
        self.host = env.get('RETHINKDB_HOST')
        self.port = env.get('RETHINKDB_PORT01')
        self.dbname = env.get('RETHINKDB_DBNAME')
        self.table = env.get('RETHINKDB_TABLE')
        self.row_item = 'data'
        self.row_carid = 'CarId'
        self.row_objectid = 'ObjectID'

    async def connect(self):
        """Подключение к RethinDB"""
        try:
            self.db.set_loop_type('asyncio')
            self.conn = await self.db.connect(host=self.host,
                                              port=self.port,
                                              db=self.dbname)
            return True, None
        except (ConnectionRefusedError, ConnectionResetError) as err:
            self.log.error(f'[RETHINKDB] connect => {err}')
            return False, f'{err}'

    async def close(self):
        """Отключение от RethinDB"""
        self.conn.close(noreply_wait=False)

    async def getAllData(self):
        """Получение всех данных из RethinDB"""
        await self.connect()
        tables = await self.db.table(self.table).run(self.conn)
        data = await self.workCursor(cursor=tables)
        # await self.close()
        self.log.info(f'DATA => {data} COUNT => {len(data)}')
        return data

    async def getKeyData(self, key: str = '11010867857032857034'):
        """Получение данных по ключу из RethinDB"""
        await self.connect()
        tables = await self.db.table(self.table).filter(
            (self.db.row[self.row_item][self.row_carid] == key) |
            (self.db.row[self.row_item][self.row_objectid] == key)
            ).run(self.conn)
        table = await self.workCursor(cursor=tables)
        # await self.close()
        self.log.info(f'DATA => {table[-1]}')
        if isinstance(table, list):
            return table[-1]
        else:
            return table

    async def workCursor(self, cursor: AsyncioCursor) -> list:
        """Обработка курсора RethinDB"""
        data = list()
        async for item in cursor:
            item = item.get(self.row_item)
            item = await self.formatData(data=item)
            data.append(item)
        return data

    async def formatData(self, data: dict) -> dict:
        """Форматирование данных"""
        if isinstance(data, dict):
            coordinates = data.pop('coordinates', None)
            coordinates = coordinates.pop('coordinates', None)
            data.pop('region', None)
            if isinstance(coordinates, list):
                longitude, latitude = coordinates
                data.update({'lat': latitude, 'lon': longitude})
        return data


rt = RethinDBWork()

loop = asyncio.get_event_loop()
loop.run_until_complete(rt.getKeyData())
loop.close()
