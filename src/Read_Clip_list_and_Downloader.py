from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
#from webdriver_manager.chrome import ChromeDriverManager
from urllib.request import urlretrieve
import os
import csv

from bs4 import BeautifulSoup as bs
import json

import datetime
from datetime import timedelta

from tkinter import messagebox


class Read_Clip_list_and_Downloader():

    def __init__(self, Clip_file, logger, driver, isWin11=False):

        self.Clip_file = Clip_file
        self.logger = logger

        self.keys = []
        self.res_lists = []
        self.driver = driver

        self.est_DT = []

        self.isWin11 = isWin11


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

        i = -1
        total = len(self.res_lists)
        for res_list in self.res_lists:

            i = i + 1
            # 이미 다운로드된 클립은 패스
            if res_list['is_downloaded'] == 'O':
                self.logger.info("이미 다운로드된 클립입니다. : " + res_list['file_path'])
                self.logger.info('클립 다운로드 완료 %3d' % (100*(i+1)/total))
                self.logger.info('전체 진행도 %3d' % (25 + 25*(i+1)/total))
                continue
            elif res_list['is_downloaded'] == 'T':
                self.logger.info("게시글 시작 : " + res_list['title'] + ' 진행 중')
                continue

            if folder_by_streamer:
                # 스트리머 이름으로 폴더 생성
                directory = re.sub('[^0-9a-zA-Zㄱ-힗 ]', '_', res_list['broadcaster_name'])

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
                # 결과 폴더 생성
                res_directory = 'results'
                # 폴더 존재 여부 확인 후 폴더 생성
                if not os.path.exists(res_directory):
                    os.mkdir(res_directory)

                # 게시글 이름으로 폴더 생성
                dir_text = res_list['file_path'].replace(os.getcwd(),'')
                directory = dir_text.split('\\')[2]

                directory = res_directory + '/' + directory

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
            vid_title = re.sub('[^0-9a-zA-Zㄱ-힗 ]', '_', vid_title)
            vid_time = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_time).replace('T','_').replace('Z','')
            self.logger.info("클립 다운로드 시작 : " + vid_title + " " + vid_time)

            #-> from urllib.request import urlretrieve 참조
            #-> 영상을 실제로 다운로드
            if folder_by_streamer:
                tmp = urlretrieve(vid_url, directory + '/' + directory_date + '/['+vid_time+']'+vid_title+'.mp4')
                del tmp
            else:
                # win 11은 경로 길이가 250자 넘어가면 안됨. 제목을 줄인다.
                vid_dir = os.getcwd() + directory + '/['+vid_time+']'+vid_title+'.mp4'
                while self.isWin11 and len(vid_dir)>=250:
                    vid_title = vid_title[:-1]
                    vid_dir = os.getcwd() + directory + '/['+vid_time+']'+vid_title+'.mp4'
                    if len(vid_title)==0:
                        self.logger.error("너무 긴 게시글 제목과 클립 제목 : " + os.getcwd() + directory + '/['+vid_time+']'+res_list['title']+'.mp4')
                        break
                    
                tmp = urlretrieve(vid_url, directory + '/['+vid_time+']'+vid_title+'.mp4')
                del tmp

            self.logger.info('클립 다운로드 완료 %3d' % (100*(i+1)/total))
            self.logger.info('전체 진행도 %3d' % (25 + 25*(i+1)/total))

            self.Update_CSV(res_list, directory, directory_date, vid_time, vid_title, folder_by_streamer)

    def Download_Clips_No_Browser(self, folder_by_streamer=True):

        i = -1
        total = len(self.res_lists)
        for res_list in self.res_lists:

            i = i + 1
            # 이미 다운로드된 클립은 패스
            if res_list['is_downloaded'] == 'O':
                self.logger.info("이미 다운로드된 클립입니다. : " + res_list['file_path'])
                self.logger.info('클립 다운로드 완료 %3d' % (100*(i+1)/total))
                self.logger.info('전체 진행도 %3d' % (25 + 25*(i+1)/total))
                continue
            elif res_list['is_downloaded'] == 'T':
                self.logger.info("게시글 시작 : " + res_list['title'] + ' 진행 중')
                continue

            if folder_by_streamer:
                # 스트리머 이름으로 폴더 생성
                directory = re.sub('[^0-9a-zA-Zㄱ-힗 ]', '_', res_list['broadcaster_name'])

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
                # 결과 폴더 생성
                res_directory = 'results'
                # 폴더 존재 여부 확인 후 폴더 생성
                if not os.path.exists(res_directory):
                    os.mkdir(res_directory)

                # 게시글 이름으로 폴더 생성
                dir_text = res_list['file_path'].replace(os.getcwd(),'')
                directory = dir_text.split('\\')[2]

                directory = res_directory + '/' + directory

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

            thumb_url = res_list['thumbnail_url']

            jpg_txt_idx = thumb_url.find('-preview-')

            if not jpg_txt_idx >= 0:
                jpg_txt_idx = thumb_url.find('-social-preview.jpg')

            vid_url = thumb_url[:jpg_txt_idx] + '.mp4'
            


            # 제목 가져오기
            vid_title = res_list['title']


            #logger.info(vid_date)

            #파일명엔 특수문자가 불가능. 전부 _로 치환
            vid_title = re.sub('[^0-9a-zA-Zㄱ-힗 ]', '_', vid_title)
            vid_time = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_time).replace('T','_').replace('Z','')
            self.logger.info("클립 다운로드 시작 : " + vid_title + " " + vid_time)

            #-> from urllib.request import urlretrieve 참조
            #-> 영상을 실제로 다운로드
            if folder_by_streamer:
                tmp = urlretrieve(vid_url, directory + '/' + directory_date + '/['+vid_time+']'+vid_title+'.mp4')
                del tmp
            else:
                # win 11은 경로 길이가 250자 넘어가면 안됨. 제목을 줄인다.
                vid_dir = os.getcwd() + '/' + directory + '/['+vid_time+']'+vid_title+'.mp4'
                while self.isWin11 and len(vid_dir)>=250:
                    vid_title = vid_title[:-1]
                    vid_dir = os.getcwd() + '/' +  directory + '/['+vid_time+']'+vid_title+'.mp4'
                    if len(vid_title)==0:
                        self.logger.error("너무 긴 게시글 제목과 클립 제목 : " + os.getcwd()  + '/' +  directory + '/['+vid_time+']'+res_list['title']+'.mp4')
                        break
                    
                tmp = urlretrieve(vid_url, directory + '/['+vid_time+']'+vid_title+'.mp4')
                del tmp

            self.logger.info('클립 다운로드 완료 %3d' % (100*(i+1)/total))
            self.logger.info('전체 진행도 %3d' % (25 + 25*(i+1)/total))

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


    def Est_Download_time(self, isBrowser = True):

        clip_count = 0
        clip_length = 0
        clip_length_for_save = 0
        title_dict_idx = 0
        idx = -1

        need2video_set =False

        for res_list in self.res_lists:

            idx = idx +1
            
            if res_list['is_downloaded'] == 'T':

                if need2video_set == False:
                    self.est_DT.append(0)
                    clip_length = 0
                    clip_length_for_save = 0
                    need2video_set = True
                    continue

                self.est_DT[title_dict_idx] = clip_length                


                # CSV 업데이트
                self.res_lists[title_dict_idx]['duration'] = clip_length_for_save
                f_clips = open(self.Clip_file,'w', encoding='UTF8', newline="")

                writer = csv.DictWriter(f_clips, fieldnames = self.keys)            
                writer.writeheader()
                writer.writerows(self.res_lists)

                f_clips.close()

                #self.logger.info("CSV 업데이트 완료")

                title_dict_idx = idx

                clip_length = 0
                clip_length_for_save = 0

                self.est_DT.append(0)
                need2video_set = True

            else:
                if res_list['is_downloaded'] == 'X':                    
                    clip_length = clip_length + float(self.res_lists[idx]['duration'])
                    clip_count = clip_count + 1

                clip_length_for_save = clip_length_for_save + float(self.res_lists[idx]['duration'])
                self.est_DT.append(0)

        self.est_DT[title_dict_idx] = clip_length

        # CSV 업데이트
        self.res_lists[title_dict_idx]['duration'] = clip_length_for_save
        f_clips = open(self.Clip_file,'w', encoding='UTF8', newline="")

        writer = csv.DictWriter(f_clips, fieldnames = self.keys)            
        writer.writeheader()
        writer.writerows(self.res_lists)

        f_clips.close()

        self.logger.info("CSV 업데이트 완료")


        # 계수는 그냥 경험적으로 구했음
        self.logger.info('예상 다운로드 용량 : 약 ' + str(round(sum(self.est_DT)*0.73/1024,2)) + 'GB')

        if sum(self.est_DT)>0:
            self.Speed_test(clip_count, sum(self.est_DT), isBrowser)

        # 남은 용량이 다운 받을 용량보다 적으면 경고
        import shutil
        total, used, free = shutil.disk_usage(os.getcwd().split('\\')[0] + '\\')

        if sum(self.est_DT)*0.73*1024*1024 > free:
            messagebox.showwarning("용량 경고", "예상되는 다운로드 용량이 디스크의 남은 용량보다 큽니다.\n디스크 용량을 확보하고 다시 실행해주세요.")

    

    def Speed_test(self, count, l, isBrowser = True):
        from Twitch_API import Twitch_API        

        TAPI = Twitch_API('', None)

        url = 'https://clips.twitch.tv/RealPlayfulMarrowCoolCat-eyq7-nreFFYGNX1g'
        id = 'RealPlayfulMarrowCoolCat-eyq7-nreFFYGNX1g'

        # 실행 시간 측정 - 개당
        st = time.time()

        res = TAPI.clip_search_by_id('RealPlayfulMarrowCoolCat-eyq7-nreFFYGNX1g')

        dt1 = time.time() - st
        
        st = time.time()

        # 실행 시간 측정 - 영상 길이 초당
        if isBrowser:
            
            # 주소 이동
            self.driver.get(url)

            # 영상 정보 받기
            vid_url = ''
            idx = 0

            while vid_url.find('https://')<0:                               #while문은 로딩이 덜 되을 떄를 대비 10초까지 기다림
                time.sleep(0.1)                    
                idx = idx + 1

                
                vid_url_element = self.driver.find_element(By.TAG_NAME,'video')
                vid_url = vid_url_element.get_attribute('src')

        else:

            thumb_url = res[0]['thumbnail_url']

            jpg_txt_idx = thumb_url.find('-preview-')

            vid_url = thumb_url[:jpg_txt_idx] + '.mp4'


        urlretrieve(vid_url, 'test.mp4')

        dt2 = time.time() - st
        
        os.remove((os.getcwd() + '\\test.mp4').replace('\\','/'))

        self.driver.get('about:blank')

        # 예상 시간 계산
        est_time = dt1 * count + (dt2/60) * l

        s = int(est_time % 60)
        m = int((est_time // 60) % 60)
        h = int((est_time // 60) // 60)

        self.logger.info('예상 다운로드 시간 : 약 ' + str(h) + ' 시간 ' + str(m) + ' 분 ' + str(s) + ' 초')



    def Run(self, folder_by_streamer=True, isBrowser = True):

        ## 클립 주소 파일이 존재할 시 불러오기
        self.get_list()

        self.Est_Download_time(isBrowser)

        #크롬 실행
        #self.driver = webdriver.Chrome(ChromeDriverManager().install())

        ### 트위치 클립 다운로드 ###
        #print('클립 다운로드를 시작합니다.')
        self.logger.info('클립 다운로드를 시작합니다.')

        if isBrowser:
            self.Download_Clips(folder_by_streamer)
        else:
            self.Download_Clips_No_Browser(folder_by_streamer)


        self.logger.info("모든 클립 다운로드가 완료되었습니다.")
        #self.logger.info("클립 다운로드용 크롬창 종료 중...")
        
        self.driver.get('about:blank')



#내가 싼 라이브러리
from Read_Clip_list_and_Downloader import Read_Clip_list_and_Downloader

# 쪼갤 시간 (초) 1일x14
Time_Split_Step_sec = 86400*14

if __name__ == '__main__':   

    import logging
    import undetected_chromedriver as uc
    import traceback

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


    # 크롬 실행
    driver = uc.Chrome()

    

    Clip_file = "Clip_list.csv"
    config_file = "config.txt"

    RCLD = Read_Clip_list_and_Downloader(Clip_file, logger, driver, isWin11=True)



    try:

        #RCLD.Run(folder_by_streamer=False)
        RCLD.Run(False, False)
        logger.info("모든 클립 다운로드가 완료되었습니다.")

        logger.info("크롬 창 종료 중...")
        driver.close()

    except:
        logger.error(traceback.format_exc())

        if traceback.format_exc().find("Connection to api.twitch.tv timed out")>=0:
            messagebox.showwarning("타임아웃", "트위치 서버가 아파서 클립 정보를 받지 못했습니다.\n 이어서 진행하려면 프로그램을 바로 다시 실행해주세요")

        else:
            messagebox.showerror("치명적인 오류 발생", "알 수 없는 오류가 발생했습니다.\n 마지막으로 생성된 log 파일을 피드백 사이트에 보고해주세요")

