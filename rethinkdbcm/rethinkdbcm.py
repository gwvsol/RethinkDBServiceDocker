# -*- coding: utf-8 -*-
import logging
from rethinkdb import RethinkDB
from rethinkdb.errors import ReqlOpFailedError, ReqlNonExistenceError, ReqlDriverError


class UseRethinkDB(object):
    """"Класс реклизующий некоторые основные методы API RethinkDB"""
    def __init__(self, host:str = '127.0.0.1', port:int = 28015) -> None:
        self.log = logging
        self.log.basicConfig(level=logging.DEBUG, \
                             format='%(asctime)s:%(levelname)s:%(message)s', \
                             datefmt='%Y-%m-%d %H:%M:%S')
        self.db = RethinkDB()
        self._host = host
        self._port = port
        self.conn = None


    def __enter__(self) -> self:
        """Подключение к базе данных RethinkDB
        https://rethinkdb.com/api/python/connect
        """
        try:
            self.conn = self.db.connect(self._host, self._port).repl()
        except ReqlDriverError as err:
            self.log.error(err.args)
        return self


    def db_list(self) -> list:
        """Получение списка всех баз данных
        https://rethinkdb.com/api/python/db_list/
        """
        try:
            return self.db.db_list().run()
        except (ReqlOpFailedError, ReqlDriverError) as err:
            self.log.error(err.args)
            return list()


    def db_create(self, name:str = None) -> dict:
        """Создание новой базы данных
        https://rethinkdb.com/api/python/db_create/
        """
        try:
            return self.db.db_create(name).run()
        except (ReqlOpFailedError, ReqlNonExistenceError, ReqlDriverError) as err:
            self.log.error(err.args)
            return dict({'error': err.args})


    def db_drop(self, name:str = None) -> dict:
        """Удаление базы данных
            https://rethinkdb.com/api/python/db_drop
        """
        try:
            return self.db.db_drop(name).run()
        except (ReqlOpFailedError, ReqlNonExistenceError, ReqlDriverError) as err:
            self.log.error(err.args)
            return dict({'error': err.args})

    
    def table(self, db_name:str = None, table_name:str = None) -> list:
        """Получение всех записей из таблицы базы данных
            https://rethinkdb.com/api/python/table
        """
        try:
            return list(self.db.db(db_name).table(table_name).run())
        except (ReqlOpFailedError, ReqlNonExistenceError, ReqlDriverError, IndexError) as err:
            self.log.error(err.args)
            return list()

    
    def table_list(self, name:str = None) -> list:
        """Получение всех таблиц из подключенной базы данных
            https://rethinkdb.com/api/python/table_list
        """
        try:
            return self.db.db(name).table_list().run()
        except (ReqlOpFailedError, ReqlNonExistenceError, ReqlDriverError) as err:
            self.log.error(err.args)
            return list()


    def table_create(self, db_name:str = None, table_name:str = None) -> dict:
        """Создание новой таблицы в базе данных
            https://rethinkdb.com/api/python/table_create
        """
        try:
            return self.db.db(db_name).table_create(table_name).run()
        except (ReqlOpFailedError, ReqlNonExistenceError, ReqlDriverError) as err:
            self.log.error(err.args)
            return dict({'error': err.args})


    def table_drop(self, db_name:str = None, table_name:str = None) -> dict:
        """Удаление таблицы из базы данных
            https://rethinkdb.com/api/python/table_drop
        """
        try:
            return self.db.db(db_name).table_drop(table_name).run()
        except (ReqlOpFailedError, ReqlNonExistenceError, ReqlDriverError) as err:
            self.log.error(err.args)
            return dict({'error': err.args})

    
    def get(self, db_name:str = None, table_name:str = None, key_name:str = None) -> dict:
        """Получение записи из таблицы базы данных по определенному ключу
            https://rethinkdb.com/api/python/get
        """
        try:
            data = self.db.db(db_name).table(table_name).get(key_name).run()
            if data: return data
            else: return dict()
        except (ReqlOpFailedError, ReqlNonExistenceError, ReqlDriverError) as err:
            self.log.error(err.args)
            return dict({'error': err.args})

    
    def insert(self, db_name:str = None, table_name:str = None, data:dict = None) -> dict():
        """Добавление новой записи в таблицу базы данных
            https://rethinkdb.com/api/python/insert
        """
        try:
            return self.db.db(name_db).table(table_name).insert(data).run()
        except (ReqlOpFailedError, ReqlNonExistenceError, ReqlDriverError) as err:
            self.log.error(err.args)
            return dict({'error': err.args})


    def update(self, db_name:str = None, table_name:str = None, \
                     key_name:str = None, data:dict = None) -> dict:
        """Обновление записи в таблице базы данных по определенному ключу
            https://rethinkdb.com/api/python/update
        """
        try:
            return self.db.db(db_name).table(table_name).get(key_name).update(data).run()
        except (ReqlOpFailedError, ReqlNonExistenceError, ReqlDriverError) as err:
            self.log.error(err.args)
            return dict({'error': err.args})

    
    def delete(self, db_name:str = None, table_name:str = None, key_name:str = None) -> dict:
        """Удаление записи в таблицы базы данных по определенному ключу
            https://rethinkdb.com/api/python/delete
        """
        try:
            return self.db.db(db_name).table(table_name).get(key_name).delete().run()
        except (ReqlOpFailedError, ReqlNonExistenceError, ReqlDriverError) as err:
            self.log.error(err.args)
            return dict({'error': err.args})


    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Отключение от базы данных
            https://rethinkdb.com/api/python/close
        """
        try:
            self.conn.close()
        except AttributeError as err:
            self.log.error(err)
        self.conn = None



class WorkRethinkDB(object):
    """Класс обрабатывающий подключение к базе данных и закрытие соединения с базой. 
       При этом методы класса повторяют некоторые основные методы API RethinkDB

