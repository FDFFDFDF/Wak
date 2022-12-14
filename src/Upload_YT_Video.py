from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs

import re
import csv
from tkinter import messagebox
import time
import pyperclip

import logging

logging.basicConfig()

class Constant:
    """A class for storing constants for YoutubeUploader class"""
    YOUTUBE_URL = 'https://www.youtube.com/'
    YOUTUBE_STUDIO_URL = 'https://studio.youtube.com'
    YOUTUBE_UPLOAD_URL = 'https://www.youtube.com/upload'
    USER_WAITING_TIME = 1
    VIDEO_TITLE = 'title'
    VIDEO_DESCRIPTION = 'description'
    #DESCRIPTION_CONTAINER = '/html/body/ytcp-uploads-dialog/paper-dialog/div/ytcp-animatable[1]/' \
    #                        'ytcp-uploads-details/div/ytcp-uploads-basics/ytcp-mention-textbox[2]'
    DESCRIPTION_CONTAINER = '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]' \
                            '/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[2]' \
                            '/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div'

    NOT_MADE_FOR_KIDS_CONTAINER = '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]'\
                                  '/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[5]'\
                                  '/ytkc-made-for-kids-select/div[4]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[2]/div[2]'


    TEXTBOX = 'textbox'
    RADIO_LABEL = 'radioLabel'
    STATUS_CONTAINER = '/html/body/ytcp-uploads-dialog/paper-dialog/div/ytcp-animatable[2]/' \
                       'div/div[1]/ytcp-video-upload-progress/span'

                       
    #NOT_MADE_FOR_KIDS_LABEL = 'NOT_MADE_FOR_KIDS'
    NOT_MADE_FOR_KIDS_LABEL = 'VIDEO_MADE_FOR_KIDS_NOT_MFK'
    NEXT_BUTTON = 'next-button'
    PUBLIC_BUTTON = 'PUBLIC'
    UNLISTED_BUTTON = 'UNLISTED'
    VIDEO_URL_ELEMENT = "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/"\
                          "ytcp-uploads-review/div[3]/ytcp-video-info/div/div[2]/div[1]/div[2]/span/a"

    HREF = 'href'
    UPLOADED = '????????? ???'
    ERROR_CONTAINER = '//*[@id="error-message"]'
    DONE_BUTTON = 'done-button'
    INPUT_FILE_VIDEO = "//input[@type='file']"


