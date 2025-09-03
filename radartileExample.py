from radartile import *

#抓取单帧给定放大等级下所有瓦片
download_radarTile('2025-09-01-00-00',zoomlevel=3,slpt=0.01)
#抓取一个时间段所有瓦片
download_radarTiles_tmrange('202503270000','202503270100',zoomlevel=4,timesp=60*60,sleep_time=0,rootpth='./')

#抓取涉及给定区域范围的瓦片数据
download_radarTiles_LL_tm('202408041800','202408042000',[115,123,26,35],zoomlevel=6,rootpth='./',timesp=60*60)
download_radarTiles_LL('202508241500',[110,125,28,35],zoomlevel=6,pth='./')

#绘制单瓦片数据（使用contourf,数据有平滑
drawBinGeo('./202508241500_7_42_106.bin',7,106,42)
#使用imshow函数绘制单瓦片数据，梗还原数据原始状态
imshowBin('./106.bin',7,106,42)
tsta='202406110000'
tend='202406150000'
tmstr='202408041124'

extents=[70,140,0,60]

#将一个目录下给定时间帧和放大倍数的所有瓦片数据（如果存在）全部拼接并返回地理坐标
arr,lat,lon=binMontage(tmstr,zoomlevel=5,pth='s://radartile/%s'%(tmstr),extents=extents)
#绘制总数据
drawCRef(arr,lat,lon,extents=extents)