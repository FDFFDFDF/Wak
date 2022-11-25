import csv
from tkinter import messagebox
import re
import math

import logging

import cv2
from ffmpeg_accel_concat import*


class Make_YT_Video():

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

    def Make_description(self, timeline_file, video_timeline_info):

        # 유튜브 description 5,000자 제한

        # 개행 기준으로 배열 생성
        list_ = video_timeline_info.split('\n')
        # 최대 글자 가진 라인의 글자 수 확인
        idx = 0
        max_name_idx = 0
        for line in list_:
            #맨 위 3줄은 타임라인 말고 다른 정보
            if idx >= 3:
                # 최대 글자 수 확인
                max_name_idx = max(max_name_idx, len(line))
            
            idx = idx + 1   

        # 글자 수 줄이기 루프
        while len(video_timeline_info) >= 5000:

            # 개행 기준으로 배열 생성
            list_ = video_timeline_info.split('\n')

            video_timeline_info = ''             

            idx = 0
            for line in list_:
                #맨 위 3줄은 타임라인 말고 다른 정보
                if idx >= 3:
                    # 가장 긴 이름의 클립부터 한 글자씩 이름 지우기
                    new_line = line[:max_name_idx] +'\n'                    
                else:
                    new_line = line +'\n'
                
                idx = idx + 1                                

                video_timeline_info = video_timeline_info + new_line
                

            max_name_idx = max_name_idx - 1


            video_timeline_info = video_timeline_info.rstrip()

        timeline_file.write(video_timeline_info)
        timeline_file.close()  


    def Update_CSV(self, res_list, switch='fixed', clip_link = '', timeline = 0.0):

        if switch == 'fixed':
            res_list['is_fixed_for_YT'] = 'O'
        elif switch == 'clip':
            res_list['Youtube_URL'] = clip_link
        elif switch == 'timeline':
            res_list['Youtube_timeline'] = timeline
        else:
            self.logger.warning("CSV 업데이트 에러 : 잘못된 스위치, 아무 것도 하지 않습니다. : " + res_list['title'])
            return

        f_clips = open(self.Clip_file,'w', encoding='UTF8', newline="")

        writer = csv.DictWriter(f_clips, fieldnames = self.keys)            
        writer.writeheader()
        writer.writerows(self.res_lists)

        f_clips.close()


        self.logger.info("CSV 업데이트 완료")



    def Make_Video(self):

        need2video_set = True

        vid_name = ''

        already_procd = False
        title_dict_idx = 0

        idx = -1
        for res_list in self.res_lists:

            idx = idx +1
            
            if res_list['is_downloaded'] == 'T':

                if res_list['is_fixed_for_YT'] == 'O':
                    self.logger.info("이미 처리된 유튭 영상 : " + res_list['file_path'])
                    already_procd = True
                    continue
                else:
                    already_procd = False
                    

                # 이 부분은 첫 루프엔 작동 안 함
                if need2video_set == False:
                    self.logger.info("유튭 영상 만들기 시작 : " + vid_name)
                    self.Make_description(timeline_file, video_timeline_info)
                    vid_concat(clip_list, vid_name)
                    self.Update_CSV(self.res_lists[title_dict_idx])
                    self.logger.info("유튭 영상 만들기 완료 : " + vid_name)
                    #delete_fixed_vid(clip_list)                    



                self.logger.info("게시글 시작 : " + res_list['title'])

                # 게시글 제목으로 영상 제목 설정
                title = res_list['title']
                title_dir = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', title)
                article_url = res_list['url']
                dir_ = res_list['file_path']
                vid_name = dir_ + title_dir +'.mp4'
                vid_name = '\"' + vid_name.replace('\\','/') + '\"'
                timeline_file_dir = dir_ + title_dir +'-timeline.txt'
                timeline_file = open(timeline_file_dir,'w',encoding='UTF-8',newline='')

                title_dict_idx = idx

                need2video_set = True
                continue

            elif res_list['is_downloaded'] == 'X':
                self.logger.error("영상이 다운로드 되지 않았습니다. : " + res_list['file_path'])
                raise

            else:
                if not already_procd:
                    if need2video_set:
                        # 영상 세팅
                        self.logger.info("영상 세팅 시작 : " + title)

                        vid_length = 0.0
                        video_timeline_info = title + ' - 클립 모음\n왁물원 주소 : ' + article_url + '\n\n'
                        clip_list = []
                        need2video_set = False

                        self.logger.info("영상 초기 세팅 완료 : " + title)
                        
                    self.logger.info("타임라인 업데이트 : " + res_list['title'])

                    cap = cv2.VideoCapture(res_list['file_path'])
                    clip_length = cap.get(cv2.CAP_PROP_FRAME_COUNT)/cap.get(cv2.CAP_PROP_FPS)
                    cap.release()
                    
                    s = int(vid_length % 60)
                    m = int((vid_length // 60) % 60)
                    h = int((vid_length // 60) // 60)

                    if h >0:
                        video_timeline = '{0:02d}'.format(h) + ":" + '{0:02d}'.format(m) + ":" + '{0:02d}'.format(math.floor(s))
                    else:
                        video_timeline = '{0:02d}'.format(m) + ":" + '{0:02d}'.format(math.floor(s))

                    video_timeline_info = video_timeline_info + video_timeline + " " + res_list['title'] + '\n'

                    self.Update_CSV(res_list, switch='timeline', timeline = vid_length)

                    vid_length = vid_length + clip_length                    

                    self.logger.info("타임라인 업데이트 완료 : " + res_list['title'])  

                    #clip_list.append(res_list['file_path'].replace('\\','/'))

                    
                    if res_list['is_fixed_for_YT'] == 'X':
                        self.logger.info("영상 속성 변경 : " + res_list['title']) 
                        change_tbn(res_list['file_path'].replace('\\','/'))
                        self.Update_CSV(res_list)
                        self.logger.info("영상 속성 변경 완료 : " + res_list['title'])  

                    #clip_list.append(res_list['file_path'].replace('\\','/').replace('.mp4','_fix.mp4'))                 

                    clip_list.append(res_list['file_path'].replace('\\','/'))

                    self.logger.info("영상 리스트 추가 : " + title +'\t'+ res_list['title']) 
            
            

        self.logger.info("유튭 영상 만들기 시작 : " + vid_name)
        self.Make_description(timeline_file, video_timeline_info)
        vid_concat(clip_list, vid_name)
        self.Update_CSV(self.res_lists[title_dict_idx])
        self.logger.info("유튭 영상 만들기 완료 : " + vid_name)
        #delete_fixed_vid(clip_list)


    def Run(self):

        self.get_list()

        self.Make_Video()


if __name__ == '__main__':

    import datetime
    import os

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

    MYTV = Make_YT_Video(Clip_file, logger)

    MYTV.Run()