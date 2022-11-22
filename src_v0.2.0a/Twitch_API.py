import csv
import logging
import traceback
import datetime, time
import os
from datetime import timedelta
import requests

from multiprocessing import  cpu_count, Pool, freeze_support
from tqdm import tqdm
import random






class Twitch_API():

    def __init__(self, Clip_file , logger):    
        # 이 부분은 일부러 비웠습니다.
        # 아래 두 주소 참고해서 본인만의 키를 발급 받아 사용하세요 킹아!
        # https://dev.twitch.tv/docs/api/get-started
        # https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#oauth-client-credentials-flow
        self.headers={'Authorization': '', 'client-id': ''}


        # 스트리머별 ID
        self.wak_id = '49045679'
        self.ine_id = '702754423'
        self.jing_id = '237570548'
        self.lilpa_id = '169700336'
        self.jururu_id = '203667951'
        self.segu_id = '707328484'
        self.vii_id = '195641865'


        # 쪼갤 시간 (초) 1일x28
        self.Time_Split_Step_sec = 86400*28 #7200


        self.Clip_file = Clip_file
        self.logger = logger


        self.st_all = datetime.datetime.now()
        self.et_all = datetime.datetime.now()
        self.streamer_id = ''
        self.user_name = ''



        self.boo = False

    def clip_search_by_id(self, id, next_page=''):

        response = requests.get("https://api.twitch.tv/helix/clips?id="+id+'&first=100'+next_page, headers=self.headers)

        res = response.json()
        clips = res['data']
        page = res["pagination"]


        # 이 부분은 id 검색에선 의미는 없을 듯
        if len(page)>0:
            rdn = random.randrange(1,100)
            time.sleep(0.01*rdn)    # Too many request 방지
            res1 = self.clip_search_by_id(id, '&after=' + page['cursor'] )
            clips = clips + res1
        
        return clips


    def clip_search_by_date(self, now, dt, next_page=''):

        now_1 =  now + timedelta(seconds=dt)

        now_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        now_1_str = now_1.strftime("%Y-%m-%dT%H:%M:%SZ")

        response = requests.get("https://api.twitch.tv/helix/clips?broadcaster_id="+self.streamer_id+"&started_at="+now_str+"&ended_at="+now_1_str+'&first=100'+next_page, headers=self.headers)

        res = response.json()
        clips = res['data']
        page = res["pagination"]


        if len(page)>0:
            rdn = random.randrange(1,100)
            time.sleep(0.01*rdn)    # Too many request 방지
            res1 = self.clip_search_by_date(now, dt, '&after=' + page['cursor'] )
            clips = clips + res1
        
        return clips

    def get_clip_info_from_twitch(self, args):

        st, et = args

        now = st
        remained_time = et - now
        remained_time = remained_time.total_seconds()

        dt = remained_time

        res_lists = []
        while remained_time>0:

            clips = self.clip_search_by_date(now, dt)

            for clip in clips:
                if clip['creator_name'] == self.user_name:
                    # 결과 배열 생성
                    res_lists.append(clip)


            now = now + timedelta(seconds=dt)

            remained_time = et - now
            remained_time = remained_time.total_seconds()

            #print(remained_time)
        #print(st,et)
        return res_lists


    def check_saved_file(self):

        if not os.path.exists(self.Clip_file):
            
            f_clips = open(self.Clip_file,'a', encoding='UTF8', newline="")       
            wr = csv.writer(f_clips)
            keys = ['id', 'url', 'embed_url', 'broadcaster_id', 'broadcaster_name', 'creator_id', 'creator_name', 'video_id', 'game_id', 'language', 'title', 'view_count', 'created_at', 'thumbnail_url', 'duration', 'vod_offset', 'is_downloaded', 'file_path']
            wr.writerow(keys)
            f_clips.close()

            return False, None

        else:
            f_clips = open(self.Clip_file,'r', encoding='UTF8')
            rdr = csv.reader(f_clips)

            read_csv = list(rdr)
            n = len(read_csv)

            #라인 개수
            if n >1:
                if read_csv[-1][-1] == 'error':
                    st_all = read_csv[-1][0]
                    f_clips.close()


                    f_clips = open(self.Clip_file,'w', encoding='UTF8', newline="")
                    wr = csv.writer(f_clips)
                    wr.writerows(read_csv[0:-1])
                    f_clips.close()

                    return False, st_all

                else:
                    return True, None


            elif n == 1:
                f_clips.close()
                return False, None

            else:
                f_clips.close()
                f_clips = open(self.Clip_file,'w', encoding='UTF8', newline="")
                wr = csv.writer(f_clips)
                keys = ['id', 'url', 'embed_url', 'broadcaster_id', 'broadcaster_name', 'creator_id', 'creator_name', 'video_id', 'game_id', 'language', 'title', 'view_count', 'created_at', 'thumbnail_url', 'duration', 'vod_offset', 'is_downloaded', 'file_path']
                wr.writerow(keys)
                f_clips.close()

                return False, None


    def read_config_file_streamer(self):

        ### config 파일 읽기

        f_conf = open('config.txt','r', encoding='UTF8')

        conf = f_conf.read().split('\n')

        # 스트리머
        streamer_name = conf[1]

        if streamer_name == '우왁굳':
            self.streamer_id = self.wak_id
        elif streamer_name == '아이네':
            self.streamer_id = self.ine_id
        elif streamer_name == '징버거':
            self.streamer_id = self.jing_id
        elif streamer_name == '릴파':
            self.streamer_id = self.lilpa_id
        elif streamer_name == '주르르':
            self.streamer_id = self.jururu_id
        elif streamer_name == '고세구':
            self.streamer_id = self.segu_id
        elif streamer_name == '비챤':
            self.streamer_id = self.vii_id
        else:
            self.streamer_id = ''
            self.logger.error('지원하지 않는 스트리머입니다. : ' + streamer_name)

        # 자기 닉네임
        self.user_name = conf[4]

        # 검색 시작 날짜
        try:
            st_string = conf[7]

            st_list = st_string.split(' ')  # 나누기
            st_date = st_list[0].split('-') # 날짜
            st_time = st_list[1].split(':') # 시간

            st_all = datetime.datetime(int(st_date[0]), int(st_date[1]), int(st_date[2]), int(st_time[0]), int(st_time[1]), int(st_time[2]))
            self.st_all = st_all - timedelta(hours=9)    # 트위치 서버는 UTC+0
        except:
            self.logger.error(traceback.format_exc())
            self.logger.error('잘못된 검색 시작 날짜입니다. : ' + st_string)


        # 검색 끝 날짜
        try:
            et_string = conf[10]

            et_list = et_string.split(' ')  # 나누기
            et_date = et_list[0].split('-') # 날짜
            et_time = et_list[1].split(':') # 시간

            et_all = datetime.datetime(int(et_date[0]), int(et_date[1]), int(et_date[2]), int(et_time[0]), int(et_time[1]), int(et_time[2]))
            self.et_all = et_all - timedelta(hours=9)    # 트위치 서버는 UTC+0
        except:
            self.logger.error(traceback.format_exc())
            self.logger.error('잘못된 검색 끝 날짜입니다. : ' + et_string)

        f_conf.close()

        return self.streamer_id, self.user_name, self.st_all, self.et_all





    def Get_and_Save_Clip_list(self):

        self.boo, st = self.check_saved_file()

        #if not os.path.exists(Clip_file):
        if not self.boo:
            self.logger.info("cofing 파일 읽기")
            self.read_config_file_streamer()

            if st is not None:
                self.st_all = datetime.datetime.strptime(st, "%Y-%m-%d %H:%M:%S") - timedelta(hours=9)

            
            ## 시간 쪼개기
            # 1. Too many Request 방지
            # 2. 오류나도 중간부터 수집 시작할 수 있게 태스크 분리
            self.logger.info("시간대 분리 시작")
            time_list =[]
            dt = self.et_all - self.st_all
            dt = dt.total_seconds()
            idx = 0

            while True:
                dt = dt - self.Time_Split_Step_sec
                st = self.st_all + timedelta(seconds=self.Time_Split_Step_sec)*idx

                if dt>0:                    
                    et = self.st_all + timedelta(seconds=self.Time_Split_Step_sec)*(idx+1)

                    time_list.append([st, et])
                else:
                    time_list.append([st, self.et_all])
                    break

                idx = idx + 1



            ### 트위치 API 리퀘스트 시작 ###
            ## 아이디 매칭하여 클립 정보 얻기 ##
            self.logger.info("Twitch API 리퀘 시작")

            for args in time_list:

                st = args[0]
                et = args[1]

                log_text = (st + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")+" ~ "+(et + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")+" - 클립 정보 수집 시작"
                self.logger.info(log_text)


                res_lists = []

                now = st
                remained_time = et - now
                remained_time = remained_time.total_seconds()

                
                cpu_num = cpu_count()
                task_num = cpu_num*3

                
                pool = Pool(cpu_num)
                #pbar = tqdm(total=cpu_num)

                args = []
                dt = remained_time/task_num
                for i in range(0, task_num):
                    args.append([st + timedelta(seconds=(dt*i)), st + timedelta(seconds=(dt*(i+1)))])
                
                #'''
                raw_res_lists=[]
                #raw_res_lists = pool.map(get_clip_info_from_twitch, args)
                for x in tqdm(pool.imap(self.get_clip_info_from_twitch, args), total=task_num):
                    raw_res_lists.append(x)
                pool.close()
                pool.join()
                '''
                
                # 싱글 코어용
                args=[st, et, streamer_id, user_name]
                raw_res_lists=[]
                raw_res_lists.append(self.get_clip_info_from_twitch(args))
                '''

                res_lists = []
                for res in raw_res_lists:
                    res_lists = res_lists + res


                self.logger.info("클립 정보 수집 완료")


                # 클립 주소 파일에 저장하기           
                self.save_clip_info(res_lists)

                #print("클립 주소 저장 완료")
                #print("다음 실행 시 왁물원이 아닌 저장된 파일에서 클립을 불러옵니다.")
                log_text = (st + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")+" ~ "+(et + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")+" - 클립 정보 저장 완료"
                self.logger.info(log_text)

            self.logger.info("모든 클립 정보 저장 완료\n 다음 실행 시 저장된 파일에서 정보를 불러옵니다.")
            #messagebox.showinfo("알림", "모든 클립 정보 저장 완료\n다음 실행 시 저장된 파일에서 정보를 불러옵니다.")
            self.boo = True

    def save_clip_info(self, res_lists, already_procd=False):
        
        f_clips = open(self.Clip_file,'a', encoding='UTF8', newline="")
        for res in res_lists:

            wr = csv.writer(f_clips)                    
            if already_procd:
                wr.writerow(list(res.values()))
            else:
                wr.writerow(list(res.values())+['X','X:\\'])

            #f_clips.write(str(res)+'\n')

                
        f_clips.close()



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

    logger.info("시작")
    res_lists=[]

    ### 클립 주소 목록 있는지 확인

    Clip_file = "Clip_list.csv"


    TAPI = Twitch_API(Clip_file, logger)
    st = None

    try:

        TAPI.Get_and_Save_Clip_list()

    except:
        from tkinter import messagebox
        #logger.error(str(res_lists))
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