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
    UPLOADED = '업로드 중'
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

        #print("저장된 클립 주소 파일에서 데이터를 불러옵니다.")
        self.logger.info("저장된 클립 정보 파일에서 데이터를 불러옵니다.")

        # 클립 주소 파일 열기
        f_clips = open(self.Clip_file,'r', encoding='UTF8')

        rdr = csv.reader(f_clips)

        read_csv = list(rdr)

        res_text_list = read_csv 

        self.keys = res_text_list.pop(0)    #맨 윗줄은 정보

        f_clips.close()

        if len(res_text_list)<=0:
            self.logger.warning("경고 : 불러올 클립이 없습니다.")
            messagebox.showwarning("경고", "불러올 클립이 없습니다.\n config.txt 파일이 제대로 세팅되었는지 확인해주세요.")
        else:
            for text_list in res_text_list:

                list_to_dict = []
                for i in range(len(self.keys)):
                    list_to_dict.append([self.keys[i],text_list[i]])

                dict_ = dict(list_to_dict)
                self.res_lists.append(dict_ )


            #print("클립 주소 불러오기 완료")
            self.logger.info("클립 주소 불러오기 완료")

    def login(self):
        #self.driver.get(Constant.YOUTUBE_URL)
        self.driver.get('https://accounts.google.com/signin')
        time.sleep(Constant.USER_WAITING_TIME)

        #while문은 로그인 완료까지 기다림
        while self.driver.current_url.find('https://myaccount.google.com/?utm_source=sign_in_no_continue')<0:
            time.sleep(1)                    

        # 브랜드 계정 채널 선택
        self.driver.get('https://www.youtube.com/channel_switcher')
        messagebox.showinfo("계정 선택", "업로드에 사용할 브랜드 계정을 선택해주세요")


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


        self.logger.info("CSV 업데이트 완료")

    def upload(self):

        idx = -1
        for res_list in self.res_lists:

            idx = idx +1

            if res_list['is_downloaded'] == 'T':
                if res_list['is_fixed_for_YT'] == 'O':
                    if res_list['Youtube_URL'] == 'https://':
                            
                        self.logger.info("유튭 영상 업로드 : " + res_list['file_path'])

                        self.driver.get(Constant.YOUTUBE_UPLOAD_URL)
                        time.sleep(Constant.USER_WAITING_TIME)

                        # 업로드
                        absolute_video_path = res_list['file_path'] + re.sub('[^0-9a-zA-Zㄱ-힗 ]', '_', res_list['title']) + '.mp4'

                        # 파일 이름이 너무 길면 8.3 이름으로 전달하기
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

                            
                        self.logger.info("유튭 영상 업로드 시작 : " + res_list['file_path'])
                        # 업로드 주소 넣는 곳 찾기
                        while True:
                            try:
                                upload_contents = self.driver.find_element(By.XPATH, Constant.INPUT_FILE_VIDEO)
                                upload_contents.send_keys(absolute_video_path)

                            except:
                                time.sleep(0.05)
                                continue
                            break

                        self.logger.info("업로드할 유튭 영상 경로 전달 완료 : " + res_list['file_path'])

                        #self.logger.debug('Attached video {}'.format(self.video_path))

                        #title_field = self.driver.find_element(By.ID, "select-files-button")
                        time.sleep(Constant.USER_WAITING_TIME*5)


                        # 제목 제한 100글자
                        title = res_list['title']
                        while len(title)>100:
                            title = title[:-1]

                        self.logger.info("유튭 영상 제목 입력 : " + res_list['file_path'])
                        # 제목
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

                        self.logger.info("유튭 영상 제목 입력 완료 : " + title)


                        self.logger.info("유튭 영상 설명 입력 : " + res_list['file_path'])
                        # 디스크립션
                        description_file = open(res_list['file_path'] + re.sub('[^0-9a-zA-Zㄱ-힗 ]', '_', res_list['title']) + '-timeline.txt', 'r', encoding='UTF8')

                        video_description = description_file.read()

                        description_field = self.driver.find_element(By.XPATH, Constant.DESCRIPTION_CONTAINER)
                        description_field.click()
                        time.sleep(Constant.USER_WAITING_TIME)
                        description_field.clear()
                        time.sleep(Constant.USER_WAITING_TIME)
                        pyperclip.copy(video_description)
                        description_field.send_keys(Keys.CONTROL, 'v')
                        self.logger.info("유튭 영상 설명 입력 완료 : " + video_description)


                        # 아동용 아님
                        kids_section = self.driver.find_element(By.XPATH, Constant.NOT_MADE_FOR_KIDS_CONTAINER)
                        kids_section.click()
                        self.logger.info("아동용 아님 : " + res_list['file_path'])


                        # 다음 버튼 연타
                        self.driver.find_element(By.ID, Constant.NEXT_BUTTON).click()
                        self.logger.debug('Clicked {}'.format(Constant.NEXT_BUTTON))

                        self.driver.find_element(By.ID, Constant.NEXT_BUTTON).click()
                        self.logger.debug('Clicked another {}'.format(Constant.NEXT_BUTTON))


                        self.driver.find_element(By.ID, Constant.NEXT_BUTTON).click()
                        self.logger.debug('Clicked another {}'.format(Constant.NEXT_BUTTON))

                        self.logger.info("페이지 넘어옴 : " + res_list['file_path'])

                        time.sleep(Constant.USER_WAITING_TIME)

                        # 일부 공개
                        unlisted_main_button = self.driver.find_element(By.NAME, Constant.UNLISTED_BUTTON)
                        unlisted_main_button.find_element(By.ID, Constant.RADIO_LABEL).click()
                        self.logger.info("일부 공개 : " + res_list['file_path'])


                        self.logger.info("업로드 대기 시작 : " + res_list['file_path'])
                        # 업로드 끝날 때까지 대기                        
                        while True:
                            #in_process = status_container.text.find(Constant.UPLOADED) != -1
                            
                            soup = bs(self.driver.page_source, 'html.parser')
                            status_container = soup.find('span',class_='progress-label style-scope ytcp-video-upload-progress')
                            in_process = status_container.get_text().find(Constant.UPLOADED) != -1
                            if in_process:
                                time.sleep(Constant.USER_WAITING_TIME)
                            else:
                                break
                        self.logger.info("업로드 완료 : " + res_list['file_path'])

                        time.sleep(Constant.USER_WAITING_TIME*3)

                        soup = bs(self.driver.page_source, 'html.parser')
                        video_url_element = soup.find('a',class_='style-scope ytcp-video-info')
                        video_url = video_url_element.get('href')
                        
                        self.logger.info("주소 받기 완료 : " + res_list['file_path'] + '\t' + video_url)

                        done_button = self.driver.find_element(By.ID, Constant.DONE_BUTTON)

                        self.logger.info("완료 버튼 누르기 : " + res_list['file_path'])
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

                        self.logger.info("유튭 영상 업로드 완료 : " + res_list['file_path'])

                        time.sleep(Constant.USER_WAITING_TIME)
                        self.logger.info("유튭 영상 정보 저장 : " + res_list['file_path'] + '\t' + video_url)
                        self.Update_CSV(self.res_lists[idx],video_url)
                        self.logger.info("유튭 영상 정보 저장 완료 : " + res_list['file_path'] + '\t' + video_url)
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
                        self.logger.info("이미 업로드된 유튭 영상 : " + res_list['Youtube_URL'])
                        #self.driver.get(res_list['Youtube_URL'])

                else:
                    self.logger.info("생성되지 않은 유튭 영상 : " + res_list['file_path'])


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
                                self.logger.info("유튭 클립 따기 시작 : 게시글 " + res_list['title'])
                                title_idx =  idx
                            else:
                                self.logger.info("너무 짧아 클립이 안 따지는 영상 : " + res_list['file_path'])
                                title_idx =  -1
                        else:
                            self.logger.info("업로드 되지 않은 유튭 영상 : " + res_list['file_path'])
                            title_idx =  -1
                    else:
                        self.logger.info("생성되지 않은 유튭 영상 : " + res_list['file_path'])
                        title_idx = -1
                else:
                    if title_idx>=0:
                        if self.res_lists[title_idx]['Youtube_URL'] == 'https://':
                            self.logger.info("업로드되지 않은 유튭 영상 : " + res_list['file_path'])
                        else:
                            if res_list['Youtube_URL'] == 'https://':
                                self.logger.info("유튭 클립 생성 : " + res_list['file_path'])
                                if idx == len(self.res_lists)-1: # 마지막 인덱스
                                    # 유튜브 클립 생성
                                    url = self.Make_Clip_and_Get_url(res_list, res_list['Youtube_timeline'], 99999, self.res_lists[title_idx]['Youtube_URL'])
                                else:
                                    # 유튜브 클립 생성
                                    if self.res_lists[idx+1]['Youtube_timeline'] == '0.0': # 마지막 클립
                                        url = self.Make_Clip_and_Get_url(res_list, res_list['Youtube_timeline'], 99999, self.res_lists[title_idx]['Youtube_URL'])
                                    else:
                                        url = self.Make_Clip_and_Get_url(res_list, res_list['Youtube_timeline'], self.res_lists[idx+1]['Youtube_timeline'], self.res_lists[title_idx]['Youtube_URL'])

                                if url is not None:
                                    self.logger.info("유튭 클립 생성 완료 : " + res_list['file_path'])

                                    self.Update_CSV(self.res_lists[idx], url)

                                    self.logger.info("유튭 클립 정보 저장 완료 : " + res_list['file_path'])

                                else:
                                    self.logger.info("유튜브가 아직 준비가 안 됐다 : " + res_list['file_path'])
                                    is_not_ready = True

                            else:
                                self.logger.info("이미 생성된 유튭 클립 : " + res_list['Youtube_URL'])

            if is_not_ready:
                self.logger.info("유튜브 처리가 덜 끝났습니다 : 5초 대기 후 다시 실행합니다.")
                time.sleep(5)

    

    def Make_Clip_and_Get_url(self, res_list, st, et, video_url):

        self.logger.info("유튜브 업로드 대기 확인")
        # 업로드 대기
        while True:
            try:
                self.driver.get(video_url)
                if self.driver.current_url.find(video_url.split('/')[-1])>=0:
                    break
            except:
                time.sleep(5)

        # 클립 버튼이 숨겨져 있을 수도 있어서 메뉴 버튼 먼저 클릭
        while True:
            try:
                dotdotdot = self.driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[2]/div/div/ytd-menu-renderer/yt-button-shape/button/yt-touch-feedback-shape/div/div[2]')
                dotdotdot.click()
            except:
                time.sleep(0.05)
                continue
            break

        # 클립 버튼 찾기
        # 클립 버튼 밖에 있을 때
        clip_button = None
        iter = 0

        while not clip_button:
            yt_buttons = self.driver.find_elements(By.ID,'flexible-item-buttons')
            
            for b in yt_buttons:
                if b.text == '클립':
                    clip_button = b
                    break

            # 유튭 진짜 페이지 복잡하게 만든다 참
            # 밖에서 못 찾아서 클립 버튼 안에 있을 때
            if not clip_button:
                yt_buttons = self.driver.find_elements(By.CLASS_NAME,'style-scope ytd-menu-service-item-renderer')
                for b in yt_buttons:
                    if b.text == '클립':
                        clip_button = b
                        break

            time.sleep(0.05)
            iter = iter +1

            # 5초 동안 해봤는데 안 나오면 다음 기회에!
            # 다음 게시글로 넘어감
            if iter >= 100:
                return None


        clip_button.click()

        # 클립 제목 입력
        Clip_title_box = self.driver.find_element(By.ID,'textarea')

        # 제목 제한 140글자인데.. 왜 59자까지만 받지? 한글을 3바이트로 계산하나?
        title = res_list['title']
        while len(title)>57:
            title = title[:-1]
        pyperclip.copy(title)
        Clip_title_box.send_keys(Keys.CONTROL, 'v')

        # 시작 시간 설정
        # 버튼 찾기
        st_buttons = self.driver.find_elements(By.ID,'start')

        for b in st_buttons:
            if b.tag_name == 'input':
                st_button = b
                break
        
        # 시간 설정
        st_button.click()
        st_button.send_keys(Keys.CONTROL, 'a')
        pyperclip.copy(str(st))
        st_button.send_keys(Keys.CONTROL, 'v')



        # 시작 시간 설정
        # 버튼 찾기
        ed_buttons = self.driver.find_elements(By.ID,'end')

        for b in ed_buttons:
            if b.tag_name == 'input':
                ed_button = b
                break
        
        # 시간 설정
        ed_button.click()
        ed_button.send_keys(Keys.CONTROL, 'a')
        pyperclip.copy(str(et))
        ed_button.send_keys(Keys.CONTROL, 'v')

        # 공유 버튼 누르기
        done_buttons = self.driver.find_elements(By.ID,'share')

        for b in done_buttons:
            if b.text == '클립 공유':
                done_button = b
                break

        done_button.click()


        # 클립 링크 복사
        idx = 0
        while True:
            try:
                links = self.driver.find_elements(By.CLASS_NAME, 'style-scope yt-copy-link-renderer')
                for b in links:
                    if b.text == '복사':
                        link = b
                        break
            
                copy_button = link.find_element(By.ID, 'copy-button')
            except:
                idx = idx + 1
                time.sleep(0.05)
                if idx>200:
                    self.logger.error('타임아웃 에러 : ' + res_list['title'])

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

    #로그 설정
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

    logger.info("시작")

    Clip_file = "Clip_list.csv"

    driver = uc.Chrome()

    UYTV = Upload_YT_Video(Clip_file, logger, driver)

    UYTV.login()
    UYTV.Run()