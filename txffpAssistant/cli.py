#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : Kyle
# @License : MIT
# @Contact : kairu_madigan@yahoo.co.jp
# @Date    : 2018/07/26 22:51

import argparse
import getpass
import logging
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

etc_type_dict = {
    "personal": "PERSONAL",
    "company": "COMPANY"
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
    

def inv_dl():
    pass


def etc_list(username, password, logger, etc_type="all"):
    if etc_type.upper() != "ALL" and etc_type.lower() not in etc_type_dict:
        raise ValueError("etc_type not in {}".format(etc_type_dict.keys()))
    
    logger.info("模拟登陆...")
    authed_session = handler.authenticated_session(
        username, password, logger=logger)

    etc_handler = handler.ETCCardHandler(
        session=authed_session, logger=logger)
    
    def get_etc_info(etc_type):
        etc = etc_handler.get_cardlist(etc_type)
        etcinfo = [ei for ei_iter in etc for ei in ei_iter]
        return etcinfo
    
    if etc_type.upper() == "ALL":
        p_etcinfo = get_etc_info("PERSONAL")
        c_etcinfo = get_etc_info("COMPANY")
    elif etc_type.upper() == "PERSONAL":
        p_etcinfo = get_etc_info("PERSONAL")
    elif etc_type.upper() == "COMPANY":
        c_etcinfo = get_etc_info("COMPANY")
        
    logger.info("已完成ETC卡信息的获取")
    
    local_keys = locals().keys()
    if "p_etcinfo" in local_keys and "c_etcinfo" in local_keys:
        logger.info("单位卡{}张，个人卡{}张".format(len(c_etcinfo), len(p_etcinfo)))
    elif "p_etcinfo" in local_keys:
        logger.info("个人卡{}张".format(len(p_etcinfo)))
    elif "c_etcinfo" in local_keys:
        logger.info("单位卡{}张".format(len(c_etcinfo)))


def main():
    description = "使用过程中出现问题，请到xxx发起issue。"
    parser= argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-d", "--debug", action="store_true", help="debug模式")
    parser.add_argument("-v", "--version", action="version", version=version_info, help="查看当前版本并退出")

    service_subparser = parser.add_subparsers(title="Commands", dest="command")
    
    # etc card list
    service_etc_list = service_subparser.add_parser("etc-list", help="查看ETC卡信息")
    service_etc_list.add_argument("-t", "--type", dest="etc_type", choices=["personal", "company", "all"],
                                  default="all", help="指定etc卡类型，默认：all")
    service_etc_list.add_argument("-a", "--auth", dest="auth", type=str, help="票根网用户名和密码")
    
    # invoice download
    service_inv_dl = service_subparser.add_parser("inv-dl", help="下载发票")
    service_inv_dl.add_argument("-e", "--extract", type=bool, default=True, help="自动解压")
    
    if len(sys.argv) == 1:
        parser.parse_args(["-h"])
    
    options = parser.parse_args()
    print(options)
    
    logger = log.stream_logger()
    # debug mode
    if options.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("启用debug模式")

    # service etc card list
    if hasattr(options, "auth") and options.auth:
        username, password = authstr_parser(options.auth)
    elif options.command is not None:
        username, password = get_uname_passwd()
    

    # logger.info("当前用户：{}".format(username))
    if options.command == "etc-list":
        etc_type = options.etc_type
        try:
            etc_list(username, password, logger, etc_type)
        except exceptions.AuthFailedError:
            sys.exit(1)
    
    
    
    # if __name__ == "__main__":
    
        
    
    pass


if __name__ == "__main__":
    main()