class Upload_YT_Video:

    def __init__(self, Clip_file, logger, driver):

        self.Clip_file = Clip_file
        self.logger = logger

        self.keys = []
        self.res_lists = []
        self.driver = driver

    def get_list(self):

        #print("????????? ?????? ?????? ???????????? ???????????? ???????????????.")
        self.logger.info("????????? ?????? ?????? ???????????? ???????????? ???????????????.")

        # ?????? ?????? ?????? ??????
        f_clips = open(self.Clip_file,'r', encoding='UTF8')

        rdr = csv.reader(f_clips)

        read_csv = list(rdr)

        res_text_list = read_csv 

        self.keys = res_text_list.pop(0)    #??? ????????? ??????

        f_clips.close()

        if len(res_text_list)<=0:
            self.logger.warning("?????? : ????????? ????????? ????????????.")
            messagebox.showwarning("??????", "????????? ????????? ????????????.\n config.txt ????????? ????????? ?????????????????? ??????????????????.")
        else:
            for text_list in res_text_list:

                list_to_dict = []
                for i in range(len(self.keys)):
                    list_to_dict.append([self.keys[i],text_list[i]])

                dict_ = dict(list_to_dict)
                self.res_lists.append(dict_ )


            #print("?????? ?????? ???????????? ??????")
            self.logger.info("?????? ?????? ???????????? ??????")

    def login(self):
        #self.driver.get(Constant.YOUTUBE_URL)
        self.driver.get('https://accounts.google.com/signin')
        time.sleep(Constant.USER_WAITING_TIME)

        #while?????? ????????? ???????????? ?????????
        while self.driver.current_url.find('https://myaccount.google.com/?utm_source=sign_in_no_continue')<0:
            time.sleep(1)                    

        # ????????? ?????? ?????? ??????
        self.driver.get('https://www.youtube.com/channel_switcher')
        messagebox.showinfo("?????? ??????", "???????????? ????????? ????????? ????????? ????????? ??????????????????")


        while self.driver.current_url != Constant.YOUTUBE_URL:
            time.sleep(1)

        #self.driver.get(Constant.YOUTUBE_URL)
        #time.sleep(Constant.USER_WAITING_TIME)
        #self.driver.save_cookies()

    def Update_CSV(self, res_list, url):

        res_list['Youtube_URL'] = url

        f_clips = open(self.Clip_file,'w', encoding='UTF8', newline="")

        writer = csv.DictWriter(f_clips, fieldnames = self.keys)            
        writer.writeheader()
        writer.writerows(self.res_lists)

        f_clips.close()


        self.logger.info("CSV ???????????? ??????")

    def upload(self):

        idx = -1
        for res_list in self.res_lists:

            idx = idx +1

            if res_list['is_downloaded'] == 'T':
                if res_list['is_fixed_for_YT'] == 'O':
                    if res_list['Youtube_URL'] == 'https://':
                            
                        self.logger.info("?????? ?????? ????????? : " + res_list['file_path'])

                        self.driver.get(Constant.YOUTUBE_UPLOAD_URL)
                        time.sleep(Constant.USER_WAITING_TIME)

                        # ?????????
                        absolute_video_path = res_list['file_path'] + re.sub('[^0-9a-zA-Z???-??? ]', '_', res_list['title']) + '.mp4'

                        # ?????? ????????? ?????? ?????? 8.3 ???????????? ????????????
                        if len(absolute_video_path)>=260:
                            import ctypes
                            from ctypes import wintypes
                            _GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
                            _GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
                            _GetShortPathNameW.restype = wintypes.DWORD
                            output_buf_size = 0
                            while True:
                                output_buf = ctypes.create_unicode_buffer(output_buf_size)
                                needed = _GetShortPathNameW(absolute_video_path, output_buf, output_buf_size)
                                if output_buf_size >= needed:
                                    absolute_video_path = output_buf.value
                                    break
                                else:
                                    output_buf_size = needed

                            
                        self.logger.info("?????? ?????? ????????? ?????? : " + res_list['file_path'])
                        # ????????? ?????? ?????? ??? ??????
                        while True:
                            try:
                                upload_contents = self.driver.find_element(By.XPATH, Constant.INPUT_FILE_VIDEO)
                                upload_contents.send_keys(absolute_video_path)

                            except:
                                time.sleep(0.05)
                                continue
                            break

                        self.logger.info("???????????? ?????? ?????? ?????? ?????? ?????? : " + res_list['file_path'])

                        #self.logger.debug('Attached video {}'.format(self.video_path))

                        #title_field = self.driver.find_element(By.ID, "select-files-button")
                        time.sleep(Constant.USER_WAITING_TIME*5)


                        # ?????? ?????? 100??????
                        title = res_list['title']
                        while len(title)>100:
                            title = title[:-1]

                        # ????????? ?????? ????????? ?????? ??? ???
                        title = re.sub('<|>','_',title)

                        self.logger.info("?????? ?????? ?????? ?????? : " + res_list['file_path'])
                        # ??????
                        while True:
                            try:
                                title_field = self.driver.find_element(By.ID, Constant.TEXTBOX)
                                #title_field = self.driver.find_element(By.ID, "select-files-button")
                                title_field.click()
                                time.sleep(Constant.USER_WAITING_TIME)

                                title_field.send_keys(Keys.CONTROL, 'a')
                                title_field.send_keys(Keys.DELETE)
                                time.sleep(Constant.USER_WAITING_TIME)

                                title_field.clear()
                                time.sleep(Constant.USER_WAITING_TIME)

                                title_field.click()
                                time.sleep(Constant.USER_WAITING_TIME)
                                
                                pyperclip.copy(title)
                                title_field.send_keys(Keys.CONTROL, 'v')
                                
                            except:
                                time.sleep(0.05)
                                continue
                            break

                        self.logger.info("?????? ?????? ?????? ?????? ?????? : " + title)


                        self.logger.info("?????? ?????? ?????? ?????? : " + res_list['file_path'])
                        # ???????????????
                        description_file = open(res_list['file_path'] + re.sub('[^0-9a-zA-Z???-??? ]', '_', res_list['title']) + '-timeline.txt', 'r', encoding='UTF8')

                        # ????????? ?????? ?????? ?????? ??? ???
                        video_description = description_file.read()
                        video_description = re.sub('<|>','_',video_description)

                        description_field = self.driver.find_element(By.XPATH, Constant.DESCRIPTION_CONTAINER)
                        description_field.click()
                        time.sleep(Constant.USER_WAITING_TIME)
                        description_field.clear()
                        time.sleep(Constant.USER_WAITING_TIME)
                        pyperclip.copy(video_description)
                        description_field.send_keys(Keys.CONTROL, 'v')
                        self.logger.info("?????? ?????? ?????? ?????? ?????? : " + video_description)


                        # ????????? ??????
                        kids_section = self.driver.find_element(By.XPATH, Constant.NOT_MADE_FOR_KIDS_CONTAINER)
                        kids_section.click()
                        self.logger.info("????????? ?????? : " + res_list['file_path'])


                        # ?????? ?????? ??????
                        self.driver.find_element(By.ID, Constant.NEXT_BUTTON).click()
                        self.logger.debug('Clicked {}'.format(Constant.NEXT_BUTTON))

                        self.driver.find_element(By.ID, Constant.NEXT_BUTTON).click()
                        self.logger.debug('Clicked another {}'.format(Constant.NEXT_BUTTON))


                        self.driver.find_element(By.ID, Constant.NEXT_BUTTON).click()
                        self.logger.debug('Clicked another {}'.format(Constant.NEXT_BUTTON))

                        self.logger.info("????????? ????????? : " + res_list['file_path'])

                        time.sleep(Constant.USER_WAITING_TIME)

                        # ?????? ??????
                        unlisted_main_button = self.driver.find_element(By.NAME, Constant.UNLISTED_BUTTON)
                        unlisted_main_button.find_element(By.ID, Constant.RADIO_LABEL).click()
                        self.logger.info("?????? ?????? : " + res_list['file_path'])


                        self.logger.info("????????? ?????? ?????? : " + res_list['file_path'])
                        # ????????? ?????? ????????? ??????                        
                        while True:
                            #in_process = status_container.text.find(Constant.UPLOADED) != -1
                            
                            soup = bs(self.driver.page_source, 'html.parser')
                            status_container = soup.find('span',class_='progress-label style-scope ytcp-video-upload-progress')
                            in_process = status_container.get_text().find(Constant.UPLOADED) != -1
                            if in_process:
                                time.sleep(Constant.USER_WAITING_TIME)
                            else:
                                break
                        self.logger.info("????????? ?????? : " + res_list['file_path'])

                        time.sleep(Constant.USER_WAITING_TIME*3)

                        soup = bs(self.driver.page_source, 'html.parser')
                        video_url_element = soup.find('a',class_='style-scope ytcp-video-info')
                        video_url = video_url_element.get('href')
                        
                        self.logger.info("?????? ?????? ?????? : " + res_list['file_path'] + '\t' + video_url)

                        done_button = self.driver.find_element(By.ID, Constant.DONE_BUTTON)

                        self.logger.info("?????? ?????? ????????? : " + res_list['file_path'])
                        # Catch such error as
                        # "File is a duplicate of a video you have already uploaded"
                        if done_button.get_attribute('aria-disabled') == 'true':
                            error_message = self.driver.find_element(By.XPATH,
                                                            Constant.ERROR_CONTAINER).text
                            self.logger.error(error_message)
                            #title_idx = -1
                            continue
                            #return False, None

                        done_button.click()

                        self.logger.info("?????? ?????? ????????? ?????? : " + res_list['file_path'])

                        time.sleep(Constant.USER_WAITING_TIME)
                        self.logger.info("?????? ?????? ?????? ?????? : " + res_list['file_path'] + '\t' + video_url)
                        self.Update_CSV(self.res_lists[idx],video_url)
                        self.logger.info("?????? ?????? ?????? ?????? ?????? : " + res_list['file_path'] + '\t' + video_url)
                        #self.driver.get(video_url)


                        while True:
                            try:
                                done_button2 = self.driver.find_element(By.XPATH, '/html/body/ytcp-uploads-still-processing-dialog/ytcp-dialog/tp-yt-paper-dialog/div[3]/ytcp-button/div')                                
                                done_button2.click()
                            except:
                                time.sleep(1)
                                continue
                            break

                    else:
                        self.logger.info("?????? ???????????? ?????? ?????? : " + res_list['Youtube_URL'])
                        #self.driver.get(res_list['Youtube_URL'])

                else:
                    self.logger.info("???????????? ?????? ?????? ?????? : " + res_list['file_path'])


    def clip(self):

        is_not_ready = True
        while is_not_ready:
            is_not_ready = False
            idx = -1
            for res_list in self.res_lists:

                idx = idx +1

                if res_list['is_downloaded'] == 'T':
                    if res_list['is_fixed_for_YT'] == 'O':
                        if res_list['Youtube_URL'] != 'https://':
                            if float(res_list['duration'])>60:
                                self.logger.info("?????? ?????? ?????? ?????? : ????????? " + res_list['title'])
                                title_idx =  idx
                            else:
                                self.logger.info("?????? ?????? ????????? ??? ????????? ?????? : " + res_list['file_path'])
                                title_idx =  -1
                        else:
                            self.logger.info("????????? ?????? ?????? ?????? ?????? : " + res_list['file_path'])
                            title_idx =  -1
                    else:
                        self.logger.info("???????????? ?????? ?????? ?????? : " + res_list['file_path'])
                        title_idx = -1
                else:
                    if title_idx>=0:
                        if self.res_lists[title_idx]['Youtube_URL'] == 'https://':
                            self.logger.info("??????????????? ?????? ?????? ?????? : " + res_list['file_path'])
                        else:
                            if res_list['Youtube_URL'] == 'https://':
                                self.logger.info("?????? ?????? ?????? : " + res_list['file_path'])
                                if idx == len(self.res_lists)-1: # ????????? ?????????
                                    # ????????? ?????? ??????
                                    url = self.Make_Clip_and_Get_url(res_list, res_list['Youtube_timeline'], 99999, self.res_lists[title_idx]['Youtube_URL'])
                                else:
                                    # ????????? ?????? ??????
                                    if self.res_lists[idx+1]['Youtube_timeline'] == '0.0': # ????????? ??????
                                        url = self.Make_Clip_and_Get_url(res_list, res_list['Youtube_timeline'], 99999, self.res_lists[title_idx]['Youtube_URL'])
                                    else:
                                        url = self.Make_Clip_and_Get_url(res_list, res_list['Youtube_timeline'], self.res_lists[idx+1]['Youtube_timeline'], self.res_lists[title_idx]['Youtube_URL'])

                                if url is not None:
                                    self.logger.info("?????? ?????? ?????? ?????? : " + res_list['file_path'])

                                    self.Update_CSV(self.res_lists[idx], url)

                                    self.logger.info("?????? ?????? ?????? ?????? ?????? : " + res_list['file_path'])

                                else:
                                    self.logger.info("???????????? ?????? ????????? ??? ?????? : " + res_list['file_path'])
                                    is_not_ready = True

                            else:
                                self.logger.info("?????? ????????? ?????? ?????? : " + res_list['Youtube_URL'])

            if is_not_ready:
                self.logger.info("????????? ????????? ??? ??????????????? : 5??? ?????? ??? ?????? ???????????????.")
                time.sleep(5)

    

    def Make_Clip_and_Get_url(self, res_list, st, et, video_url):

        self.logger.info("????????? ????????? ?????? ??????")
        # ????????? ??????
        while True:
            try:
                self.driver.get(video_url)
                if self.driver.current_url.find(video_url.split('/')[-1])>=0:
                    break
            except:
                time.sleep(5)

        # ?????? ????????? ????????? ?????? ?????? ????????? ?????? ?????? ?????? ??????
        while True:
            try:
                dotdotdot = self.driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[2]/div/div/ytd-menu-renderer/yt-button-shape/button/yt-touch-feedback-shape/div/div[2]')
                dotdotdot.click()
            except:
                time.sleep(0.05)
                continue
            break

        # ?????? ?????? ??????
        # ?????? ?????? ?????? ?????? ???
        clip_button = None
        iter = 0

        while not clip_button:
            yt_buttons = self.driver.find_elements(By.ID,'flexible-item-buttons')
            
            for b in yt_buttons:
                if b.text == '??????':
                    clip_button = b
                    break

            # ?????? ?????? ????????? ???????????? ????????? ???
            # ????????? ??? ????????? ?????? ?????? ?????? ?????? ???
            if not clip_button:
                yt_buttons = self.driver.find_elements(By.CLASS_NAME,'style-scope ytd-menu-service-item-renderer')
                for b in yt_buttons:
                    if b.text == '??????':
                        clip_button = b
                        break

            time.sleep(0.05)
            iter = iter +1

            # 5??? ?????? ???????????? ??? ????????? ?????? ?????????!
            # ?????? ???????????? ?????????
            if iter >= 100:
                return None


        clip_button.click()

        # ?????? ?????? ??????
        Clip_title_box = self.driver.find_element(By.ID,'textarea')

        # ?????? ?????? 140????????????.. ??? 59???????????? ??????? ????????? 3???????????? ?????????????
        title = res_list['title']
        while len(title)>57:
            title = title[:-1]
        pyperclip.copy(title)
        Clip_title_box.send_keys(Keys.CONTROL, 'v')

        # ?????? ?????? ??????
        # ?????? ??????
        st_buttons = self.driver.find_elements(By.ID,'start')

        for b in st_buttons:
            if b.tag_name == 'input':
                st_button = b
                break
        
        # ?????? ??????
        st_button.click()
        st_button.send_keys(Keys.CONTROL, 'a')
        pyperclip.copy(str(st))
        st_button.send_keys(Keys.CONTROL, 'v')



        # ?????? ?????? ??????
        # ?????? ??????
        ed_buttons = self.driver.find_elements(By.ID,'end')

        for b in ed_buttons:
            if b.tag_name == 'input':
                ed_button = b
                break
        
        # ?????? ??????
        ed_button.click()
        ed_button.send_keys(Keys.CONTROL, 'a')
        pyperclip.copy(str(et))
        ed_button.send_keys(Keys.CONTROL, 'v')

        # ?????? ?????? ?????????
        done_buttons = self.driver.find_elements(By.ID,'share')

        for b in done_buttons:
            if b.text == '?????? ??????':
                done_button = b
                break

        done_button.click()


        # ?????? ?????? ??????
        idx = 0
        while True:
            try:
                links = self.driver.find_elements(By.CLASS_NAME, 'style-scope yt-copy-link-renderer')
                for b in links:
                    if b.text == '??????':
                        link = b
                        break
            
                copy_button = link.find_element(By.ID, 'copy-button')
            except:
                idx = idx + 1
                time.sleep(0.05)
                if idx>200:
                    self.logger.error('???????????? ?????? : ' + res_list['title'])

                continue
            break


        copy_button.click()

        clip_url = pyperclip.paste()

        return clip_url


    def Run(self):
        self.get_list()

        #self.login()

        self.upload()

        self.clip()


if __name__ == '__main__':

    import undetected_chromedriver as uc
    import datetime
    import os

    #?????? ??????
    logger = logging.getLogger()
    logger.handlers = []
    #logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(formatter)
    logger.addHandler(streamhandler)
    if not os.path.exists('logs'):
        os.mkdir('logs')
    filehandler = logging.FileHandler('logs/logfile_{:%Y%m%d-%H_%M_%S}.log'.format(datetime.datetime.now()), encoding='utf-8')
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)

    logger.info("??????")

    Clip_file = "Clip_list.csv"

    driver = uc.Chrome()

    UYTV = Upload_YT_Video(Clip_file, logger, driver)

    UYTV.login()
    UYTV.Run()