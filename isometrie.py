import random
import cv2 as cv
import numpy as np
import math as mth

height = 1024
width = 1296
gridsize = 32
xoffset = width/2
yoffset = +gridsize*4

def clamp(num, min_value, max_value):
    num = max(min(num, max_value), min_value)
    return num

def create_grit(img,gridsize,color):
    global height
    global width

    for i in range(1,int(width/gridsize)+1):
        cv.line(img,(gridsize*i,0),(gridsize*i,height),color)

    for j in range(int(height/gridsize)):
        cv.line(img,(0,gridsize*j),(width,gridsize*j),color)

    return img


class IsoCube:

    def __init__(self,_IsoCenter,_color,_zoffset = 0):
        self.IsoCenter = _IsoCenter
        self.color = _color
        self.zoffset = _zoffset
    def IsometricToCoords(self,point):
        
        cX = point[0] * 1 + point[1] * -1
        cY = point[0] * 0.5 + point[1] * 0.5

        return (cX,cY)
    
    def draw(self,img):
        global gridsize, xoffset, yoffset
        
        b, g, r = self.color
        #hier een betere functie voorschrijven
        topcolor = b, g, r
        rsidecolor = clamp(b+100,0,255), clamp(g+100,0,255), clamp(r+100,0,255)
        lsidecolor = clamp(b-55,0,255), clamp(g-55,0,255), clamp(r-55,0,255)
        midlinecolor = clamp(b+150,0,255), clamp(g+150,0,255), clamp(r+150,0,255)
        outlinecolor = clamp(b-205,0,255), clamp(g-205,0,255), clamp(r-205,0,255)

        cX, cY = self.IsometricToCoords(self.IsoCenter)

        #topside
        bovenVierkant = [[0,0],[1,-0.5],[0,-1],[-1,-0.5]]
        for i, point in enumerate(bovenVierkant):
            bovenVierkant[i] = [int((cX + point[0])*gridsize+xoffset),int((cY+point[1])*gridsize+yoffset+self.zoffset)]
        cv.fillConvexPoly(img,np.array(bovenVierkant),topcolor)
        
        #lside
        lsideVierkant = [[0,0],[-1,-0.5],[-1,0.5],[0,1]]
        for i, point in enumerate(lsideVierkant):
            lsideVierkant[i] = [int((cX + point[0])*gridsize+xoffset),int((cY+point[1])*gridsize+yoffset+self.zoffset)]
        cv.fillConvexPoly(img,np.array(lsideVierkant),lsidecolor)

        #rside
        rsideVierkant = [[0,0],[1,-0.5],[1,0.5],[0,1]]
        for i, point in enumerate(rsideVierkant):
            rsideVierkant[i] = [int((cX + point[0])*gridsize+xoffset),int((cY+point[1])*gridsize+yoffset+self.zoffset)]
        cv.fillConvexPoly(img,np.array(rsideVierkant),rsidecolor)

        return 1 

class IsoCubeController:
    def __init__(self):
        self.isomap = np.zeros((101,101),dtype=IsoCube)
        self.gridsize = (101,101)
        self.fallinglist = []

    def addCube(self,coord,color):
        x, y = coord
        self.isomap[x,y] = IsoCube(coord,color,0)
    
    def removeCube(self,coord):
        x, y = coord
        self.isomap[x,y] = 0

    def draw(self,img):
        for x in range(len(self.isomap)):
            for y in range(len(self.isomap[0])):
                if(self.isomap[x,y] != 0):
                    self.isomap[x,y].draw(img)
                   

    def grid(self,gridsize,spacing,color='rnd',offset=0,checkerColors=[(0,255,0),(255,0,0)]):
        self.gridsize=gridsize
        for x in range(gridsize[0]):
            for y in range(gridsize[1]):
                if(color == 'rnd'):
                    cubecolor = (random.randrange(50,255),random.randrange(50,255),random.randrange(50,255))
                elif(color == 'checker'):
                    cubecolor = checkerColors[0] if((x + y ) % 2 == 0) else checkerColors[1]
                else:
                    cubecolor = color
                if(offset == 'rnd'):
                    cubeoffset = random.randrange(-gridsize[0],gridsize[0])
                else:
                    cubeoffset = offset
                
                self.isomap[x,y] = IsoCube((x*spacing,y*spacing),cubecolor,cubeoffset)

    def wave(self,scroll,ampitude = 16, periode = 1,offset = (0,0)):
        for x in range(len(self.isomap)):
            for y in range(len(self.isomap[0])):
                if(self.isomap[len(self.isomap)-1-x,y] != 0):
                    self.isomap[len(self.isomap)-1-x,y].zoffset = mth.sin((x+offset[0])/periode+(y+offset[1])/periode+scroll)*ampitude
                    
    def sidewave(self,scroll,ampitude = 16,periode = 1,offset = (0,0)):
        for x in range(len(self.isomap)):
            for y in range(len(self.isomap[0])):
                if(self.isomap[len(self.isomap)-1-x,y] != 0):
                    self.isomap[len(self.isomap)-1-x,y].zoffset = mth.sin((x+offset[0])/periode+scroll)*ampitude + mth.cos((y+offset[1])/periode+scroll)*ampitude
    
    def funtion(self,f,args=[]):
         for x in range(len(self.isomap)):
            for y in range(len(self.isomap[0])):
                if(self.isomap[x,y] != 0):
                    self.isomap[x,y].zoffset = f(x,y,self.isomap[x,y].zoffset,*args)

    def setColor(self,coord,color):
        x, y = coord
        self.isomap[x,y].color = color
    
    def setColorFunc(self,f,args=[]):
        for x in range(len(self.isomap)):
            for y in range(len(self.isomap[0])):
                if(self.isomap[x,y] != 0):
                    self.isomap[x,y].color = f(x,y,self.isomap[x,y].color,*args)
    
    def rndfallingcubes(self,i,fallspeed):
        d =  1

        if(d == 1):
            rX, rY = random.randrange(0,self.gridsize[0]), random.randrange(0,self.gridsize[1])
            while(self.isomap[rX,rY] == 0):
                rX, rY = random.randrange(0,self.gridsize[0]), random.randrange(0,self.gridsize[1])
            self.fallinglist.append([rX,rY,i])
            self.isomap[rX,rY].color = (0,0,255)

        for index, cube in enumerate(self.fallinglist):
            
            global height
            x, y, j = cube
            self.isomap[x, y].zoffset = self.isomap[x, y].zoffset + fallspeed if(i > j + 1) else self.isomap[x, y].zoffset
            
        return 0

