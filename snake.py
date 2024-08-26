import random
import time
import cv2 as cv
import numpy as np
import math as mth

height = 1024
width = 1296
gridsize = 64
xoffset = width/2
yoffset = gridsize*2

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
        rsidecolor = clamp(b+50,0,255), clamp(g+50,0,255), clamp(r+50,0,255)
        lsidecolor = clamp(b-25,0,255), clamp(g-25,0,255), clamp(r-25,0,255)
        midlinecolor = clamp(b+150,0,255), clamp(g+150,0,255), clamp(r+150,0,255)
        outlinecolor = clamp(b-205,0,255), clamp(g-205,0,255), clamp(r-205,0,255)

        cX, cY = self.IsometricToCoords(self.IsoCenter)

        #topside
        bovenVierkant = [[0,0],[1,-0.5],[0,-1],[-1,-0.5]]
        for i, point in enumerate(bovenVierkant):
            bovenVierkant[i] = [int((cX + point[0])*gridsize+xoffset),int((cY+point[1])*gridsize+yoffset+self.zoffset - self.IsoCenter[2]*gridsize)]
        cv.fillConvexPoly(img,np.array(bovenVierkant),topcolor)
        
        #lside
        lsideVierkant = [[0,0],[-1,-0.5],[-1,0.5],[0,1]]
        for i, point in enumerate(lsideVierkant):
            lsideVierkant[i] = [int((cX + point[0])*gridsize+xoffset),int((cY+point[1])*gridsize+yoffset+self.zoffset - self.IsoCenter[2]*gridsize)]
        cv.fillConvexPoly(img,np.array(lsideVierkant),lsidecolor)

        #rside
        rsideVierkant = [[0,0],[1,-0.5],[1,0.5],[0,1]]
        for i, point in enumerate(rsideVierkant):
            rsideVierkant[i] = [int((cX + point[0])*gridsize+xoffset),int((cY+point[1])*gridsize+yoffset+self.zoffset - self.IsoCenter[2]*gridsize)]
        cv.fillConvexPoly(img,np.array(rsideVierkant),rsidecolor)

        return 1 

