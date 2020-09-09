import time
import urllib.parse

import requests
import pandas as pd
from pypinyin import lazy_pinyin
from lxml import etree
from bs4 import BeautifulSoup

EXCHANGE_RATE = {"HK":0.88,"NY": 6.84}
class spider(object):
    def __init__(self, name):
        self.url = "https://cn.investing.com/instruments/HistoricalDataAjax"
        self.name = name
        self.headers = {
            "Accept": "text/plain, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "cn.investing.com",
            "Origin": "https://cn.investing.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest",
        }

        self.q_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "cn.investing.com",
            "Referer": "https://cn.investing.com/equities/alibaba-historical-data",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
        }
        filename = "".join(lazy_pinyin(name))
        self.output_address = "Data/{}_stock.csv".format(filename)

    def constructData(self, ad_pattern):
        url = self.getHref(name)
        return self.extractData(url, data_pattern)

    def getHref(self, name):
        name = urllib.parse.quote(name)
        url = "https://cn.investing.com/search/?q=" + name
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        hrefs = soup.find_all(attrs={"class":"js-inner-all-results-quote-item row"})
        f_href = ""
        # 取最佳的href值
        for index, data in enumerate(hrefs):
            href = data["href"]
            name = data.find_all(attrs={"class":"third"})[0].get_text()
            if index == 0:
                f_href = href
            if name == self.name:
                f_href = href
                break
        comb_url = "https://cn.investing.com" + f_href + "-historical-data"
        return comb_url

    def extractData(self, url, data_pattern):
        response = requests.post(url, headers=self.q_headers)
        selector = etree.HTML(response.text)
        ids = selector.xpath('//*[@id="leftColumn"]/script[3]/text()')[0]
        ids = ids.split("=")[1]
        ids = ids.replace("\n", "")
        ids = ids.split(",")
        pairId = ids[0].split(":")[1]
        smlId = ids[1].split(":")[1].strip("}")
        header = selector.xpath('//*[@id="leftColumn"]/div[7]/h2/text()')[0]
        data_pattern["curr_id"] = pairId
        data_pattern["smlID"] = smlId
        data_pattern["header"] = header
        market = selector.xpath("//*[@id=\"DropdownBtn\"]/i[1]/text()")[0]
        self.market = "NY" if market == "纽约" else "HK"
        return data_pattern

    def requestURL(self, data):
        """
        爬取网页
        """
        response = requests.post(self.url, data, headers=self.headers)
        return response
    
    def parseWeb(self, response):
        """
        解析网页
        """
        data_list = []

        parse_data = BeautifulSoup(response.text, "html.parser")
        data_all = parse_data.find_all("tr")
        length = len(data_all)
        for index, data in enumerate(data_all):
            data = data.get_text().split("\n")
            split_data = data[6].split(" ")
            data = data[1:6] + split_data
            if index == 0:
                columns = data
            elif index == length - 1:
                continue  # 最值数据
            else:
                for i in range(1,5):
                    data[i] = float(data[i]) * EXCHANGE_RATE[self.market]
                data_list.append(data)
        data_frame = pd.DataFrame(data_list, columns=columns)
        return data_frame

    def outputData(self, data_frame):
        """
        保存数据
        """
        data_frame.to_csv(self.output_address)
    
    def run(self,data):
        """
        运行爬虫
        """
        response = self.requestURL(data)
        data_frame = self.parseWeb(response)
        self.outputData(data_frame)

if __name__ == "__main__":
    data_pattern= {
        "curr_id": 0,
        "smlID": 0,
        "header": "",
        "st_date": "2018/09/08",
        "end_date": "2020/09/08",
        "interval_sec": "Monthly",
        "sort_col": "date",
        "sort_ord": "DESC",
        "action": "historical_data",
        }
    names = ["腾讯", "阿里巴巴", "百度", "新浪", "爱奇艺", "网易", "搜狗", "猎豹移动", "凤凰新媒体", "哔哩哔哩", "汽车之家", "360", "斗鱼", "陌陌", "美图", "小米"]
    for name in names:
        stock_spider = spider(name)
        data = stock_spider.constructData(data_pattern)  # 获取模板需要填入的数据curr_id\smlID\header
        stock_spider.run(data)
        time.sleep(10)  # 休眠10秒