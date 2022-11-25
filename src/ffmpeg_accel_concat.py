import os

def save_flist(files):
    f_data = 'file \'' + '\'\nfile \''.join(files) + '\''
    print(f_data)

    f_list = 'list.txt'
    with open(f_list, 'w', encoding='UTF-8') as f:
        f.write(f_data)
    return f_list

def vid_concat(files, output_path):

    f_list = save_flist(files)

    call = f'ffmpeg -f concat -safe 0 -i {f_list} -c copy {output_path} -y'         # only supporte the same video_format, copy and not recode.

    #call = f'ffmpeg -f concat -safe 0 -i {f_list} -vcodec h264_nvenc {output_path} -y'    # cuda accelerate. 인코딩용

    print(call)

    os.system(call)

    os.remove(f_list)


def change_tbn(file):

    new_file = file.replace('.mp4','_fix.mp4')

    # https://k66google.tistory.com/578
    # tbn 숫자는 아무거도 해도 일단 되는 듯?
    call = f'ffmpeg -i \"' + file + '\" -video_track_timescale 11988 -vcodec copy -acodec copy \"' + new_file +'\" -y'

    print(call)

    os.system(call)

    os.remove(file)

    os.rename(new_file, file)




def delete_fixed_vid(file_list):

    for file in file_list:
        f = file.replace('/','\\')
        os.remove(f)