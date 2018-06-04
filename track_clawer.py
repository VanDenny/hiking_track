from Clawer_Base.clawer_frame import Clawer
from selenium import webdriver
import time
import pandas as pd
import traceback
import requests


class Track_info:
    def __init__(self, key_name, file_path):
        self.driver = webdriver.Chrome()
        self.url = 'http://www.2bulu.com/track/track_search.htm?key=%s' % key_name
        self.res_list = []
        self.file_path = file_path

    def open_web(self):
        self.driver.get(self.url)

    def parser(self):
        items = self.driver.find_elements_by_class_name('guiji_discription')
        for item in items:
            info_dict = {}
            info_1 = item.find_element_by_xpath(".//a[@target='_blank']")
            info_2 = item.find_elements_by_xpath(".//ul/li")
            title = info_1.find_element_by_class_name('guiji_name')
            info_dict['trackId'] = info_1.get_attribute('href').split('trackId=')[1]
            info_dict['name'] = title.text
            info_dict['type'] = title.find_element_by_xpath(".//span").text.replace('【', '').replace('】', '')
            distance = info_2[0].find_element_by_xpath('.//span[@class="s1"]').text
            info_dict['distance'] = float(
                distance.replace('km', '').strip()
            )
            info_dict['pic_num'] = float(
                info_2[0].find_element_by_xpath('.//span[@class="s2"]').text
            )
            user_date = info_2[0].find_element_by_xpath('.//span[@class="s7"]').text.split('   ')
            info_dict['user'] = user_date[0].replace('by ', '')
            if len(user_date) == 2:
                info_dict['date'] = user_date[1]
            else:
                info_dict['date'] = ''
            od = info_2[1].text.strip().split('-')
            info_dict['initial'] = od[0].strip()
            if len(od) == 2:
                info_dict['distination'] = od[1].strip()
            else:
                info_dict['distination'] = od[0].strip()
            info_dict['like'] = float(
                info_2[2].find_element_by_xpath('.//span[@class="s3"]').text.replace('赞(', '').replace(')', '')
            )
            try:
                info_dict['download'] = float(
                    info_2[2].find_element_by_xpath('.//span[@class="s4"]').text.replace('下载(', '').replace(')', '')
                )
            except:
                info_dict['download'] = 0
            info_dict['collect'] = float(
                info_2[2].find_element_by_xpath('.//span[@class="s5"]').text.replace('收藏(', '').replace(')', '')
            )
            print(info_dict)
            self.res_list.append(info_dict)

    def is_next_page(self):
        page_eles = self.driver.find_element_by_class_name('pages')
        pages = page_eles.find_elements_by_xpath(".//a[@href='javascript:void(0);']")
        self.next_page = pages[-1]
        if self.next_page.text == "下一页":
            return True
        else:
            return False

    def saver(self):
        df = pd.DataFrame(self.res_list)
        df.to_excel(self.file_path)

    def process(self):
        self.open_web()
        input('是否开始抓取：')
        page_num = 1
        try:
            while True:
                if page_num >= 1:
                    time.sleep(1)
                    try:
                        self.parser()
                    except:
                        time.sleep(5)
                        self.parser()
                if self.is_next_page():
                    try:
                        self.next_page.click()
                    except:
                        time.sleep(5)
                        page_eles = self.driver.find_element_by_class_name('pages')
                        pages = page_eles.find_elements_by_xpath(".//a[@href='javascript:void(0);']")
                        self.next_page = pages[-1]
                        self.next_page.click()
                    page_num += 1
                    time.sleep(2)
                else:
                    break
            self.saver()
        except:
            self.saver()
            traceback.print_exc()







if __name__ == '__main__':
    track_info = Track_info('越秀', 'result/越秀.xlsx')
    track_info.process()
