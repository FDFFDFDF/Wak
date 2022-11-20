from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from webdriver_manager.chrome import ChromeDriverManager
from urllib.request import urlretrieve
import os
import csv


import datetime
from datetime import timedelta

from tkinter import messagebox


class Read_Clip_list_and_Downloader():

    def __init__(self, Clip_file, logger):

        self.Clip_file = Clip_file
        self.logger = logger

        self.keys = []
        self.res_lists = []
        self.driver = None

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

    def Download_Clips(self, folder_by_streamer=True):

        for res_list in self.res_lists:

            # 이미 다운로드된 클립은 패스
            if res_list['is_downloaded'] == 'O':
                self.logger.info("이미 다운로드된 클립입니다. : " + res_list['file_path'])
                continue

            if folder_by_streamer:
                # 스트리머 이름으로 폴더 생성
                directory = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', res_list['broadcaster_name'])

                # 폴더 존재 여부 확인 후 폴더 생성
                if not os.path.exists(directory):
                    os.mkdir(directory)

                # 날짜별로 폴더 생성
                vid_UTC0 = datetime.datetime.strptime(res_list['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                vid_UTC9 = vid_UTC0 + timedelta(hours=9)
                vid_time = vid_UTC9.strftime("%Y-%m-%dT%H:%M:%SZ")
                vid_date = vid_time[0:vid_time.find("T")]
                directory_date= re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_date)

                # 폴더 존재 여부 확인 후 폴더 생성
                if not os.path.exists(directory+'/'+ directory_date):
                    os.mkdir(directory+'/'+ directory_date)

            else:
                # 게시글 이름으로 폴더 생성
                dir_text = res_list['file_path'].replace(os.getcwd(),'')
                directory = dir_text.split('\\')[1]

                # 폴더 존재 여부 확인 후 폴더 생성
                if not os.path.exists(directory):
                    os.mkdir(directory)

                # 날짜별로 폴더 생성
                vid_UTC0 = datetime.datetime.strptime(res_list['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                vid_UTC9 = vid_UTC0 + timedelta(hours=9)
                vid_time = vid_UTC9.strftime("%Y-%m-%dT%H:%M:%SZ")
                vid_date = vid_time[0:vid_time.find("T")]
                directory_date= re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_date)


            Clip_link = res_list['url']

            #print("클립 접속 : ", Clip_link)
            self.logger.info("클립 접속 : " + Clip_link)

            # 클립 주소가 아닐 시 루프 넘어감
            if Clip_link.find('https://clips.twitch.tv/')<0:
                #print("!유효한 주소가 아닙니다 : ", Clip_link)
                self.logger.warning("!유효한 주소가 아닙니다 : " + Clip_link)
                continue

            # 주소 이동
            self.driver.get(Clip_link)

            # 영상 정보 받기
            vid_url = ''
            idx = 0
            while vid_url.find('https://')<0:                               #while문은 로딩이 덜 되을 떄를 대비 10초까지 기다림
                time.sleep(0.1)                    
                idx = idx + 1

                if self.driver.current_url.find('clip_missing')>=0:
                    self.logger.error("!클립이 지워졌습니다 : " + Clip_link)       # 클립이 지워졌을 경우
                    idx = 100
                    break

                vid_url_element = self.driver.find_element(By.TAG_NAME,'video')
                vid_url = vid_url_element.get_attribute('src')

                if idx>=100:
                    break

            if idx>=100:
                self.logger.error("영상이 존재하지 않습니다? 왜지? : " + Clip_link)
                continue


            # 제목 가져오기
            vid_title = res_list['title']


            #logger.info(vid_date)

            #파일명엔 특수문자가 불가능. 전부 _로 치환
            vid_title = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_title)
            vid_time = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_time).replace('T','_').replace('Z','')
            self.logger.info("클립 다운로드 시작 : " + vid_title + " " + vid_time)

            #-> from urllib.request import urlretrieve 참조
            #-> 영상을 실제로 다운로드
            if folder_by_streamer:
                urlretrieve(vid_url, directory + '/' + directory_date + '/['+vid_time+']'+vid_title+'.mp4')
            else:
                urlretrieve(vid_url, directory + '/['+vid_time+']'+vid_title+'.mp4')

            self.logger.info("클립 다운로드 완료")

            self.Update_CSV(res_list, directory, directory_date, vid_time, vid_title, folder_by_streamer)

    
    def Update_CSV(self, res_list, directory, directory_date, vid_time, vid_title, folder_by_streamer=True):

        res_list['is_downloaded'] = 'O'
        if folder_by_streamer:
            res_list['file_path'] = os.getcwd() +'\\'+ directory + '\\' + directory_date + '\\['+vid_time+']'+vid_title+'.mp4'
        else:
            pass
        f_clips = open(self.Clip_file,'w', encoding='UTF8', newline="")

        writer = csv.DictWriter(f_clips, fieldnames = self.keys)            
        writer.writeheader()
        writer.writerows(self.res_lists)

        f_clips.close()


        self.logger.info("CSV 업데이트 완료")

        

    def Run(self, folder_by_streamer=True):

        ## 클립 주소 파일이 존재할 시 불러오기
        self.get_list()

        #크롬 실행
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

        ### 트위치 클립 다운로드 ###
        #print('클립 다운로드를 시작합니다.')
        self.logger.info('클립 다운로드를 시작합니다.')

        self.Download_Clips(folder_by_streamer)


        self.logger.info("모든 클립 다운로드가 완료되었습니다.")
        
        self.driver.close()
