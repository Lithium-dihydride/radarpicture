#created by LiH2
import os.path
import time
import numpy as np

zoomlevel_dict={
        3: [[2,3],[5,6,7]],
        4: [[4,5,6],[11,12,13,14]],
        5: [[8,9,10,11,12,13],[22,23,24,25,26,27,28]],
        6: [[16,17,18,19,20,21,22,23,24,25,26],
            [44,45,46,47,48,49,50,51,52,53,54,55,56]],
        7: [[i for i in range(32,54)],
            [i for i in range(88,114)]]
    }
leftTileXidx={3:143,4:29,5:57,6:114,7:228,}
rightTileXidx={3:28,4:56,5:113,6:227,7:199,}
topTileYidx={3:85,4:170,5:85,6:170,7:85,}
TileSp={3:0.176,4:0.088,5:0.044,6:0.022,7:0.011}


# get geography range about tile num
def binLL(zml,xti,yti):
    la=np.zeros(256,dtype='float')
    lo=np.zeros(256,dtype="float")
    if xti == zoomlevel_dict[zml][1][0]:
        lo[:leftTileXidx[zml]] = np.nan
        lo[leftTileXidx[zml]:] = np.array([70+ i * TileSp[zml] for i in range(256-leftTileXidx[zml])])
    elif xti == zoomlevel_dict[zml][1][-1]:
        lo[rightTileXidx[zml]+1:] = np.nan
        lo[:rightTileXidx[zml]+1] = np.arange(70+(256*(xti-zoomlevel_dict[zml][1][0])-leftTileXidx[zml])*TileSp[zml],
                                    70+(256*(xti-zoomlevel_dict[zml][1][0])-leftTileXidx[zml]+rightTileXidx[zml]+0.9999)*TileSp[zml],
                                              TileSp[zml])
    elif xti in zoomlevel_dict[zml][1]:
        """lo = np.arange(70+(256*(xti-zoomlevel_dict[zml][1][0])-leftTileXidx[zml])*TileSp[zml],
                       70+(256*(xti-zoomlevel_dict[zml][1][0])+255-leftTileXidx[zml])*TileSp[zml],
                       TileSp[zml])"""
        lo = np.array([70+(256*(xti-zoomlevel_dict[zml][1][0])-leftTileXidx[zml])*TileSp[zml] + TileSp[zml]*i
                       for i in range(256)])
    else:
        return None

    if (yti == zoomlevel_dict[zml][0][-1]):
        la[topTileYidx[zml] + 1:] = np.nan
        la[:topTileYidx[zml] + 1] = np.arange(
            256 * (yti-zoomlevel_dict[zml][0][0]) * TileSp[zml],
            ((256 * (yti-zoomlevel_dict[zml][0][0])) + topTileYidx[zml] + 0.9999) * TileSp[zml],
            TileSp[zml])
    elif (yti in zoomlevel_dict[zml][0]):
        """la = np.arange(256 * (yti-zoomlevel_dict[zml][0][0]) * TileSp[zml],
                       256 * (yti-zoomlevel_dict[zml][0][0] + 1)  * TileSp[zml],
                       TileSp[zml])"""
        la = np.array([256 * (yti-zoomlevel_dict[zml][0][0]) * TileSp[zml] + i*TileSp[zml] for i in range(256)])
    else:
        pass
    return lo,la


#
def binMontage(tmstr,zoomlevel,pth,extents,):
    [minlon, maxlon, minlat, maxlat] = extents
    [le, ri, bo, to] = getllidx(minlon, maxlon, minlat, maxlat, zoomlevel)
    resarr=np.zeros(shape=(256*(to-bo+1),256*(ri-le+1)),dtype='int')
    lat=np.zeros(256*(to-bo+1),dtype='float')
    lon=np.zeros(256*(ri-le+1),dtype='float')
    for i,_x in enumerate(range(le,ri+1)):
        for j,_y in enumerate(range(bo,to+1)):
            fnm=('%s/%s_%d_%d_%d.bin'%(pth,tmstr,zoomlevel,_y,_x))
            print(256*i,256*(i+1),256*j,256*(j+1))
            try:
                resarr[256*j:256*(j+1),256*i:256*(i+1)]=bin2arr(fnm)
            except:
                print('no such file '+ fnm)
            lo,la=binLL(zoomlevel,_x,_y)
            if(i==0):
                lat[256*j:256*(j+1)]=la
            if(j==0):
                lon[256*i:256*(i+1)]=lo
    return resarr,lat,lon


# turn binfile to np.array
def bin2arr(binf):
    import numpy as np
    image = np.zeros((256, 256), dtype="float")
    with open(binf, 'rb') as binf:
        # 每次读取 2 字节
        for y in range(256):
            for x in range(256):
                data = binf.read(2)
                if len(data) == 2:
                    value = int.from_bytes(data, byteorder="big", signed=False)
                    image[y][x] = value
    return image


