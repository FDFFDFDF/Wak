from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup as bs
import lxml.html

import copy
import pyperclip
import time

import logging
import traceback
import datetime


import csv
import re
import os
from tkinter import messagebox

fonts = ['se-ff-system', 'se-ff-nanumgothic', 'se-ff-nanummyeongjo', 'se-ff-nanumbarungothic', 'se-ff-nanumsquare', 'se-ff-nanummaruburi', 'se-ff-nanumdasisijaghae', 'se-ff-nanumbareunhipi', 'se-ff-nanumuriddalsongeulssi']
sizes = ['11', '13', '15', '16', '19', '24', '28', '30', '34', '38']

class Naver_Cafe_Article_Modifier:

    def __init__(self, Clip_file, logger, driver):
        
        self.Clip_file = Clip_file
        self.logger = logger

        self.time_list =[]

        self.res_lists = []

        self.modi_list = []

        self.driver = driver
        self.AC = ActionChains(driver)


    def get_list(self):

        #print("저장된 클립 주소 파일에서 데이터를 불러옵니다.")
        self.logger.info("저장된 클립 정보 파일에서 데이터를 불러옵니다.")

        # 클립 주소 파일 열기
        f_clips = open(self.Clip_file,'r', encoding='utf-8-sig')

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

    def make_list(self):

        title_dict_idx = -1
        idx = -1

        for res_list in self.res_lists:

            idx = idx +1
            
            if res_list['is_downloaded'] == 'T':

                self.modi_list.append([res_list,[]])

                title_dict_idx = title_dict_idx +1

            else:
                self.modi_list[title_dict_idx][1].append(res_list)

    def Naver_login(self):
    
        #네이버 로그인 주소
        url = 'https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com'


        #네이버 로그인 페이지로 이동
        self.driver.get(url)
        time.sleep(2) #로딩 대기

        '''#아무리 편해도 개인정보 수집인데..
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

    def check_author(self):

        url = 'https://cafe.naver.com/steamindiegame'

        self.driver.get(url)

        # 로딩 대기 루프
        while True:
            try:
                # 나의 활동 클릭
                my_act = self.driver.find_elements(By.CLASS_NAME, 'tit-action')

                if len(my_act)>0:
                    break

            except:
                time.sleep(0.05)
                continue

        my_act[0].click()
        # 로딩 대기 루프
        while True:
            try:
                # 나의 활동 클릭
                prfl_info = self.driver.find_elements(By.CLASS_NAME, 'prfl_info')

                if len(prfl_info)>0:
                    break

            except:
                time.sleep(0.05)
                continue
                

        # 내 닉네임 받기
        My_name = prfl_info[0].text
        self.logger.info("내 닉네임 : "+ My_name)

        # 내가 쓴 게시글인지 확인
        idx = 0
        for i in range(len(self.modi_list)):
            url = self.modi_list[idx][0]['url']
            self.driver.get(url)

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
            self.logger.info("게시글 접속 : "+ url)

            # 로딩 대기 루프
            while True:
                soup = bs(self.driver.page_source, 'html.parser')
                title_html = soup.find_all('h3',class_='title_text')

                if len(title_html)>0:
                    break

                time.sleep(0.05)

            # 내가 쓴 게시물이 아니면 빼기
            if My_name != self.driver.find_element(By.CLASS_NAME, 'nickname').text:
                BaseButtons = self.driver.find_elements(By.CLASS_NAME, 'BaseButton__txt')
                isMine = False
                for b in BaseButtons:
                    if b.text == '수정':
                        isMine = True
                        break

                if not isMine:
                    self.logger.warning("내가 쓴 게시글 아님 : "+ url)
                    self.modi_list.pop(idx)
                    idx = idx - 1
                else:
                    self.logger.info("닉네임은 다르지만 내가 쓴 게시글 : "+ url)
            else:
                self.logger.info("내가 쓴 게시글 : "+ url)

            idx = idx + 1

        self.logger.info("내가 쓴 게시글 선정 완료")



    def Modify(self):

        
        for ml in self.modi_list:
            if len(ml[1])==0:
                self.logger.warning('클립이 없는 게시글 : ', ml[0]['title'])
                continue
            else:
                # 게시글 접속
                url = ml[0]['url']
                url_id = url.split('/')[-1]
                modi_url = 'https://cafe.naver.com/ca-fe/cafes/27842958/articles/' + url_id + '/modify'


                self.logger.info('게시글 접속 : ' + modi_url + '\t' + ml[0]['title'])
                self.driver.get(modi_url)
                try:
                    WebDriverWait(self.driver, 1).until(EC.alert_is_present())
                    alert = self.driver.switch_to.alert

                    alert.accept()
                except:
                    pass

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
                        time.sleep(3)

                    except:
                        time.sleep(0.05)
                        continue
                    break      


                #time.sleep(5)
                self.logger.info('게시글 접속 완료 : ' + modi_url + '\t' + ml[0]['title'])
                messagebox.showinfo("게시글 접속 완료", "현재 주소를 복사하여 다른 크롬창을 열어 붙여넣기해서 백업본을 만들어주세요. 다 되셨으면 확인을 눌러주세요")

                # 다 해체해버리게따
                # 글 수정 중에 애들 성질이 자꾸 바뀜. lmxl로 xpath 기준으로 수정
                self.logger.info('게시글 분석 시작 : ' + modi_url + '\t' + ml[0]['url'] + '\t' + ml[0]['title'])
                tree = lxml.html.fromstring(self.driver.page_source)
                root = tree.getroottree()


                self.logger.info('게시글 분석 시작 : 텍스트')
                # 하이퍼링크 텍스트 먼저 찾기
                contain_clip_texts_lxml = []

                def check_url(contain_link_texts_lxml):
                    for t in contain_link_texts_lxml:
                        if t.attrib['data-href'].find('https://clips.twitch.tv')>=0 or (t.attrib['data-href'].find("https://www.twitch.tv/")>=0 and t.attrib['data-href'][t.attrib['data-href'].find("https://www.twitch.tv/")+22:].find("/clip/")>=0):
                            t_text = t.text
                            if t_text != None:
                                if t_text.find('&ZeroWidthSpace')<0:
                                    contain_clip_texts_lxml.append(t)
                            else:
                                t_mark = t.getchildren()
                                if len(t_mark)>0:
                                    t_mark_text = t_mark[0].text
                                    if t_mark_text != None:
                                        if t_mark_text.find('&ZeroWidthSpace')<0:
                                            contain_clip_texts_lxml.append(t)
                                    else:
                                        t_mark_u = t_mark[0].getchildren()
                                        if len(t_mark_u)>0:
                                            t_mark_u_text = t_mark_u[0].text
                                            if t_mark_u_text != None:
                                                if t_mark_u_text.find('&ZeroWidthSpace')<0:
                                                    contain_clip_texts_lxml.append(t)
                                            else:
                                                t_mark_u_u = t_mark_u[0].getchildren()
                                                if len(t_mark_u_u)>0:
                                                    t_mark_u_u_text = t_mark_u_u[0].text
                                                    if t_mark_u_u_text != None:
                                                        if t_mark_u_u_text.find('&ZeroWidthSpace')<0:
                                                            contain_clip_texts_lxml.append(t)

                    return contain_clip_texts_lxml

                for s in sizes:
                    for f in fonts:
                        contain_link_texts_lxml = tree.xpath("//*[@class='" + f + " se-fs"+s+" se-link __se-node']")

                        contain_link_texts_lxml = check_url(contain_link_texts_lxml)

                        contain_link_texts_lxml = tree.xpath("//*[@class='" + f + " se-fs"+s+" se-highlight se-link __se-node']")

                        contain_link_texts_lxml = check_url(contain_link_texts_lxml)

                        contain_link_url_emoji_lxml = tree.xpath("//*[@class='se-emoji " + f + " se-fs"+s+" se-highlight se-link __se-node']")

                        contain_link_url_emoji_lxml = check_url(contain_link_url_emoji_lxml)

                        contain_link_url_emoji_lxml = tree.xpath("//*[@class='se-emoji " + f + " se-fs"+s+" se-link __se-node']")

                        contain_link_url_emoji_lxml = check_url(contain_link_url_emoji_lxml)


                self.logger.info('게시글 분석 시작 : 섬네일')
                # 섬네일 형식도 찾기
                contain_clip_thumb_lxml = []
                contain_link_thumb_lxml = tree.xpath("//*[@class='se-oglink-url']")

                for t in contain_link_thumb_lxml:
                    if t.text.find('twitch')>=0:
                        contain_clip_thumb_lxml.append(t)

                #    if oglink.get_attribute('alt').find(clip_info['title'][:57])>=0:
                #        contain_clip_thumbs.append(oglink)


                self.logger.info('텍스트 링크 수정 시작')
                # 텍스트 링크 수정
                idx = -1
                for lt in contain_clip_texts_lxml:

                    xpath = root.getpath(lt)

                    t = self.driver.find_element(By.XPATH, xpath)

                    idx = idx + 1
                    link = t.get_attribute('data-href')

                    self.logger.info('텍스트 링크 수정 시작 : ' + link + '\t' + ml[0]['url'] + '\t' + ml[0]['title'])

                    if link.find('https://youtube.com/clip')>=0:
                        self.logger.info('이미 바뀐 텍스트 링크 : ' + link + '\t' + ml[0]['url'] + '\t' + ml[0]['title'])
                        continue                        

                    clip_info = None
                    if link.find('https://clips.twitch.tv')>=0:
                        clip_id = link.split('/')[3]
                    elif link.find("https://www.twitch.tv/")>=0 and link[link.find("https://www.twitch.tv/")+22:].find("/clip/")>=0:
                        clip_id = link.split('/')[5].split('?')[0]
                    else:
                        self.logger.error('존재하지 않는 텍스트 링크 : ' + link + '\t' + ml[0]['url'] + '\t' + ml[0]['title'])
                        continue                    

                    for clip in ml[1]:
                        if clip['id'] == clip_id:
                            clip_info = clip
                            break

                    if not clip_info:
                        self.logger.error('존재하지 않는 텍스트 링크 : ' + link + '\t' + ml[0]['url'] + '\t' + ml[0]['title'])
                        continue

                    # 텍스트 자체가 링크
                    if t.text.find('https://clips.twitch.tv')>=0 or (t.text.find("https://www.twitch.tv/")>=0 and t.text[t.text.find("https://www.twitch.tv/")+22:].find("/clip/")>=0):

                        # 위치 체크
                        str_idx = xpath.find('/section/article/div[')
                        str_idx2 = xpath[str_idx:].find(']') + str_idx
                        order = xpath[str_idx+len('/section/article/div['):str_idx2]

                        # 섬네일과 세트인지 먼저 확인
                        isSet = False
                        isImg = True
                        for thumb in contain_clip_thumb_lxml:
                            xpath_thumb = root.getpath(thumb)
                            thumb_str_idx = xpath_thumb.find('/section/article/div[')
                            thumb_str_idx2 = xpath_thumb[thumb_str_idx:].find(']') + thumb_str_idx
                            thumb_order = xpath_thumb[thumb_str_idx+len('/section/article/div['):thumb_str_idx2]

                            # 연속으로 있으면
                            if int(order)+1==int(thumb_order):
                                # 같은 내용이면
                                thumb_ = self.driver.find_element(By.XPATH, xpath_thumb[:thumb_str_idx2]+']')
                                thumb_title = thumb_.find_element(By.CLASS_NAME, 'se-oglink-title')
                                if thumb_title.text.find(clip_info['title'][:57].replace('\ufeff',''))>=0:

                                    isSet = True
                                    # 섬네일 이미지 있는지 없는지
                                    if len(thumb_.find_elements(By.CLASS_NAME, "se-oglink-thumbnail-resource"))>0:
                                        isImg= True
                                    else:
                                        isImg = False

                                    break

                        self.AC.click(t).perform()
                        self.AC.double_click(t).perform()
                        time.sleep(0.1)
                        
                        # 유튭 클립 있으면
                        if clip_info['Youtube_URL'] != 'https://' or clip_info['is_fixed_for_YT'] != 'X':
                            self.logger.info('텍스트 링크 유튜브로 대체 시작 : ' + link + '\t' + clip_info['Youtube_URL'])
                            pyperclip.copy(clip_info['Youtube_URL'])
                            time.sleep(0.1)
                            self.AC.key_down(Keys.CONTROL)
                            self.AC.send_keys('v')
                            self.AC.key_up(Keys.CONTROL).perform()

                            # 섬네일 나타날 때까지 대기
                            while True:
                                try:                        
                                    # 불여놓은 곳 다음 줄 확인
                                    generated_thumb_ = self.driver.find_element(By.XPATH, xpath[:str_idx+len('/section/article/div[')] + str(int(order)+1) + ']')  
                                    generated_thumb = generated_thumb_.find_element(By.CLASS_NAME, 'se-oglink-thumbnail-resource')
                                    
                                    # 섬네일 소스가 유튜브고, 제목이 맞으면
                                    if generated_thumb.accessible_name.find(clip_info['title'][:57].replace('\ufeff',''))>=0 and generated_thumb.get_attribute('src').find('https://i.ytimg.com')>=0:

                                        if isSet:
                                            # 이미지 없는 섬네일이여야 하면
                                            if not isImg:
                                                self.AC.click(generated_thumb_).perform()
                                                time.sleep(0.1)
                                                img_delete_button = generated_thumb_.find_element(By.CLASS_NAME, "se-oglink-thumbnail-delete")
                                                self.AC.click(img_delete_button).perform()

                                            time.sleep(0.1)

                                            # 세트면 원래 있던 애를 지우기
                                            ori_thumb = self.driver.find_element(By.XPATH, xpath[:str_idx+len('/section/article/div[')] + str(int(order)+2) + ']')  
                                            self.AC.click(ori_thumb).perform()
                                            time.sleep(0.1)     
                                            self.AC.send_keys(Keys.BACKSPACE).perform()
                                            '''
                                            for i in range(len(contain_clip_thumb_lxml)):
                                                if contain_clip_thumb_lxml[i] == thumb:
                                                    contain_clip_thumb_lxml.pop(i)
                                            '''
                                            time.sleep(0.1)                                             

                                        else:
                                            self.AC.click(generated_thumb).perform()
                                            time.sleep(0.1)
                                            self.AC.send_keys(Keys.BACKSPACE).perform()

                                        break

                                    else:
                                        time.sleep(0.05)

                                except:
                                    time.sleep(0.05)
                                    continue
                                #break

                            #self.AC.send_keys(Keys.DELETE).perform()

                        else:
                            # 없으면 네이버 동영상으로 업로드
                            self.logger.info('텍스트 링크 네이버 영상으로 대체 시작 : ' + link + '\t' + clip_info['file_path'])
                            self.AC.send_keys(Keys.BACKSPACE).perform()
                            vid_upload_button = self.driver.find_element(By.CLASS_NAME, 'se-toolbar-item-video')
                            vid_upload_button.click()
                            time.sleep(0.1)
                            vid_upload_url = self.driver.find_element(By.ID, 'nvu_file_input')

                            absolute_video_path = clip_info['file_path']
                        

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

                            #time.sleep(0.5)
                            #vid_upload_url.clear()
                            time.sleep(0.5)
                            vid_upload_url.send_keys(absolute_video_path)

                            # 업로드 완료까지 대기
                            while True:
                                vid_done_button = self.driver.find_elements(By.CLASS_NAME, 'nvu_btn_type2')

                                if len(vid_done_button)>0:
                                    break
                                time.sleep(0.5)

                            # 제목 입력
                            nav_title_field = self.driver.find_element(By.ID, 'nvu_inp_tit')
                            nav_title_field.send_keys(clip_info['title'].replace('\ufeff','')[:40])

                            # 업로드 완료
                            vid_done_button[0].click()

                            if isSet:
                                time.sleep(0.1)
                                # 세트면 원래 있던 애를 지우기
                                ori_thumb = self.driver.find_element(By.XPATH, xpath[:str_idx+len('/section/article/div[')] + str(int(order)+2) + ']')  
                                self.AC.click(ori_thumb).perform()
                                time.sleep(0.1)     
                                self.AC.send_keys(Keys.BACKSPACE).perform()

                            time.sleep(0.1)                        
                    
                    # 텍스트 안에 링크
                    else:
                        self.logger.info('텍스트 안에 링크 유튜브로 대체 시작 : ' + link + '\t' + clip_info['Youtube_URL'] + '\t' + t.text)
                        # 텍스트 클릭
                        self.AC.click(t).perform()
                        time.sleep(0.1)

                        # 하이퍼링크 버튼 누르기
                        link_button = self.driver.find_element(By.CLASS_NAME,'se-toolbar-item-link')
                        self.AC.click(link_button).perform()                        
                        time.sleep(0.1)

                        # 입력하는 곳 찾고 주소 변경
                        input_field = self.driver.find_element(By.CLASS_NAME,'se-custom-layer-link-input')

                        # 이미 되어 있으면 넘어가기
                        if input_field.get_attribute('value') == clip_info['Youtube_URL']:
                            continue

                        self.AC.click(input_field).perform()
                        time.sleep(0.1)

                        self.AC.key_down(Keys.CONTROL)
                        self.AC.send_keys('a')
                        self.AC.key_up(Keys.CONTROL).perform()
                        time.sleep(0.1)
                        self.AC.send_keys(Keys.BACKSPACE).perform()
                        time.sleep(0.1)

                        self.AC.click(input_field).perform() 

                        # 유튭 클립 있으면
                        if clip_info['Youtube_URL'] != 'https://' or clip_info['is_fixed_for_YT'] != 'X':
                            pyperclip.copy(clip_info['Youtube_URL'])
                            time.sleep(0.1)
                            self.AC.key_down(Keys.CONTROL)
                            self.AC.send_keys('v')
                            self.AC.key_up(Keys.CONTROL).perform()
                            time.sleep(0.1)
                        else:
                            self.logger.error('존재하지 않는 유튜브 클립 : ' + link + '\t' + ml[0]['url'] + '\t' + ml[0]['title'] + '\t' + clip_info['Youtube_URL'])
                            continue

                        # 변경 완료 버튼
                        link_done = self.driver.find_element(By.CLASS_NAME,'se-custom-layer-link-apply-button')       
                        self.AC.click(link_done).perform()


                    self.logger.info('텍스트 링크 수정 완료 : ' + link + '\t' + ml[0]['url'] + '\t' + ml[0]['title'])

                # 섬네일식 링크 수정
                self.logger.info('섬네일 수정 시작 : ' + ml[0]['url'] + '\t' + ml[0]['title'])
                idx = -1
                for lt in contain_clip_thumb_lxml:

                    xpath_thumb = root.getpath(lt)
                    thumb_str_idx = xpath_thumb.find('/section/article/div[')
                    thumb_str_idx2 = xpath_thumb[thumb_str_idx:].find(']') + thumb_str_idx
                    thumb_order = xpath_thumb[thumb_str_idx+len('/section/article/div['):thumb_str_idx2]

                    
                    thumb_ = self.driver.find_element(By.XPATH, xpath_thumb[:thumb_str_idx2]+']')
                    # 네이버 동영상으로 이미 바뀌었으면
                    if thumb_.get_attribute('class').find('se-video')>=0:
                        self.logger.info('이미 네이버 영상으로 바뀐 섬네일 ' + xpath_thumb[:thumb_str_idx2]+']'+ ml[0]['url'] + '\t' + ml[0]['title'])
                        continue                             

                    thumb_title = thumb_.find_element(By.CLASS_NAME, 'se-oglink-title')
                    thumb_from = thumb_.find_element(By.CLASS_NAME, 'se-oglink-url')

                    thumb_title_text = thumb_title.text

                    if thumb_from.text.find('youtube.com')>=0:
                        self.logger.info('이미 바뀐 섬네일 링크 : ' + thumb_from.text + '\t' + ml[0]['url'] + '\t' + ml[0]['title'])
                        continue     


                    clip_info = None
                    for clip in ml[1]:
                        if thumb_title_text.find(clip['title'][:57].replace('\ufeff',''))>=0:
                            clip_info = clip
                            break

                    if not clip_info:
                        self.logger.error('존재하지 않는 섬네일 : ' + thumb_title_text + '\t' + ml[0]['url'] + '\t' + ml[0]['title'])
                        continue

                    # 섬네일 이미지 있는지 없는지
                    if thumb_.find_element(By.CLASS_NAME, "se-oglink-thumbnail-resource"):
                        isImg= True
                    else:
                        isImg = False

                    # 지우고 새 섬네일 넣기
                    self.AC.click(thumb_title).perform()
                    time.sleep(0.1)                
                    self.AC.send_keys(Keys.BACKSPACE).perform()
                    time.sleep(0.1)
                    self.AC.send_keys(Keys.ENTER).perform()

                    # 유튭 클립 있으면
                    if clip_info['Youtube_URL'] != 'https://' or clip_info['is_fixed_for_YT'] != 'X':

                        self.logger.info('섬네일 링크 유튜브로 대체 시작 : ' + thumb_title_text + '\t' + clip_info['Youtube_URL'])
                        pyperclip.copy(clip_info['Youtube_URL'])
                        time.sleep(0.1)
                        self.AC.key_down(Keys.CONTROL)
                        self.AC.send_keys('v')
                        self.AC.key_up(Keys.CONTROL).perform()

                        
                        # 섬네일 나타날 때까지 대기
                        while True:
                            try:                        
                                # 불여놓은 곳 확인
                                generated_thumb_ = self.driver.find_element(By.XPATH, xpath[:thumb_str_idx+len('/section/article/div[')] + str(int(thumb_order)) + ']')  
                                generated_thumb = generated_thumb_.find_element(By.CLASS_NAME, 'se-oglink-thumbnail-resource')
                                
                                # 섬네일 소스가 유튜브고, 제목이 맞으면
                                if generated_thumb.accessible_name.find(clip_info['title'][:57].replace('\ufeff',''))>=0 and generated_thumb.get_attribute('src').find('https://i.ytimg.com')>=0:

                                    # 이미지 없는 섬네일이여야 하면
                                    if not isImg:
                                        self.AC.click(generated_thumb_).perform()
                                        time.sleep(0.1)
                                        img_delete_button = generated_thumb_.find_element(By.CLASS_NAME, "se-oglink-thumbnail-delete")
                                        self.AC.click(img_delete_button).perform()

                                    time.sleep(0.1)

                                    # 생긴 링크는 지우기
                                    generated_link_text_ = self.driver.find_element(By.XPATH, xpath[:thumb_str_idx+len('/section/article/div[')] + str(int(thumb_order)-1) + ']')
                                    generated_link_text = generated_link_text_.find_elements(By.CLASS_NAME, "__se-node")[-1]
                                    self.AC.click(generated_link_text).perform()
                                    self.AC.double_click(generated_link_text).perform()
                                    time.sleep(0.1)
                                    self.AC.send_keys(Keys.BACKSPACE).perform()
                                    self.AC.send_keys(Keys.BACKSPACE).perform()


                                    time.sleep(0.1)                                             



                                    break

                                else:
                                    time.sleep(0.05)

                            except:
                                time.sleep(0.05)
                                continue
                    else:
                        # 없으면 네이버 동영상으로 업로드
                        self.logger.info('섬네일 링크 네이버 영상으로 대체 시작 : ' + thumb_title_text + '\t' + clip_info['file_path'])
                        self.AC.send_keys(Keys.BACKSPACE).perform()
                        vid_upload_button = self.driver.find_element(By.CLASS_NAME, 'se-toolbar-item-video')
                        vid_upload_button.click()
                        time.sleep(0.1)
                        vid_upload_url = self.driver.find_element(By.ID, 'nvu_file_input')

                        absolute_video_path = clip_info['file_path']
                    

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

                        #time.sleep(0.5)
                        #vid_upload_url.clear()
                        time.sleep(0.5)
                        vid_upload_url.send_keys(absolute_video_path)

                        # 영상 여러개 올라가는 버그 임시 해결하기
                        while True:
                            vid_list = self.driver.find_elements(By.CLASS_NAME, 'nvu_upload_select')

                            if len(vid_list)>0:
                                break
                            time.sleep(0.5)

                        #vid_items = vid_list[0].find_elements(By.CLASS_NAME, 'nvu_item')
                        vid_delete_buttons = vid_list[0].find_elements(By.CLASS_NAME, 'nvu_btn_delete')
                        
                        d_len = len(vid_delete_buttons)
                        for d in range(d_len - 1):
                            vid_items = vid_list[0].find_elements(By.CLASS_NAME, 'nvu_item')
                            vid_delete_buttons = vid_list[0].find_elements(By.CLASS_NAME, 'nvu_btn_delete')
                            self.AC.click(vid_items[0]).perform()
                            time.sleep(0.1)
                            self.AC.click(vid_delete_buttons[0]).perform()
                            while True:
                                vid_del_conform = self.driver.find_elements(By.CLASS_NAME, 'nvu_area_btn')
                                if len(vid_del_conform)>0:
                                    break
                                time.sleep(0.1)
                            self.AC.click(vid_del_conform[0].find_element(By.CLASS_NAME, 'nvu_btn_type2')).perform()

                            time.sleep(0.1)

                        # 업로드 완료까지 대기
                        while True:
                            vid_done_button = self.driver.find_elements(By.CLASS_NAME, 'nvu_btn_type2')

                            if len(vid_done_button)>0:
                                break
                            time.sleep(0.5)

                        # 제목 입력
                        nav_title_field = self.driver.find_element(By.ID, 'nvu_inp_tit')
                        nav_title_field.send_keys(clip_info['title'].replace('\ufeff','')[:40])

                        # 업로드 완료
                        vid_done_button[0].click()
                        time.sleep(0.1) 

                    self.logger.info('섬네일 링크 수정 완료 : ' + thumb_title_text + '\t' + ml[0]['url'] + '\t' + ml[0]['title'])

            
            messagebox.showinfo("게시글 작성 완료", "수정 글을 백업본과 비교하여 검토해주세요.\n게시글 등록을 원하신다면 등록 버튼을 누른 후, 확인을 눌러주세요.\n등록을 원하시지 않으시면 확인만 눌러주세요.")
            

    def Run(self):

        self.get_list()

        self.make_list()

        self.Naver_login()

        self.check_author()

        #self.Make_New()

        self.Modify()








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

    driver = webdriver.Chrome(ChromeDriverManager().install())

    Clip_file = "Clip_list.csv"


    NCAM = Naver_Cafe_Article_Modifier(Clip_file, logger, driver)

    try:
        NCAM.Run()

        logger.info("완료되었습니다.")

    except:
        logger.error(traceback.format_exc())

        from tkinter import messagebox
        if traceback.format_exc().find("Connection to api.twitch.tv timed out")>=0:
            messagebox.showwarning("타임아웃", "트위치 서버가 아파서 클립 정보를 받지 못했습니다.\n 이어서 진행하려면 프로그램을 바로 다시 실행해주세요")

        else:
            messagebox.showerror("치명적인 오류 발생", "알 수 없는 오류가 발생했습니다.\n 마지막으로 생성된 log 파일을 피드백 사이트에 보고해주세요")