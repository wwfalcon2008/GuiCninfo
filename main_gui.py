import sys
import time
import urllib.request

import gui
import json
import requests
from PyQt5 import QtWidgets
from gui import Ui_Form

from Cninfoer import Cninfoer
from Dialog_Form import DialogForm


class GuiCninfo(QtWidgets.QWidget, Ui_Form):
    # crawler_thread = CrawlThread('', '', '', '', '', '')
    logger = None
    running_flag = False
    pause_flag = False
    path = './download/'
    csv_name = path + 'list.csv'
    category=''

    def __init__(self):
        super(GuiCninfo, self).__init__()
        self.setupUi(self)
        self.logger = self.textBrowser
        self.pushButton_stop.setEnabled(False)
        self.pushButton_start.setEnabled(True)
        self.pushButton_column.setEnabled(True)
        self.pool = []

    def start(self, event):
        self.logger.append('开始')
        # if self.running_flag==False:
        pageNum = self.lineEdit_pageNum.text()
        recordNum = self.lineEdit_recordNum.text()
        pageSize = '30'
        ## 下拉菜单选择分组，默认深沪京 szse
        if self.comboBox_column.currentIndex() == 0:
            column = 'szse'  # 深沪京
        elif self.comboBox_column.currentIndex() == 1:
            column = 'fund'  # 基金
        elif self.comboBox_column.currentIndex() == 2:
            column = 'bond'  # 债券
        elif self.comboBox_column.currentIndex() == 3:
            column = 'hke'  # 港股
        else:
            column = 'third'  # 三板
        tabName = 'fulltext'
        if self.comboBox_tabname.currentIndex() == 0:
            tabName = 'fulltext'  # 公告
        elif self.comboBox_tabname.currentIndex() == 1:
            tabName = 'relation'  # 调研
        else:
            tabName = 'supervise'  # 持续督导

        plate = ''
        stock = self.get_stock(self.lineEdit_stock.text(), column)
        searchkey = self.lineEdit_searchkey.text()
        secid = ''
        # category = Dialog Selector
        category = self.category
        trade = ''
        fromDate = self.lineEdit_from_date.text()
        toDate = self.lineEdit_to_date.text()
        seDate = fromDate + '~' + toDate
        sortName = ''
        sortType = ''
        isHLtitle = 'true'

        self.logger.append('开始爬取...')
        print('开始爬取...')

        self.pushButton_column.setEnabled(False)
        self.pushButton_stop.setEnabled(True)
        self.pushButton_start.setEnabled(False)

        # self.cninfoer = Cninfoer(pageNum, pageSize, column, tabName, plate, stock,
        #         searchkey, secid, category, trade, seDate, sortName,
        #         sortType, isHLtitle, self.logger, self.path, self.csv_name, '0')
        # self.cninfoer.start()

        self.total_pages = self.get_totalpages_utilityfunc(pageNum, pageSize,
                                                           column, tabName,
                                                           stock, searchkey,
                                                           category, seDate,
                                                           isHLtitle)
        print('计划下载页数：', self.total_pages - int(pageNum) + 1)
        if self.total_pages < 1:
            # self.cninfoer = Zombie()
            line = '无可爬取文件'
            self.logger.append(line)
            print(line)
        else:
            # for i in range(int(pageNum), self.total_pages+1):
            cninfoer = Cninfoer(pageNum, pageSize, column, tabName, plate,
                                stock,
                                searchkey, secid, category, trade, seDate,
                                sortName,
                                sortType, isHLtitle, self.logger,
                                self.path, self.csv_name, self.total_pages,
                                self.pushButton_start, self.pushButton_stop)
            cninfoer.start()
            self.pool.append(cninfoer)

            time.sleep(1)

    def stop(self, event):
        for p in self.pool:
            p.stop_flag = True
            p.fp.close()
        print('主动终止爬虫')
        # self.cninfoer.fp.close()
        self.logger.append('爬虫终止')
        self.pushButton_stop.setEnabled(False)
        self.pushButton_start.setEnabled(True)
        self.pushButton_column.setEnabled(True)

    def clean(self, event):
        self.logger.setText('')
        self.lineEdit_searchkey.setText('')
        self.lineEdit_stock.setText('')
        self.lineEdit_from_date.setText(gui.Ui_Form.sdate())
        self.lineEdit_to_date.setText(gui.Ui_Form.edate())

    def column_select(self, event):
        self.d = DialogForm(self.category)
        self.d.show()
        if self.d.exec_() == self.d.Accepted:
            self.category = self.d.get_output()
            selected = self.d.get_selected()
            i = 0
            line = ''
            for s in selected:
                if s == 1:
                    line += self.category_list[i] + ','
                i += 1
            print('selected: ', line)
            self.lineEdit_selected.setText(line)
            self.logger.append('分类选择：')
            self.logger.append(line)
        print('colum_select:', self.category)

    # def textBrowser_scroll(self, event):
    #     pass

    def get_stock(self, stock, column):
        hke_stock_url = 'http://www.cninfo.com.cn/new/data/hke_stock.json'
        szse_stock_url = 'http://www.cninfo.com.cn/new/data/szse_stock.json'
        fund_stock_url = 'http://www.cninfo.com.cn/new/data/fund_stock.json'
        bond_stock_url = 'http://www.cninfo.com.cn/new/data/fund_stock.json'
        third_stock_url = 'http://www.cninfo.com.cn/new/data/gfzr_stock.json'

        if column == 'szse':  # 深沪京
            url = szse_stock_url
        elif column == 'fund':  # 基金
            url = fund_stock_url
        elif column == 'bond':  # 债券
            url = bond_stock_url
        elif column == 'hke':  # 港股
            url = hke_stock_url
        else:  # 三板
            url = third_stock_url

        stock = stock.lower()
        stock_json = urllib.request.urlopen(
            url=url).read().decode('utf-8')
        # print(stock_json)
        stock_json = json.loads(stock_json)
        # print(stock_json)

        for s in stock_json['stockList']:
            if (stock in s.get('code')) or (stock in s.get('pinyin')) or (
                    stock in s.get('zwjc')):
                orgId = s.get('orgId')
                code = s.get('code')
                zwjc = s.get('zwjc')
                stock_info = '%s, %s, %s' % (code, zwjc, orgId)
                print(stock_info)
                self.logger.append(stock_info)
                return code + ',' + orgId

        self.logger.append('未找到指定股票代码/简称/拼音')
        return stock

    @staticmethod
    def get_totalpages_utilityfunc(pageNum, pageSize, column, tabName, stock,
                                   searchkey, category, seDate, isHLtitle):
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
            'Cookie': 'JSE0-4232152b32',
            'Origin': 'http://www.cninfo.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39',
            'X-Requested-With': 'XMLHttpRequest',
        }
        print(formdata)
        response = requests.post(url=base_url, headers=headers,
                                 data=formdata)

        json_text = response.text
        records = json.loads(json_text)
        # print(records)
        totalpages = records['totalpages']

        totalpages = int(totalpages) + 1
        print('TOTALPAGES_UTILITY: ', totalpages)
        return totalpages

    category_list = [
        '年报',
        '半年报',
        '一季报',
        '三季报',
        '业绩预告',
        '权益分派',
        '董事会',
        '监事会',
        '股东大会',
        '日常经营',
        '公司治理',
        '中介报告',
        '首发',
        '增发',
        '股权激励',
        '配股',
        '解禁',
        '公司债',
        '可转债',
        '其它融资',
        '股权变动',
        '补充更正',
        '澄清致歉',
        '风险提示',
        '特别处理和退市',
        '退市整理期', ]


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui_cninfo = GuiCninfo()
    gui_cninfo.show()

    sys.exit(app.exec_())