def bin2nc(arr,lon,lat):
    import netCDF4 as nc


# download single radar tile binfile according to time,zoomlevel and tileidx
def download_radarTile(tmstr,zoomlevel,xti,yti,pth='d://0/rdtil/',fnm=None):
    import requests
    import time
    _t=time.strptime(tmstr,"%Y%m%d%H%M")
    ymd='%4d%02d%02d'%(_t.tm_year,_t.tm_mon,_t.tm_mday)
    h=_t.tm_hour
    m=_t.tm_min

    headers = {
        "authority": "data.cma.cn",
        "method": "GET",
        "path": "/tiles/China/RADAR_L3_MST_CREF_GISJPG_Tiles_CR/%s/%02d/%02d/%d/%d/%d.bin"
                %(ymd,h,m,zoomlevel,yti,xti),
        "scheme": "https",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept_Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Origin": "https://data.cma.cn",
        "Priority": "u=1, i",
        "Referer": "https://data.cma.cn/dataGis/static/gridgis/",
        "Sec-Ch-Ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Windows",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "sec-fetch-site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
    }
    url='https://image.data.cma.cn/tiles/China/RADAR_L3_MST_CREF_GISJPG_Tiles_CR//%s/%02d/%02d/%d/%d/%d.bin'\
        %(ymd, h, m, zoomlevel, yti, xti)
    try:
        response = requests.get(url, headers=headers)
        if(response.status_code==200):
            if fnm == None:
                fnm = '%s%02d%02d_%d_%d_%d.bin' % (ymd, h, m, zoomlevel, yti, xti)
            with open(pth+fnm,"wb") as resf:
                resf.write(response.content)
            print('success save '+url +' as '+pth+fnm)
        else:
            print(response.status_code,url)
    except:
        print()
        print("response error ",url)


# download all radar tile binfile under a zoomlevel according to time
def download_radarTiles_zoom(tmstr,zoomlevel,pth='d://0/rdtil/l3/',fnm=None,slpt=1.0):

    for _y in zoomlevel_dict[zoomlevel][0]:
        for _x in zoomlevel_dict[zoomlevel][1]:
            download_radarTile(tmstr,zoomlevel,_x,_y,pth,fnm)


# download all radar tile binfile under a zoomlevel according to timerange
def download_radarTiles_tmrange(tstar,tend,zoomlevel,timesp=6*60,sleep_time=1.0,rootpth="d://0/rdtil/l3/"):
    _ts=time.mktime(time.strptime(tstar,"%Y%m%d%H%M%S"))+8*3600
    _te=time.mktime(time.strptime(tend , "%Y%m%d%H%M%S"))+8*3600
    _t=_ts
    while _t<=_te:
        t=time.gmtime(_t)
        tstr="%4d%02d%02d%02d%02d"%(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min)
        if not os.path.exists('%s%s/'%(rootpth,tstr)):
            os.mkdir('%s%s/'%(rootpth,tstr))
        download_radarTiles_zoom(tstr,zoomlevel,pth='%s%s/'%(rootpth,tstr),slpt=sleep_time)
        _t+=timesp


# download all radar tile binfile limited by geography range in a time frame
def download_radarTiles_LL(tmstr,extents,zoomlevel,pth):
    [minlon,maxlon,minlat,maxlat]=extents
    [le, ri, bo, to]=getllidx(minlon,maxlon,minlat,maxlat,zoomlevel)
    for x in range(le,ri+1):
        for y in range(bo,to+1):
            download_radarTile(tmstr,zoomlevel,x,y,pth,)


# download all radar tile binfile limited by geography range during a time range
def download_radarTiles_LL_tm(tstar,tend,extents,zoomlevel,timesp=6*60,sleep_time=1.0,rootpth="d://0.rdtil.l3"):
    _ts = time.mktime(time.strptime(tstar, "%Y%m%d%H%M%S"))+8*3600
    _te = time.mktime(time.strptime(tend, "%Y%m%d%H%M%S"))+8*3600
    _t = _ts
    while _t <= _te:
        t = time.gmtime(_t)
        tstr = "%4d%02d%02d%02d%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min)
        if not os.path.exists('%s%s/' % (rootpth, tstr)):
            os.mkdir('%s%s/' % (rootpth, tstr))
        download_radarTiles_LL(tstr,extents,zoomlevel, pth='%s%s/' % (rootpth, tstr),)
        _t += timesp


