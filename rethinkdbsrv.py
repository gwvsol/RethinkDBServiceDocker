# -*- coding: utf-8 -*-
import logging
import time
from rethinkdb import RethinkDB
from rethinkdb.errors import ReqlOpFailedError
from rethinkdb.errors import ReqlNonExistenceError
from rethinkdb.errors import ReqlDriverError
from rethinkdb.net import DefaultCursor
from os import environ as env
from pprint import pprint


class UseRethinkDB(object):
    """"Класс реклизующий некоторые методы API RethinkDB"""
    def __init__(self) -> None:
        self._host = env.get('RETHINKDB_HOST')
        self._port = env.get('RETHINKDB_PORT01')
        self._dbname = env.get('RETHINKDB_DBNAME')
        self._tablename = env.get('RETHINKDB_TABLE')
        self._row_item = 'data'
        self._during = 900
        self._row_time = 'time'
        self._row_carid = 'CarId'
        self._row_objectid = 'ObjectID'
        self.log = logging
        self.format = '%(asctime)s.%(msecs)d|\
%(levelname)s|%(module)s.%(funcName)s:%(lineno)d %(message)s'
        self.log.basicConfig(level=logging.INFO,
                             format=self.format,
                             datefmt='%Y-%m-%d %H:%M:%S')
        self.db = RethinkDB()
        self.conn = None

    def __enter__(self):
        """Подключение к базе данных RethinkDB"""
        try:
            self.conn = self.db.connect(self._host, self._port).repl()
        except ReqlDriverError as err:
            self.log.error(err.args)
        return self

    def getAllData(self) -> list:
        """Получение всех записей из таблицы базы данных"""
        try:
            return list(self.db.db(self._dbname).table(self._tablename).run())
        except (ReqlOpFailedError, ReqlNonExistenceError,
                ReqlDriverError, IndexError) as err:
            self.log.error(err.args)
            return list()

    def getKeyData(self, key: (int, str)) -> dict:
        """Получение записей из таблицы базы данных
            по ключам CarId и ObjectID"""
        try:
            # return self.db.db(self._dbname).table(self._tablename).filter(
            #     (self.db.row[self._row_item][self._row_carid] == key) |
            #     (self.db.row[self._row_item][self._row_objectid] == key)).run()
            rcv = self.db.db(self._dbname).table(self._tablename).get(key).keys().run()
            print(rcv)
            return rcv
        except (ReqlOpFailedError, ReqlNonExistenceError,
                ReqlDriverError, IndexError) as err:
            self.log.error(err.args)
            return list()

    def countActualData(self) -> int:
        """Получение количества актуальных записей в базе данных"""
        actual = 0
        try:
            utc_now = time.time()
            ny, nm, nd, nh, nmi, ns, *_ = time.gmtime(utc_now)
            y, m, d, h, mi, s, *_ = time.gmtime(utc_now - self._during)
            actual = self.db.db(self._dbname).table(
                   self._tablename).filter((
                         self.db.row[self._row_time].during(
                                    self.db.time(y, m, d, h, mi, s, 'Z'),
                                    self.db.time(ny, nm, nd, nh, nmi, ns, 'Z')
                                    )
                        )
                ).count().run()
            return actual
        except (ReqlOpFailedError, ReqlNonExistenceError,
                ReqlDriverError, IndexError) as err:
            self.log.error(err.args)
            return 0

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Отключение от базы данных"""
        try:
            self.conn.close()
        except AttributeError as err:
            self.log.error(err)
        self.conn = None


class RethinDBWork(object):
    """Класс обрабатывающий подключение и закрытие соединения с базой"""
    def __init__(self) -> None:
        self.db = UseRethinkDB
        self.row_item = 'data'
        self.row_region = 'region'
        self.row_coordinates = 'coordinates'
        self.row_lon = 'lon'
        self.row_lat = 'lat'

    def getAllData(self) -> list:
        """Получение всех данных из RethinDB"""
        with self.db() as db:
            tables = db.getAllData()
        return self.workCursor(cursor=tables)

    def getKeyData(self, key: str = '9705395') -> dict:
        """Получение данных по ключу из RethinDB по CarId или ObjectID"""
        with self.db() as db:
            tables = db.getKeyData(key)
            data = self.workCursor(cursor=tables)
        if isinstance(data, list):
            if len(data) >= 1:
                return data[-1]
            else:
                return data
        else:
            return data

    def workCursor(self, cursor: (DefaultCursor, list)) -> list:
        """Обработка курсора RethinDB"""
        data = list()
        for item in cursor:
            item = item.get(self.row_item)
            item = self.formatData(data=item)
            data.append(item)
        return data

    def formatData(self, data: dict) -> dict:
        """Форматирование данных"""
        if isinstance(data, dict):
            coordinates = data.pop(self.row_coordinates, None)
            coordinates = coordinates.pop(self.row_coordinates, None)
            data.pop(self.row_region, None)
            if isinstance(coordinates, list):
                longitude, latitude = coordinates
                data.update({self.row_lat: latitude, self.row_lon: longitude})
        return data

    def countActualData(self) -> int:
        """Получение количества актуальных записей в базе данных"""
        with self.db() as db:
            count = db.countActualData()
        return count


db = RethinDBWork()
pprint(db.getKeyData('17605'))
# pprint(db.getAllData())
# pprint(db.countActualData())
