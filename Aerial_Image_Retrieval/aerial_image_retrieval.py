# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 01:16:14 2019

@author: Hao
"""

from urllib import request
import math
import sys
from PIL import Image
import os

MAXLEVEL = 23
MINLAT, MAXLAT = -85.05112878, 85.05112878
MINLON, MAXLON = -180., 180.
TILESIZE = 256

def to_binary(num):
    temp = 0 
    level =0
    while(num>=0.5):
        res = num%2
        temp=(10**level)*res+temp
        num=num//2
        level+=1
    return temp     
def latlon_to_pixelXY(lat,lon,level):
    sinLatitude = math.sin(lat*math.pi/180)
    pixelX=((lon+180)/360)*256*2**level
    pixelY=(0.5-math.log((1+sinLatitude)/(1-sinLatitude))/(4*math.pi))*256*2**level     
    return math.floor(pixelX),math.floor(pixelY)
   
    
def pixelXY_to_tileXY(pixelX,pixelY):
    return math.floor(pixelX/256.0),math.floor(pixelY/256.0)
        
        
        
def tileXY_to_northwest_pixelXY(tileX,tileY):
    return int(tileX*TILESIZE),int(tileY*TILESIZE)
   
        
def tileXY_to_quadkey(tileX,tileY,level):
    return '{0:0{1}d}'.format(to_binary(tileX)+2*to_binary(tileY),level)

def get_maps(tileX,tileY,level):
    quadkey = tileXY_to_quadkey(tileX,tileY,level)
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(THIS_FOLDER,'output','temp','{0}.jpeg'.format(quadkey))
    
    if os.path.exists(filename):
        return True , Image.open(filename)
    else:
        with request.urlopen("http://h0.ortho.tiles.virtualearth.net/tiles/h{0}.jpeg?g=131".format(quadkey)) as file:
            image = Image.open(file)
        if image.mode=='P': # if image mode ==P means maps we get is a gray pic showed not available, normal maps should be RGB
            return False, None
        else:
            image.save(filename)
            return True, image


def image_retrieval(lat1,lon1,lat2,lon2):
    for level in range(MAXLEVEL,11,-1):
        pixel_x1,pixel_y1 = latlon_to_pixelXY(lat1,lon1,level)
        pixel_x2,pixel_y2 = latlon_to_pixelXY(lat2,lon2,level)
        
        tile_x1,tile_y1 = pixelXY_to_tileXY(pixel_x1,pixel_y1)
        tile_x2,tile_y2 = pixelXY_to_tileXY(pixel_x2,pixel_y2)
        flag = True
        
        try:
            result = Image.new('RGB', ( (tile_x2-tile_x1 +1)*TILESIZE , (tile_y2-tile_y1 +1)*TILESIZE ))
        except MemoryError:
            print("The Request Area is too large, skip level {0}".format(level))
            continue

        totaltiles = (tile_x2-tile_x1+1)*(tile_y2-tile_y1+1)

        
        count = 0
        batchszie = max(100,math.floor(totaltiles/200))
        
        for tile_x in range(tile_x1,tile_x2+1):
            for tile_y in range(tile_y1,tile_y2+1):
                flag, tile_maps = get_maps(tile_x,tile_y,level)
                #print(flag)
                count+=1
                if count==2:
                    print("About {0} tiles".format( totaltiles ))
                if count%batchszie==0:
                    print("{0} % tiles had downloaded".format(100*count/totaltiles))
                if flag:
                    result.paste(tile_maps,((tile_x -tile_x1)*TILESIZE,(tile_y-tile_y1)*TILESIZE))
                else:
                    break
            if not flag:
                break
        if not flag:
            print("Level {0} is not available for given area".format(level))
            continue
        else:
            nw_pixel_x,nw_pixel_y = tileXY_to_northwest_pixelXY(tile_x1,tile_y1)
            result_crop = result.crop((pixel_x1-nw_pixel_x,pixel_y1-nw_pixel_y,pixel_x2-nw_pixel_x+1,pixel_y2-nw_pixel_y+1))
            print("Aerial Image Retrieval done for level {0}".format(level))
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join( THIS_FOLDER,'output','aerial_image_{0}_{1}_{2}_{3}_level_{4}.jpeg'.format(lat1,lon1,lat2,lon2,level))
            result_crop.save(filename)
            return True
    return False
        
    


def main():
    try:
        os.mkdir('./output/')
        os.mkdir('./output/temp/')
    except FileExistsError:
        pass
        
    
    
    try:
        latlonlatlon = sys.argv[1:]
    except IndexError:
        sys.exit("No enough input")
    
    if len(latlonlatlon) !=4:
        sys.exit("Please input lat1, lon1, lat2, lon2.") 
    lat1,lon1,lat2,lon2=float(latlonlatlon[0]),float(latlonlatlon[1]),float(latlonlatlon[2]),float(latlonlatlon[3])
    lat1,lat2 = max(lat1,lat2),min(lat1,lat2)
    lon1,lon2 = min(lon1,lon2),max(lon1,lon2)
  
    if lon1==lon2 or lat1==lat2:
        sys.exit("Please given a bounding box.")
        
    if max(lon1,lon2) > MAXLON or min(lon1,lon2) <MINLON or max(lat1,lat2) > MAXLAT or min(lat1,lat2) <MINLON:
        sys.exit("Please input valid lat and lon.")
    
    output_flag = image_retrieval(lat1,lon1,lat2,lon2)           
    if output_flag:
        print("Aerial Image Retrieval is done.")
    else:
        print("Something Wrong, Try to execute again.")
if __name__ == '__main__':
    main()