# draw picture with array,latitude and longtitude
def drawCRef(arr,lat,lon,tistr='',extents=None,outf=None):
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.io.shapereader as shpreader
    from old_colortable import color_RGB_norm
    import matplotlib.colors
    import numpy as np

    # from old_TransCodnt import trans
    plt.rcParams['font.family'] = "Microsoft YaHei"

    self_cmap = matplotlib.colors.ListedColormap(color_RGB_norm[1:13]).with_extremes(bad="white", under="white",
                                                                                     over="white")
    bounds = np.arange(0, 13, 1)
    norm = matplotlib.colors.BoundaryNorm(bounds, self_cmap.N)

    proj = ccrs.PlateCarree()

    arr = np.where(arr > 1000, 0, arr / 10)

    fig = plt.figure(figsize=(8,6),dpi=300)
    ax = fig.add_subplot(111, projection=proj)
    if(extents is not None):
        ax.set_extent(extents)
    nonanxidx = np.where(~np.isnan(lon))[0]
    nonanyidx = np.where(~np.isnan(lat))[0]
    im = ax.contourf(lon[nonanxidx], lat[nonanyidx], arr[nonanyidx][:, nonanxidx],
                     transform=proj, cmap=self_cmap,levels=range(5, 70, 5))
    plt.colorbar(im)
    if tistr!='':
        plt.title(tistr)

    fpth = "D://MICAPS4.0.5/data/shapefiles/Province.shp"
    reader = shpreader.Reader(fpth)
    geoms = reader.geometries()
    ax.add_geometries(geoms, proj, lw=0.5, fc="none")

    fpth = "D://MICAPS4.0.5/data/shapefiles/City.shp"
    reader = shpreader.Reader(fpth)
    geoms = reader.geometries()
    ax.add_geometries(geoms, proj, lw=0.2, fc="none")

    #ax.coastlines()

    if(outf is not None):
        plt.savefig(outf)
    else:
        plt.show()


# draw picture with single bin file
def drawBinGeo(fnm,zml,xti,yti,tistr=''):
    image = bin2arr(fnm)
    lon, lat = binLL(zml, xti, yti)
    drawCRef(image,lat,lon,tistr)


# get bin file's index which included by geography range
def getllidx(minlon,maxlon,minlat,maxlat,zoomlevel):
    le,ri = zoomlevel_dict[zoomlevel][1][0],zoomlevel_dict[zoomlevel][1][-1]
    bo,to = zoomlevel_dict[zoomlevel][0][-1],zoomlevel_dict[zoomlevel][0][0]
    sp=TileSp[zoomlevel]
    for y in zoomlevel_dict[zoomlevel][0]:
        for x in zoomlevel_dict[zoomlevel][1]:
            lo,la=binLL(zoomlevel,x,y)
            if(minlon<np.nanmax(lo) and minlon>np.nanmin(lo)-sp):
                le=x
            if(maxlon<np.nanmax(lo)+sp and maxlon>np.nanmin(lo)):
                ri=x
            if(minlat<np.nanmax(la) and minlat>np.nanmin(la)-sp):
                bo=y
            if(maxlat<np.nanmax(la)+sp and maxlat>np.nanmin(la)):
                to=y
    return [le,ri,bo,to]


# draw picture with singel bin file using imshow
def imshowBin(binf):
    import numpy as np
    import matplotlib.pyplot as plt
    image=bin2arr(binf)
    fig,ax=plt.subplots()

    im=ax.imshow(image)
    ax.invert_yaxis()
    plt.colorbar(im)
    plt.show()


# draw picture with singel bin file using imshow with geography coordinate
def imshowBinGeo(fnm,zml,xti,yti,tistr=''):
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.io.shapereader as shpreader
    from old_colortable import color_RGB_norm
    import matplotlib.colors
    import numpy as np

    # from old_TransCodnt import trans
    plt.rcParams['font.family'] = "Microsoft YaHei"

    self_cmap = matplotlib.colors.ListedColormap(color_RGB_norm[1:13]).with_extremes(bad="white", under="white",
                                                                                     over="white")
    bounds = np.arange(0, 13, 1)
    norm = matplotlib.colors.BoundaryNorm(bounds, self_cmap.N)

    proj = ccrs.PlateCarree()

    image = bin2arr(fnm)
    image = np.where(image > 1000, 0, image / 10)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection=proj)
    lon, lat = binLL(zml, xti, yti)
    extents=[np.min(lon),np.max(lon),np.min(lat),np.max(lat)]
    im = ax.imshow(image[::-1,:],extent=extents,transform=proj,)
    plt.colorbar(im)

    fpth = "D://MICAPS4.0.5/data/shapefiles/Province.shp"
    reader = shpreader.Reader(fpth)
    geoms = reader.geometries()
    ax.add_geometries(geoms, proj, lw=0.5, fc="none")

    if tistr != '':
        plt.title(tistr)

    fpth = "D://MICAPS4.0.5/data/shapefiles/City.shp"
    reader = shpreader.Reader(fpth)
    geoms = reader.geometries()
    ax.add_geometries(geoms, proj, lw=0.2, fc="none")

    #ax.coastlines()
    plt.show()
