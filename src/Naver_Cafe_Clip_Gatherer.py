from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains


from bs4 import BeautifulSoup as bs
import pyperclip
import time
from datetime import timedelta

import logging
import traceback
import datetime

from tqdm import tqdm

import csv
import re
import os

#내가 싼 라이브러리
from Twitch_API import Twitch_API



keys = ['id', 'url', 'embed_url', 'broadcaster_id', 'broadcaster_name', 
        'creator_id', 'creator_name', 'video_id', 'game_id', 'language', 
        'title', 'view_count', 'created_at', 'thumbnail_url', 'duration', 'vod_offset', 
        'is_downloaded', 'file_path', 'is_fixed_for_YT','Youtube_URL','Youtube_timeline']

empty_dict ={}

for k in keys:
    if k in ['broadcaster_id', 'creator_id', 'video_id', 'game_id', 'view_count', 'duration']:
        empty_dict[k] = 0
    else:
        empty_dict[k] = 'x'

empty_dict['created_at'] = '1900-01-01T00:00:00Z'


# 이세돌 엄마 게시판 링크
Mom_board_link = 'https://cafe.naver.com/steamindiegame?iframe_url=/ArticleList.nhn%3Fsearch.clubid=27842958%26search.menuid=350%26search.boardtype=L'
# 이세돌 핫클립 게시판 링크
Hot_board_link = 'https://cafe.naver.com/steamindiegame?iframe_url=/ArticleList.nhn%3Fsearch.clubid=27842958%26search.menuid=331%26search.boardtype=L'
# 이세돌 자유 게시판 링크
Free_board_link = 'https://cafe.naver.com/steamindiegame?iframe_url=/ArticleList.nhn%3Fsearch.clubid=27842958%26search.menuid=327%26search.boardtype=L'
# 이세돌 NEWS 게시판 링크
News_board_link = 'https://cafe.naver.com/steamindiegame?iframe_url=/ArticleList.nhn%3Fsearch.clubid=27842958%26search.menuid=347%26search.boardtype=L'
# 이세돌 팬영상 게시판 링크
Vid_board_link = 'https://cafe.naver.com/steamindiegame?iframe_url=/ArticleList.nhn%3Fsearch.clubid=27842958%26search.menuid=361%26search.boardtype=L'
# 이세돌 유튭각 게시판 링크
YouG_board_link = 'https://cafe.naver.com/steamindiegame?iframe_url=/ArticleList.nhn%3Fsearch.clubid=27842958%26search.menuid=349%26search.boardtype=L'
# 이세돌 컨텐츠 게시판 링크
Cont_board_link = 'https://cafe.naver.com/steamindiegame?iframe_url=/ArticleList.nhn%3Fsearch.clubid=27842958%26search.menuid=404%26search.boardtype=L'


# 고멤 핫클립 게시판 링크
GHot_board_link = 'https://cafe.naver.com/steamindiegame?iframe_url=/ArticleList.nhn%3Fsearch.clubid=27842958%26search.menuid=489%26search.boardtype=L'

# 우왁굳 핫클립 게시판 링크
WHot_board_link = 'https://cafe.naver.com/steamindiegame?iframe_url=/ArticleList.nhn%3Fsearch.clubid=27842958%26search.menuid=66%26search.boardtype=L'
# 왁스비 게시판 링크
WXB_board_link = 'https://cafe.naver.com/steamindiegame?iframe_url=/ArticleList.nhn%3Fsearch.clubid=27842958%26search.menuid=428%26search.boardtype=L'