class SnakeGame:
    def __init__(self,gridsize,areasize):

        self.GAMEOVER = 1
        self.GAMESTART = 2
        self.GAMEPLAYING = 3


        self.cubemap = np.zeros((areasize[0],areasize[1],2),dtype=IsoCube)
        print(self.cubemap.size)
        self.gridsize = gridsize
        self.areasize = areasize
        first_pos = (areasize[0]//2,areasize[1]//2,1)
        self.snakelist = [first_pos]
        self.cubemap[first_pos[0],first_pos[1],1] = IsoCube((first_pos[0],first_pos[1],1),(0,0,200))
        self.snakesize = 2
        self.foodlist = []
        self.gamestate = self.GAMESTART
        return
    def grid(self,areasize,lvl=0):

        for x in range(areasize[0]):
            for y in range(areasize[1]):
                cubecolor = (0,153,0) if((x + y ) % 2 == 0) else (0,204,102)
                self.cubemap[x,y,lvl] = IsoCube((x,y,lvl),cubecolor,0)
        return   

    def draw(self,canvas):
        for x in range(len(self.cubemap)):
            for y in range(len(self.cubemap[0])):
                for z in range(len(self.cubemap[0][0])):
                    if(self.cubemap[x,y,z] != 0):
                        self.cubemap[x,y,z].draw(canvas)

        return canvas

    def randomfood(self):

        def checkForCollision(food_pos):
            X = random.randrange(0,self.areasize[0]-1)
            Y = random.randrange(0,self.areasize[1]-1)
            food_pos = (X,Y,1)
            print(self.snakelist)
            print(food_pos in self.snakelist)
            if(food_pos in self.snakelist):
                print("Reroll",food_pos)
                food_pos = checkForCollision(food_pos)
            print("Prima",food_pos)
            return food_pos

        
        X = random.randrange(0,self.areasize[0]-1)
        Y = random.randrange(0,self.areasize[1]-1)
        food_pos = checkForCollision((X,Y,1))
        print("final", food_pos)
        self.foodlist.append(food_pos)
        self.cubemap[food_pos[0],food_pos[1],1] = IsoCube((food_pos[0],food_pos[1],1),(0,255,255))
        
    def snake(self,direction):
        first_pos = self.snakelist[-1]
        snakelength = len(self.snakelist)
        ## checks of je niet collide met je zelf nog maken
        new_pos = (first_pos[0]+direction[0],first_pos[1]+direction[1],1)
        last_pos = self.snakelist[0]

        if(new_pos in self.snakelist or (new_pos[0] < 0 or new_pos[0] > self.areasize[0] - 1) or (new_pos[1] < 0 or new_pos[1] > self.areasize[1] - 1)):
            self.gamestate = self.GAMEOVER

            return

        if((new_pos[0],new_pos[1],1) in self.foodlist):
            self.snakesize += 1
            self.foodlist.remove((new_pos[0],new_pos[1],1))
            self.cubemap[new_pos[0],new_pos[1],1] = 0
            self.randomfood()


        if(snakelength > self.snakesize):
            self.snakelist.remove(last_pos)
            self.cubemap[last_pos[0],last_pos[1],1] = 0

        self.snakelist.append(new_pos)
        color = (0,0,255) if((new_pos[0] + new_pos[1]) % 2 == 0) else (127,127,255)
        self.cubemap[new_pos[0],new_pos[1],1] = IsoCube(new_pos,(0,0,200))
        self.cubemap[first_pos[0],first_pos[1],1].color = (0,0,255) 
        
        return
    
    def restart(self):
        self.cubemap = np.zeros((self.areasize[0],self.areasize[1],2),dtype=IsoCube)
        self.grid(self.areasize)

        first_pos = (self.areasize[0]//2,self.areasize[1]//2)
        self.snakelist = [first_pos]
        self.cubemap[first_pos[0],first_pos[1],1] = IsoCube((first_pos[0],first_pos[1],1),(0,0,200))
        self.snakesize = 2
        self.foodlist = []
        self.randomfood()

        self.gamestate = self.GAMEPLAYING

        return
    def keyInput(self,key):

        if(key == 255): 
            return
            
        if(key == 101):
            self.snake((0,-1))

        if(key == 100):
            self.snake((1,0))

        if(key == 115):
            self.snake((0,1))

        if(key == 119):
            self.snake((-1,0))

    def wave(self,scroll,ampitude = 16, periode = 1,offset = (0,0)):
        for x in range(len(self.cubemap)):
            for y in range(len(self.cubemap[0])):
                for z in range(len(self.cubemap[0][0])):
                    if(self.cubemap[len(self.cubemap)-1-x,y,z] != 0):
                        self.cubemap[len(self.cubemap)-1-x,y,z].zoffset = mth.sin((x+offset[0])/periode+(y+offset[1])/periode+scroll)*ampitude #- z*self.gridsize

    def play(self):
        canvas = np.zeros((height,width,3), dtype=np.uint8)
        canvas = create_grit(canvas,gridsize,(100,0,0))
        self.grid(self.areasize,0)
        last_input = 255
        gameTimer_start = time.time_ns()//1000000
        gameSpeed = [10,500,5000] #ms
        gameTimeBookmark = [0,0,0]
        gameTimer = 0
        print(gameTimer_start)
        self.gamestate = self.GAMEPLAYING
        self.randomfood()
        i=0
        while(1):
            
            
            if(gameTimer >= gameTimeBookmark[0]):
                new_canvas = canvas.copy()
                k = cv.waitKey(30) & 0xff

                if(k == 122):
                    self.restart()
                    last_input = 255
                last_input = k if (k == 100 or k == 101 or k == 115 or k == 119) else last_input
            
                if(gameTimer >= gameTimeBookmark[1] and self.gamestate == self.GAMEPLAYING):
                    self.keyInput(last_input)
                    gameTimeBookmark[1] += gameSpeed[1]
                self.wave(i,periode=2,ampitude=self.gridsize//2)
                self.draw(new_canvas)
                cv.imshow("Snake",new_canvas)

                if (k == 27):
                    break
                i += 0.1
                gameTimeBookmark[0] += gameSpeed[0]
            gameTimer = time.time_ns()//1000000 - gameTimer_start
            
        return

game = SnakeGame(gridsize,(10,10))

canvas = np.zeros((height,width,3), dtype=np.uint8)
canvas = create_grit(canvas,gridsize,(100,0,0))


game.play()
cv.destroyAllWindows()