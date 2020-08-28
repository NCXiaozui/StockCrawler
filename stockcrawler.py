import requests
import pandas as pd
from bs4 import BeautifulSoup

class spider(object):
    def __init__(self):
        self.url = "https://cn.investing.com/instruments/HistoricalDataAjax"
        self.headers = {
            "Accept": "text/plain, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "cn.investing.com",
            "Origin": "https://cn.investing.co",
            "Referer":"https://cn.investing.com/equities/alibaba-historical-data",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.output_address = "~/Data/baidu_stock.csv"

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
    data = data = {
        "curr_id": 941155,
        "smlID": 1507702,
        "header": "BABA历史数据",
        "st_date": "2018/09/08",
        "end_date": "2020/09/08",
        "interval_sec": "Monthly",
        "sort_col": "date",
        "sort_ord": "DESC",
        "action": "historical_data",
        }
    stock_spider = spider()
    stock_spider.run(data)