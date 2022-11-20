#######################################
#### 필수 설치 목록                 ####
#### pip install selenium          ####
#### pip install webdriver-manager ####
#### pip install pyperclip         ####
#### pip install bs4               ####
#### pip install re                ####
#######################################



from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import pyperclip
import time
import re
from webdriver_manager.chrome import ChromeDriverManager
#from urllib.request import urlretrieve     v0.1.1 제거됨
import os

import logging
import traceback
import datetime

### v0.1.1 추가 ###
import csv
from datetime import timedelta
from tqdm import tqdm
from tkinter import messagebox


#내가 싼 라이브러리
from Twitch_API import Twitch_API
from Read_Clip_list_and_Downloader import Read_Clip_list_and_Downloader
### v0.1.1 추가 end ###


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

    

    ### v0.1.1 추가 ###
    Clip_file = "Clip_list.csv"
    #Clip_file = "Clip_list.txt"

    TAPI = Twitch_API(Clip_file, logger)
    RCLD = Read_Clip_list_and_Downloader(Clip_file, logger)

    try:
        ### 클립 주소 목록 있는지 확인
        TAPI.boo, st = TAPI.check_saved_file()

        #if not os.path.exists(Clip_file):
        if not TAPI.boo:
            ### v0.1.1 추가 end ###
            
            ### config 파일 읽기
            f_conf = open('config.txt','r', encoding='UTF8')

            conf = f_conf.read().split('\n')

            #id
            uid = conf[2][5:]
            #pw
            upw = conf[3][5:]

            #페이지 주소
            Page_Address_list = conf[5:]

            f_conf.close()


            ### 네이버 카페 접속 ###

            ## 네이버 로그인 ##

            #크롬 브라우저 실행
            driver = webdriver.Chrome(ChromeDriverManager().install())


            #네이버 로그인 주소
            url = 'https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com'


            #네이버 로그인 페이지로 이동
            driver.get(url)
            time.sleep(2) #로딩 대기

            #아이디 입력폼
            tag_id = driver.find_element(By.NAME,'id')
            #패스워드 입력폼
            tag_pw = driver.find_element(By.NAME,'pw')

            # id 입력
            # 입력폼 클릭 -> paperclip에 선언한 uid 내용 복사 -> 붙여넣기
            tag_id.click()
            pyperclip.copy(uid)
            tag_id.send_keys(Keys.CONTROL, 'v')
            time.sleep(1)

            # pw 입력
            # 입력폼 클릭 -> paperclip에 선언한 upw 내용 복사 -> 붙여넣기
            tag_pw.click()
            pyperclip.copy(upw)
            tag_pw.send_keys(Keys.CONTROL, 'v')
            time.sleep(1)

            #로그인 버튼 클릭
            login_btn = driver.find_element(By.ID,'log.login')
            login_btn.click()
            time.sleep(2)

            pyperclip.copy('')

            ## 네이버 카페 접속 및 클립 주소 얻기 ##
            Naver_res_lists = []

            for Page_Address in Page_Address_list:

                #페이지 이동
                driver.get(Page_Address)

                time.sleep(2)

                #iframe 전환
                driver.switch_to.frame('cafe_main')

                #html 받기
                soup = bs(driver.page_source, 'html.parser')

                #게시글 제목 얻기
                #print("게시글 접속 : ", Page_Address)
                logger.info("게시글 접속 : "+ Page_Address)
                naver_title = soup.find('h3',class_='title_text').get_text()
                #print(naver_title)
                logger.info(naver_title)


                Clip_links = []

                #링크 찾기 - 1
                datas = soup.find_all('a',class_='se-link')

                #트위치 클립 링크만 솎아내기
                for data in datas:
                    link = data.get('href')

                    if link.find('https://clips.twitch.tv/')>=0:
                        Clip_links.append(link)
                        #print("클립 주소 추가 : ",link)
                        logger.info("클립 주소 추가 : " + link)

                #링크 찾기 - 2
                datas = soup.find_all('a',class_='se-oglink-info')

                #트위치 클립 링크만 솎아내기
                for data in datas:
                    link = data.get('href')

                    if link.find('https://clips.twitch.tv/')>=0:
                        Clip_links.append(link)
                        #print("클립 주소 추가 : ",link)
                        logger.info("클립 주소 추가 : " + link)



                ### v0.1.1 추가 ###
                # 클립 정보 받기
                clip_infos = []
                for clip_link in tqdm(Clip_links):
                    # 트위치 서버에 리퀘스트
                    logger.info("클립 정보 받기 : " + clip_link)
                    clip_id = re.split('[/&?]',clip_link)[3]
                    clip_info_list = TAPI.clip_search_by_id(clip_id)

                    if len(clip_info_list)>0:
                        clip_info = clip_info_list[0]
                    else:
                        logger.error("클립 정보 에러 : " + clip_link)
                        continue
                    

                    clip_info['is_downloaded'] = 'X'

                    ## 파일 경로 미리 만들기
                    # 게시글 제목
                    directory = naver_title.lstrip().rstrip()
                    directory = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', directory)

                    # 클립 제목
                    vid_title = clip_info['title']
                    vid_title = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_title)


                    # 클립 날짜
                    vid_UTC0 = datetime.datetime.strptime(clip_info['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                    vid_UTC9 = vid_UTC0 + timedelta(hours=9)
                    vid_time = vid_UTC9.strftime("%Y-%m-%dT%H:%M:%SZ")
                    vid_time = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_time).replace('T','_').replace('Z','')

                    
                    clip_info['file_path'] = os.getcwd() +'\\'+ directory + '\\['+vid_time+']'+vid_title+'.mp4'

                    clip_infos.append(clip_info)
                    logger.info("클립 정보 받기 완료 : " + clip_link)

                ### v0.1.1 추가 end ###



                # 결과 배열 생성
                Naver_res_lists.append([naver_title, Clip_links, clip_infos])


                #print(Clip_links)

            logger.info("클립 주소 수집 완료")

            ### v0.1.1 추가 ###
            info_list = []
            for res_list in Naver_res_lists:
                info_list = info_list + res_list[2]

            TAPI.save_clip_info(info_list, already_procd=True)
            TAPI.boo = True
            driver.close()
            ### v0.1.1 추가 end ###

            ''' v0.1.1 제거됨
            # 클립 주소 파일에 저장하기
            f_clips = open(Clip_file,'w', encoding='UTF8')

            for Naver_res in Naver_res_lists:

                # 결과 배열에서 게시글 제목과 링크 주소 얻기

                naver_title = Naver_res[0]  #제목
                Clip_links = Naver_res[1]   #링크

                # 게시글 제목 먼저 저장.
                # tab(\t)은 다음에 불러올 때 사용할 구분자
                #print("게시글 저장 : ", naver_title)
                logger.info("게시글 저장 : " + naver_title)
                f_clips.write(naver_title+'\t\n')

                # 링크들 저장

                for clip in Clip_links:
                    #print("링크 저장 : ", clip)
                    logger.info("게시글 저장 : " + naver_title)
                    f_clips.write(clip+'\n')
                    
            f_clips.write('\n\n\t\n')
            f_clips.close()
            '''
            #print("클립 주소 저장 완료")
            #print("다음 실행 시 왁물원이 아닌 저장된 파일에서 클립을 불러옵니다.")
            logger.info("클립 주소 저장 완료\n 다음 실행 시 왁물원이 아닌 저장된 파일에서 클립을 불러옵니다.")



        """ v0.1.1 제거됨
        ## 클립 주소 파일이 존재할 시 불러오기
        else:
            #print("저장된 클립 주소 파일에서 데이터를 불러옵니다.")
            logger.info("저장된 클립 주소 파일에서 데이터를 불러옵니다.")

            # 클립 주소 파일 열기
            f_clips = open(Clip_file,'r', encoding='UTF8')

            res_text_list = f_clips.read().split("\n")

            Naver_res_lists=[]

            # 제목 먼저 검색
            idx = 0
            for idx in range(0, len(res_text_list)):
                
                # 결과 배열에서 게시글 제목과 링크 주소 얻기
                if res_text_list[idx].find('\t')>=0:
                    #print("게시글 정보 불러오기 : ",res_text_list[idx-1])
                    logger.info("게시글 정보 불러오기 : " + res_text_list[idx-1])
                    #if len(res_text_list[idx-1])>0:
                    Naver_res_lists.append([res_text_list[idx-1],idx-1])  #[게시글 제목, 그 부분의 인덱스]

            # 검색된 제목의 인덱스를 참고해 매치되는 클립 찾기
            idx_prev = Naver_res_lists[0][1]
            for idx in range(1,len(Naver_res_lists)):
                
                Clip_links = []
                for i in range(idx_prev+2, Naver_res_lists[idx][1]):
                    #print("클립 정보 불러오기 : ", res_text_list[i])
                    logger.info("클립 정보 불러오기 : " + res_text_list[i])
                    Clip_links.append(res_text_list[i])
                
                # 맨 마지막 값은 빈 값. 지워주기
                Clip_links.pop(-1)

                idx_prev = Naver_res_lists[idx][1]
                Naver_res_lists[idx-1][1] = Clip_links

            # 맨 마지막 값은 쓰레기 값. 지워주기
            Naver_res_lists.pop(-1)



            #print("클립 주소 불러오기 완료")
            logger.info("클립 주소 불러오기 완료")

            #크롬 실행
            driver = webdriver.Chrome(ChromeDriverManager().install())



        ### 트위치 클립 다운로드 ###
        #print('클립 다운로드를 시작합니다.')
        logger.info('클립 다운로드를 시작합니다.')

        
        for Naver_res_list in Naver_res_lists:


            # 게시글별로 폴더 생성
            naver_title = Naver_res_list[0].lstrip().rstrip()
            directory = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', naver_title)

            # 폴더 존재 여부 확인 후 폴더 생성
            if not os.path.exists(directory):
                os.mkdir(directory)


            for Clip_link in Naver_res_list[1]:

                #print("클립 접속 : ", Clip_link)
                logger.info("클립 접속 : " + Clip_link)

                # 클립 주소가 아닐 시 루프 넘어감
                if Clip_link.find('https://clips.twitch.tv/')<0:
                    #print("!유효한 주소가 아닙니다 : ", Clip_link)
                    logger.warning("!유효한 주소가 아닙니다 : " + Clip_link)
                    continue

                # 주소 이동
                driver.get(Clip_link)

                # 영상 정보 받기
                vid_url = ''
                idx = 0
                while vid_url.find('https://')<0:                               #while문은 로딩이 덜 되을 떄를 대비 10초까지 기다림
                    time.sleep(1)                    
                    idx = idx + 1

                    if driver.current_url.find('clip_missing')>=0:
                        logger.warning("!클립이 지워졌습니다 : " + Clip_link)       # 클립이 지워졌을 경우
                        idx = 10
                        break

                    vid_url_element = driver.find_element(By.TAG_NAME,'video')
                    vid_url = vid_url_element.get_attribute('src')

                    if idx>=10:
                        break

                if idx>=10:
                    logger.warning("영상이 존재하지 않습니다? 왜지? : " + Clip_link)
                    continue


                #html 받기
                soup = bs(driver.page_source, 'html.parser')

                #제목 찾기
                try:
                    vid_title = soup.select_one("title").get_text().replace(" - Twitch","")
                    logger.info("클립 제목 :" + vid_title)
                    
                except:
                    logger.warning("!제목 수집 에러" + naver_title +" "+ Clip_link)
                    vid_title = "Clip_link"
                if not vid_title:
                    logger.warning("!제목 수집 에러" + naver_title +" "+ Clip_link)
                    vid_title = "Clip_link"

                '''
                제대로 작동 안하는 경우가 너무 많아 -관-
                #날짜 찾기
                try:
                    vid_date = soup.select_one('meta[property="og:video:release_date"]')['content']
                    vid_date = vid_date[0:vid_date.find('T')]
                except:
                    logger.warning("!날짜 수집 에러" + naver_title +" "+ vid_title)
                    vid_date = "20xx_XX_xx"
                '''
                vid_date = ''

                #logger.info(vid_date)

                #파일명엔 특수문자가 불가능. 전부 _로 치환
                vid_title = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_title)
                vid_date = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_date)
                logger.info("클립 다운로드 시작 : " + vid_title + '\t' + vid_date)

                #-> from urllib.request import urlretrieve 참조
                #-> 영상을 실제로 다운로드
                #urlretrieve(vid_url, directory+'/['+vid_date+']'+vid_title+'.mp4')
                urlretrieve(vid_url, directory+'/'+vid_title+'.mp4')

                logger.info("클립 다운로드 완료")
        """


        ### v0.1.1 추가 ###
        RCLD.Run(folder_by_streamer=False)
        ### v0.1.1 추가 end ###


        logger.info("모든 클립 다운로드가 완료되었습니다.")


        #driver.close()

    except:
        #logger.error(str(Naver_res_lists))
        logger.error(traceback.format_exc())

        if traceback.format_exc().find("Connection to api.twitch.tv timed out")>=0:
            messagebox.showwarning("타임아웃", "트위치 서버가 아파서 클립 정보를 받지 못했습니다.\n 이어서 진행하려면 프로그램을 바로 다시 실행해주세요")

        else:
            messagebox.showerror("치명적인 오류 발생", "알 수 없는 오류가 발생했습니다.\n 마지막으로 생성된 log 파일을 피드백 사이트에 보고해주세요")

        if not TAPI.boo:     
            csv_error_log = [(st + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")] + ['error']*17

            f_clips = open(Clip_file,'a', encoding='UTF8',newline="")       
            wr = csv.writer(f_clips)
            wr.writerow(csv_error_log)
            f_clips.close()
        