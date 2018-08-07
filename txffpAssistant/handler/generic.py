#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : Kyle
# @License : MIT
# @Contact : kairu_madigan@yahoo.co.jp
# @Date    : 2018-07-23 12:36

import os
import re

from lxml import etree

from txffpAssistant import exceptions
from txffpAssistant.handler import base


__all__ = ["CardInfo", "ETCCardHandler", "InvoiceRecordHandler", "invpdf_cld_dl"]


class CardInfo(object):
    
    def __init__(self, **kwargs):
        self.region = kwargs.get("region") or None
        self.etc_id = kwargs.get("etc_id") or None
        self.iccard = kwargs.get("iccard") or None
        self.carnum = kwargs.get("carnum") or None
        self.page_num = kwargs.get("page_num") or None
        self.card_type = kwargs.get("card_type") or None


class RecordInfo(object):
    
    def __init__(self, **kwargs):
        self.date = kwargs.get("date") or None
        self.month = kwargs.get("month") or None
        self.etc_id = kwargs.get("etc_id") or None
        self.status = kwargs.get("status") or None
        self.amount = kwargs.get("amount") or None
        self.company = kwargs.get("company") or None
        self.page_num = kwargs.get("page_num") or None
        self.inv_type = kwargs.get("inv_type") or None
        self.etc_type = kwargs.get("etc_type") or None
        self.inv_count = kwargs.get("inv_count") or None
        self.record_id = kwargs.get("inv_id") or None
        self.taxpaper_id = kwargs.get("taxpaper_id") or None


class ETCCardHandler(base.GeneralHandler):
    carinfo_log_format = (
        "etc卡信息（第{page_num}页）\n"
        "{etc_id_nm:>20}:  {etc_id}\n"
        "{iccard_nm:>20}:  {iccard}\n"
        "{carnum_nm:>20}:  {carnum}\n"
        "{region_nm:>20}:  {region}\n"
        "{type_nm:>20}:  {card_type}\n"
    )
    
    # carinfo_exteral = dict(
    #     cardid_nm="ETC ID",
    #     iccard_nm="IC CARD",
    #     carnum_nm="PLATE NUMBER",
    #     region_nm="REGION",
    #     type_nm="TYPE",
    # )
    
    def api_card_list(self, user_type, page_num=1,
                      type_="invoiceApply", change_view="card",
                      query_str=""):
        url = "https://pss.txffp.com/pss/app/login/cardList/manage"
        method = "POST"
        data = {
            "userType": user_type,
            "type": type_,
            "changeView": change_view,
            "queryStr": query_str,
            "pageNo": page_num,
        }
        response = self.request(
            url=url,
            data=data,
            method=method)
        return response
    
    def api_card_binding(self, user_type, page_num=1,
                         change_view="card", query_str=""):
        url = "https://pss.txffp.com/pss/app/login/cardBinding/manage"
        method = "POST"
        data = {
            "userType": user_type,
            "changeView": change_view,
            "queryStr": query_str,
            "pageNo": page_num,
        }
        response = self.request(
            url=url,
            method=method,
            data=data)
        return response
    
    def get_cardlist(self, user_type="COMPANY"):
        page_num = 1
        while True:
            self.logger.info("开始获取第{}页的ETC卡信息...".format(page_num))
            
            response = self.api_card_list(user_type, page_num)
            if not response.content:
                raise exceptions.NoneResponseError("获取etc卡数据失败，原因：响应为空")
            
            cardinfos = self._get_cardlist_cardinfo(
                response.text, user_type, page_num)
            yield cardinfos
            
            if self.has_next_page(response.text):
                page_num += 1
            else:
                break
    
    def _get_bind_cardinfo(self, html, card_type, page_num):
        node = etree.HTML(html)
        card_nodes = node.xpath(
            "//dl[contains(@class,'etc_card_dl')]/div/a[2]")
        
        for card_node in card_nodes:
            region = card_node.xpath("./dt/text()")[0]
            iccard = card_node.xpath("./dd[1]/text()")[0]
            carnum = card_node.xpath("./dd[2]/text()")[0]
            etc_id = card_node.get("href").split("/")[-2]
            
            cardinfo = CardInfo()
            cardinfo.region = region
            cardinfo.etc_id = etc_id
            cardinfo.iccard = iccard.strip()[-20:]
            cardinfo.carnum = carnum.strip()[-7:]
            cardinfo.page_num = page_num
            cardinfo.card_type = card_type
            # cardinfo = {
            #     "region": region,
            #     "iccard": iccard.strip()[-20:],
            #     "carnum": carnum.strip()[-7:],
            #     "cardid": cardid,
            #     "card_type": card_type,
            # }
            
            self.logger.debug(self.carinfo_log_format.format(
                etc_id_nm="ETC ID",
                iccard_nm="IC CARD",
                carnum_nm="PLATE NUMBER",
                region_nm="REGION",
                type_nm="TYPE",
                **cardinfo.__dict__))
            yield cardinfo
    
    def _get_cardlist_cardinfo(self, html, card_type, page_num):
        node = etree.HTML(html)
        card_nodes = node.xpath(
            "//dl[@class='etc_card_dl']/div[@class='etc_card_div']")
        
        for card_node in card_nodes:
            region = card_node.xpath("./a/dt/text()")[0]
            iccard = card_node.xpath("./a/dd[1]/text()")[0]
            carnum = card_node.xpath("./a/dd[2]/text()")[0]
            etc_id = card_node.xpath("./a")[0].get("onclick")[13:-2]

            cardinfo = type("CardInfo", (), {})
            cardinfo.region = region
            cardinfo.etc_id = etc_id
            cardinfo.iccard = iccard.strip()[-20:]
            cardinfo.carnum = carnum.strip()[4:]
            cardinfo.page_num = page_num
            cardinfo.card_type = card_type
            
            # cardinfo = {
            #     "region": region,
            #     "iccard": iccard.strip()[-20:],
            #     "carnum": carnum.strip()[4:],
            #     "cardid": cardid,
            #     "card_type": card_type,
            #     "page_num": page_num
            # }
            
            self.logger.debug(self.carinfo_log_format.format(
                etc_id_nm="ETC ID",
                iccard_nm="IC CARD",
                carnum_nm="PLATE NUMBER",
                region_nm="REGION",
                type_nm="TYPE",
                **cardinfo.__dict__))
            yield cardinfo


