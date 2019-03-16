#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/3/16
@Author  : wangjh
@desc    : PyCharm
"""
import platform
import pymysql
from db_config import log

pl = platform.system()


class HandDb(object):
    original_sql = """insert into {table_name}({columns}) values {column_values}"""

    def __init__(self, table):
        self.table = table

    def generate_sql_dict(self, item):
        """
        生产单条sql插入语句
        :param table: 表名
        :param item: 数据字典形式
        :return:
        """
        # print(item)
        if self.table == "tb_credit":
            item['credit_level'] = 'A'
        dbcol = []
        values = []
        for k in item:
            dbcol.append(k)
            values.append(item.get(k, ""))
        sql = self.original_sql.format(table_name=self.table, columns=",".join(dbcol), column_values=tuple(values))
        return sql

    def generate_sql_list(self, data, cols):
        """

        :param data: list
        :param cols: list
        :return:
        """
        if self.table == "tb_credit" and 'credit_level' not in cols:
            cols.append('credit_level')
            data.append("A")
        sql = self.original_sql.format(table_name=self.table, columns=",".join(cols), column_values=tuple(data))
        # print(sql)
        return sql


class DbHandle(object):
    '''数据库操作类'''

    def __init__(self):
        '''初始化数据库连接'''
        self.__db_port = 3306
        if pl == "Windows":
            self.__db_host = '127.0.0.1'
            self.__db_user = 'root'
            self.__db_passwd = '123456!'

        else:
            self.__db_host = '127.0.0.1'
            self.__db_user = 'root'
            self.__db_passwd = '123456'
        self.__db_name = 'test'
        self.__conn = None  # 数据库连接
        self.__cur = None  # 操作游标

        self.__conn = pymysql.connect(host=self.__db_host, user=self.__db_user,
                                      passwd=self.__db_passwd, db=self.__db_name,
                                      port=self.__db_port, charset='utf8')
        self.__cur = self.__conn.cursor()

    def __db_connect(self):
        '''连接数据库'''
        try:
            self.__conn = pymysql.connect(host=self.__db_host, user=self.__db_user,
                                          passwd=self.__db_passwd, db=self.__db_name,
                                          port=self.__db_port, charset='utf8')
            self.__cur = self.__conn.cursor()
        except Exception as e:
            raise e

    def __db_close(self):
        '''关闭数据库'''
        try:
            self.__cur.close()
            self.__conn.close()
        except Exception as e:
            raise e

    def db_conn_close(func):
        def wrapper(self, **kwargs):
            # 创建数据库连接
            self.__db_connect()
            r = func(self, **kwargs)
            # 关闭数据库连接
            self.__db_close()
            return r

        return wrapper

    def insert_db_func(self, **kwargs):
        sql = kwargs.get("sql")
        try:
            self.__cur.execute(sql)
            self.__conn.commit()
            log.crawler.info("insert db success")
        except Exception as err:
            log.detail.info(sql)
            log.error.info(err)
            self.__conn.rollback()

    @db_conn_close
    def get_table_fields(self, **kwargs):
        fields = []
        table_name = kwargs.get('tname')
        self.__cur.execute('desc {}'.format(table_name))
        results = self.__cur.fetchall()
        for r in results:
            fields.append(r[0])
        return fields

    @db_conn_close
    def find_data_from_db(self, **kwargs):
        sql = kwargs.get("sql")
        try:
            self.__cur.execute(sql)
            data = self.__cur.fetchall()
            return data
        except Exception as err:
            raise err


db = DbHandle()


def persis_data_into_mysql(table, data):
    hd = HandDb(table)
    sql = hd.generate_sql_dict(data)
    db.insert_db_func(sql=sql)


if __name__ == '__main__':
    pass
