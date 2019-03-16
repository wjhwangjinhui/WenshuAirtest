#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/3/16
@Author  : wangjh
@desc    : PyCharm
"""
import datetime
import time
from _sha1 import sha1
from multiprocessing import Process
from airtest.core.api import *
from db_config.save_mysql import persis_data_into_mysql
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from db_config.connect_db import HandleRedis
from airtest.core.api import *
from airtest.core.android.android import *

__author__ = "user"
auto_setup(__file__)
r = HandleRedis(1)
adb = ADB()
devicesList = adb.devices()


def xinshi_con(poco, case_type):
    key = r.get_data_redis("TB_WENSHU_MINSHI")
    print(key)
    poco(name="com.lawyee.wenshuapp:id/searchview_search_et").click()
    time.sleep(0.5)
    poco(name="com.lawyee.wenshuapp:id/searchinput_search_et").set_text(key)
    poco(name="android.widget.ImageView")[1].click()
    time.sleep(1)
    casename_obj_list = poco(name='com.lawyee.wenshuapp:id/li_wsl_casename_tv')
    if casename_obj_list:
        casename_list = []
        for i in range(2):
            casename_obj_list = poco(name='com.lawyee.wenshuapp:id/li_wsl_casename_tv')
            courtname_obj_list = poco(name='com.lawyee.wenshuapp:id/li_wsl_courtname_tv')
            caseno_obj_list = poco(name='com.lawyee.wenshuapp:id/li_wsl_caseno_tv')
            publicdata_obj_list = poco(name='com.lawyee.wenshuapp:id/li_wsl_publicdata_tv')
            num = \
            sorted([len(casename_obj_list), len(courtname_obj_list), len(caseno_obj_list), len(publicdata_obj_list)])[
                0]
            for k in range(int(num)):
                try:
                    casename = casename_obj_list[k].get_text()
                    if casename not in casename_list:
                        casename_list.append(casename)
                        courtname = courtname_obj_list[k].get_text()
                        caseno = caseno_obj_list[k].get_text()
                        publicdata = publicdata_obj_list[k].get_text()
                        a = casename_obj_list[k]
                        case_content = get_case_content(poco, a)
                        if not case_content:
                            continue
                        else:
                            hash_sha1 = sha1()
                            h_sha1 = hash_sha1.copy()
                            my_str = casename + case_type + publicdata
                            h_sha1.update(my_str.encode('utf-8'))
                            sha1_str = h_sha1.hexdigest()
                            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            data = {
                                'HASH': sha1_str,
                                'CASE_TYPE': case_type,
                                'CASE_NAME': casename,
                                'COURT_NAME': courtname,
                                'CASE_NO': caseno,
                                'PUBLIC_DATA': publicdata,
                                'CASE_CONTENT': case_content,
                                'DATA_SOURCE': '裁判文书手机APP',
                                'CRAWLER_TIME': now_time,
                            }
                            table = 'TB_WENSHU_APP'
                            persis_data_into_mysql(table, data)
                            poco(name='android.widget.ImageView').click()
                            time.sleep(0.5)
                    else:
                        continue
                except Exception as e:
                    print(e)
                    break
            time.sleep(0.5)
            poco.swipe([0.5, 0.7], [0.5, 0.65], duration=0.2)
            time.sleep(0.5)
            poco.swipe([0.5, 0.95], [0.5, 0.5], duration=0.3)
        poco(name='android.widget.ImageView').click()
        xinshi(poco)

    else:
        poco(name='android.widget.ImageView').click()
        xinshi(poco)


def get_case_content(poco, a):
    for i in range(5):
        if i == 3:
            return ''
        a.click()
        try:
            t_list = []
            case_content = ''
            while True:
                if '公 告' in t_list:
                    break
                time.sleep(0.2)
                con = poco(type='android.view.View')
                for c in con:
                    t = c.get_name()
                    # t = c.get_text()
                    if t not in t_list:
                        # file = casename + '.txt'
                        # with open(file, 'a+', encoding='utf-8')as f:
                        #     f.write(t + '\n')
                        t_list.append(t)
                        case_content += t + '\n'
                poco.swipe([0.5, 0.95], [0.5, 0.5], duration=0.3)
            return case_content
        except Exception as e:
            print(i, e)
            poco(name='android.widget.ImageView').click()


def xinshi(poco):
    time.sleep(0.5)
    case_type = "刑事案件"
    poco(text=case_type).click()
    time.sleep(0.5)
    xinshi_con(poco, case_type)


def main(num):
    while True:
        try:
            dev = connect_device('android:///127.0.0.1:{}?cap_method=javacap&touch_method=adb'.format(num))
            poco = AndroidUiautomationPoco(device=dev, use_airtest_input=True, screenshot_each_action=False)
            poco(text="裁判文书网").click()
            xinshi(poco)
            PACKAGE = "com.lawyee.wenshuapp"
            stop_app(PACKAGE)
            print('*' * 110)
            time.sleep(10)
        except Exception as e:
            print(e)
            PACKAGE = "com.lawyee.wenshuapp"
            stop_app(PACKAGE)
            print('<' * 110)
            time.sleep(100)


if __name__ == '__main__':
    for num in ['21563']:
        t = Process(target=main, args=(num,))
        t.start()