class InvoiceRecordHandler(base.GeneralHandler):
    """发票记录"""
    
    record_info_log_format = (
        "{month}发票记录信息（第{page_num}页）\n"
        "{etc_id_nm:>20}:  {etc_id}\n"
        "{record_id_nm:>20}:  {record_id}\n"
        "{apply_date_nm:>20}:  {date}\n"
        "{amount_nm:>20}:  {amount}\n"
        "{inv_type_nm:>20}:  {inv_type}\n"
        "{company_nm:>20}:  {company}\n"
        "{taxpaper_id_nm:>20}:  {taxpaper_id}\n"
        "{inv_count_nm:>20}:  {inv_count}\n"
        "{status_nm:>20}:  {status}\n"
    )
    
    # carinfo_exteral = dict(
    #     etc_id_nm="ETC ID",
    #     inv_id_nm="RECORD ID",
    #     apply_date_nm="APPLY DATETIME",
    #     amount_nm="AMOUNT",
    #     inv_type_nm="TYPE",
    #     company_nm="COMPANY",
    #     taxpaper_id_nm="TAXPAPER ID",
    #     inv_count_nm="COUNT",
    #     status_nm="STATUS",
    # )
    
    def api_query_apply(self, card_id, month, page_size=6,
                        user_type="COMPANY", title_name="",
                        station_name=""):
        url = "https://pss.txffp.com/pss/app/login/invoice/query/queryApply"
        method = "POST"
        data = {
            "pageSize": page_size,
            "cardId": card_id,
            "userType": user_type,
            "month": month,
            "titleName": title_name,
            "stationName": station_name,
        }
        response = self.request(
            url=url,
            data=data,
            method=method)
        return response
    
    def api_query_trade(self, card_id, month, page_size=6,
                        user_type="COMPANY", title_name="",
                        station_name=""):
        url = "https://pss.txffp.com/pss/app/login/invoice/query/queryTrade"
        method = "POST"
        data = {
            "pageSize": page_size,
            "cardId": card_id,
            "userType": user_type,
            "month": month,
            "titleName": title_name,
            "stationName": station_name,
        }
        response = self.request(
            url=url,
            data=data,
            method=method)
        return response
    
    def get_record_info(self, card_id, month, user_type,
                        page_size=6, title_name="", station_name=""):
        page_num = 1
        while True:
            response = self.api_query_apply(
                month=month,
                card_id=card_id,
                page_size=page_size,
                user_type=user_type,
                title_name=title_name,
                station_name=station_name)
            if not response.content:
                raise exceptions.NoneResponseError("获取发票记录信息失败，原因：服务器响应为空")
            
            record_info_iter = self._get_query_apply_data(
                response.text, page_num, month, card_id, user_type)
            yield record_info_iter
            
            if self.has_next_page(html=response.text):
                page_num += 1
            else:
                break
    
    def _get_query_apply_data(self, html, page_num, month, etc_id, user_type):
        node = etree.HTML(html)
        record_nodes = node.xpath("//table[@class='table_wdfp']")
        
        for record_node in record_nodes:
            taxpaper_id = record_node.xpath(".//tr[2]/td[1]/table/tr[1]/td[2]/text()")[0]
            apply_date = record_node.xpath("./tr[1]/td/table/tr[1]/th[1]/text()")[0]
            inv_count = record_node.xpath(".//tr[2]/td[1]/table/tr[1]/td[3]/span/text()")[0]
            inv_type = record_node.xpath("./tr[1]/td/table/tr[1]/th[3]/text()")[0]
            company = record_node.xpath(".//tr[2]/td[1]/table/tr[1]/td[1]/text()")[0]
            record_id = record_node.xpath("./tr[1]/td/table/tr/th[4]/a[1]")[0]
            amount = record_node.xpath("./tr[1]/td/table/tr[1]/th[2]/span/text()")[0][2:]
            status = record_node.xpath(".//tr[2]/td[1]/table/tr[1]/td[4]/span/text()")[0]
            
            taxpaper_id = re.sub("\n|\s", "", taxpaper_id)[16:]
            apply_date = apply_date[7:]
            company = re.sub("\n|\s", "", company)[5:]
            record_id = record_id.get("href").split("/")[-4]
            
            record_info = RecordInfo()
            record_info.date = apply_date
            record_info.month = month
            record_info.etc_id = etc_id
            record_info.status = status
            record_info.amount = amount
            record_info.company = company
            record_info.page_num = page_num
            record_info.inv_type = inv_type
            record_info.etc_type = user_type
            record_info.inv_count = inv_count
            record_info.record_id = record_id
            record_info.taxpaper_id = taxpaper_id
            
            # record_info = dict(
            #     taxpaper_id=taxpaper_id,
            #     apply_date=apply_date,
            #     inv_count=inv_count,
            #     inv_type=inv_type,
            #     company=company,
            #     amount=amount,
            #     inv_id=inv_id,
            #     etc_id=etc_id,
            #     status=status,
            #     month=month,
            # )
            
            self.logger.debug(self.record_info_log_format.format(
                etc_id_nm="ETC ID",
                record_id_nm="RECORD ID",
                apply_date_nm="APPLY DATETIME",
                amount_nm="AMOUNT",
                inv_type_nm="TYPE",
                company_nm="COMPANY",
                taxpaper_id_nm="TAXPAPER ID",
                inv_count_nm="COUNT",
                status_nm="STATUS",
                **record_info.__dict__))
            yield record_info
            

def invpdf_cld_dl(session, card_id, inv_id):
    url = (
        "https://pss.txffp.com/pss/app/login/invoice/"
        "query/download/{inv_id}/{card_id}/APPLY"
    )
    url = url.format(card_id=card_id, inv_id=inv_id)
    response = session.get(url=url)
    return response
