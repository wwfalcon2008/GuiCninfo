import os
import threading
import time
from urllib.request import urlretrieve

import requests

import json


class Cninfoer(threading.Thread):
    def __init__(self, pageNum, pageSize, column, tabName, plate, stock,
                 searchkey, secid, category, trade, seDate, sortName,
                 sortType, isHLtitle, logger, path, csv_name, total_pages,
                 pushButton_start, pushButton_stop):
        super(Cninfoer, self).__init__()
        self.pageNum = pageNum
        self.pageSize = pageSize
        self.column = column
        self.tabName = tabName
        self.plate = plate
        self.stock = stock
        self.searchkey = searchkey
        self.secid = secid
        self.category = category
        self.trade = trade
        self.seDate = seDate
        self.sortName = sortName
        self.sortType = sortType
        self.isHLtitle = isHLtitle
        self.logger = logger
        self.path = path
        self.csv_name = csv_name
        self.total_pages = total_pages
        self.totalRecordNum = 0
        self.downloader_counter = 0
        self.stop_flag = False
        self.pushButton_start = pushButton_start
        self.pushButton_stop = pushButton_stop
        self.headline = '股票代码,公司名称,公告标题,公告时间,Id,存放位置,文件链接\n'

        if not os.path.exists(self.path):
            os.mkdir(self.path)

        if not os.path.exists(self.csv_name):
            self.title_line = self.headline
        else:
            self.title_line = ''
        # self.fp = open(self.csv_name+pageNum+'.csv', 'a', encoding='utf-8')
        # 注意编码格式
        self.fp = open(self.csv_name, 'a', encoding='gbk')

    def run(self):
        self.counter = 0
        time.sleep(0.5)
        p = self.pageNum
        self.total_pages = self.get_totalpages_utilityfunc()
        print('总页数:', self.total_pages, ' 起始页码:', p)
        while not self.stop_flag and int(p) <= self.total_pages:
            self.crawl(p, pageSize=self.pageSize,
                       column=self.column, tabName=self.tabName,
                       plate=self.plate, stock=self.stock,
                       searchkey=self.searchkey, secid=self.secid,
                       category=self.category, trade=self.trade,
                       seDate=self.seDate, sortName=self.sortName,
                       sortType=self.sortType, isHLtitle=self.isHLtitle)
            time.sleep(0.5)
            p = str(int(p) + 1)
        self.logger.append('爬虫下载完成')
        self.fp.close()
        self.pushButton_stop.click()

    def __del__(self):
        self.fp.close()
        self.logger.append('Cninfoer terminated')

    def crawl(self, pageNum, pageSize, column, tabName, plate, stock,
              searchkey, secid, category, trade, seDate, sortName,
              sortType, isHLtitle):
        print('page::::', int(self.pageNum), ' totalpage::::', self.total_pages)
        j = self.get_json(pageNum, pageSize, column, tabName, plate, stock,
                          searchkey, secid, category, trade, seDate,
                          sortName,
                          sortType, isHLtitle)

        self.downloader(j)
        print('>>>>>>>>>>', self.pageNum)

    @staticmethod
    def get_json(pageNum, pageSize, column, tabName, plate, stock,
                 searchkey, secid, category, trade, seDate, sortName,
                 sortType, isHLtitle):
        base_url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
        formdata = {
            "pageNum": pageNum,
            "pageSize": pageSize,
            "column": column,
            "tabName": tabName,
            "stock": stock,
            "searchkey": searchkey,
            "category": category,
            "seDate": seDate,
            "isHLtitle": isHLtitle,
        }
        headers = {
            'Accept': r'*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'JSESSIONID=4A49726D78F4706E8776111D25E1844D; insert_cookie=45380249; _sp_ses.2141=*; routeId=.uc1; SID=43f9d443-23f0-4d20-b78d-8e1cbf723384; _sp_id.2141=9652e861-2ea6-44ad-b54c-8809684d3af6.1647231961.1.1647232672.1647231961.1be5cf4a-3edc-4989-8415-79de6d152b32',
            'Origin': 'http://www.cninfo.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39',
            'X-Requested-With': 'XMLHttpRequest',
        }
        print(formdata)
        response = requests.post(url=base_url, headers=headers,
                                 data=formdata)
        return response.text

    def get_totalpages_utilityfunc(self):
        json_text = self.get_json(self.pageNum, self.pageSize, self.column,
                                  self.tabName, self.plate, self.stock,
                                  self.searchkey, self.secid, self.category,
                                  self.trade, self.seDate, self.sortName,
                                  self.sortType, self.isHLtitle)
        records = json.loads(json_text)
        # print(records)
        totalpages = records['totalpages']
        # print(totalpages)
        totalpages = int(totalpages) + 1
        print('TOTALPAGES_UTILITY: ', totalpages)
        return totalpages

    def downloader(self, json_text):
        self.downloader_counter += 1
        print("DOWNLOADER_COUNTER: ", self.downloader_counter)
        records = json.loads(json_text)
        self.totalRecordNum = records['totalRecordNum']
        self.totalpages = self.get_totalpages_utilityfunc()
        pages_line = '总页数： %s, 当前页码 %s' % (self.totalpages, self.pageNum)
        record_line = '总记录条数： %s' % self.totalRecordNum
        self.logger.append(pages_line)
        self.logger.append(record_line)
        print(pages_line)
        print(record_line)

        if int(self.totalRecordNum) == 0:
            self.logger.append('没有相关内容')
        else:
            self.logger.append('下载清单记录在' + self.csv_name)
            self.fp.write(self.title_line)
            self.logger.append(self.headline)
            print(self.headline)

            for r in records["announcements"]:
                secName = r['secName']
                announcementTitle = r['announcementTitle']
                announcementId = r['announcementId']
                url = r['adjunctUrl']
                announcementTime = r['announcementTime']
                secCode = r['secCode']
                url = r'http://static.cninfo.com.cn/' + url

                secName = secName.replace('<em>', '').replace('</em>', '')
                announcementTitle = announcementTitle.replace('<em>', '') \
                    .replace('</em>', '')
                announcementId = announcementId.replace('<em>', '') \
                    .replace('</em>', '')
                url = url.replace('<em>', '').replace('</em>', '')
                timeArray = time.localtime(announcementTime / 1000)
                announcementTime = time.strftime('%Y-%m-%d',
                                                 timeArray)
                secCode = secCode.replace('<em>', '').replace('</em>', '')
                self.counter += 1
                print(self.counter, secCode, secName, announcementTitle,
                      announcementTime,
                      announcementId, url)
                folder_path = self.path + secName + '/'
                if not os.path.exists(folder_path):
                    os.mkdir(folder_path)

                filename = self.get_filename(secCode, folder_path,
                                             announcementTitle,
                                             announcementTime,
                                             url)
                # line = '%s,%s,%s,%s,%s,%s, %s\n' % (secCode, secName,
                #                                 announcementTitle,
                #                                 announcementTime,
                #                                 announcementId,filename,
                #                                 url)
                line = f'{secCode},{secName},{announcementTitle},' \
                       f'{announcementTime},{announcementId},{filename},{url}'

                self.logger.append('downloading:')
                self.logger.append(line)
                ## download file， 注意去重
                if not os.path.exists(filename):
                    self.fp.write(line)
                    urlretrieve(url=url, filename=filename)
                    print('downloading...\n', filename, ' from ', url)
                else:
                    self.logger.append('<---文件已存在')
                    print('文件已存在： ', filename)
                if self.stop_flag:
                    break
                time.sleep(0.5)

    def get_filename(self, secCode, folder_path, title, announcementTime, url):
        symbol_list = ['?', '"', '/', '\\', '<', '>', '\*', '|', ':', '-',
                       '\t', ' ']
        for s in symbol_list:
            title = title.strip().replace(s, '_')

        filename = folder_path + announcementTime + title + \
                   secCode + '.' + \
                   url.split('.')[-1]
        return filename