class Naver_Cafe_Clip_Gatherer():

    def __init__(self, Clip_file, config_file, logger, driver, dt=86400*14, st=None, isWin11=False):
        
        self.Clip_file = Clip_file
        self.config_file = config_file
        self.logger = logger

        self.uid = ''
        self.upw = ''
        self.Board_type = ''
        self.Writer_Name = ''
        self.st_all = datetime.datetime.now()
        self.et_all = datetime.datetime.now()

        self.st = st
        self.Page_Adrees_idx = 0

        self.url = ''

        self.isWin11 = isWin11

        # 쪼갤 시간 (초)
        self.Time_Split_Step_sec = dt

        self.time_list =[]

        self.driver = driver
        self.AC = ActionChains(driver)

        self.TAPI = Twitch_API('', None)



    def Read_config_file(self):
    
        ### config 파일 읽기
        f_conf = open('config.txt','r', encoding='UTF8')

        conf = f_conf.read().split('\n')

        #id
        self.uid = conf[2][5:]
        #pw
        self.upw = conf[3][5:]

        # 게시판 종류
        self.Board_type = conf[6]

        # 글 작성자
        self.Writer_Name = conf[9]

        # 검색 시작 날짜
        try:
            st_all_text = conf[12]

            st_date = st_all_text.split('-') # 날짜

            self.st_all = datetime.datetime(int(st_date[0]), int(st_date[1]), int(st_date[2]))

        except:
            self.logger.error(traceback.format_exc())
            self.logger.error('잘못된 검색 시작 날짜입니다. : ' + st_all_text)

        # 검색 끝 날짜
        try:
            et_all_text = conf[15]

            et_date = et_all_text.split('-') # 날짜

            self.et_all = datetime.datetime(int(et_date[0]), int(et_date[1]), int(et_date[2]))

        except:
            self.logger.error(traceback.format_exc())
            self.logger.error('잘못된 검색 끝 날짜입니다. : ' + et_all_text)



        f_conf.close()

        if self.st is not None:
            self.st_all = datetime.datetime.strptime(self.st, "%Y-%m-%d %H:%M:%S")

    def Load_from_UI(self, argument, option):

        ### config 파일 읽기
        #f_conf = open('config.txt','r', encoding='UTF8')

        #conf = f_conf.read().split('\n')

        #id
        #self.uid = conf[2][5:]
        #pw
        #self.upw = conf[3][5:]

        # 게시판 종류
        self.Board_type = argument[option]['board']

        # 글 작성자
        self.Writer_Name = argument[option]['user']

        # 검색 시작 날짜
        try:
            st_all_text = argument[option]['startDate']

            st_date = st_all_text.split('-') # 날짜

            self.st_all = datetime.datetime(int(st_date[0]), int(st_date[1]), int(st_date[2]))

        except:
            self.logger.error(traceback.format_exc())
            self.logger.error('잘못된 검색 시작 날짜입니다. : ' + st_all_text)

        # 검색 끝 날짜
        try:
            et_all_text = argument[option]['endDate']

            et_date = et_all_text.split('-') # 날짜

            self.et_all = datetime.datetime(int(et_date[0]), int(et_date[1]), int(et_date[2]))

        except:
            self.logger.error(traceback.format_exc())
            self.logger.error('잘못된 검색 끝 날짜입니다. : ' + et_all_text)



        #f_conf.close()

        if self.st is not None:
            self.st_all = datetime.datetime.strptime(self.st, "%Y-%m-%d %H:%M:%S")

    def Naver_login(self):
    
        #네이버 로그인 주소
        url = 'https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com'


        #네이버 로그인 페이지로 이동
        self.driver.get(url)
        time.sleep(2) #로딩 대기

        '''#아무리 편해도 개인정보 수집인데.. 다음 버전부턴 삭제
        #아이디 입력폼
        tag_id = self.driver.find_element(By.NAME,'id')
        #패스워드 입력폼
        tag_pw = self.driver.find_element(By.NAME,'pw')

        # id 입력
        # 입력폼 클릭 -> paperclip에 선언한 uid 내용 복사 -> 붙여넣기
        tag_id.click()
        pyperclip.copy(self.uid)
        tag_id.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)

        # pw 입력
        # 입력폼 클릭 -> paperclip에 선언한 upw 내용 복사 -> 붙여넣기
        tag_pw.click()
        pyperclip.copy(self.upw)
        tag_pw.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)

        #로그인 버튼 클릭
        login_btn = self.driver.find_element(By.ID,'log.login')
        login_btn.click()
        time.sleep(2)

        pyperclip.copy('')
        '''
        
        self.logger.info("네이버 로그인 대기 중...")
        #while문은 로그인 완료까지 기다림
        while self.driver.current_url.find('https://nid.naver.com/login/ext/deviceConfirm')<0 and self.driver.current_url.find('https://www.naver.com/')<0:
            #self.logger.info("네이버 로그인 대기 중...")
            time.sleep(1)
        self.logger.info("네이버 로그인 완료")


    def Choose_Board(self):

        if self.Board_type.find('엄마')>=0:
            # 이세돌 엄마 게시판 링크
            self.url = Mom_board_link
            self.logger.info("엄마 게시판 선택")

        elif self.Board_type.find('이세돌 | 핫클립')>=0:
            # 이세돌 핫클립 게시판 링크
            self.url = Hot_board_link
            self.logger.info("이세돌 핫클립 게시판 선택")

        elif self.Board_type.find('고멤 | 핫클립')>=0:
            # 고멤 핫클립 게시판 링크
            self.url = GHot_board_link
            self.logger.info("고멤 핫클립 게시판 선택")

        elif self.Board_type.find('우왁굳 | 핫클립')>=0:
            # 우왁굳 핫클립 게시판 링크
            self.url = WHot_board_link
            self.logger.info("우왁굳 핫클립 게시판 선택")

        elif self.Board_type.find('이세돌 | 자유게시판')>=0:
            # 이세돌 자유 게시판 링크
            self.url = Free_board_link
            self.logger.info("이세돌 자유 게시판 선택")

        elif self.Board_type.find('이세돌 | 팬영상')>=0:
            # 이세돌 팬영상 게시판 링크
            self.url = Vid_board_link
            self.logger.info("이세돌 팬영상 게시판 선택")

        elif self.Board_type.find('이세돌 | NEWS')>=0:
            # 이세돌 뉴스 게시판 링크
            self.url = News_board_link
            self.logger.info("이세돌 NEWS 게시판 선택")

        elif self.Board_type.find('아 오늘 방송 못봤는데')>=0:
            # 왁스비 게시판 링크
            self.url = WXB_board_link
            self.logger.info("아 오늘 방송 못봤는데 게시판 선택")

        elif self.Board_type.find('이세돌 오늘의 유튭각')>=0:
            # 이세돌 유튭각 게시판 링크
            self.url = YouG_board_link
            self.logger.info("이세돌 유튭각 게시판 선택")         

        elif self.Board_type.find('이세돌 컨텐츠용 게시판')>=0:
            # 이세돌 컨텐츠 게시판 링크
            self.url = Cont_board_link
            self.logger.info("이세돌 컨텐츠용 게시판")   

        else:
            self.url = ''
            self.logger.error("잘못된 게시판 선택 : " + self.Board_type)
            raise Exception("잘못된 게시판 선택 : " + self.Board_type)


    def Schedule_time_list(self):

        ## 시간 쪼개기
        # 네이버 카페 검색 기능 버그 때문
        # 검색 게시글 2000개 넘어가면 결과 중복으로 리턴함        
        dt = self.et_all - self.st_all
        dt = dt.total_seconds()
        idx = 0

        while True:
            dt = dt - self.Time_Split_Step_sec
            st = self.st_all + timedelta(seconds=self.Time_Split_Step_sec)*idx

            if dt>0:                    
                et = self.st_all + timedelta(seconds=self.Time_Split_Step_sec)*(idx+1)

                self.time_list.append([st, et])
            else:
                self.time_list.append([st, self.et_all])
                break

            idx = idx + 1

    def Get_Board_Page_Num(self, st, et):
        
        Page_Num_Address_list =[]


        # 사이트 접속
        self.driver.get(self.url)
        #time.sleep(2)
        self.logger.info("게시판 접속")

        # 로딩 대기 루프
        while True:
            try:
                #iframe 전환
                self.driver.switch_to.frame('cafe_main')
            except:
                time.sleep(0.05)
                continue

            break
        
        # 로딩 대기
        while True:
            try:
                # 글 작성자 검색
                search_by = self.driver.find_element(By.ID,'divSearchBy')

                search_by.click()
                #time.sleep(0.25)
                search_by_author = self.driver.find_element(By.XPATH,'/html/body/div[1]/div/div[7]/form/div[2]/ul/li[3]/a')

                search_by_author.click()
                #time.sleep(0.25)

                search_box = self.driver.find_element(By.ID,'query')

                search_box.click()

                pyperclip.copy(self.Writer_Name)
                search_box.send_keys(Keys.CONTROL, 'v')

            except:
                time.sleep(0.05)

            break

        # 값이 반영될 때까지 대기
        while True:
            if search_box.get_attribute('value') == self.Writer_Name:
                break
            time.sleep(0.05)

        self.logger.info("글 작성자로 검색 : " + self.Writer_Name)

        search_button = self.driver.find_element(By.CLASS_NAME,'btn-search-green')
        search_button.click()

        # HTML에서 searchdate의 value 바꾸기 - 기간 설정
        search_by_date = self.driver.find_element(By.ID,'searchdate')
        self.driver.execute_script("arguments[0].setAttribute('value','"+ st.strftime("%Y-%m-%d") + et.strftime("%Y-%m-%d")+"')", search_by_date)

        # 값이 반영될 때까지 대기
        while True:
            if search_by_date.get_attribute('value') == st.strftime("%Y-%m-%d") + et.strftime("%Y-%m-%d"):
                break
            time.sleep(0.05)

        self.logger.info("기간 검색 : " + st.strftime("%Y-%m-%d") + ' ~ '+ et.strftime("%Y-%m-%d"))

        list_search = self.driver.find_element(By.CLASS_NAME,'list-search')
        search_button = list_search.find_element(By.CLASS_NAME,'btn-search-green')

        search_button.click()
        #time.sleep(2)

        try:
            tmp = self.driver.find_element(By.CLASS_NAME,'nodata')
            self.logger.info("게시글 없음 : " + st.strftime("%Y-%m-%d") + ' ~ '+ et.strftime("%Y-%m-%d"))
            return []
        except:
            pass

        # 50개씩 검색으로 전환
        soup = bs(self.driver.page_source, 'html.parser')
        search_list_size = soup.find('div', id='listSizeSelectDiv')
        search_list_size_list = search_list_size.find_all('a')
        for i in search_list_size_list:
            if i.get_text() == '50개씩':
                self.driver.get('https://cafe.naver.com' + i.get('href'))

        self.driver.switch_to.frame('cafe_main')


        # 페이지들 주소 수집
        page_remains = True
        while page_remains:


            #html 받기
            soup = bs(self.driver.page_source, 'html.parser')
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
                    self.driver.get('https://cafe.naver.com' + next_url)
                    #time.sleep(2)
                    self.driver.switch_to.frame('cafe_main')
                    #time.sleep(1)

                # 이전 페이지 버튼
                elif page_element.get('class')==['pgL']:
                    pass

                # 페이지 번호 버튼
                else:
                    Page_Num_Address_list.append('https://cafe.naver.com' + page_element.get('href'))

        self.logger.info("게시글 목록 페이지 수집 완료 : " + st.strftime("%Y-%m-%d") + ' ~ '+ et.strftime("%Y-%m-%d"))

        return Page_Num_Address_list


    def Get_Article_URL(self, Page_Num_Address_list):


        self.logger.info("게시글 링크 수집 시작")
        Page_Address_list = []
        for Page_Num_Address in Page_Num_Address_list:

            self.logger.info("게시글 목록 접속 : " + Page_Num_Address)
            # 페이지 이동
            self.driver.get(Page_Num_Address)
            self.driver.switch_to.frame('cafe_main')

            # 로딩 대기 루프
            while True:
                #html 받기
                soup = bs(self.driver.page_source, 'html.parser')
                boards = soup.find_all('div',class_='article-board m-tcol-c')
                if len(boards)>=2:
                    break
                time.sleep(0.05)

            board = boards[1]
            article_list = board.find_all('a', class_='article')

            for article in article_list:
                Page_Address_list.append('https://cafe.naver.com' + article.get('href'))

            search_date_idx = Page_Num_Address.find("searchdate=")
            self.logger.info("게시글 링크 수집 완료 : "
            + Page_Num_Address[search_date_idx+11:search_date_idx+21] + " ~ "   # 해당 검색 시작 날짜
            + Page_Num_Address[search_date_idx+21:search_date_idx+31]           # 해당 검색 끝 날짜
            + " 페이지 : " + Page_Num_Address[-1:])                              # 해당 검색 페이지 번호

        return Page_Address_list


    def Get_Clip_URL(self, Page_Address_list):        

        ## 네이버 카페 게시글 접속 및 클립 주소 얻기 ##         
        for PA_idx in range(self.Page_Adrees_idx, len(Page_Address_list)):
            
            Page_Address = Page_Address_list[PA_idx]

            #페이지 이동
            self.driver.get(Page_Address)

            #time.sleep(2)

            # 로딩 대기 루프
            while True:
                try:
                    #iframe 전환
                    self.driver.switch_to.frame('cafe_main')
                except:
                    time.sleep(0.05)
                    continue

                break

            #게시글 제목 얻기
            #print("게시글 접속 : ", Page_Address)
            self.logger.info("게시글 접속 : "+ Page_Address)

            # 로딩 대기 루프
            while True:
                soup = bs(self.driver.page_source, 'html.parser')
                title_html = soup.find_all('h3',class_='title_text')

                if len(title_html)>0:
                    break

                time.sleep(0.05)


            naver_title = soup.find('h3',class_='title_text').get_text()
            #print(naver_title)
            self.logger.info(naver_title + ' 진행 중')


            Clip_links = []

            # 링크 찾기
            # se-link : 링크만, se-oglink-info : 섬네일 같이 있는 링크
            datas = soup.find_all('a',class_=['se-link', 'se-oglink-info'])

            #트위치 클립 링크만 솎아내기
            for data in datas:
                link = data.get('href')

                if link.find('https://clips.twitch.tv/')>=0:
                    Clip_links.append(link)
                    #print("클립 주소 추가 : ",link)
                    self.logger.info("클립 주소 추가 : " + link)

                # v0.4.0a 추가
                else:
                    # https://www.twitch.tv/{스트리머}/clip/{ID} 방식 주소 대응
                    link_split = link.split('/')
                    if link_split[2] == 'www.twitch.tv' and link_split[-2] == 'clip':
                        
                        link = 'https://clips.twitch.tv/' + link_split[-1]

                        Clip_links.append(link)
                        #print("클립 주소 추가 : ",link)
                        self.logger.info("클립 주소 추가 : " + link)

            # v0.4.0a 추가
            # 네이버 동영상 몇개 있는지 찾기
            naver_vids = soup.find_all('div',class_='se-component se-video se-l-default')

            nvid_count = 0

            for i in naver_vids:
                nvid_count =  nvid_count +1


            # 중복 제거
            res = []
            for i in Clip_links:
                if i not in res:
                    res.append(i)
            Clip_links = res


            # 게시글 링크 다시 받기
            Copy_url_button = self.driver.find_element(By.CLASS_NAME,'button_url')
            Copy_url_button.click()
            time.sleep(0.05)
            new_page_Address = pyperclip.paste()


            # 게시글 정보 저장
            f_clips = open(self.Clip_file,'a', encoding='UTF8', newline="")

            wr = csv.writer(f_clips)

            # 결과 폴더
            res_directory = 'results'
            # 게시글 제목
            directory = naver_title.lstrip().rstrip()
            directory = re.sub('[^0-9a-zA-Zㄱ-힗 ]', '_', directory)



            # id	URL	embed_url	broadcaster_id	broadcaster_name	creator_id	creator_name	video_id	game_id	language	title	view_count	created_at	thumbnail_url	duration	vod_offset	is_downloaded	file_path
            article_log = ['네이버 게시글']*1 + [new_page_Address] + ['x','0','x','0'] + [self.Writer_Name] + ['x',str(nvid_count),'x'] + [naver_title.lstrip().rstrip()] + ['0','x','x','0',''] + ['T', os.getcwd() + '\\' + res_directory +'\\'+ directory + '\\'] + ['T', 'https://', 0.0]
            wr.writerow(article_log)                    
                    
            f_clips.close()


            
            ''' 12월 14일 사망
            # v1.1.0 추가 글쓰기 페이지로 이동
            self.logger.info('게시글 작성 접속 : ' + new_page_Address + '\t' + naver_title.lstrip().rstrip())
            self.driver.get('https://cafe.naver.com/ca-fe/cafes/27842958/articles/write?boardType=L')


            # 게시글 나타날 때까지 대기
            article_len = 0
            while True:
                try:                        
                    soup = bs(self.driver.page_source, 'html.parser')
                    container = soup.find('article', class_='se-components-wrap')
                    lines = container.find_all('div', class_='se-component')

                    if len(lines) > article_len:
                        article_len = len(lines)
                    else:
                        break
                    time.sleep(1)

                except:
                    time.sleep(0.05)
                    continue
                break      
            # v1.1.0 추가 글쓰기 페이지로 이동 끝
            '''
            # 클립 정보 받기
            clip_infos = []
            for clip_link in Clip_links:


                #12월 13일 오전 9시 사망
                byebyeTwitch = False

                # 트위치 서버에 리퀘스트
                self.logger.info("클립 정보 받기 : " + clip_link)
                clip_id = re.split('[/&?]',clip_link)[3]
                clip_info_list = self.TAPI.clip_search_by_id(clip_id)

                if len(clip_info_list)>0:
                    clip_info = clip_info_list[0]
                else:
                    #self.logger.info("트위치 서버 접속 불가 : " + clip_link + "\t 네이버에서 클립 정보를 가져옵니다.")
                    #byebyeTwitch = True
                    self.logger.error("클립이 삭제되었습니다. : " + clip_link + '\t' + new_page_Address)
                    continue
                

                #12월 14일 사망
                if byebyeTwitch:

                    # 딕셔너리 설정
                    clip_info = empty_dict

                    clip_info['id'] = clip_id
                    clip_info['url'] = clip_link
                    clip_info['embed_url'] = '네이버에서 가져온 클립 정보'
                    clip_info['language'] = 'ko'

                    # 게시글 작성란에 클립 넣기
                    t = self.driver.find_element(By.CLASS_NAME, 'se-component-content')  

                    self.AC.click(t).perform()
                    time.sleep(0.1)

                    pyperclip.copy(clip_link)
                    time.sleep(0.1)
                    self.AC.key_down(Keys.CONTROL)
                    self.AC.send_keys('v')
                    self.AC.key_up(Keys.CONTROL).perform()

                    # 섬네일 나타날 때까지 대기
                    isdeleted = False
                    while True:
                        try:
                            # 섬네일 정보 찾기
                            generated_thumb_info = self.driver.find_elements(By.CLASS_NAME, 'se-oglink-info-container')

                            if len(generated_thumb_info)>0:

                                # 클립 삭제 여부 확인
                                thumb_summary = generated_thumb_info[0].find_elements(By.CLASS_NAME, 'se-oglink-summary')

                                if len(thumb_summary)>0:
                                    if thumb_summary[0].text == 'Twitch는 세계 최고의 동영상 플랫폼이자 게이머를 위한 커뮤니티입니다.':
                                        isdeleted = True

                                    break

                        except:
                            time.sleep(0.05)
                            continue

                    if isdeleted:
                        self.logger.error("클립이 삭제되었습니다. : " + clip_link)
                        continue

                    
                    while True:
                        try:                   
                            # 섬네일 이미지 찾기
                            generated_thumb = self.driver.find_elements(By.CLASS_NAME, 'se-oglink-thumbnail-resource')                        

                            if len(generated_thumb)>0:
                                generated_thumb = generated_thumb[0]
                                break
                        except:
                            time.sleep(0.05)
                            continue                        
                    
                    alt = generated_thumb.get_attribute('alt')

                    clip_info['broadcaster_name'] = alt[:alt.find(' - ')]
                    clip_info['title'] = alt[alt.find(' - ') + 3:]

                    thumb_src = generated_thumb.get_attribute('src')

                    thumb_url = thumb_src[thumb_src.find('https://clips-media-assets2.twitch.tv'):]


                    clip_info['thumbnail_url'] = thumb_url.replace('%257','%7')

                    self.AC.click(generated_thumb).perform()
                    self.AC.key_down(Keys.CONTROL)
                    self.AC.send_keys('a')
                    self.AC.key_up(Keys.CONTROL).perform()
                    self.AC.send_keys(Keys.DELETE).perform()



                clip_info['is_downloaded'] = 'X'

                ## 파일 경로 미리 만들기
                # 결과 폴더
                res_directory = 'results'

                # 게시글 제목
                directory = naver_title.lstrip().rstrip()
                directory = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', directory)

                # 클립 제목
                vid_title = clip_info['title']
                vid_title = re.sub('[^0-9a-zA-Zㄱ-힗 ]', '_', vid_title)


                # 클립 날짜
                vid_UTC0 = datetime.datetime.strptime(clip_info['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                vid_UTC9 = vid_UTC0 + timedelta(hours=9)
                vid_time = vid_UTC9.strftime("%Y-%m-%dT%H:%M:%SZ")
                vid_time = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_time).replace('T','_').replace('Z','')

                
                clip_info['file_path'] = os.getcwd() + '\\' + res_directory +'\\'+ directory + '\\['+vid_time+']'+vid_title+'.mp4'

                # win 11은 경로 길이가 250자 넘어가면 안됨. 제목을 줄인다.
                idx = -1
                while self.isWin11 and len(clip_info['file_path'])>=250:
                    clip_info['file_path'] = os.getcwd() + '\\' + res_directory +'\\'+ directory + '\\['+vid_time+']' + vid_title[:idx]+'.mp4'
                    if len(vid_title[:idx])==0:
                        self.logger.error("너무 긴 게시글 제목과 클립 제목 : " + os.getcwd() + '\\' + res_directory +'\\'+ directory + '\\['+vid_time+']'+vid_title+'.mp4')
                        break
                    idx = idx - 1
                    

                clip_info['is_fixed_for_YT'] = 'X'

                clip_info['Youtube_URL'] = 'https://'

                clip_info['Youtube_timeline'] = 0.0

                clip_infos.append(clip_info)
                self.logger.info("클립 정보 받기 완료 : " + clip_link)

                
                # 클립 리스트 저장
                f_clips = open(self.Clip_file,'a', encoding='UTF8', newline="")

                wr = csv.writer(f_clips)
                wr.writerow(list(clip_info.values()))
                        
                f_clips.close()

                self.Page_Adrees_idx = self.Page_Adrees_idx + 1


            self.driver.get('about:blank')
            try:
                WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert

                alert.accept()
            except:
                pass


        #print(Clip_links)
    
    def Check_Duplication(self):

        f_clips = open(self.Clip_file,'r', encoding='UTF8', newline="")

        rdr = csv.reader(f_clips)

        read_csv = list(rdr)

        f_clips.close()

        title_idx_list = []

        idx = -1

        # 맨 윗줄은 이름
        read_csv.pop(0)

        for res_list in read_csv:

            idx = idx +1
            
            # is_downloaded 변수
            if res_list[16] == 'T':
                title_idx_list.append(idx)

        article_list = []
        for i in range(len(title_idx_list)-1):
            article_list.append(read_csv[title_idx_list[i]:title_idx_list[i+1]])
        article_list.append(read_csv[title_idx_list[-1]:])

        idx_1 = -1
        for i in article_list:
            idx_1 = idx_1 + 1
            idx_2 = -1
            for j in article_list:
                idx_2 = idx_2 + 1                
                if not idx_1 == idx_2:
                    # URL 변수
                    if i[0][1]==j[0][1]:
                        self.logger.info("게시글 중복 감지 : " + i[0][10])
                        more_clip = max(len(i),len(j))
                        if more_clip == len(i):
                            article_list.pop(idx_2)
                            idx_2 = idx_2 - 1
                        elif more_clip == len(j):
                            article_list.pop(idx_1)
                            idx_1 = idx_1 - 1
                        else:
                            self.logger.error("뭐여 이 부분은 어케 옴")
                        self.logger.info("게시글 중복 제거 완료")

        csv_list =[]
        for i in article_list:
            csv_list = csv_list + i

        f_clips = open(self.Clip_file,'w', encoding='UTF8', newline="")       
        wr = csv.writer(f_clips)
        #keys = ['id', 'url', 'embed_url', 'broadcaster_id', 'broadcaster_name', 'creator_id', 'creator_name', 'video_id', 'game_id', 'language', 'title', 'view_count', 'created_at', 'thumbnail_url', 'duration', 'vod_offset', 'is_downloaded', 'file_path']
        keys = ['id', 'url', 'embed_url', 'broadcaster_id', 'broadcaster_name', 
        'creator_id', 'creator_name', 'video_id', 'game_id', 'language', 
        'title', 'view_count', 'created_at', 'thumbnail_url', 'duration', 'vod_offset', 
        'is_downloaded', 'file_path', 'is_fixed_for_YT','Youtube_URL','Youtube_timeline']

        wr.writerow(keys)
        wr.writerows(csv_list)
       
                
        f_clips.close()


    def Run(self):
    
        # 설정 파일 읽기
        #self.Read_config_file()

        ### 네이버 카페 접속 ###

        #크롬 브라우저 실행
        #self.driver = webdriver.Chrome(ChromeDriverManager().install())

        ## 네이버 로그인 ##
        self.Naver_login()

        ## 게시판 선택 ##
        self.Choose_Board()
        
        ## 검색 기간에 따라 스케쥴링
        self.Schedule_time_list()

        ## 네이버 카페 게시판 접속 및 게시글 주소 얻기 ##      
        for args in tqdm(self.time_list):
            
            st = args[0]
            et = args[1]    
            self.st = st                    
        
            # 검색 페이지 주소
            Page_Num_Address_list = self.Get_Board_Page_Num(st, et)
            
            if len(Page_Num_Address_list) == 0:
                continue

            # 게시글 주소
            Page_Address_list = self.Get_Article_URL(Page_Num_Address_list)

            if len(Page_Address_list) == 0:
                continue            
            
            # 게시글의 클립 주소 수집 및 저장
            self.Get_Clip_URL(Page_Address_list)


        self.logger.info("클립 주소 수집 완료")
        #self.logger.info("왁물원용 크롬창 종료 중...")

        self.logger.info("클립 주소 중복 정리 시작")
        self.Check_Duplication()
        self.logger.info("클립 주소 중복 정리 완료")

        #self.driver.close()

        #self.TAPI.boo = True
        return True

    def Run2(self, page_list):
        
        # 설정 파일 읽기
        #self.Read_config_file()

        ### 네이버 카페 접속 ###

        #크롬 브라우저 실행
        #self.driver = webdriver.Chrome(ChromeDriverManager().install())

        ## 네이버 로그인 ##
        self.Naver_login()

        Page_Address_list = page_list

        # 게시글의 클립 주소 수집 및 저장
        self.Get_Clip_URL(Page_Address_list)


        self.logger.info("클립 주소 수집 완료")
        #self.logger.info("왁물원용 크롬창 종료 중...")

        self.logger.info("클립 주소 중복 정리 시작")
        self.Check_Duplication()
        self.logger.info("클립 주소 중복 정리 완료")

        #self.driver.close()

        #self.TAPI.boo = True
        return True


if __name__ == '__main__':   

    # 쪼갤 시간 (초) 1일x14
    Time_Split_Step_sec = 86400*14

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

    driver = webdriver.Chrome(ChromeDriverManager().install())

    Clip_file = "Clip_list.csv"
    config_file = "config.txt"

    TAPI = Twitch_API(Clip_file, logger)
    NCCG = Naver_Cafe_Clip_Gatherer(Clip_file, config_file, logger, driver, Time_Split_Step_sec)

    try:
        ### 클립 주소 목록 있는지 확인
        TAPI.boo, st = TAPI.check_saved_file()
        NCCG.st = st

        if not TAPI.boo:         

            NCCG.Run()
            logger.info("클립 주소 저장 완료\n 다음 실행 시 왁물원이 아닌 저장된 파일에서 클립을 불러옵니다.")

        logger.info("완료되었습니다.")

    except:
        logger.error(traceback.format_exc())

        if not TAPI.boo:     
            csv_error_log = [NCCG.st.strftime("%Y-%m-%d %H:%M:%S")] + ['error']*20

            f_clips = open(Clip_file,'a', encoding='UTF8',newline="")       
            wr = csv.writer(f_clips)
            wr.writerow(csv_error_log)
            f_clips.close()

        from tkinter import messagebox
        if traceback.format_exc().find("Connection to api.twitch.tv timed out")>=0:
            messagebox.showwarning("타임아웃", "트위치 서버가 아파서 클립 정보를 받지 못했습니다.\n 이어서 진행하려면 프로그램을 바로 다시 실행해주세요")

        else:
            messagebox.showerror("치명적인 오류 발생", "알 수 없는 오류가 발생했습니다.\n 마지막으로 생성된 log 파일을 피드백 사이트에 보고해주세요")

