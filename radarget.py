#这个程序用于爬取雷达图
import urllib.request
#from time import strptime, mktime, gmtime, time
import time
import eventlet
import os
from radarstation import rdsta
eventlet.monkey_patch()

def main(district, _from, _to, dir,mode=1):

    CNT=0
    print ('')
    f_er=open(dir+"/er.txt","a")
    print ('start download...')
    from_ts = time.mktime(time.strptime(_from, '%Y-%m-%d %H:%M:%S'))+  8 * 3600   #(雷达文件名按照UTC存储）
    to_ts = time.mktime(time.strptime(_to, '%Y-%m-%d %H:%M:%S'))+  8 * 3600
    ts = from_ts
    u = 'http://image.nmc.cn/product/'
    i = 0
    while ts <= to_ts:
        time_s = time.gmtime(ts)
        year = time_s.tm_year
        month = time_s.tm_mon
        day = time_s.tm_mday
        hour = time_s.tm_hour
        min = time_s.tm_min
        sec = time_s.tm_sec
        #name = 'SEVP_AOC_RDCP_SLDAS_EBREF_%s_L88_PI_%d%02d%02d%02d%02d%02d001.PNG' % (district,year, month, day, hour, min, sec)
        name = 'SEVP_AOC_RDCP_SLDAS3_ECREF_%s_L88_PI_%d%02d%02d%02d%02d%02d000.PNG' % (district,year, month, day, hour, min, sec)

        url = u + '%d/%02d/%02d/RDCP/%s' % (year, month, day, name)
        i = i + 1
        try:
            with eventlet.Timeout(5, False):
                download(url, dir, name)
            CNT+=1
            print(name)
            print(i, '%d-%02d-%02d %02d:%02d:%02d' % (year, month, day, hour, min, sec), url)
        except:
            f_er.write(name+'\n')
        if (mode==1):
            ts = ts + 6 * 60                   #6分钟一张图
        elif(mode==2):
            ts=ts+60
    print ('')
    print ('report to ++, it has done! %d images download'%(CNT) )
    #print ('Cost %d hour %d minute %d second.' % (s.tm_hour, s.tm_min, s.tm_sec))

def download(url, dir, name):
    n = dir + '/' + name
    urllib.request.urlretrieve(url, n)

desrDir = input('Input the dest dir to save the pics : \n')            #文件保存路径
district = input('Input the district code (etc : AECN or 杭州；单站数据支持批量下载，城市之间以空格隔开，如杭州 衢州) : \n').split()  #区域（华东AECN华中ACCN）
_from = input('Input the from datetime (in UTC, YYYY-DD-MM HH:mm:ss) : \n')#起始时间（UTC），雷达图时间
_to = input('Input the to datetime (in UTC, YYYY-DD-MM HH:mm:ss) : \n')#结束时间

if (not os.path.exists(desrDir)):
    os.mkdir(desrDir)
'''
if(len(district)==1):
    if(district[0] in ["ACCN","AECN","ASCN","ASWC","ANWC","ACHN","ANCN","ANEC"]):
        main(district[0], _from, _to, desrDir)
    else:
        sta=district[0]
        if (not os.path.exists(desrDir + '/' + sta)):
            os.mkdir(desrDir + '/' + sta)
        main(rdsta[sta], _from, _to, desrDir+'/'+sta,mode=2)
else:
    for sta in district:
        if sta in rdsta:
            if (not os.path.exists(desrDir+'/'+sta)):
                os.mkdir(desrDir+'/'+sta)
            main(rdsta[sta], _from, _to, desrDir+'/'+sta,mode=2)
        else:
            print('%s is not in radarstation list'%(sta))
'''
for sta in district:
    if(sta in ["ACCN","AECN","ASCN", "ASWC","ANWC","ACHN","ANCN","ANEC"]):
        main(sta, _from, _to, desrDir)
    elif sta in rdsta:
        if (not os.path.exists(desrDir+'/'+sta)):
            os.mkdir(desrDir+'/'+sta)
        main(rdsta[sta], _from, _to, desrDir+'/'+sta,mode=2)
    else:
        print('%s is not in radarstation list'%(sta))

        'ACCN AECN ACHN 丽水 衢州 金华 台州 温州 上饶 三明 杭州 临安 黄山 宁波 湖州 绍兴'