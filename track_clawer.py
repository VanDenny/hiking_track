from Clawer_Base.clawer_frame import Clawer
from selenium import webdriver
import time
import pandas as pd
import traceback
import os
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


class Track_IdDes(Clawer):
    def __init__(self, trackId=''):
        super(Track_IdDes, self).__init__('')
        self.trackId = trackId
        self.url = 'http://www.2bulu.com/space/download_track.htm?trackId={}%3D&type=3'.format(trackId)

    def scheduler(self):
        code = self.respond.get('code')
        if code == "2":
            return self.parser()
        elif code == '1':
            print('登录失败')
        else:
            print('%s 未知错误' % self.url)

    def parser(self):
        if self.respond:
            res_dict = {}
            gpx_url = self.respond.get('url')
            res_dict['trackId'] = self.trackId
            res_dict['gpx_url'] = gpx_url
            return res_dict
        else:
            print('%s 出现未知错误' % self.url)

    def process(self):
        self.requestor()
        if self.scheduler():
            return self.scheduler()

class Gpx_downloader(Clawer):
    def __init__(self, url):
        super(Gpx_downloader, self).__init__('')
        self.url = url

    def scheduler(self):
        return self.parser()

    def parser(self):
        return self._respond

    def process(self):
        self.requestor()
        if self.scheduler():
            return self.scheduler()





def get_track_iddes(track_info_path):
    Track_IdDes().cookie_init()
    df = pd.read_excel(track_info_path)
    trackIds = df.trackId
    res_list = []
    for i in trackIds:
        print(i)
        trackId = i.replace('=', '')
        # print(Track_IdDes._cookies)
        res_dict = Track_IdDes(trackId).process()
        if isinstance(res_dict,dict):
            res_list.append(res_dict)
    res_df = pd.DataFrame(res_list)
    path_parts = os.path.splitext(track_info_path)
    out_path = path_parts[0] + '_des.xlsx'
    res_df.to_excel(out_path)


def get_gpx(gpx_url_path):
    df = pd.read_excel(gpx_url_path)
    url_infos = df.to_dict('records')
    for url_info in url_infos[110:]:
        print(url_info['order'])
        gps_downloader = Gpx_downloader(url_info['gpx_url'])
        content = gps_downloader.process()
        path_parts = os.path.split(gpx_url_path)
        out_path = os.path.join(path_parts[0], url_info['filename'])
        with open(out_path, 'w') as f:
            f.write(content)




if __name__ == '__main__':
    # get_track_iddes(r'D:\program_lib\hiking_track\result\威海.xlsx')
    get_gpx(r'D:\program_lib\hiking_track\result\威海_des.xlsx')
    # track_info = Track_info('越秀', 'result/越秀.xlsx')
    # track_info.process()
