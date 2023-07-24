#-*- coding: utf-8 -*- 

#更新:可直接拖入路径过来了,可拖入目录或者视频


from gevent import monkey
#从gevent库里导入monkey模块。
monkey.patch_all()
#monkey.patch_all()能把程序变成协作式运行，就是可以帮助程序实现异步。
import gevent,time
#导入gevent、time、requests
from gevent.queue import Queue
#从gevent库里导入queue模块

import os
from select import select
import subprocess
import cv2
import time
from PIL import Image
import glob
import re
import shutil
import win32con
import win32clipboard as w 
import piexif
import math


lastFolder=""
mediaVideo=[".mp4",".avi",".flv",".f4v",".rmvb",".mkv",".wmv",".ts"]
work = Queue()
tasks_list  = [ ]

def videoToImage():
    global lastFolder
    while not work.empty():
        videoFile=""
        try:
            videoFile = work.get_nowait()
            print("当前处理文件:"+videoFile)
            if lastFolder!="":
                if os.path.exists(lastFolder):
                    try:
                        shutil.rmtree(lastFolder)
                    except Exception as e:
                        with open("PicBug.txt","a",encoding="utf8") as file:
                           file.write("错误信息45:"+str(e)+"发生错误的行数: "+str(e.__traceback__.tb_lineno)+"\r")
                        print(str(e))  
                lastFolder=""
            contentlist=[] 
            # 存原始视频的目录
            # dir_video_src = os.path.join(os.getcwd(), '.\\videos')
            workpath = os.getcwd() 
            # 存处理后提取到关键帧图片数据的目录
            image_des=os.path.join(workpath,".\\imagesTemp\\",str(time.time()).replace(".",""))
            image_des= image_des.replace("\\.\\","\\")+"\\"

            # print("image_des:"+image_des)
            if not os.path.exists(image_des):
                os.makedirs(image_des)
                # print("已自动创建：", image_des)
            else:
                # print("图片缓存文件夹存在")
                pass
            
            if not os.path.exists("PreviewImage"):
                os.makedirs("PreviewImage")
                print("已自动创建：", "PreviewImage")
            else:
                # print("图片预览文件夹存在")    
                pass
            
            

            videoFilepath=videoFile
            # 将视频文件路径转化为标准的路径
            videoFile=videoFile.replace("\\","/").replace('"','').replace("'","").strip()

            checkname=workpath+"\\PreviewImage\\"+"videoview_%s.jpg"%(subwords(videoFile))
            
            if os.path.exists(checkname):
                print(videoFile+" 文件存在,跳过")
                continue
         

            # 视屏获取
            videoCapture=cv2.VideoCapture(videoFile)
            # 帧率(frames per second)
            fps = videoCapture.get(cv2.CAP_PROP_FPS)
            # 总帧数(frames)
            frames = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
            # print("速率："+str(fps))
            # print("总帧数："+str(frames))

            if fps==0:
                print("文件:"+videoFile+"无法获得时长,请手动检查这个文件是否有问题")
                with open("PicBug.txt","a",encoding="utf8") as file:
                    file.write("文件:"+videoFile+"无法获得时长,请手动检查这个文件是否有问题\r")
                continue
            totalSeconds=frames/fps
            # print("totalSeconds"+str(totalSeconds/16))
            # print("视屏总时长："+"{0:.2f}".format(frames/fps)+"秒")
            numberOfSegments=float(totalSeconds/16)
            numberOfSegments=round(numberOfSegments, 3)
            a=time.strftime('%H:%M:%S', time.gmtime(1000))
            for x in range(16):
                # print("当前帧时间"+str(time.gmtime((x+1)*numberOfSegments)))
                # print(numberOfSegments)
                ffmpeg_path = "ffmpeg"       
                output = subprocess.check_output([
                    ffmpeg_path,
                    "-ss",time.strftime('%H:%M:%S', time.gmtime((x+1)*numberOfSegments)),
                    "-i",videoFile,
                    "-r","1",
                    "-y", #直接覆盖
                    "-vframes","1",
                    "-an","-f","mjpeg",
                    "{path}".format(path=image_des+"jietu_{:02d}.jpg".format(x+1)),
                ], stderr = subprocess.STDOUT) 
                stats = os.stat(image_des+"jietu_{:02d}.jpg".format(x+1))
                if stats.st_size==0:
                    print(image_des+"jietu_{:02d}.jpg".format(x+1)+"大小为0,移除")
                    os.remove(image_des+"jietu_{:02d}.jpg".format(x+1))


            image_names = sorted(glob.glob(image_des+"*"))
            # print("原始video名字:"+videoFile)
            # print("格式化video名字:"+subwords(videoFile))
            image_concat(image_names,subwords(videoFile),workpath+"\\PreviewImage\\",image_des,videoFilepath) #img名字,视频名字,img存放位置,缓存图片文件夹,原始视频名字

            
        except Exception as e:
            with open("PicBug.txt","a",encoding="utf8") as file:
                file.write("错误信息127:"+str(e)+"发生错误的行数: "+str(e.__traceback__.tb_lineno)+"\r")
            print(str(e))