from rethinkdbcm import WorkRethinkDB
db = WorkRethinkDB()
db.db_list()

    """
    def __init__(self, host:str = '127.0.0.1', port:int = 28015) -> None:
        self.db = UseRethinkDB
        self.conf = dict({'host': host, 'port': port})
    

    def db_list(self) -> list:
        """Получение списка баз данных"""
        with self.db(**self.conf) as db:
            return db.db_list()


    def db_create(self, db_name:str = None) -> dict:
        """Создание новой базы данных"""
        with self.db(**self.conf) as db:
            return db.db_create(db_name)


    def db_drop(self, db_name:str = None) -> dict:
        """Удаление базы данных"""
        with self.db(**self.conf) as db:
            return db.db_drop(db_name)


    def table(self, db_name:str = None, table_name:str = None) -> list:
        """Получение всех записей из таблицы базы данных"""
        with self.db(**self.conf) as db:
            return db.table(db_name, table_name)


    def table_list(self, db_name:str = None) -> list:
        """Получение всех таблиц из подключенной БД"""
        with self.db(**self.conf) as db:
            return db.table_list(db_name)


    def table_create(self, db_name:str = None, table_name:str = None) -> dict:
        """Создание новой таблицы в базе данных"""
        with self.db(**self.conf) as db:
            return db.table_create(db_name, table_name)


    def table_drop(self, db_name:str = None, table_name:str = None) -> dict:
        """Удаление таблицы из базы данных"""
        with self.db(**self.conf) as db:
            return db.table_drop(db_name, table_name)

    
    def get(self, db_name:str = None, table_name:str = None, key_name:str = None) -> dict:
        """Получение записи из таблицы базы данных по определенному ключу"""
        with self.db(**self.conf) as db:
            return db.get(db_name, table_name, key_name)


    def insert(self, db_name:str = None, table_name:str = None, data:dict = None) -> dict():
        """Добавление новой записи в таблицу базы данных"""
        with self.db(**self.conf) as db:
            return db.insert(db_name, table_name, key_name, data)

    
    def update(self, db_name:str = None, table_name:str = None, \
                     key_name:str = None, data:dict = None) -> dict:
        """Обновление записи в таблице базы данных по определенному ключу"""
        with self.db(**self.conf) as db:
            return db.update(db_name, table_name, key_name, data)


    def delete(self, db_name:str = None, table_name:str = None, key_name:str = None) -> dict:
        """Удаление записи в таблицы базы данных по определенному ключу"""
        with self.db(**self.conf) as db:
            return db.delete(db_name, table_name, key_name)

