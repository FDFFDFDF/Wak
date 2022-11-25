#######################################
#### 필수 설치 목록                 ####
#### pip install selenium          ####
#### pip install webdriver-manager ####
#### pip install pyperclip         ####
#### pip install bs4               ####
#### pip install re                ####
#### pip install opencv-python     ####
#######################################

import os

import logging
import traceback
import datetime

import csv
from tkinter import messagebox


#내가 싼 라이브러리
from Twitch_API import Twitch_API
from Read_Clip_list_and_Downloader import Read_Clip_list_and_Downloader
from Naver_Cafe_Clip_Gatherer import Naver_Cafe_Clip_Gatherer
from Make_YT_Video import Make_YT_Video


# 쪼갤 시간 (초) 1일x14
Time_Split_Step_sec = 86400*14

if __name__ == '__main__':   

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
    res_lists=[]

    

    Clip_file = "Clip_list.csv"
    config_file = "config.txt"

    TAPI = Twitch_API(Clip_file, logger)
    RCLD = Read_Clip_list_and_Downloader(Clip_file, logger)
    NCCG = Naver_Cafe_Clip_Gatherer(Clip_file, config_file, logger, Time_Split_Step_sec)
    MYTV = Make_YT_Video(Clip_file, logger)



    try:
        ### 클립 주소 목록 있는지 확인
        TAPI.boo, st = TAPI.check_saved_file()
        NCCG.st = st

        if not TAPI.boo:         

            NCCG.Run()
            logger.info("클립 주소 저장 완료\n 다음 실행 시 왁물원이 아닌 저장된 파일에서 클립을 불러옵니다.")
            TAPI.boo =True

        RCLD.Run(folder_by_streamer=False)
        logger.info("모든 클립 다운로드가 완료되었습니다.")

        logger.info("유튜브 영상 만들기 시작")
        MYTV.Run()
        logger.info("모든 유튜브 영상 만들기 완료")

    except:
        logger.error(traceback.format_exc())

        if not TAPI.boo:     
            csv_error_log = [NCCG.st.strftime("%Y-%m-%d %H:%M:%S")] + ['error']*20

            f_clips = open(Clip_file,'a', encoding='UTF8',newline="")       
            wr = csv.writer(f_clips)
            wr.writerow(csv_error_log)
            f_clips.close()

        if traceback.format_exc().find("Connection to api.twitch.tv timed out")>=0:
            messagebox.showwarning("타임아웃", "트위치 서버가 아파서 클립 정보를 받지 못했습니다.\n 이어서 진행하려면 프로그램을 바로 다시 실행해주세요")

        else:
            messagebox.showerror("치명적인 오류 발생", "알 수 없는 오류가 발생했습니다.\n 마지막으로 생성된 log 파일을 피드백 사이트에 보고해주세요")


        