#functies voor in de renderer
def inversSPOffset(x,y,offset):
    return offset if((x+y)%2 == 0) else -offset

def dampedWave(x,y,offset,i,a,b,c):
    return a*mth.e**(-b*x) * mth.cos(x/c+i)*mth.e**(-b*y) * mth.cos(y/c+i)

def quadDampedWave(x,y,offset,i,a,b,c,size):
    off1 = a*mth.e**(-b*x) * mth.cos(x/c+i)*mth.e**(-b*y) * mth.cos(y/c+i)
    off2 = a*mth.e**(-b*(size-x)) * mth.cos((size-x)/c+i)*mth.e**(-b*y) * mth.cos(y/c+i)
    off3 = a*mth.e**(-b*x) * mth.cos(x/c+i)*mth.e**(-b*(size-y)) * mth.cos((size-y)/c+i)
    off4 = a*mth.e**(-b*(size-x)) * mth.cos((size-x)/c+i)*mth.e**(-b*(size-y)) * mth.cos((size-y)/c+i)
    return off1 + off2 + off3 + off4

def dropletWave(x,y,offset,i,a,b,c,size):
    
    if(x == size/2 and y == size/2):
        return (a*mth.e**(-b*(x-size/2)) * mth.cos((x-size/2)/c+i)*mth.e**(-b*(y-size/2)) * mth.cos((y-size/2)/c+i))

    off1 = a*mth.e**(-b*(x-size/2)) * mth.cos((x-size/2)/c+i)*mth.e**(-b*(y-size/2)) * mth.cos((y-size/2)/c+i) if(x > size/2  and y >= size/2) else 0
    off2 = a*mth.e**(-b*(size/2-x)) * mth.cos((size/2-x)/c+i)*mth.e**(-b*(y-size/2)) * mth.cos((y-size/2)/c+i) if(x <= size/2 and y > size/2) else 0
    off3 = a*mth.e**(-b*(x-size/2)) * mth.cos((x-size/2)/c+i)*mth.e**(-b*(size/2-y)) * mth.cos((size/2-y)/c+i) if(x >= size/2 and y < size/2) else 0
    off4 = a*mth.e**(-b*(size/2-x)) * mth.cos((size/2-x)/c+i)*mth.e**(-b*(size/2-y)) * mth.cos((size/2-y)/c+i) if(x < size/2 and y <= size/2) else 0
    
    return (off1 + off2 + off3 + off4)

def rotatingPlane(x,y,offset,i,a,size):

    d = int((i%40)/10)
    c = (i%10)/10
    if d == 0:
        return (c*a)*(x-size/2) + ((1-c)*a)*(y-size/2)
    if d == 1:
        return ((1-c)*a)*(x-size/2) - ((c)*a)*(y-size/2)
    if d == 2:
        return -(c*a)*(x-size/2) - ((1-c)*a)*(y-size/2)
    if d == 3:
        return -((1-c)*a)*(x-size/2) + ((c)*a)*(y-size/2)

def fmodulo(x,y,offset,i,j,a):
    return a if(x % i[0] == j[0] or y % i[1] == j[1]) else offset

def kleur(x,y,offset,a):
    return a[x%i] if(x % 1) else offset

def golf(x,t,y,a,k,w,phi,i):
    y = a*mth.sin(k*x - w*(t-i) + phi)
    return y 

canvas = np.zeros((height,width,3), dtype=np.uint8)
canvas = create_grit(canvas,gridsize,(100,0,0))

cubecontrol = IsoCubeController()
size = 10
cubecontrol.grid((size,size),1,color='checker',checkerColors=[(255,255,0),(255,0,255)])


i = 0.1
while 1:

    new_canvas = canvas.copy()
  
    #cubecontrol.wave(i,periode=10,ampitude=gridsize*2)
    #cubecontrol.funtion(golf,[size,0.1,1,0,i])

    #cubecontrol.funtion(dropletWave,[i,gridsize,-0.06,3,size-1])

    #cubecontrol.funtion(quadDampedWave,[i,gridsize*4,0.01,10,size])  

    #cubecontrol.wave(i,periode=10,ampitude=gridsize*2)
    #cubecontrol.funtion(inversSPOffset,[])

    #cubecontrol.funtion(rotatingPlane,[i,gridsize/2,size])

    #cubecontrol.funtion(rotatingPlane,[i,gridsize/2,size])
    #cubecontrol.funtion(inversSPOffset,[])

    cubecontrol.wave(i,periode=10,ampitude=gridsize*2)
    cubecontrol.funtion(fmodulo,[(2,2),(0,0),0])
    cubecontrol.setColorFunc(fmodulo,[(2,2),(0,0),(255,0,255)])

    #cubecontrol.rndfallingcubes(i,gridsize/2)

    cubecontrol.draw(new_canvas)

    i += 0.1

    cv.imshow("Image",new_canvas)

    k = cv.waitKey(30) & 0xff
    if (k == 27):
        break

cv.destroyAllWindows()