def image_concat(image_names,filename,img_dir,image_des,videoFilepath,max_resolution=2560):
    
    global lastFolder
    """ image_names: list, 存放的是图片的绝对路径 """
    # 1.创建一块背景布
    image = Image.open(image_names[0])
    width, height = image.size
    
    target_shape = (4*width, 4*height)
    background = Image.new('RGB', target_shape, (0,0,0,))


    # 2.依次将图片放入背景中(注意图片尺寸规整、mode规整、放置位置)
    for ind, image_name in enumerate(image_names):
        img = Image.open(image_name)
        img = img.resize((width, height))  # 尺寸规整
        if img.mode != "RGB":             # mode规整
            img = img.convert("RGB")
        row, col = ind//4, ind%4
        location = (col*width, row*height) # 放置位置
        background.paste(img, location)



    scalenormal=True
    if scalenormal==True:

        exif_dict = {"0th": {},
                    "Exif": {},
                    "GPS": {},
                    "1st": {},
                    "thumbnail": None}
        # exif_dict = piexif.load(image.info['exif'])
        date1 = time.strftime('%Y-%m-%d %H:%M:%S')
        # exif_dict['0th'][40091]=bytes(videoFilepath, encoding='utf-16')
        exif_dict['0th'][40092]=bytes(os.path.basename(videoFilepath), encoding='utf-16')
        exif_dict['0th'][270]=bytes(videoFilepath, encoding='utf-8')
        exif_dict["0th"][piexif.ImageIFD.Make] = bytes(videoFilepath, encoding='gbk')
        exif_dict["0th"][piexif.ImageIFD.Model] = bytes(os.path.basename(videoFilepath), encoding='gbk')
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date1
        exif_bytes = piexif.dump(exif_dict)

        # 分配图片文件（完整）路径
        img_filename = img_dir+"videoview_%s.jpg"%(filename)


        resolution = background.size


        # 计算最终目标分辨率 控制最大边限制
        if max_resolution > 0:
            ratio = min(max_resolution / width, max_resolution / height)
            target_shape = (math.ceil(width * ratio), math.ceil(height * ratio))
        else:
            target_shape = (resolution[0], resolution[1])
        
        background_resized = background.resize(target_shape)
        background_resized.save(img_filename, quality=75, exif=exif_bytes)  
  
        
    else:
        # background.resize(px,Image.ANTIALIAS).save(img_dir+"videoview_%s.jpg"%(filename),quality=80)
        pass

    lastFolder=image_des

def currentdirectory(selectpath):
    list_video = []    
    # dir_video_des = os.path.join(os.getcwd(), '.\\temp_images')
    if selectpath=="":        
        dir_video_des=os.getcwd()
    else:
        dir_video_des=selectpath

    for item_filename in os.listdir(dir_video_des):
        if os.path.splitext(item_filename)[1] in mediaVideo:
            if selectpath=="":                
                list_video.append(item_filename)
            else:
                list_video.append(selectpath+"\\"+item_filename)
            print(item_filename)
    if len(list_video) == 0:
        print("视频文件不存在")
    return list_video

