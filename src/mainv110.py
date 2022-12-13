#######################################
#### 필수 설치 목록                 ####
#### pip install selenium          ####
#### pip install webdriver-manager ####
#### pip install pyperclip         ####
#### pip install bs4               ####
#### pip install re                ####
#### pip install opencv-python     ####
#### pip install undetected-chromedriver
#### pip install pyqt5             ####
#### pip install lxml              ####
#######################################

import os, sys
import platform

import logging
import traceback
import datetime

from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc


import csv
from tkinter import messagebox

from multiprocessing import freeze_support


#내가 싼 라이브러리
from Twitch_API import Twitch_API
from Read_Clip_list_and_Downloader import Read_Clip_list_and_Downloader
from Naver_Cafe_Clip_Gatherer import Naver_Cafe_Clip_Gatherer
from Make_YT_Video import Make_YT_Video
from Upload_YT_Video import Upload_YT_Video

from UI import*


def make_config_file(config_file, boo1, boo2, boo3, opt):
    if opt =='option1': n = 1
    elif opt =='option2': n = 2
    elif opt =='option3': n = 3
    f = open(config_file,'w',encoding='utf-8')
    f.write(str(n)+str(int(boo1))+str(int(boo2))+str(int(boo3)))
    f.close()



# 쪼갤 시간 (초) 1일x14
Time_Split_Step_sec = 86400*14

if __name__ == '__main__':   

    freeze_support()

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

    logger.info(platform.platform())
    logger.info(sys.getwindowsversion().build)
    logger.info(platform.machine())
    logger.info("시작")

    # 윈도우 버전 체크
    if sys.getwindowsversion().build > 20000:
        is_Win11 = True
    else:
        is_Win11 = False

    # 디버그용
    #is_Win11 = True

    ChromeDriverManager().install()
    # 크롬 실행 - 시크릿 모드로, 그냥 모드로 구글 로그인하면 방문 기록 박살남
    options = uc.ChromeOptions()
    options.add_argument('--incognito')
    driver = uc.Chrome(options=options)

    logger.info("크롬 실행 완료")

    Clip_file = "Clip_list.csv"
    #config_file = "config.txt"
    config_file = "wakark.cf"

    TAPI = Twitch_API(Clip_file, logger)
    RCLD = Read_Clip_list_and_Downloader(Clip_file, logger, driver, isWin11 = is_Win11)
    NCCG = Naver_Cafe_Clip_Gatherer(Clip_file, config_file, logger, driver, Time_Split_Step_sec, isWin11 = is_Win11)
    MYTV = Make_YT_Video(Clip_file, logger)
    UYTV = Upload_YT_Video(Clip_file, logger, driver)

    TAPI.boo, st = TAPI.check_saved_file()

    def main_(arg, opt_str):

        try:
            if opt_str == 'option1' or opt_str == 'option2':
                if arg[opt_str]['YTUpload']:
                    UYTV.login()

            ### 클립 주소 목록 있는지 확인
            #TAPI.boo, st = TAPI.check_saved_file()
            NCCG.st = st
            TAPI.st = st

            if not TAPI.boo:         
                logger.info('%d 단계 진행 중' % 1)
                if opt_str == 'option1':
                    NCCG.Run2(arg[opt_str]['addressList'])
                elif opt_str == 'option2':
                    NCCG.Load_from_UI(arg, opt_str)
                    NCCG.Run()
                elif opt_str == 'option3':
                    TAPI.Get_and_Save_Clip_list(False, arg, opt_str)

                logger.info("클립 주소 저장 완료\n 다음 실행 시 왁물원이 아닌 저장된 파일에서 클립을 불러옵니다.")
                
                make_config_file(config_file, arg[opt_str]['YTMake'], arg[opt_str]['YTUpload'], arg[opt_str]['isBrowser'], opt_str)

                TAPI.boo =True


            logger.info('전체 진행도 %3d' % 25)

            if opt_str == 'option1' or opt_str == 'option2':
                folder_by_streamer=False
            else:
                folder_by_streamer=True

            isBrowser = not arg[opt_str]['isBrowser']

            RCLD.Run(folder_by_streamer, isBrowser)

            logger.info("모든 클립 다운로드가 완료되었습니다.")
            logger.info('전체 진행도 %3d' % 50)

            if opt_str == 'option1' or opt_str == 'option2':
                if arg[opt_str]['YTMake']:
                    logger.info("유튜브 영상 만들기 시작")
                    MYTV.Run()
                    logger.info("모든 유튜브 영상 만들기 완료")
                logger.info('전체 진행도 %3d' % 75)

                if arg[opt_str]['YTUpload']:
                    logger.info("유튜브 영상 업로드 시작")
                    UYTV.Run()
                    logger.info("모든 유튜브 영상 업로드 완료")

            logger.info('전체 진행도 %3d' % 100)
            logger.info("크롬 창 종료 중...")
            driver.close()

        except:
            logger.error(traceback.format_exc())

            if not TAPI.boo: 
                if opt_str == 'option1':
                    csv_error_log = [NCCG.Page_Adrees_idx] + ['error']*20

                elif opt_str == 'option2':    
                    if NCCG.st != None:
                        csv_error_log = [NCCG.st.strftime("%Y-%m-%d %H:%M:%S")] + ['error']*20
                    else:
                        st_all_text = arg[opt_str]['startDate']

                        st_date = st_all_text.split('-') # 날짜

                        st_all = datetime.datetime(int(st_date[0]), int(st_date[1]), int(st_date[2]))
                        csv_error_log = [st_all.strftime("%Y-%m-%d %H:%M:%S")] + ['error']*20
                else:
                    csv_error_log = [TAPI.st.strftime("%Y-%m-%d %H:%M:%S")] + ['error']*20

                f_clips = open(Clip_file,'a', encoding='UTF8',newline="")       
                wr = csv.writer(f_clips)
                wr.writerow(csv_error_log)
                f_clips.close()

            if traceback.format_exc().find("Connection to api.twitch.tv timed out")>=0:
                messagebox.showwarning("타임아웃", "트위치 서버가 아파서 클립 정보를 받지 못했습니다.\n 이어서 진행하려면 프로그램을 바로 다시 실행해주세요")

            else:
                messagebox.showerror("치명적인 오류 발생", "알 수 없는 오류가 발생했습니다.\n 마지막으로 생성된 log 파일을 피드백 사이트에 보고해주세요")


    app = QApplication(sys.argv)

    myWindow = WindowClass(logger, main_, TAPI.boo)    
    #myWindow.show()

    app.exec_()