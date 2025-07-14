#这个程序用于爬取雷达图
import urllib.request
#from time import strptime, mktime, gmtime, time
import time
from email.policy import default

import eventlet
import os
from radarstation import rdsta
eventlet.monkey_patch()
def downradar(district,_from,_to,dir,):
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

    default_path="/data/home/inspur/0/radar"
    desrDir=default_path+dir
    if(desrDir.find("default")!=-1):
        desrDir=default_path+desrDir.replace("default","")
    if (not os.path.exists(desrDir)):
        os.mkdir(desrDir)
    for sta in district:
        if(sta in ["ACCN","AECN","ASCN", "ASWC","ANWC","ACHN","ANCN","ANEC"]):
            main(sta, _from, _to, desrDir)
        elif sta in rdsta:
            if (not os.path.exists(desrDir+'/'+sta)):
                os.mkdir(desrDir+'/'+sta)
            main(rdsta[sta], _from, _to, desrDir+'/'+sta,mode=2)
        else:
            print('%s is not in radarstation list'%(sta))

        'ACCN AECN ACHN 丽水 衢州 金华 台州 温州 上饶 三明 建安 杭州 临安 黄山 宁波 湖州 绍兴'
        "丽水 衢州 金华 台州 温州 上饶 三明 建阳 杭州 临安 黄山 宁波 湖州 绍兴 长沙 吉安 南昌 郴州 永州 桂林"
        "丽水 衢州 金华 台州 温州 上饶 三明 建阳 杭州 临安 黄山 宁波 湖州 绍兴 南昌 武汉 长沙 贵阳 黄冈 宜昌 九江 丽水 武汉 常德 温州 建阳 上饶 衢州 金华"

while(True):
    t=time.gmtime(time.time())
    month=t.tm_mon
    day=t.tm_mday
    hour=t.tm_hour
    dir="/%02d%02d"%(month,day)
    print(t)
    if(hour==1):
        _to = '2025-%02d-%02d %02d:00:00' % (month, day,0)
        t = time.gmtime(time.time()-3600*12)
        month = t.tm_mon
        day = t.tm_mday
        dir = "/%02d%02d" % (month, day)
        _from = '2025-%02d-%02d %02d:00:00' % (month, day,12)
        print(_from, _to, dir)
        downradar(["ACCN","AECN","ACHN","ANEC","ANCN","丽水","衢州","金华","杭州","温州","建阳"],_from,_to,dir)#
    elif(hour==13):
        _from = '2025-%02d-%02d %02d:00:00' % (month, day,0)
        _to = '2025-%02d-%02d %02d:00:00' % (month, day,12)
        dir = "/%02d%02d" % (month, day)
        print(_from,_to,dir)
        downradar(["ACCN","AECN","ACHN","ANEC","ANCN","丽水","衢州","金华","杭州","温州","建阳"],_from,_to,dir)

    else:
        print(t)
    time.sleep(3600)