def walkdirectory(selectpath):
    list_video = []
    for dirpath, dirnames, filenames in os.walk(selectpath):
        for filename in filenames:
            if os.path.splitext(filename)[1] in mediaVideo:
                print(os.path.join(dirpath, filename)) 
                list_video.append(os.path.join(dirpath, filename))
    return list_video

def loopOperation(list_video):
    for i in list_video:
        work.put_nowait(i)
    #创建空的任务列表
    for x in range(10):
    #相当于创建了10个协程
        task = gevent.spawn(videoToImage)
        #用gevent.spawn()函数创建执行crawler()函数的任务。
        tasks_list.append(task)
        #往任务列表添加任务。
    gevent.joinall(tasks_list)
     
def subwords(words):  
    words=re.sub('[? * : " < > | - .]', '', words) 
    words=re.sub(r'/', '_', words) 
    words=re.sub(r'\\', '_', words) 
    return words

def get_cut():    
    w.OpenClipboard()
    b=w.GetClipboardData(win32con.CF_UNICODETEXT)
    w.CloseClipboard()
    return b 

if __name__ == '__main__':
    typeSelect=5
    selectpath="D:\\Users\\Administrator\\Desktop\\新建文件夹\\"
    selectpath="E:\\迅雷下载\\进击的巨人第二季合集"
    selectpath="C:\\test"
    selectpath=r"C:\test\视频014.mp4"
    while True:
        typeSelect=input("1遍历当前目录;2扫描路径,不包含子目录;3扫描路径,同时遍历子目录;4复制剪贴板的路径;选择1-4;或者直接拖拽过来一个视频直接生成:")
        if typeSelect in ["1", "2", "3", "4"]: 
            typeSelect=str(typeSelect)
            if typeSelect=='1': #当前目录
                print("正在遍历当前目录")
                list_video=currentdirectory("")
                loopOperation(list_video)
            elif typeSelect=='2': #选择目录
                selectpath=input("请粘贴一个路径过来,本选项只会扫描当前路径")
                list_video=currentdirectory(selectpath)
                loopOperation(list_video)
            elif typeSelect=='3':  #遍历目录
                selectpath=input("请粘贴一个路径过来,本选项会同时遍历子目录")
                list_video=walkdirectory(selectpath)
                loopOperation(list_video)
            elif typeSelect=='4': #选择文件
                input("请把连接复制到剪切板上,按任意键继续")
                relist=get_cut()
                relist=re.split("\r\n",relist)
                # print(relist)
                loopOperation(relist)
                # for i in relist:
                #     print(i)
                # pass
            elif typeSelect=='5': #预设路径
                list_video=[selectpath]
                loopOperation(list_video)

            else:
                print(typeSelect)
        else:
            # print("未选择数字,请选择一个数字")
            # 去除两端的空白字符
            typeSelect = typeSelect.strip()

            # 如果路径被双引号包围，则去除双引号
            if typeSelect.startswith('"') and typeSelect.endswith('"'):
                typeSelect = typeSelect[1:-1]

            # 判断路径是否存在
            if os.path.exists(typeSelect):
                # 判断路径是否是目录
                if os.path.isdir(typeSelect):
                    typeSelect2=input("你拖入了一个目录,是否扫描子文件夹内视频? 1不扫描子目录, 2扫描子目录 选择1-2 默认可以直接回车不扫描子目录")
                    typeSelect2=str(typeSelect2)
                    if typeSelect2 != "2":
                        list_video=currentdirectory(typeSelect)
                        loopOperation(list_video)
                    else:
                        list_video=walkdirectory(typeSelect)
                        loopOperation(list_video)

                else:
                    list_video=[typeSelect]
                    loopOperation(list_video)

                    
            else:
                print("路径不存在,请确认这个路径是否是正确的")                



        try:
            shutil.rmtree("imagesTemp")
            pass
        except Exception as e:
            with open("PicBug.txt","a",encoding="utf8") as file:
                file.write("错误信息273:"+str(e)+"发生错误的行数: "+str(e.__traceback__.tb_lineno)+"\r")
            print(str(e))      
            pass
        
        print("程序运行完毕!")
        
            
