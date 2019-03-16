#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/3/16
@Author  : wangjh
@desc    : PyCharm
"""
import os
import sys

cur_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(cur_dir))
import platform
import redis
from db_config import log

pl = platform.system()


class Connect_redis(object):
    def __init__(self, db):
        self.db = db

    def connect(self):
        if pl == "Linux":
            redis_obj = redis.Redis(host='127.0.0.1', port=6379, db=self.db)
        else:
            redis_obj = redis.Redis(host='127.0.0.1', port=6379, db=self.db)
        return redis_obj


class RedisPool:
    if pl == "Windows":
        def __init__(self, client_host="127.0.0.1", client_port=6379, client_db=0):
            self.client_host = client_host
            self.client_port = client_port
            self.client_db = client_db
    else:
        def __init__(self, client_host="127.0.0.1", client_port=6379, client_db=0):
            self.client_host = client_host
            self.client_port = client_port
            self.client_db = client_db

    def redis_pool(self):
        if pl == "Windows":
            pool = redis.ConnectionPool(
                host=self.client_host,
                port=self.client_port,
                db=self.client_db)
        else:
            pool = redis.ConnectionPool(
                host=self.client_host,
                port=self.client_port,
                db=self.client_db)
        return redis.StrictRedis(connection_pool=pool)


class HandleRedis(object):
    def __init__(self, db):
        self.db = db
        self.redisobj = RedisPool(client_db=self.db)
        self.redispool = self.redisobj.redis_pool()

    def cache_dict_redis(self, k, data):
        """
        将数据存到redis以集合的形式存储
        :param k:
        :param data:
        :return:
        """
        redisobj = RedisPool(client_db=self.db)
        redispool = self.redisobj.redis_pool()
        if not isinstance(data, dict):
            raise ValueError
        redispool.sadd(k, data)
        log.crawler.info("cache redis success k is:%s" % k)

    def cache_list_redis(self, k, datas):
        """

        将列表数据以集合的形式缓存到redis
        :param k:
        :param datas:
        :return:
        """

        if not isinstance(datas, list):
            raise ValueError("缓存的数据不是list存在错误..........")
        self.redispool.sadd(k, *datas)
        log.crawler.info("cache redis success k is:%s,length is:%d" % (k, len(datas)))

    def get_data_redis(self, k):
        value = self.redispool.spop(k)
        if value:
            value = value.decode()
            return value
        else:
            return None

    def get_many_data_redis(self, k):
        values = self.redispool.srem(k, '5', '6')
        if values:
            return values

    def put_str_into_redis(self, k, data):
        self.redispool.sadd(k, data)
        log.crawler.info("cache redis success key is:%s" % k)

    def spop_data_from_redis(self, k):
        data = self.redispool.spop(k)
        if data:
            return data

    def get_length(self, k):
        # 获取键k里有多少条数据
        num = self.redispool.scard(k)
        if num:
            return num
        else:
            return None
