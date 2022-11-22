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
# v0.2.0a 추가
from selenium.webdriver.support.select import Select
# v0.2.0a 추가 end
from bs4 import BeautifulSoup as bs
import pyperclip
import time
import re
from webdriver_manager.chrome import ChromeDriverManager
import os

import logging
import traceback
import datetime

import csv
from datetime import timedelta
from tqdm import tqdm
from tkinter import messagebox


#내가 싼 라이브러리
from Twitch_API import Twitch_API
from Read_Clip_list_and_Downloader import Read_Clip_list_and_Downloader

# 이세돌 엄마 게시판 링크
Mom_board_link = 'https://cafe.naver.com/steamindiegame?iframe_url=/ArticleList.nhn%3Fsearch.clubid=27842958%26search.menuid=350%26search.boardtype=L'
# 이세돌 핫클립 게시판 링크
Hot_board_link = 'https://cafe.naver.com/steamindiegame?iframe_url=/ArticleList.nhn%3Fsearch.clubid=27842958%26search.menuid=331%26search.boardtype=L'


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

    TAPI = Twitch_API(Clip_file, logger)
    RCLD = Read_Clip_list_and_Downloader(Clip_file, logger)

    try:
        ### 클립 주소 목록 있는지 확인
        TAPI.boo, st = TAPI.check_saved_file()

        if not TAPI.boo:         


            ### config 파일 읽기
            f_conf = open('config.txt','r', encoding='UTF8')

            conf = f_conf.read().split('\n')

            #id
            uid = conf[2][5:]
            #pw
            upw = conf[3][5:]

            # 게시판 종류
            Board_type = conf[6]

            # 글 작성자
            Writer_Name = conf[9]

            # 검색 시작 날짜
            try:
                st_all_text = conf[12]

                st_date = st_all_text.split('-') # 날짜

                st_all = datetime.datetime(int(st_date[0]), int(st_date[1]), int(st_date[2]))

            except:
                logger.error(traceback.format_exc())
                logger.error('잘못된 검색 시작 날짜입니다. : ' + st_all_text)

            # 검색 끝 날짜
            try:
                et_all_text = conf[15]

                et_date = et_all_text.split('-') # 날짜

                et_all = datetime.datetime(int(et_date[0]), int(et_date[1]), int(et_date[2]))

            except:
                logger.error(traceback.format_exc())
                logger.error('잘못된 검색 끝 날짜입니다. : ' + et_all_text)



            f_conf.close()


            if st is not None:
                st_all = datetime.datetime.strptime(st, "%Y-%m-%d %H:%M:%S")

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

            
            ## 네이버 카페 게시판 접속 및 게시글 주소 얻기 ##

            if Board_type.find('엄마')>=0:
                # 이세돌 엄마 게시판 링크
                url = Mom_board_link
                logger.info("엄마 게시판 선택")

            elif Board_type.find('핫클립')>=0:
                # 이세돌 핫클립 게시판 링크
                url = Hot_board_link
                logger.info("핫클립 게시판 선택")
            else:
                url = ''
                logger.error("잘못된 게시판 선택 : " + Board_type)
                raise Exception("잘못된 게시판 선택 : " + Board_type)


            ## 시간 쪼개기
            # 네이버 카페 검색 기능 버그 때문
            # 검색 게시글 2000개 넘어가면 결과 중복으로 리턴함
            time_list =[]
            dt = et_all - st_all
            dt = dt.total_seconds()
            idx = 0

            while True:
                dt = dt - Time_Split_Step_sec
                st = st_all + timedelta(seconds=Time_Split_Step_sec)*idx

                if dt>0:                    
                    et = st_all + timedelta(seconds=Time_Split_Step_sec)*(idx+1)

                    time_list.append([st, et])
                else:
                    time_list.append([st, et_all])
                    break

                idx = idx + 1


            
            for args in tqdm(time_list):

                st = args[0]
                et = args[1]
                
                Page_Num_Address_list =[]


                # 사이트 접속
                driver.get(url)
                #time.sleep(2)
                logger.info("게시판 접속")

                # 로딩 대기 루프
                while True:
                    try:
                        #iframe 전환
                        driver.switch_to.frame('cafe_main')
                    except:
                        time.sleep(0.05)
                        continue

                    break
                
                # 글 작성자 검색
                search_by = driver.find_element(By.ID,'divSearchBy')

                search_by.click()
                #time.sleep(1)
                search_by_author = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[7]/form/div[2]/ul/li[3]/a')

                search_by_author.click()
                #time.sleep(1)

                search_box = driver.find_element(By.ID,'query')

                search_box.click()

                pyperclip.copy(Writer_Name)
                search_box.send_keys(Keys.CONTROL, 'v')

                # 값이 반영될 때까지 대기
                while True:
                    if search_box.get_attribute('value') == Writer_Name:
                        break
                    time.sleep(0.05)

                logger.info("글 작성자로 검색 : " + Writer_Name)

                search_button = driver.find_element(By.CLASS_NAME,'btn-search-green')
                search_button.click()

                # HTML에서 searchdate의 value 바꾸기 - 기간 설정
                search_by_date = driver.find_element(By.ID,'searchdate')
                driver.execute_script("arguments[0].setAttribute('value','"+ st.strftime("%Y-%m-%d") + et.strftime("%Y-%m-%d")+"')", search_by_date)

                # 값이 반영될 때까지 대기
                while True:
                    if search_by_date.get_attribute('value') == st.strftime("%Y-%m-%d") + et.strftime("%Y-%m-%d"):
                        break
                    time.sleep(0.05)

                logger.info("기간 검색 : " + st.strftime("%Y-%m-%d") + ' ~ '+ et.strftime("%Y-%m-%d"))

                list_search = driver.find_element(By.CLASS_NAME,'list-search')
                search_button = list_search.find_element(By.CLASS_NAME,'btn-search-green')

                search_button.click()
                #time.sleep(2)

                try:
                    tmp = driver.find_element(By.CLASS_NAME,'nodata')
                    logger.info("게시글 없음 : " + st.strftime("%Y-%m-%d") + ' ~ '+ et.strftime("%Y-%m-%d"))
                    continue
                except:
                    pass

                # 50개씩 검색으로 전환
                soup = bs(driver.page_source, 'html.parser')
                search_list_size = soup.find('div', id='listSizeSelectDiv')
                search_list_size_list = search_list_size.find_all('a')
                for i in search_list_size_list:
                    if i.get_text() == '50개씩':
                        driver.get('https://cafe.naver.com' + i.get('href'))

                
                driver.switch_to.frame('cafe_main')



                # 페이지들 주소 수집
                page_remains = True
                while page_remains:


                    #html 받기
                    soup = bs(driver.page_source, 'html.parser')
                    # 페이지 번호들에 붙은 주소 얻기
                    page_ = soup.find('div',class_='prev-next')


                    total_page_list = page_.find_all('a')

                    next_url = ''
                    page_remains = False

                    for page_element in total_page_list:

                        # 다음 페이지 버튼
                        if page_element.get('class')==['pgR']:
                            next_url = page_element.get('href')
                            page_remains = True

                            # 다음 페이지 이동
                            driver.get('https://cafe.naver.com' + next_url)
                            #time.sleep(2)
                            driver.switch_to.frame('cafe_main')
                            #time.sleep(1)

                        # 이전 페이지 버튼
                        elif page_element.get('class')==['pgL']:
                            pass

                        # 페이지 번호 버튼
                        else:
                            Page_Num_Address_list.append('https://cafe.naver.com' + page_element.get('href'))

                logger.info("게시글 목록 페이지 수집 완료 : " + st.strftime("%Y-%m-%d") + ' ~ '+ et.strftime("%Y-%m-%d"))


                logger.info("게시글 링크 수집 시작")
                Page_Address_list = []
                for Page_Num_Address in Page_Num_Address_list:

                    logger.info("게시글 목록 접속 : " + Page_Num_Address)
                    # 페이지 이동
                    driver.get(Page_Num_Address)
                    driver.switch_to.frame('cafe_main')

                    # 로딩 대기 루프
                    while True:
                        #html 받기
                        soup = bs(driver.page_source, 'html.parser')
                        boards = soup.find_all('div',class_='article-board m-tcol-c')
                        if len(boards)>=2:
                            break
                        time.sleep(0.05)

                    board = boards[1]
                    article_list = board.find_all('a', class_='article')

                    for article in article_list:
                        Page_Address_list.append('https://cafe.naver.com' + article.get('href'))

                    search_date_idx = Page_Num_Address.find("searchdate=")
                    logger.info("게시글 링크 수집 완료 : "
                    + Page_Num_Address[search_date_idx+11:search_date_idx+21] + " ~ "   # 해당 검색 시작 날짜
                    + Page_Num_Address[search_date_idx+21:search_date_idx+31]           # 해당 검색 끝 날짜
                    + " 페이지 : " + Page_Num_Address[-1:])                              # 해당 검색 페이지 번호



                ## 네이버 카페 게시글 접속 및 클립 주소 얻기 ##
                Naver_res_lists = []
                

                for Page_Address in Page_Address_list:

                    #페이지 이동
                    driver.get(Page_Address)

                    #time.sleep(2)

                    # 로딩 대기 루프
                    while True:
                        try:
                            #iframe 전환
                            driver.switch_to.frame('cafe_main')
                        except:
                            time.sleep(0.05)
                            continue

                        break

                    #게시글 제목 얻기
                    #print("게시글 접속 : ", Page_Address)
                    logger.info("게시글 접속 : "+ Page_Address)

                    # 로딩 대기 루프
                    while True:
                        soup = bs(driver.page_source, 'html.parser')
                        title_html = soup.find_all('h3',class_='title_text')

                        if len(title_html)>0:
                            break

                        time.sleep(0.05)


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

                    # 중복 제거
                    Clip_links = list(set(Clip_links))


                    # 게시글 정보 저장
                    f_clips = open(Clip_file,'a', encoding='UTF8', newline="")

                    wr = csv.writer(f_clips)

                    # 결과 폴더
                    res_directory = 'results'
                    # 게시글 제목
                    directory = naver_title.lstrip().rstrip()
                    directory = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', directory)

                    # id	URL	embed_url	broadcaster_id	broadcaster_name	creator_id	creator_name	video_id	game_id	language	title	view_count	created_at	thumbnail_url	duration	vod_offset	is_downloaded	file_path
                    article_log = ['네이버 게시글']*1 + [Page_Address] + ['x','0','x','0'] + [Writer_Name] + ['x','0','x'] + [naver_title.lstrip().rstrip()] + ['0','x','x','0',''] + ['T', os.getcwd() + '\\' + res_directory +'\\'+ directory + '\\']
                    wr.writerow(article_log)                    
                            
                    f_clips.close()


                    # 클립 정보 받기
                    clip_infos = []
                    for clip_link in Clip_links:
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
                        # 결과 폴더
                        res_directory = 'results'

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

                        
                        clip_info['file_path'] = os.getcwd() + '\\' + res_directory +'\\'+ directory + '\\['+vid_time+']'+vid_title+'.mp4'

                        clip_infos.append(clip_info)
                        logger.info("클립 정보 받기 완료 : " + clip_link)

                        
                        # 클립 리스트 저장
                        f_clips = open(Clip_file,'a', encoding='UTF8', newline="")

                        wr = csv.writer(f_clips)
                        wr.writerow(list(clip_info.values()))
                                
                        f_clips.close()

                #print(Clip_links)

            logger.info("클립 주소 수집 완료")



            TAPI.boo = True
            driver.close()

            #print("클립 주소 저장 완료")
            #print("다음 실행 시 왁물원이 아닌 저장된 파일에서 클립을 불러옵니다.")
            logger.info("클립 주소 저장 완료\n 다음 실행 시 왁물원이 아닌 저장된 파일에서 클립을 불러옵니다.")


        ### v0.1.1 추가 ###
        RCLD.Run(folder_by_streamer=False)
        ### v0.1.1 추가 end ###


        logger.info("모든 클립 다운로드가 완료되었습니다.")


        #driver.close()

    except:
        #logger.error(str(Naver_res_lists))
        logger.error(traceback.format_exc())

        if not TAPI.boo:     
            csv_error_log = [st.strftime("%Y-%m-%d %H:%M:%S")] + ['error']*17

            f_clips = open(Clip_file,'a', encoding='UTF8',newline="")       
            wr = csv.writer(f_clips)
            wr.writerow(csv_error_log)
            f_clips.close()

        if traceback.format_exc().find("Connection to api.twitch.tv timed out")>=0:
            messagebox.showwarning("타임아웃", "트위치 서버가 아파서 클립 정보를 받지 못했습니다.\n 이어서 진행하려면 프로그램을 바로 다시 실행해주세요")

        else:
            messagebox.showerror("치명적인 오류 발생", "알 수 없는 오류가 발생했습니다.\n 마지막으로 생성된 log 파일을 피드백 사이트에 보고해주세요")


        