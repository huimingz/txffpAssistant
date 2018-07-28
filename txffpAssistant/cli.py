#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : Kyle
# @License : MIT
# @Contact : kairu_madigan@yahoo.co.jp
# @Date    : 2018/07/26 22:51

import argparse
import getpass
import logging
import os
import string
import sys

from . import exceptions
from . import handler
from . import logger as log
from . import __version__ as version


version_info = "txffpAssistant version {}".format(version)

logg_level_dict = {
    "debug": logging.DEBUG,
    "info": logging.info,
    "warn": logging.WARN,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}


def get_password() -> str:
    password = getpass.getpass("enter your password: ")
    return password


def get_username() -> str:
    username = input("enter your username: ")
    return username


def get_uname_passwd() -> (str, str):
    username = get_username()
    password = get_password()
    return username, password


def authstr_parser(authstr:str) -> (str, str):
    parsed = authstr.split(":", 1)
    if len(parsed) == 1:
        username = parsed[0]
        password = get_password()
    else:
        username = parsed[0]
        password = parsed[1]
    return username, password
        
        
class MonthAction(argparse.Action):
    
    def __call__(self, parser, namespace, values, option_string=None):
        self.validator(values)
        setattr(namespace, self.dest, values)
        
    def validator(self, yearmonth):
        if not yearmonth.isdigit() or len(yearmonth) != 6:
            print("Error: 月份信息不合法，格式：year+month, 例：201805", file=sys.stderr)
            sys.exit(1)
        year = yearmonth[:4]
        month = yearmonth[4:]
        month_all = ["{:02d}".format(m) for m in range(1, 13)]
        if month not in month_all:
            print("Error: 月份信息不合法，所指定月份不存在")
            sys.exit(1)


class AuthAction(argparse.Action):
    
    def __call__(self, parser, namespace, values, option_string=None):
        values = self.validator(values)
        setattr(namespace, self.dest, values)
        
    def validator(self, values: str):
        if values.startswith(":"):
            print("Error: 认证账户格式错误", file=sys.stderr)

        parsed = values.split(":", 1)
        if len(parsed) == 1:
            password = get_password()
            values = parsed[0] + ":" + password
        return values


class IDAction(argparse.Action):
    
    def __call__(self, parser, namespace, values, option_string=None):
        self.validator(values)
        setattr(namespace, self.dest, values)
    
    @staticmethod
    def ishexdigit(char):
        result = (char in string.hexdigits)
        return result
        
    def validator(self, values: str):
        if len(values) != 32:
            print("Error: ID信息不合法，长度不等于32", file=sys.stderr)
            sys.exit(1)
    
        resultmap = map(self.ishexdigit, values)
        if False in resultmap:
            print("Error: ID信息不合法，存在非十六进制字符")
            sys.exit(1)
            

class Service(object):
    
    def __init__(self, options, logger):
        self.options = options
        self.logger = logger
        self.username = ""
        self.password = ""
        
    def auth(self):
        if hasattr(self.options, "auth") and self.options.auth:
            self.username, self.password = authstr_parser(self.options.auth)
        else:
            self.username, self.password = get_uname_passwd()

    def login(self):
        self.auth()
    
        self.logger.info("模拟登陆...")
        authed_session = handler.authenticated_session(
            self.username, self.password, logger=self.logger)
        return authed_session
            
    def run(self):
        pass
    

class EtcService(Service):
    
    @staticmethod
    def get_etc_info(handler, etc_type):
        etc = handler.get_cardlist(etc_type)
        etcinfo = [ei for ei_iter in etc for ei in ei_iter]
        return etcinfo
    
    def run(self):
        authed_session = self.login()
        
        etc_handler = handler.ETCCardHandler(
            session=authed_session, logger=self.logger)
        
        etc_type = self.options.etc_type.upper()
        if etc_type == "ALL":
            p_etcinfo = self.get_etc_info(etc_handler, "PERSONAL")
            c_etcinfo = self.get_etc_info(etc_handler, "COMPANY")
        elif etc_type == "PERSONAL":
            p_etcinfo = self.get_etc_info(etc_handler, "PERSONAL")
        elif etc_type == "COMPANY":
            c_etcinfo = self.get_etc_info(etc_handler, "COMPANY")

        self.logger.info("已完成ETC卡信息的获取")
        local_keys = locals().keys()
        if "p_etcinfo" in local_keys and "c_etcinfo" in local_keys:
            self.logger.info("单位卡{}张，个人卡{}张".format(len(c_etcinfo), len(p_etcinfo)))
        elif "p_etcinfo" in local_keys:
            self.logger.info("个人卡{}张".format(len(p_etcinfo)))
        elif "c_etcinfo" in local_keys:
            self.logger.info("单位卡{}张".format(len(c_etcinfo)))
        
        
class RecordService(Service):
    
    def run(self):
        authed_session = self.login()
        
        rd_handler = handler.InvoiceRecordHandler(
            session=authed_session, logger=self.logger)

        user_type = self.options.user_type.upper()
        card_id = self.options.etc_id
        month = self.options.month
        
        inv_rd = rd_handler.get_record_info(card_id, month, user_type)
        record_info = [ri for ri_iter in inv_rd for ri in ri_iter]
        self.logger.info("已完成发票记录信息的获取")
        self.logger.info("共{}条发票记录".format(len(record_info)))
        

def main():
    description = "使用过程中出现问题，请到xxx发起issue。"
    parser= argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-d", "--debug", action="store_true", help="debug模式")
    parser.add_argument("-v", "--version", action="version", version=version_info, help="查看当前版本并退出")

    service_subparser = parser.add_subparsers(title="Commands", dest="command")
    
    # etc card list
    service_etc = service_subparser.add_parser("etc", help="查看ETC卡信息")
    service_etc.add_argument("--type", dest="etc_type", choices=["personal", "company", "all"],
                                  default="all", help="指定etc卡类型，默认：all")
    service_etc.add_argument("--auth", action=AuthAction, dest="auth", type=str,
                                  help="票根网用户名和密码，格式：username:password")
    
    # invoice record
    service_record = service_subparser.add_parser("record" ,help="查看开票记录")
    service_record.add_argument("--id", action=IDAction ,dest="etc_id", type=str, required=True, help="指定ETC卡id")
    service_record.add_argument("--month", action=MonthAction, dest="month", type=str, required=True, help="开票年月，例如: 201805")
    service_record.add_argument("--type", dest="user_type", choices=["personal", "company"],
                                  default="company", help="指定etc卡类型，默认：company")
    service_record.add_argument("--auth", action=AuthAction, dest="auth", type=str, help="票根网用户名和密码，格式：username:password")
    
    
    # invoice download
    service_inv_dl = service_subparser.add_parser("inv-dl", help="下载发票")
    service_inv_dl.add_argument("-e", "--extract", type=bool, default=True, help="自动解压")
    
    if len(sys.argv) == 1:
        parser.parse_args(["-h"])
    
    options = parser.parse_args()
    print("options: {}".format(options))
    
    logger = log.stream_logger()
    # debug mode
    if options.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("启用debug模式")

    if options.command:
        class_name = options.command.title() + "Service"
        service = eval(class_name)(options, logger)
        service.run()


if __name__ == "__main__":
    main()
