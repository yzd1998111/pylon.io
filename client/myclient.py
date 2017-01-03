import math 
import pygame 
from pygame.locals import *
import os 
import sys
import socket
import random
from heapq import * 
import time
import numpy as np
import threading 
from functools import reduce 
from PIL import Image, ImageFilter
sys.path.append("/Users/yuanzhendong/desktop/tp3")
os.chdir("/Users/yuanzhendong/desktop/tp3")
from client.myplayer import *
from queue import Queue 
import string 
import copy
import time 
import ast 
import select 

#### adapted From 15112 ####
def readFile(path):
    with open(path,"rt") as f:
        return f.read()

def writeFile(path,contents):
    with open(path, "wt") as f:
        f.write(contents)   
###########################helper func#################
def fade(word,pos):
    label = bigfont.render(word,True,data.whiteColor)
    nextShow = pygame.Surface(bigfont.size(word))
    nextShow.blit(label,(0,0))
    # blit a new surface to blit word 
    for x in range (0,200,5):
        nextShow.set_alpha(x)
        screen.blit(nextShow, pos)
        pygame.display.flip()
    for x in range (0,200,5):
        screen.fill(data.blackColor)
        nextShow.set_alpha(225-x)
        screen.blit(nextShow,pos)
        pygame.display.flip()

def calTurnRadius(speed,turn):
    # calculate the turn radius 
    diameter=170+speed*10-turn*5
    radi=round(diameter/2)
    return radi
def simplify(degree):
    # simplify degrees 
    while (degree<0):
        degree+=360
    while (degree>360):
        degree-=360
    return degree 
    
def findNewPos(startX,startY,destX,destY,step,solution):
    if ((destX,destY) not in data.map2):
        return (destX,destY)
    else:
         # find new pos if current pos is illegal 
        if (solution==1):
            if (step%2==0):
                findNewPos(startX,startY,destX-5,destY,step+1)
            else:
                findNewPos(startX,startY,destX,destY-5,step+1)
        elif (solution==2):
            if (step%2==0):
                findNewPos(startX,startY,destX-5,destY,step+1)
            else:
                findNewPos(startX,startY,destX,destY+5,step+1)
        elif (solution==3):
            if (step%2==0):
                findNewPos(startX,startY,destX+5,destY,step+1)
            else:
                findNewPos(startX,startY,destX,destY-5,step+1)
        elif (solution==4):
            if (step%2==0):
                findNewPos(startX,startY,destX+5,destY,step+1)
            else:
                findNewPos(startX,startY,destX,destY+5,step+1) 
def resetFont():
    data.color1=data.blackColor
    data.color2=data.blackColor
    data.color3=data.blackColor
    data.color4=data.blackColor
    data.color5=data.blackColor
    data.color6=data.blackColor

def apply(pos):
    return (pos[0]+data.me.offsetX,pos[1]+data.me.offsetY)
    
def rand():
    xpos=random.randint(30,2970)
    ypos=random.randint(30,2970)
    if ((xpos,ypos) not in data.map2):
        return (xpos,ypos)
    else:
        return rand()

def heruistics(curX,curY,endX,endY):
    # mahattan distance 
    xdif=abs(endX-curX)
    ydif=abs(endY-curY)
    dis=(xdif**2+ydif**2)**0.5
    return dis
def conv(degrees):
    return (degrees/180)*math.pi
    
def replace(str1,str2):
    # replace the record 
    with open("record/record.txt","rt") as old:
        oldData=old.read()
        old.close()
    newData=oldData.replace(str1,str2)
    with open("record/record.txt","wt") as new:
        new.write(newData)
        new.close()
       
def callTime(f):
    def timeAndCall(*args,**kwargs):
        # for evaluation of time efficiency 
        start = time.clock()
        result = f(*args, **kwargs)
        end=time.clock()
        curTimesAndTime=data.callTime.get(f,[0,0])
        curTimesAndTime[0]+=end-start
        curTimesAndTime[1]+=1
        data.callTime[f]=curTimesAndTime
        return result
    return timeAndCall
    
def handleServer(server):
    # non blocknig socket 
    server.setblocking(1)
    msg = ""
    realMsg = ""
######### credit to jacky xu 
    while True:
        rlist,xlist,wlist=select.select([server],[],[])
        if (len(rlist)>0):
############
            msg += server.recv(512).decode("UTF-8")
            realMsg = msg.split("\n")
            while (len(realMsg) > 1):
                readyMsg = realMsg[0]
                msg="".join(realMsg[1:])
                serverUpdate(readyMsg)
                realMsg=realMsg[1:]
                    

failure=0
HOST = ""
PORT = 50003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
########################### Game ####################
class node:
    def __init__(self,curX,curY,gval,fval,turn,dir):
        self.curX=curX
        self.curY=curY
        self.gval=gval
        self.fval=fval
        self.turn=turn
        self.dir=dir
    def __lt__(self,other):
        return self.fval<other.fval
    def newfval(self,endX,endY):
        self.fval=self.gval+heruistics(self.curX,self.curY,endX,endY)+self.turn*0.5
    def newgval(self,dir):
        if (dir%2==0): self.gval += 1
        else: self.gval += 1.4
        

class playerShip():
    def __init__(self,name,posX,posY,image):
        self.curveMotion=[]
        self.angle=0
        self.name=name
        self.speed=10
        self.turn=6
        self.Hull=100
        self.recover=1
        self.range=5
        self.dmg=4
        self.reload=2
        self.collision=1
        self.image=pygame.image.load(image)
        self.ramEnabled=False 
        self.newImage=pygame.transform.rotate(self.image,self.angle+90)
        self.equip=[]
        self.level=0
        self.upgrade=0
        self.equips=1
        self.recover=2
        self.collision=3
        self.fleets=0
        self.score=0
        self.coins=0
        self.curSpeed=5
        self.hullLev=0
        self.recoverLev=0
        self.rangeLev=0
        self.dmgLev=0
        self.reloadLev=0
        self.mpos=None
        self.speedLev=0
        self.turnLev=0
        self.collisionLev=0
        (self.posX,self.posY)=posX,posY
        self.sideReady=[True,3,3]
        self.bigReady=[True,4,4]
        self.swivelReady=[True,2,2] 
        self.movingReady=[True,3,3]
        self.mineReady=[True,4,4]
        self.frontReady=[True,4,4]
        self.backReady=[True,4,4]
        self.left,self.right=False,False
        self.destination=None
        self.solutions=[]
        self.elapsed=0
        self.accler=False 
        self.decler=False 
        self.blood=100
        self.offsetX,self.offsetY=620-posX,450-posY
        self.rect1=self.image.get_rect(center=(620,450))
        self.recordSpeed=self.curSpeed
    def upgradeHull(self):
        if (self.coins>=(10+self.hullLev*20) and self.hullLev<data.maxLev and self.upgrade<75):
            self.coins-=10+data.me.hullLev*20
            self.hullLev+=1 
            self.Hull+=30
            self.blood+=30
            self.speed-=0.15
            self.upgrade+=1
    def upgradeSpeed(self):
        if (self.coins>=(10+self.speedLev*20) and self.speedLev<data.maxLev and self.upgrade<75):
            self.coins-=10+data.me.speedLev*20
            self.speedLev+=1 
            self.speed+=0.4
            self.upgrade+=1
    def upgradeRecover(self):
        if (self.coins>=(10+self.recoverLev*20) and self.recoverLev<data.maxLev and self.upgrade<75):
            self.coins-=10+data.me.recoverLev*20
            self.recoverLev+=1 
            self.recover+=2
            self.upgrade+=1
    def upgradeDamage(self):
        if (self.coins>=(10+self.dmgLev*20) and self.dmgLev<data.maxLev and self.upgrade<75):
            self.coins-=10+data.me.dmgLev*20
            self.dmgLev+=1 
            self.dmg+=0.1 
            self.upgrade+=1
    def upgradeReload(self):
        if (self.coins>=(10+self.reloadLev*20) and self.reloadLev<data.maxLev and self.upgrade<75):
            self.coins-=10+data.me.reloadLev*20
            self.reloadLev+=1 
            self.reload*=0.94
            self.upgrade+=1
    def upgradeCollision(self):
        if (self.coins>=(10+self.collisionLev*20) and self.collisionLev<data.maxLev and self.upgrade<75):
            self.coins-=10+data.me.collisionLev*20
            self.collisionLev+=1 
            self.collision+=3
            self.upgrade+=1
    def upgradeRange(self):
        if (self.coins>=(10+self.rangeLev*20) and self.rangeLev<data.maxLev and self.upgrade<75):
            self.coins-=10+data.me.rangeLev*20
            self.rangeLev+=1 
            self.range+=0.4
            self.upgrade+=1
    def upgradeTurn(self):
        if (self.coins>=(10+self.turnLev*20) and self.turnLev<data.maxLev and self.upgrade<75):
            self.coins-=10+data.me.turnLev*20
            self.turnLev+=1 
            self.turn+=0.5
            self.upgrade+=1
    def getExp(self):
        if (self.level==0):
            return round((self.score/500)*100)
        elif (self.level==1):
            return round((self.score-500)/3000*100)
        elif (self.level==2):
            return round((self.score-3000)/6000*100)
        elif (self.level==3):
            return round((self.score-6000)/10000*100)
        elif (self.level==4):
            return round((self.score-10000)/20000*100)
    def addEquip(self,weapon):
        self.equips-=1 
        if (weapon=="sideCannon"):    
            self.equip.append(self.sideReady)
        # elif (weapon=="bigCannon"):  
        #     self.equip.append(self.bigReady)
        # elif (weapon=="swivelCannon"):  
        #     self.equip.append(self.swivelReady)
        elif (weapon=="batteringRam"):
            self.ramEnabled=True 
        elif (weapon=="mineDropper"):  
            self.equip.append(self.mineReady)
        elif (weapon=="frontCannon"):  
            self.equip.append(self.frontReady)
        elif (weapon=="rearCannon"):
            self.equip.append(self.backReady)
        elif (weapon=="movingCannon"):
            self.equip.append(self.movingReady)
    def calDir(self):
        # calculate diretion 
        while (self.angle)<0:
            self.angle+=360
        while (self.angle)>360:
            self.angle-=360 
        if (0<=self.angle<90): return 1 
        elif (90<=self.angle<180): return 2 
        elif (180<=self.angle<270): return 3 
        elif (270<=self.angle<360): return 4 
        
    def updatePos(self):
        # update the player pos and collision detection    
        tempX,tempY,tempAngle=self.posX,self.posY,self.angle
        tempOffX,tempOffY=self.offsetX,self.offsetY
        self.posY-=self.curSpeed*math.sin(conv(self.angle))
        self.posX+=self.curSpeed*math.cos(conv(self.angle))
        flag,collide=True,False  
        
       
        for x in range(-25,25,1):
            for y in range(-25,25,1):
                posX,posY=round(self.posX+y),round(self.posY+x)
                if ((posX,posY) in data.map2):
                    collide=True 
                    flag=False  
                    break 
                    
        if not (39<=self.posY<=2961 and  39<=self.posX<=2961):
            flag=False             
        for eachPlayer in data.players:
            player=data.players[eachPlayer]
            if (heruistics(player.posX,player.posY,data.me.posX,data.me.posY)<=80):
                print(self.name)
                self.blood-=player.collision
                
                flag=False 
        if (flag):
            self.offsetY+=self.curSpeed*math.sin(conv(self.angle))
            self.offsetX-=self.curSpeed*math.cos(conv(self.angle))
        else:
            self.posY=tempY
            self.posX=tempX
            self.curSpeed=4
            self.offsetX,self.offsetY=tempOffX,tempOffY
        if (collide):
            self.blood-=4
    def updateCondition(self):
        self.angle=simplify(self.angle)
        data.scoreDict[self.score]=self.name 
        self.rotatePlayer() 
        
        for coins in data.coinList:
            itsVal=data.val[coins[0]]
            xPos=coins[1]
            yPos=coins[2]
            dist=heruistics(xPos,yPos,self.posX,self.posY)
            if  (dist<=52):
                self.coins+=itsVal
                self.score+=itsVal
                data.coinList.remove(coins)
                        
        for eachEquip in self.equip:
            if (eachEquip[0]==False):
                if (eachEquip[2]+0.8>=(eachEquip[1]*self.reload)):
                    eachEquip[2]=eachEquip[1]*self.reload
                    eachEquip[0]=True 
                else: eachEquip[2]+=0.8 
        if (self.score >=500 and self.level==0):
            self.equips+=1 
            self.level+=1 
        elif (self.score >= 3000 and self.level==1):
            self.equips+=1 
            self.level+=1 
        elif (self.score >= 6000 and self.level==2):
            self.equips+=1 
            self.level+=1 
        elif (self.score >= 10000 and self.level==3):
            self.equips+=1 
            self.level+=1 
        elif (self.score > 20000 and self.level==4):
            self.equips+=1 
            self.level+=1 
        if (self.blood+self.recover>=self.Hull):
            self.blood=self.Hull
        else:
            self.blood+=self.recover
        if (self.accler==True):
            if(self.curSpeed +2 <self.speed):
                self.curSpeed+=2 
            else:
                self.curSpeed=self.speed
        if (self.decler==True):
            if (self.curSpeed-2 >=data.minSpeed):
                self.curSpeed-=2 
            else:
                self.curSpeed=data.minSpeed
        if (self.left==True): 
            self.angle+=self.turn
            
        elif (self.right==True): 
            self.angle-=self.turn  
          
        if (self.blood<=0 and data.readyMsg=="NotReady"):
            self.blood=0
            global failure
            failure+=1 
            data.lose=True 
            
    def drawPlayer(self):
        # draw the player with the image 
        name=myfont.render("%d %s"%(self.upgrade,self.name),True,data.whiteColor)
        left1,Top1=self.posX+data.me.offsetX-40,self.posY+data.me.offsetY+45
        percent=self.blood/self.Hull
        if (percent<0): percent=0
        xName,yName=self.posX+data.me.offsetX-50,self.posY+data.me.offsetY-70
        pygame.draw.rect(screen,data.blackColor,(left1,Top1,60,10),0)
        pygame.draw.rect(screen,(0,255,0),(left1,Top1,60*percent,10),0)
        screen.blit(name,(xName,yName))
        rec=self.newImage.get_rect(center=(self.posX+data.me.offsetX,self.posY+data.me.offsetY))
        leftX=rec[0]
        leftY=rec[1]
        screen.blit(self.newImage,(leftX,leftY))
    
    def rotatePlayer(self):
        # player rotation 
        oldCenter=self.rect1.center
        self.newImage=pygame.transform.rotate(self.image,self.angle+90)
        self.rect1=self.newImage.get_rect()
        self.rect1.center=oldCenter 
        
    def checkShoot(self):
        # check whether the player can shoot 
        if (self.frontReady in self.equip and self.frontReady[0]==True):
            moves=self.range 
            damage=int(self.dmg*10)
            curPosX=self.posX+math.cos(conv(self.angle))*40
            curPosY=self.posY-math.sin(conv(self.angle))*40
            turretDir=conv(self.angle)
            if (data.readyMsg=="Sail"):           
                msg = "Shoot %d %d %d %d %d %s\n"%(curPosX,curPosY,turretDir,moves,damage,name)
                data.server.send(bytes(msg,"UTF-8"))
            bulData=[[curPosX,curPosY],turretDir,moves,damage,name]
            data.bullet.append(bulData)
            self.frontReady[0]=False 
            self.frontReady[2]=0
        
        if (self.backReady in self.equip and self.backReady[0]==True):
            
            moves=self.range 
            damage=int(self.dmg*15)
            curPosX=self.posX+math.cos(conv(180+self.angle))*40
            curPosY=self.posY-math.sin(conv(180+self.angle))*40
            turretDir=conv(180+self.angle)
            if (data.readyMsg=="Sail"):
                msg = "Shoot %d %d %d %d %d %s \n"%(curPosX,curPosY,turretDir,moves,damage,name)
                data.server.send(msg.encode())
            bulData=[[curPosX,curPosY],turretDir,moves,damage,name]
            data.bullet.append(bulData)
            self.backReady[0]=False 
            self.backReady[2]=0
            # if (data.soundEffect==True):
            #     data.cannonSound.play()
        if (self.movingReady in self.equip and self.movingReady[0]==True):
            moves=self.range
            damage=int(self.dmg*10)
            if (self.mpos[0]>620):
                turretDir=math.atan((450-self.mpos[1])/(self.mpos[0]-620))
            elif (self.mpos[0]!=620 and self.mpos[1]!=450):
                turretDir=math.pi+math.atan((450-self.mpos[1])/(self.mpos[0]-620))
            elif (self.mpos[0]==620 and self.mpos[1]==450):
                turretDir=90
            curPosX=self.posX+math.cos(turretDir)*40
            curPosY=self.posY-math.sin(turretDir)*40
            if (data.readyMsg=="Sail"):
                msg = "Shoot %d %d %d %d %d %s \n"%(curPosX,curPosY,turretDir,moves,damage,name)
                data.server.send(msg.encode())
            bulData=[[curPosX,curPosY],turretDir,moves,damage,name]
            data.bullet.append(bulData)
            self.movingReady[0]=False 
            self.movingReady[2]=0
            # if (data.soundEffect==True):
            #     data.cannonSound.play()
    
        if (self.mineReady in self.equip and self.mineReady[0]==True):
            curPosX=self.posX+math.cos(conv(180+self.angle))*40
            curPosY=self.posY-math.sin(conv(180+self.angle))*40
            if (data.gameEntered==True and data.readyMsg=="Sail"):
                msg = "Mine %d %d %s %d\n" %(curPosX,curPosY,self.name,30)
                data.server.send(bytes(msg,"UTF-8"))
            data.mines.append(((curPosX,curPosY),self.name,30))
            self.mineReady[0]=False 
            self.mineReady[2]=0
            
        if (self.sideReady in self.equip and self.sideReady[0]==True):
            moves=self.range
            damage=int(self.dmg*15)        
            curPosX1=self.posX+math.cos(conv(-90+self.angle))*40
            curPosY1=self.posY-math.sin(conv(-90+self.angle))*40
            curPosX2=self.posX+math.cos(conv(90+self.angle))*40
            curPosY2=self.posY-math.sin(conv(90+self.angle))*40
            turretDir1=conv(-90+self.angle)
            turretDir2=conv(90+self.angle)
            if (data.readyMsg=="Sail"):
                msg1 = "Shoot %d %d %d %d %d %s \n"%(curPosX1,curPosY1,turretDir1,moves,damage,name)
                data.server.send(msg1.encode())
                msg2 = "Shoot %d %d %d %d %d %s \n"%(curPosX2,curPosY2,turretDir2,moves,damage,name)
                data.server.send(msg2.encode())
            bulData1=[[curPosX1,curPosY1],turretDir1,moves,damage,name]
            bulData2=[[curPosX2,curPosY2],turretDir2,moves,damage,name]
            data.bullet.append(bulData1)
            data.bullet.append(bulData2)
            self.sideReady[0]=False 
            self.sideReady[2]=0
            if (data.soundEffect==True and data.readyMsg=="NotReady"):
                data.cannonSound.play()
                
    def solveDest(self):
        # the core pathfinding algorithm that is based on two values 
        self.recordSpeed=self.curSpeed 
        solutions={(True,True):4,(True,False):1,(False,True):3,(False,False):2}
        endingX,endingY=self.destination[0],self.destination[1]
        solution=solutions[(endingX>self.posX,endingY>self.posY)]
        self.destination=None 
        if ((endingX,endingY) in data.map2):
            endingX,endingY=findNewPos(self.posX,self.posY,endingX,endingY,solution)
        curQuadrant=self.calDir()
        startX,startY=self.posX,self.posY
        destQuadrant=solutions[(endingX>self.posX,endingY>self.posY)]
        if (endingX==startX and startY>endingY):
            destQuadrant=None
            haveToMoveInDir=90
        elif (endingX==startX and startY<=endingY):
            destQuadrant=None
            haveToMoveInDir=270
        elif (destQuadrant==1):
            haveToMoveInDir=simplify(int(math.atan((-endingY+startY)/(endingX-startX))/(math.pi)*180))
        elif (destQuadrant==2):
            haveToMoveInDir=simplify(180-int(math.atan((-endingY+startY)/(startX-endingX))/(math.pi)*180))
        elif (destQuadrant==3):    
            haveToMoveInDir=simplify(180+int(math.atan((-startY+endingY)/(startX-endingX))/(math.pi)*180))
        elif (destQuadrant==4):    
            haveToMoveInDir=simplify(360-int(math.atan((-startY+endingY)/(endingX-startX))/(math.pi)*180))
        turnRadius=calTurnRadius(self.speedLev,self.turnLev)
        if (abs(self.angle-haveToMoveInDir)>self.turn and heruistics(startX,startY,endingX,endingY)<turnRadius):
            return 
        else:
            if (abs(self.angle-haveToMoveInDir)>self.turn):
                moveOrder=[]
                self.curveMotion=[]
                if(destQuadrant==None and haveToMoveInDir==90 and (self.angle>270 or self.angle<90) ):
                    moveOrder=["counter","clock"]
                elif(destQuadrant==None and haveToMoveInDir==270 and (self.angle>270 or self.angle<90)):
                    moveOrder=["clock","counter"]
                elif (destQuadrant>curQuadrant and (haveToMoveInDir-self.angle)>180):
                    moveOrder=["clock","counter"]
                elif(destQuadrant>curQuadrant and (haveToMoveInDir-self.angle)<=180):
                    moveOrder=["counter","clock"]
                elif(destQuadrant<curQuadrant and (self.angle-haveToMoveInDir)<=180):
                    moveOrder=["clock","counter"]
                elif(destQuadrant<curQuadrant and (self.angle-haveToMoveInDir)>180):
                    moveOrder=["counter","clock"]
                elif(destQuadrant==curQuadrant and self.angle>haveToMoveInDir):
                    moveOrder=["clock","counter"]
                elif(destQuadrant==curQuadrant and self.angle<haveToMoveInDir):
                    moveOrder=["counter","clock"]
                elif(destQuadrant==None and haveToMoveInDir==90 and 0<=self.angle-90<=180):
                    moveOrder=["clock","counter"]
                elif(destQuadrant==None and haveToMoveInDir==270 and 0<=self.angle-90<=180):
                    moveOrder=["counter","clock"]
                for eachDirection in moveOrder:
                    try:
                        result=self.simulateDirection(eachDirection,[(self.posX,self.posY)],self.angle,haveToMoveInDir,[])
                    
                        if (result!=None):
                            self.curveMotion=result
                            break
                        else:
                            continue 
                    except:
                        print(haveToMoveInDir,self.angle)
                if (len(self.curveMotion)==0):
                    return 
            simuX,simuY=startX,startY
            simuCurveMotion=copy.deepcopy(self.curveMotion)
            while (len(simuCurveMotion)>0):
                #implement motion
                angle=simuCurveMotion.pop(0)
                simuX+=math.cos(angle)*self.curSpeed
                simuY+=math.sin(angle)*self.curSpeed
            
            startX,startY=round(600/self.recordSpeed),round(600/self.recordSpeed)
            endX,endY=round((endingX-simuX)/self.recordSpeed)+startX,startY+round((endingY-simuY)/self.recordSpeed)
            if (endX<0 or endY<0):
                endX=50
                endY=80
            self.solutions=list(map(lambda x: (x[0],x[1]),self.astar(startX,startY,endX,endY,data.dirs)))
            
    def simulateDirection(self,eachDirection,curPath,angle,finalDir,angles):
      #simulate collision during turning 
        if (abs(angle-finalDir)<=self.turn):
            angles.append(angle)
            return angles  
        elif (curPath[-1] in data.map2): 
            return None 
        else:
            if (eachDirection=="counter"):
                newPosX=self.posX+math.cos(angle)*self.curSpeed
                newPosY=self.posY+math.sin(angle)*self.curSpeed
                curPath.append((newPosX,newPosY))
                angles.append(angle)
                angle+=self.turn 
                angle=simplify(angle)
                self.simulateDirection(eachDirection,curPath,angle,finalDir,angles)
            else:
                newPosX=self.posX+math.cos(angle)*self.curSpeed
                newPosY=self.posY+math.sin(angle)*self.curSpeed
                curPath.append((newPosX,newPosY))
                angles.append(angle)
                angle=simplify(angle-self.turn) 
                self.simulateDirection(eachDirection,curPath,angle,finalDir,angles)
        return angles   
        
########### this part has credit to http://code.activestate.com/recipes/578919-python-a-pathfinding-with-binary-heap/
    def astar(self,startX,startY,endX,endY,dirs):
        # find the shortest path 
        NumberOfDirs=8
        cellCount=1200/self.recordSpeed
        pixels=math.ceil(cellCount)
        frontier=[[0]*pixels for val in range(pixels)]
        closed=[[0]*pixels for val in range(pixels)]
        motion=[[0]*pixels for val in range(pixels)]
        startNode=node(startX,startY,0,0,0,0)
        startNode.newfval(endX,endY)
        frontier[startY][startX]=startNode.fval
        #either in lower or higher queue
        priorityqueue=[[],[]]
        priority=0
        heappush(priorityqueue[priority],startNode)
        while priorityqueue[priority]:       
            topNode=priorityqueue[priority][0]
            n0=node(topNode.curX,topNode.curY,topNode.gval,topNode.fval,topNode.turn,topNode.dir)
            a,b,curTurn,curDir=n0.curX,n0.curY,topNode.turn,topNode.dir
            heappop(priorityqueue[priority])
            closed[b][a]=1
            frontier[b][a]=0
            if (a == endX and b == endY):
                backList=[]
                while (a!= startX or b!=startY):
                    direction=motion[b][a]
                    backList.append(data.dirs[(direction+4)%8])
                    a+=dirs[direction][0]  # we are moving backwards
                    b+=dirs[direction][1]
                backList.reverse()
                return backList
            for dir in range(NumberOfDirs):
                childX=a+dirs[dir][0]
                childY=b+dirs[dir][1]
                #check legal
                if not (childX<0 or childX>cellCount or childY<0 or childY>cellCount
                    or (childX*self.recordSpeed,childY*self.recordSpeed) in data.map2 or closed[childY][childX]==1):
                    if (dir!=curDir):
                        newTurn=curTurn+1
                    else: newTurn=curTurn
                    childNode=node(childX,childY,n0.gval,n0.fval,newTurn,dir)
                    childNode.newgval(dir)
                    childNode.newfval(endX,endY)
                    if frontier[childY][childX] ==0 : 
                        frontier[childY][childX]=childNode.fval
                        heappush(priorityqueue[priority],childNode)
                        motion[childY][childX]=(dir+4)%8
                    elif frontier[childY][childX]>childNode.fval:
                        # we have a lower fval now,it is better 
                        frontier[childY][childX]=childNode.fval
                        motion[childY][childX]=(dir+4)%8
                        # we must set it to the top in our Priorityqueue
                        while (priorityqueue[priority][0].curX!=childX or 
                                priorityqueue[priority][0].curY!=childY):
                                    # all the others are set to lower priority 
                            heappush(priorityqueue[1-priority],
                                priorityqueue[priority][0])
                            # we take them out and put them at lower priority
                            heappop(priorityqueue[priority])
                        # we get our lower fval node 
                        heappop(priorityqueue[priority])
                        if (len(priorityqueue[priority])>len(
                            priorityqueue[1-priority])):
                            priority=1-priority
                        while (len(priorityqueue[priority])>0):
                            heappush(priorityqueue[1-priority],priorityqueue[priority][0])
                            heappop(priorityqueue[priority])
                        priority=1-priority
                        heappush(priorityqueue[priority],childNode)
        return ""
    def __repr__(self):
        name="player%s %d %d %s"%(self.name,self.posX,self.posY,str(self.image))
        return name
###################################

############# this part has credit to https://gamedevelopment.tutsplus.com/tutorials/finite-state-machines-theory-and-implementation--gamedev-11867
class finiteStateAI(playerShip):
    def __init__(self,name,posX,posY,image,enemy):
        super().__init__(name,posX,posY,image)
        self.state="attack"
        self.name=name
        self.posX=posX
        self.image=pygame.image.load(image)
        self.enemy=enemy
        self.elpsed=0
        self.working=False
    def transToState(self,state):
        self.state=state
    def Update(self):
        self.elpsed+=1 
        self.execute()
    def isStrong(self):
        if (self.upgrade>=self.enemy.upgrade or self.upgrade==75):
            return True   
        else: 
            return False 
       
    def execute(self):
        # execute current state 
        dist=heruistics(data.me.posX,data.me.posY,self.posX,self.posY)
        if (self.state=="attack"):
            if (self.enemy.blood<=30 and self.blood>40):
                self.transToState("escape")        
       
            elif ((self.isStrong() and dist>150) or self.ramEnabled==True):
                self.transToState("chase")
            elif (self.isStrong() and dist<=150):
                self.atk()
                
        elif (self.state=="wander"):
            if (dist):
                self.normal()
            elif (dist<400 and self.isStrong()==False):            
                self.transToState("escape")
            else:            
                self.transToState("attack")
                
        elif (self.state=="chase"):
            if (self.blood<50):
                self.transToState("escape")
            elif (self.ramEnabled==True):
                self.track()
            elif(dist<900):
                self.transToState("attack")
                
        elif (self.state=="escape"):
            if (self.enemy.blood<=50 and self.blood>50):
                self.transToState("attack")
            elif (dist<=500):
                self.findSafe()
            else:
                self.transToState("wander")
            #tracking the player pos and pathfind
    def track(self):
        if (self.elpsed%10==0):
            self.destination=(self.enemy.posX,self.enemy.posY)
    def findSafe(self):
        # find another random safe place 
        if (self.elpsed%10==0): 
            if (self.enemy.posX>=self.posX,self.enemy.posY>=self.posY):
                newLocation=self.findRandLocation(-1,-1)
                self.destination=(self.posX+newLocation[0],self.posY+newLocation[1])
            elif (self.enemy.posX>= self.posX,self.enemy.posY<self.posY):
                newLocation=self.findRandLocation(-1,+1)
                self.destination=(self.posX+newLocation[0],self.posY+newLocation[1])
            elif (self.enemy.posX<self.posX,self.enemy.posY<self.posY):
                newLocation=self.findRandLocation(+1,+1)
                self.destination=(self.posX+newLocation[0],self.posY+newLocation[1])
            elif (self.enemy.posX<self.posX,self.enemy.posY>=self.posY):
                newLocation=self.findRandLocation(+1,-1)
                self.destination=(self.posX+newLocation[0],self.posY+newLocation[1])
        if (self.mineReady in self.equip and self.ready==True):
            self.checkShoot()
            
    def findRandLocation(self,directionX,directionY):
        amplifyX,amplifyY=directionX*random.randint(100,200),directionY*random.randint(100,200)
        if (self.enemy.posX+amplifyX<=20 or self.enemy.posX+amplifyX>=2980 or 
            self.enemy.posY+amplifyY<=20 or self.enemy.posY+amplifyY>=2980 or
            (self.enemy.posX+amplifyX,self.enemy.posY+amplifyY) in data.map2):
            self.findRandLocation(directionX,directionY)
        else: return (amplifyX,amplifyY)
            
    def normal(self):
        # normal coin collecting events 
        if (len(self.solutions)==0):
            min=99999
            for eachCoin in data.coinList:
                dist=heruistics(eachCoin[1],eachCoin[2],self.posX,self.posY)
                if (dist<min):
                    min=dist
                    self.coinToGet=eachCoin
                elif (dist==min and eachCoin[1]>self.coinToGet[2] ):
                    self.coinToGet=eachCoin
                else: pass
            self.destination=(self.coinToGet[1],self.coinToGet[2])
            self.tryUpgrade()
            
            # while (self.equips>0):
            #     weaponList=["frontCannon","mineDropper","rearCannon",
            #     "sideCannon","batteringRam","movingCannon"]
            #     weaponNum=random.randint(0,5)
            #     weapon=weaponList[weaponNum]
            #     if (weapon not in self.equip):
            #         self.addEquip(weapon)
             
    def tryUpgrade(self):
        # try to upgrade 
        if (self.ramEnabled==True):
            self.upgradeCollision()
        if (self.frontReady or self.frontReady or self.sideReady or self.movingReady in self.equip):
            self.upgradeDamage()
            self.upgradeRange()
            self.upgradeReload()
        else: 
            self.upgradeTurn()
            self.upgradeSpeed()
            self.upgradeHull()
            self.upgradeRecover()
        
    def atk(self):
        # avoidBullet 
        if (self.ready==True):
            if (self.movingReady in self.equip):
                pass
            elif (self.sideReady or self.backReady or self.frontReady in self.equip):
                self.checkShoot()
            else:
                pass 
        
            # if (player.mpos[0]>620):
            #     turretDir=math.atan((450-player.mpos[1])/(player.mpos[0]-620))
            # else:
            #     turretDir=math.pi+math.atan((450-player.mpos[1])/(player.mpos[0]-620))
            # curPosX=data.me.posX+math.cos(turretDir)*40
            # curPosY=data.me.posY-math.sin(turretDir)*40
            # bulData=[[curPosX,curPosY],turretDir,moves,damage,name]
            # data.bullet.append(bulData)
            # if ("movingCannon" in player.equip):
            #     moves=player.range
            #     damage=player.dmg
            #     print(player.mpos[0])
            #     if (player.mpos[0]>620):
            #         turretDir=math.atan((450-player.mpos[1])/(player.mpos[0]-620))
            #     else:
            #         turretDir=math.pi+math.atan((450-player.mpos[1])/(player.mpos[0]-620))
            #     curPosX=data.me.posX+math.cos(turretDir)*40
            #     curPosY=data.me.posY-math.sin(turretDir)*40
            #     bulData=[[curPosX,curPosY],turretDir,moves,damage,name]
            #     data.bullet.append(bulData)
   
    
      
#####################################3####
pygame.init()
clock=pygame.time.Clock()
pygame.mixer.init(44100, -16, 2, 4096)
myfont = pygame.font.SysFont("timesnewroman", 34)
myfont1 = pygame.font.SysFont("timesnewroman", 24)  #intiial22
bigfont=pygame.font.SysFont("timesnewroman",52)
screen = pygame.display.set_mode((1240,900),DOUBLEBUF)

class Struct(object): pass
data = Struct()
def init(data):
    data.leftPlayer=""
    data.settingPg=pygame.image.load("images/background.jpg")
    data.settingPg=pygame.transform.scale(data.settingPg,(1240,900))
    data.whiteColor,data.blackColor=(255,255,255),(0,0,0)
    data.drawingWeapon=False 
    data.err=False 
    data.gratitude=pygame.image.load("images/gratitude.jpg").convert()
    data.gratitude=pygame.transform.scale(data.gratitude,(1240,900))
    data.drawWeaponFront,data.drawWeaponSide,data.drawWeaponRear=False,False,False   
    data.upgradeTree={"front":["frontCannon","batteringRam"],
        "side":["sideCannon","movingCannon"],"rear":["mineDropper","rearCannon"]}
    data.frontWeapon=pygame.image.load("images/front.png").convert()
    data.sideWeapon=pygame.image.load("images/side.png").convert()
    data.rearWeapon=pygame.image.load("images/rear.png").convert()
    data.frontWeapon=pygame.transform.scale(data.frontWeapon,(80,80))
    data.sideWeapon=pygame.transform.scale(data.sideWeapon,(80,80))
    data.rearWeapon=pygame.transform.scale(data.rearWeapon,(80,80))
    data.weaponPics={"front":data.frontWeapon,"side":data.sideWeapon,"rear":data.rearWeapon}
    data.yes=False
    data.no=False
    data.chatMsg=""
    data.displayMsg=""
    data.lose=False
    data.start=0 
    data.picGear,data.picDeath,data.picMulti,data.picCredit,data.picInstruction=False,False,False,False,False 
    data.death=pygame.image.load("images/death.png").convert()
    data.black=pygame.image.load("images/black.png").convert_alpha()
    data.gear=pygame.image.load("images/gear.png").convert()
    data.multi=pygame.image.load("images/multi.png").convert()
    data.coin=pygame.image.load("images/coin.png").convert()
    data.instruction=pygame.image.load("images/instruction.png").convert()
    data.death=pygame.transform.scale(data.death,(20,20))
    data.gear=pygame.transform.scale(data.gear,(20,20))
    data.multi=pygame.transform.scale(data.multi,(20,20))
    data.coin=pygame.transform.scale(data.coin,(20,20))
    data.instruction=pygame.transform.scale(data.instruction,(20,20))
    data.credit=False 
    data.settings=False 
    data.blueShip=pygame.image.load("images/ship2.png")
    data.blueShip=pygame.transform.scale(data.blueShip,(190,117))
    data.redShip=pygame.image.load("images/ship1.png")
    data.redShip=pygame.transform.scale(data.redShip,(190,117))
    data.greenShip=pygame.image.load("images/ship0.png")
    data.greenShip=pygame.transform.scale(data.greenShip,(190,117))
    data.orangeShip=pygame.image.load("images/ship4.png")
    data.orangeShip=pygame.transform.scale(data.orangeShip,(190,117))
    data.purpleShip=pygame.image.load("images/ship3.png")
    data.purpleShip=pygame.transform.scale(data.purpleShip,(190,117))
    data.enterMsg=False 
    data.scoreDict=dict()
    data.server=server
    data.gameChat=False 
    data.lobby=False 
    data.callTime=dict()
    data.color=1
    data.shipImages=[]
    data.processedShips=[]
    data.cannonSound=pygame.mixer.Sound("audio/cannon.ogg")
    data.swivelSound=pygame.mixer.Sound("audio/swivel.ogg")
    data.soundEffect=True 
    data.music=True 
    data.pathFinding=False
    data.nameDefault=False 
    data.colorDefault=False 
    # a given name and color here 
    data.readyMsg="NotReady"
    data.instructPg=True 
    data.readyDict=dict()
    data.content=readFile("record/record.txt")
    data.map=[[0]*100 for val in range(100)]
    data.map2=set()
    data.front=False 
    data.loading=True 
    data.gameEntered=False 
    data.time=0
    data.coinList=[]
    data.numOfPlayers=1
    data.maxLev=14
    data.players=dict()
    # data.Sound=pygame.mixer.Sound("audio/song1.ogg")
    data.imageCoord=[]
    data.images=[]
    data.newImages=[]
    data.mines=[]
    data.lobby=False     
    data.dirs=[(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(+1,-1)]  
    data.angleList=[0,315,270,225,180,135,90,45] 
    data.minSpeed=0
    data.color1=data.blackColor
    data.color2=data.blackColor
    data.color3=data.blackColor
    data.color4=data.blackColor
    data.color5=data.blackColor
    data.color6=data.blackColor
    data.verticesList=[]
    data.val=[10,20,30,50,100,500]
    data.colorDict={10:(220,220,220),20:(255,128,0),30:(255,255,102),
            50:(255,0,0),100:(135,206,250),500:(0,255,0)}
    data.locations=[(500,1000),(100,1500),(1500,2000),(2500,1000)]
    data.bullet=[]
    data.vertices=[]
    data.level=None 
    data.list1=[]
    data.bar= pygame.Surface((200,20))  
    data.bar.set_alpha(70)                
    data.bar.fill(data.blackColor) 
    data.bar2= pygame.Surface((110,20))  
    data.bar2.set_alpha(70)                
    data.bar2.fill(data.blackColor) 
    data.bar3= pygame.Surface((300,20))  
    data.bar3.set_alpha(70)                
    data.bar3.fill(data.blackColor) 
   
    try:
        if ("defaultName=None" in data.content):
            data.nameMsg="" 
        else:
            for eachLine in data.content.splitlines():
                if ("defaultName" in eachLine):
                    try:
                        data.nameMsg=eachLine[13:]
                        break
                    except:
                        print("empty string")
    except:
        data.nameMsg=""
    try:
        if ("defaultColor=None" in data.content):
            data.color=0 
        else:
            for eachLine in data.content.splitlines():
                if ("defaultColor" in eachLine):
                    try: 
                        data.color=int(eachLine[-1])
                        break
                    except:
                        print("empty color")
    except:
        data.color=0
    def listImages(path):
        for each in os.listdir(path):
            if (each.startswith("ship") and "processed" not in each):
                newpath1=path+"/"+each
                data.shipImages.append(newpath1)
            elif (each.startswith("land") and "processed" not in each):
                newpath2=path+"/"+each
                data.images.append(newpath2)
    listImages("images")
    
    def imageProcessing():
        #process image by pixels 
        R_NEW, G_NEW, B_NEW = (210, 180, 140)
        for ships in data.shipImages:
            ship=Image.open(ships)
            newWidth=100
            newHeight=int(newWidth/ship.size[0]*ship.size[1])
            ship=ship.resize((newWidth,newHeight),Image.ANTIALIAS)
            shipPixel=ship.load()
            R_OLD,G_OLD,B_OLD = shipPixel[1,1][0],shipPixel[1,1][1],shipPixel[1,1][2]
            for xPix in range(newWidth):
                for yPix in range(newHeight):
                    r,g,b,a = shipPixel[xPix,yPix]              
                    if (R_OLD<=r<= R_OLD or G_OLD<=g<= G_OLD or B_OLD<=b<= B_OLD):                        
                        shipPixel[xPix, yPix]= (r,g,b,0)
                    else:                      
                        shipPixel[xPix, yPix] = (r,g,b,a)
            newImage1=ships[:-4]+"processed.png"
            ship.save(newImage1)
            data.processedShips.append(newImage1)
    
        for eachImage in data.images: 
            im = Image.open(eachImage)
            # newWidth=random.randint(300,500)
            newWidth=300
            newHeight=int(newWidth/im.size[0]*im.size[1])
            im = im.resize((newWidth,newHeight), Image.ANTIALIAS)
            pixels = im.load()        
          
            R_OLD, G_OLD, B_OLD = pixels[1,1][0],pixels[1,1][1],pixels[1,1][2]
            aList=[[0]* newHeight for val in range(newWidth)]
            for xPixel in range(newWidth):
                for yPixel in range(newHeight):
                    r,g,b,a = pixels[xPixel,yPixel]    
                    if (r,g,b) != (R_OLD, G_OLD, B_OLD):
                        aList[xPixel][yPixel]=1
                        pixels[xPixel, yPixel] = (R_NEW, G_NEW, B_NEW,a)
                    else:                      
                        aList[xPixel][yPixel]=0 
                        pixels[xPixel, yPixel]= (R_OLD, G_OLD, B_OLD,0)
            data.imageCoord.append(aList)
            newImage2=eachImage[:-4]+"processed.png"
            im.save(newImage2)
            data.newImages.append(newImage2)
    imageProcessing()
    def pygameProcessing():
        # further processing through changing the location and size 
        for imageIndex in range(len(data.newImages)):
            eachImage=data.newImages[imageIndex]
            # location=(random.randint(510,2490),random.randint(510,2490))
            location=data.locations[imageIndex]
            imageCoords=data.imageCoord[imageIndex]
            for row in range(len(imageCoords)):
                for col in range(len(imageCoords[0])):
                    if (imageCoords[row][col]==0):
                        pass
                    else:
                        xPix,yPix=location[0]+row,location[1]+col
                        data.map[round(xPix/30)][round(yPix/30)]=1
                        data.map2.add((xPix,yPix))         
            realImage=pygame.image.load(eachImage).convert_alpha()
            eachImage=(realImage,location)
            data.newImages[imageIndex]=eachImage
    pygameProcessing()
    data.logo8=pygame.image.load("logo2/008.png").convert_alpha()
    data.logo8=pygame.transform.scale(data.logo8,(720,150))
    data.logo9=pygame.image.load("logo2/009.png").convert_alpha()
    data.logo9=pygame.transform.scale(data.logo9,(745,166))
    data.logo10=pygame.image.load("logo2/010.png").convert_alpha()
    data.logo10=pygame.transform.scale(data.logo10,(761,175))
    data.back=pygame.image.load("images/back.png").convert()
    data.back=pygame.transform.scale(data.back,(50,50))
    def newLife():
        xPos,yPos=random.randint(500,2500),random.randint(500,2500)
        flag=True 
        for x in range(-31,31):
            for y in range(-31,31):
                if ((xPos+x,yPos+y) in data.map2):
                    flag=False 
                    return newLife()
        else: 
            data.me=playerShip("Kosbie",xPos,yPos,data.processedShips[data.color])
    newLife()
    def newAI():
        xPos,yPos=data.me.posX+200,data.me.posY+200
        flag=True 
        for x in range(-31,31):
            for y in range(-31,31):
                if ((xPos+x,yPos+y) in data.map2):
                    flag=False 
                    return newAI()
        else:
            return finiteStateAI("cold",xPos,yPos,data.processedShips[(data.color+1)%5],data.me)
          
    data.newAI=newAI()
    data.newAI.addEquip("batteringRam")
    data.newAI.speed=8
    data.newAI.curSpeed=8
    data.newAI.collision=20
    data.newAI.Hull=1000
    data.newAI.blood=1000
    data.snowList=[]
    data.elapsed=0 
    data.me.addEquip("frontCannon")
init(data)

def coinGenerator():
    curCoinCount=len(data.coinList)
    maxCoinCount=160
    lack=160-curCoinCount   
    for eachLack in range(lack):
        randCoin=random.randint(0,100)
        pos=rand()
        if (randCoin<35): type=0
        elif (randCoin<=60): type=1
        elif (randCoin<=75): type=2
        elif (randCoin<=90): type=3
        elif (randCoin<=98): type=4
        else: type=5       
        coinInfo=(type,pos[0],pos[1],random.randint(30,2970))
        data.coinList.append(coinInfo)
        
def drawFront():
    if (data.front==True):  
        errMsg=""
        global failure 
        if (data.err==True):
            errMsg = "Sorry,you have no friend"
           
        if (failure==0): 
            blitPlace=(550,200)
            frontMsg="pylon.io"
        else: 
            blitPlace=(435,200)
            frontMsg="Set Sail Again, Warrior!"
        screen.fill(data.whiteColor)
        drawSnow()
        drawBox()
        errLabel=myfont.render(errMsg,True,data.blackColor)
        screen.blit(errLabel,(490,400))
        mainLabel=bigfont.render(frontMsg,True,data.blackColor)
        Label1=myfont.render("Single Player",True,data.color1)
        Label2=myfont.render("Multiplayer Player",True,data.color2)
        Label3=myfont.render("Death Match",True,data.color3)
        Label4=myfont.render("Instructions",True,data.color4)
        Label5=myfont.render("Credit",True,data.color5)
        Label6=myfont.render("Settings",True,data.color6)
        screen.blit(data.back,(1100,20))
        screen.blit(mainLabel,blitPlace)
        screen.blit(Label1,(510,500))
        screen.blit(Label2,(510,550))
        screen.blit(Label3,(510,600))
        screen.blit(Label4,(510,650))
        screen.blit(Label5,(510,700))
        screen.blit(Label6,(510,750))
        if (data.picGear==True): screen.blit(data.gear,(615,755))
        elif (data.picDeath==True): screen.blit(data.death,(665,602))
        elif (data.picMulti==True): screen.blit(data.multi,(730,550))
        elif (data.picCredit==True): screen.blit(data.coin,(585,700))
        elif (data.picInstruction==True): screen.blit(data.instruction,(665,650))
        
def drawSnow():
    if (len(data.snowList)==0):
        # create random circle in random directions 
        data.snowList=[
        (random.randint(1,1200),random.randint(1,1000),
        random.randint(-1,1),2,random.randint(6,8),
        (random.randint(0,255),random.randint(0,255),random.randint(0,255))) 
            for each in range(40)]
        
    while (len(data.snowList)<40):
        # once a snow fall to ground 
        color=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        data.snowList.append((random.randint(1,1200),random.randint(1,1000),
        random.randint(-1,1),4,random.randint(6,8),color)) 
                  
    
    data.snowList=list(map(lambda x:(x[0]+x[2],x[1]+x[3],x[2],x[3],x[4],x[5]),
            data.snowList))
    data.snowList=list(filter(lambda x: x[0]>10 and x[0]<1240
            and x[1]>0 and x[1]<900,data.snowList))
            
    for eachCircle in data.snowList:
        pygame.draw.circle(screen,eachCircle[5],(eachCircle[0],
                eachCircle[1]),eachCircle[4],0)

def drawBox():
    # draw user name box 
    pygame.draw.rect(screen,(220,220,220),[290,550,200,27],0)
    nameTag=myfont.render("%s" % data.nameMsg,True,data.blackColor)
    userName=myfont.render("UserName:",True,data.blackColor)
    screen.blit(nameTag,(300,550))
    screen.blit(userName,(155,550))
    
def drawChatBox():
    # draw chatting message 
    pygame.draw.rect(screen,data.whiteColor,[190,850,500,20],0)
    chat=myfont1.render("%s"%data.chatMsg,True,data.blackColor)
    screen.blit(chat,(200,850))
    
def drawInstruct():  
# player insturction page again 
    if ("first=True" in data.content):
        if (data.start==0):
            fade("Hi",(600,450))
            fade("Welcome to pylon.io",(440,450))
            fade("This is an instruction to get you familiar with this game",(130,450))
            fade("Use the arrowKey to control the direction",(280,450))
            fade("Collect coins for upgrades",(360,450))
            fade("Get score to level up and get more weapons",(280,450))
            data.start+=1 
        mouse=pygame.mouse.get_pos()
        if (data.yes==True ):
            screen.blit(data.logo9,(270,365))
            pygame.display.update()
        elif (data.no==True):
            screen.blit(data.logo10,(258,360))
            pygame.display.update()
        else:
            screen.blit(data.logo8,(283,370))
            pygame.display.update()
    else:
        data.instructPg=False
        data.front=True 
        
def getKeyPress(event):
    player=data.me
    tempPos=data.me.posX,data.me.posY
    tempAngle=data.me.angle 
    if (data.front==True and data.enterMsg==True):
        if (event.type==pygame.KEYDOWN):
            if (event.key==K_BACKSPACE):
                data.nameMsg=data.nameMsg[:-1]
            elif (pygame.key.name(event.key) in string.printable):
                data.nameMsg+=pygame.key.name(event.key)
            elif (event.key==K_SPACE):
                data.nameMsg+=" "
    if (data.gameEntered==True and event.type==pygame.KEYDOWN):
        data.me.solutions=[]
        if (data.gameChat==True):
            if (event.key==K_BACKSPACE):
                data.chatMsg=data.chatMsg[:-1]
            elif (pygame.key.name(event.key) in string.printable):
                data.chatMsg+=pygame.key.name(event.key)
            elif (event.key==K_SPACE):
                data.chatMsg+=" "
            elif (event.key ==K_RETURN and data.gameChat==True):
              
                if (data.chatMsg!=""):
                    msg="chat"+" "+data.chatMsg+"\n"
                    data.server.send(bytes(msg,"UTF-8"))
                 
                    data.chatMsg=""
                data.gameChat=False
        else:
            if (event.key ==K_ESCAPE): 
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "leave\n" 
                    data.server.send(bytes(msg,"UTF-8"))     
                sys.exit(0)
            elif (event.key ==K_r):
                init(data)
                data.readyMsg="NotReady" 
            elif (data.readyMsg=="Sail" and event.key ==K_RETURN and data.gameChat==False):
                data.gameChat=True 
           
            elif (event.key ==K_LEFT and data.lose==False):
                data.me.destination=None 
                data.me.left=True 
                data.me.right=False             
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "Start Left\n" 
                    data.server.send(bytes(msg,"UTF-8"))                
            elif (event.key ==K_RIGHT and data.lose==False):
                data.me.destination=None 
                data.me.right=True 
                data.me.left=False 
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "Start Right\n" 
                    data.server.send(bytes(msg,"UTF-8"))                
            elif (event.key ==K_UP and data.lose==False):
                data.me.destination=None 
                data.me.accler=True 
                data.me.decler=False 
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "Start Acc\n" 
                    data.server.send(bytes(msg,"UTF-8"))           
            elif (event.key ==K_DOWN and data.lose==False):
                data.me.destination=None 
                data.me.decler=True 
                data.me.accler=False 
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "Start Dec\n" 
                    data.server.send(bytes(msg,"UTF-8"))
                    data.me.decler=True 
                    data.me.accler=False
            elif (event.key ==K_SPACE and data.lose==False):
                data.me.checkShoot()
            elif (event.key ==K_1 and data.lose==False):
                player.upgradeHull()
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "Upgrade Hull\n" 
                    data.server.send(bytes(msg,"UTF-8"))                
            elif (event.key ==K_2 and data.lose==False):
                player.upgradeRecover()
             
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "Upgrade Recover\n" 
                    data.server.send(bytes(msg,"UTF-8"))
            elif (event.key ==K_3 and data.lose==False):               
                player.upgradeRange()
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "Upgrade Range\n" 
                    data.server.send(bytes(msg,"UTF-8"))
                
            elif (event.key ==K_4 and data.lose==False):
                player.upgradeDamage()
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "Upgrade Damage\n" 
                    data.server.send(bytes(msg,"UTF-8"))
            
            elif (event.key ==K_5 and data.lose==False):    
                player.upgradeReload()
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "Upgrade Reload\n" 
                    data.server.send(bytes(msg,"UTF-8"))
            
            elif (event.key ==K_6 and data.lose==False):
                player.upgradeSpeed()
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "Upgrade Speed\n" 
                    data.server.send(bytes(msg,"UTF-8"))
                
            elif (event.key ==K_7 and data.lose==False):                
                player.upgradeTurn()
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "Upgrade Turn\n" 
                    data.server.send(bytes(msg,"UTF-8"))
                
            elif (event.key ==K_8 and data.lose==False):                
                player.upgradeCollision()
                if (data.gameEntered==True and data.readyMsg=="Sail"):
                    msg = "Upgrade Collision\n" 
                    data.server.send(bytes(msg,"UTF-8"))
        
    if (event.type==pygame.KEYUP):
        if (event.key == K_LEFT):            
            if (data.gameEntered==True and data.readyMsg=="Sail" and data.lose==False):
                msg = "Stop Left\n"
                data.server.send(bytes(msg,"UTF-8"))    
            data.me.left=False  
        elif (event.key ==K_RIGHT):            
            if (data.gameEntered==True and data.readyMsg=="Sail" and data.lose==False):
                msg = "Stop Right\n"
                data.server.send(bytes(msg,"UTF-8"))    
            data.me.right=False  
        elif (event.key ==K_UP):           
            if (data.gameEntered==True and data.readyMsg=="Sail" and data.lose==False):
                msg = "Stop Acc\n"
                data.server.send(bytes(msg,"UTF-8"))  
            data.me.accler=False 
        elif (event.key ==K_DOWN): 
            if (data.gameEntered==True and data.readyMsg=="Sail" and data.lose==False):
                msg = "Stop Dec\n"
                data.server.send(bytes(msg,"UTF-8"))
            data.me.decler=False 
        
def getMousePress(event):
    mpos=pygame.mouse.get_pos()
    cursorX,cursorY=mpos[0],mpos[1]
    if (data.front==True):
        if (cursorX>=510 and cursorX<=730 and cursorY>475 and cursorY<=525):
            resetFont()
            data.color1=(0,0,255)
            data.picGear,data.picDeath,data.picMulti,data.picCredit,data.picInstruction=False,False,False,False,False
        elif (cursorX>=510 and cursorX<=810 and cursorY>525 and cursorY<=575):
            resetFont()
            data.color2=(0,0,255)
            data.picGear,data.picDeath,data.picMulti,data.picCredit,data.picInstruction=False,False,True ,False,False      
        elif (cursorX>=510 and cursorX<=670 and cursorY>=575 and cursorY<=625):
            resetFont()
            data.picGear,data.picDeath,data.picMulti,data.picCredit,data.picInstruction=False,True,False,False,False
            data.color3=(0,0,255)
        elif (cursorX>=510 and cursorX<=710 and cursorY>=625 and cursorY<=675):
            data.picGear,data.picDeath,data.picMulti,data.picCredit,data.picInstruction=False,False,False,False,True
            resetFont()
            data.color4=(0,0,255)
        elif (cursorX>=510 and cursorX<=610 and cursorY>=675 and cursorY<=725):
            data.picGear,data.picDeath,data.picMulti,data.picCredit,data.picInstruction=False,False,False,True,False
            resetFont()
            data.color5=(0,0,255)
        elif (cursorX>=510 and cursorX<=670 and cursorY>= 725 and cursorY<775):
            resetFont()
            data.picGear,data.picDeath,data.picMulti,data.picCredit,data.picInstruction=True,False,False,False,False
            data.color6=(0,0,255)
        else:
            data.picGear,data.picDeath,data.picMulti,data.picCredit,data.picInstruction=False,False,False,False,False
            resetFont()
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1 and cursorX>=510 and cursorX<=730 and cursorY>475 and cursorY<=525):
           
            data.players[0]=data.newAI
            data.pathFinding=True 
            data.gameEntered=True 
            if (data.nameMsg!=""):
                data.me.name=data.nameMsg 
            data.front=False
        if( event.type == pygame.MOUSEBUTTONDOWN and event.button==1 
            and cursorX>=295 and cursorX<=495 and cursorY>550 and cursorY<=577):
            data.enterMsg=True 
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1 
            and cursorX>=510 and cursorX<=810 and cursorY>525 and cursorY<=575):
            if (data.nameMsg!=""):
                data.me.name=data.nameMsg 
            try:
               
                server.connect((HOST,PORT))
                threading.Thread(target = handleServer, args = (server,)).start()
                msg="readyState %s\n"%data.readyMsg
                data.server.send(bytes(msg,"UTF-8"))
                data.front=False 
                data.lobby=True
                data.pathFinding=False  
                end=True
            except:
                data.err=True
               
               
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1
            and 1100<cursorX<1150 and 20<cursorY<70):
            sys.exit(0)
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1): 
            if (cursorX>=510 and cursorX<=580 and cursorY>675 and cursorY<=725):
                data.front=False   
                data.credit=True     
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1):
            if(cursorX>=510 and cursorX<=650 and cursorY>725 and cursorY<=775):               
                data.front=False 
                data.settings=True      
 
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1 ):
            if (cursorX>=510 and cursorX<=650 and cursorY>650 and cursorY<=670):
                replace("first=False","first=True")
                data.content=readFile("record/record.txt")
                data.front=False
                data.start=0
                data.instructPg=True
                
                
    elif (data.lobby==True):
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1
            and 520<cursorX<700 and 700<cursorY<765):
            data.readyMsg="Sail" if data.readyMsg=="NotReady" else "NotReady"
            msg="readyState %s\n"%data.readyMsg
            data.server.send(bytes(msg,"UTF-8"))
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1
            and 920<cursorX<1070 and 50<cursorY<130):
            data.lobby=False 
            data.front=True 
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1):
            if (1100<cursorX<1150 and 20<cursorY<70):
                data.front=True 
                data.lobby=False 
    elif (data.credit==True):
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1
            and 920<cursorX<1070 and 50<cursorY<130):
            data.credit=False 
            data.front=True 
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1):
            if (1100<cursorX<1150 and 20<cursorY<70):
                data.front=True 
                data.credit=False 
        elif (data.drawWeaponSide==True):
            count=0
            weaponRemain=data.upgradeTree["side"]
            for each in weaponRemain:
                msg=myfont.render(each,True,data.whiteColor)
                pos=(530,770-count*30)
                screen.blit(msg,pos)
                count+=1
        elif (data.drawWeaponRear==True):
            count=0
            weaponRemain=data.upgradeTree["rear"]
            for each in weaponRemain:
                msg=myfont.render(each,True,data.whiteColor)
                pos=(670,770-count*30)
                screen.blit(msg,pos)
    elif (data.gameEntered==True):
        data.me.mpos=pygame.mouse.get_pos()
        if (data.drawingWeapon==True):            
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1 and data.lose==False):                
                if (400<cursorX<480 and 770<cursorY<790):
                    addweapon=data.upgradeTree["front"][0]
                    data.upgradeTree["front"].remove(addweapon)
                    data.me.addEquip(addweapon)
                if (400<cursorX<480 and 740<cursorY<760 and len(data.upgradeTree["front"])==2):
                    addweapon=data.upgradeTree["front"][1]
                    data.upgradeTree["front"].remove(addweapon)
                    data.me.addEquip(addweapon)
                if (540<cursorX<620 and 770<cursorY<790):
                    addweapon=data.upgradeTree["side"][0]
                    data.upgradeTree["side"].remove(addweapon)
                    data.me.addEquip(addweapon)
                if (540<cursorX<620 and 740<cursorY<760 and len(data.upgradeTree["side"])==2):
                    addweapon=data.upgradeTree["side"][1]
                    data.upgradeTree["side"].remove(addweapon)
                    data.me.addEquip(addweapon)
                if (680<cursorX<760 and 770<cursorY<790):
                    addweapon=data.upgradeTree["rear"][0]
                    data.upgradeTree["rear"].remove(addweapon)
                    data.me.addEquip(addweapon)
                if (680<cursorX<760 and 740<cursorY<760 and len(data.upgradeTree["rear"])==2):
                    addweapon=data.upgradeTree["rear"][1]
                    data.upgradeTree["rear"].remove(addweapon)
                    data.me.addEquip(addweapon)
                    
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==3 and data.lose==False):
            dest=pygame.mouse.get_pos()
            destX=round(data.me.posX+dest[0]-620)
            destY=round(data.me.posY+dest[1]-450)
            data.me.destination=(destX,destY)
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1 and data.lose==False):
            data.me.checkShoot()
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1 and data.lose==False and data.me.equips>0):
            if (400<cursorX<480 and 800<cursorY<880 and "front" in data.upgradeTree):
                data.drawingWeapon=True 
                data.drawWeaponFront,data.drawWeaponSide,data.drawWeaponRear=True,False,False  
            elif (540<cursorX<620 and 800<cursorY<880 and "side" in data.upgradeTree):
                data.drawingWeapon=True 
                data.drawWeaponFront,data.drawWeaponSide,data.drawWeaponRear=False,True,False 
            elif (680<cursorX<760 and 800<cursorY<880 and "rear" in data.upgradeTree):
                data.drawingWeapon=True 
                data.drawWeaponFront,data.drawWeaponSide,data.drawWeaponRear=False,False,True  
            else: 
                data.drawWeaponFront,data.drawWeaponSide,data.drawWeaponRear=False,False,False    
    elif (data.instructPg==True):
        if (440<=cursorX<=540 and 480<=cursorY<=500):
            data.yes=True
            data.no=False
        elif (700<=cursorX<=770 and 480<=cursorY<=500):
            data.no=True
            data.yes=False
        else:
            data.no,data.yes=False,False 
            
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 440<=cursorX<=540 and 480<=cursorY<=500):
            replace("first=True","first=False")
            data.content=readFile("record/record.txt")
            data.instructPg=False
            data.front=True 
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 700<=cursorX<=770 and 480<=cursorY<=500):
            data.front=False 
            data.instructPg==True
            data.start=0
            drawInstruct()
    elif (data.settings==True):
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button==1):
            if (1100<cursorX<1150 and 20<cursorY<70):
                data.front=True 
                data.settings=False 
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 140<=cursorX<=160 and 260<=cursorY<=280):
            data.color=0
            data.me.image=pygame.image.load(data.processedShips[data.color]) 
            data.me.newImage=pygame.transform.rotate(data.me.image,90)
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 370<=cursorX<=390 and 260<=cursorY<=280):
            data.color=1
            data.me.image=pygame.image.load(data.processedShips[data.color]) 
            data.me.newImage=pygame.transform.rotate(data.me.image,90)
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 600<=cursorX<=620 and 260<=cursorY<=280):
            data.color=2
            data.me.image=pygame.image.load(data.processedShips[data.color]) 
            data.me.newImage=pygame.transform.rotate(data.me.image,90)
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 830<=cursorX<=850 and 260<=cursorY<=280):
            data.color=3
            data.me.image=pygame.image.load(data.processedShips[data.color]) 
            data.me.newImage=pygame.transform.rotate(data.me.image,90)
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 1060<=cursorX<=1080 and 260<=cursorY<=280):
            data.color=4
            data.me.image=pygame.image.load(data.processedShips[data.color]) 
            data.me.newImage=pygame.transform.rotate(data.me.image,90)
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 950<=cursorX<=970 and 550<=cursorY<=570):
            data.soundEffect=True
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 950<=cursorX<=970 and 600<=cursorY<=620):
            data.music=True 
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 950<=cursorX<=970 and 650<=cursorY<=670):
            data.pathFinding=True 
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 950<=cursorX<=970 and 700<=cursorY<=720):
            data.nameDefault=True  
            oldMsg,newMsg="defaultName=None","defaultName=%s"%data.nameMsg
            replace(oldMsg,newMsg)
            data.content=readFile("record/record.txt")
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 950<=cursorX<=970 and 750<=cursorY<=770):
            data.colorDefault=True  
            oldMsg,newMsg="defaultColor=None","defaultColor=%d"%data.color
            replace(oldMsg,newMsg)
            data.content=readFile("record/record.txt")
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 1100<=cursorX<=1120 and 550<=cursorY<=570):
            data.soundEffect=False
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 1100<=cursorX<=1120 and 600<=cursorY<=620):
            data.music=False  
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 1100<=cursorX<=1120 and 650<=cursorY<=670):
            data.pathFinding=False 
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 1100<=cursorX<=1120 and 700<=cursorY<=720):
            data.nameDefault=False 
            oldMsg,newMsg="defaultName=%s"%data.nameMsg,"defaultName=None"
            replace(oldMsg,newMsg)
            data.content=readFile("record/record.txt")
        if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
            and 1100<=cursorX<=1120 and 750<=cursorY<=770):
            data.colorDefault=False 
            oldMsg,newMsg="defaultColor=%d"%data.color,"defaultColor=None"
            replace(oldMsg,newMsg)
            data.content=readFile("record/record.txt")
            
def drawBoard():
    for y in range (100):
        for x in range(100):
            leftX,leftY=30*x+data.me.offsetX,30*y+data.me.offsetY
            pygame.draw.rect(screen,(102,108,115),[leftX,leftY,30,30],1)
    screen.blit(data.bar,(30,68))   
    screen.blit(data.bar,(30,98))    
    screen.blit(data.bar,(30,128))    
    screen.blit(data.bar,(30,158))    
    screen.blit(data.bar,(30,188))    
    screen.blit(data.bar,(30,218))    
    screen.blit(data.bar,(30,248))    
    screen.blit(data.bar,(30,278))     
    screen.blit(data.bar,(30,338))    
    screen.blit(data.bar,(30,368))  
    screen.blit(data.bar,(30,398))   
    screen.blit(data.bar,(30,428))      
    screen.blit(data.bar2,(30,828))   
    

    # if (len(data.equipments)!=0):
    #     for each in 
    #         draweaweaweasd
    # data.list1.append((int(data.me.posX),int(data.me.posY)))
    # for each in data.list1:
    #     pygame.draw.circle(screen,(255,0,0),(each),3,0)
    
def drawcoin():
    for each in data.coinList:
        xPos=round(each[1]+data.me.offsetX)
        yPos=round(each[2]+data.me.offsetY)
        type=data.val[each[0]]
        color=data.colorDict[type]
        if (color==(220,220,220) or color==(255,255,102) or color==(255,128,0)):
            pygame.draw.circle(screen,color,(xPos,yPos),11,0)
        else:
            pointList=[(xPos-13,yPos),(xPos,yPos+16),(xPos+13,yPos),(xPos,yPos-16)]
            pygame.draw.polygon(screen,color,pointList,0)

def drawTexts():
    LabelCoin=myfont1.render("coins ",True,data.whiteColor)
    LabelUpgrades=myfont1.render("Upgrades %d/75"%data.me.upgrade,True,data.whiteColor)
    Label1=myfont1.render("Hull Strength%19s"%"1",True,data.whiteColor)
    Label2=myfont1.render("Auto Repairs%19s"%"2",True,data.whiteColor)
    Label3=myfont1.render("Cannon Range%16s"%"3",True,data.whiteColor)
    Label4=myfont1.render("Cannon Damage%13s"%"4",True,data.whiteColor)
    Label5=myfont1.render("Reload Speed%18s"%"5",True,data.whiteColor)
    Label6=myfont1.render("Move Speed%21s"%"6",True,data.whiteColor)
    Label7=myfont1.render("Turn Speed%23s"%"7",True,data.whiteColor)
    Label8=myfont1.render("Ram Damage%19s"%"8",True,data.whiteColor)
    Label9=myfont1.render("Fleet %d/3"%data.me.fleets,True,data.whiteColor)
    Label10=myfont1.render("Fishing Boat%20s"%"9",True,data.whiteColor)
    Label11=myfont1.render("Mine Dropper%19s"%"0",True,data.whiteColor)
    Label12=myfont1.render("BattleShip%23s"%"T",True,data.whiteColor)
    Label13=myfont1.render("Man of War%22s"%"Y",True,data.whiteColor)
    Label14=myfont1.render("Score %d"%data.me.score,True,data.whiteColor)
    Label15=myfont1.render("$ %d" %(10+20*data.me.hullLev),True,(220,220,220))
    Label16=myfont1.render("$ %d" %(10+20*data.me.recoverLev),True,(220,220,220))
    Label17=myfont1.render("$ %d" %(10+20*data.me.rangeLev),True,(220,220,220))
    Label18=myfont1.render("$ %d" %(10+20*data.me.dmgLev),True,(220,220,220))
    Label19=myfont1.render("$ %d" %(10+20*data.me.reloadLev),True,(220,220,220))
    Label20=myfont1.render("$ %d" %(10+20*data.me.speedLev),True,(220,220,220))
    Label21=myfont1.render("$ %d" %(10+20*data.me.turnLev),True,(220,220,220))
    Label22=myfont1.render("$ %d" %(10+20*data.me.collisionLev),True,(220,220,220))
    Label23=myfont1.render("$ 100",True,(220,220,220))
    Label24=myfont1.render("$ 500",True,(220,220,220))
    Label25=myfont1.render("$ 1500",True,(220,220,220))
    Label26=myfont1.render("$ %d" %data.me.coins,True,(220,220,220))

    screen.blit(LabelCoin,(50,10))
    screen.blit(LabelUpgrades,(40,40))
    screen.blit(Label1,(40,70))
    screen.blit(Label2,(40,100))
    screen.blit(Label3,(40,130))
    screen.blit(Label4,(40,160))
    screen.blit(Label5,(40,190))
    screen.blit(Label6,(40,220))
    screen.blit(Label7,(40,250))
    screen.blit(Label8,(40,280))
    screen.blit(Label9,(50,310))
    screen.blit(Label10,(40,340))
    screen.blit(Label11,(40,370))
    screen.blit(Label12,(40,400))
    screen.blit(Label13,(40,430))
    screen.blit(Label14,(40,830))
    screen.blit(Label15,(170,70))
    screen.blit(Label16,(170,100))
    screen.blit(Label17,(170,130))
    screen.blit(Label18,(170,160))
    screen.blit(Label19,(170,190))
    screen.blit(Label20,(170,220))
    screen.blit(Label21,(170,250))
    screen.blit(Label22,(170,280))
    screen.blit(Label23,(160,370))
    screen.blit(Label24,(160,400))
    screen.blit(Label25,(160,430))
    screen.blit(Label26,(100,10))
   
def drawGame():
    # pygame.mixer.quit()
    screen.fill((91,138,179))
    screen.fill((111,140,179))  
    drawBoard()
    # drawLand()
    drawcoin()
    drawTexts()
    if (data.readyMsg=="Sail"):
        drawLeaderBoard()
    drawUpgrade()
    drawBullet()
    if (data.gameChat==True):
        drawChatBox()
    data.me.drawPlayer()
    if (len(data.players)>0):
        for eachID in data.players:
            player=data.players[eachID]
            player.drawPlayer()
    if (data.lose==True): 
        data.front=True 
        init(data)
    if (data.displayMsg!="" or data.leftPlayer!=""): drawChat()
    if (data.me.equips>0): 
        drawWeaponBox()
    pygame.display.update()
    
def drawWeaponBox():
    deleteList=[]
    for eachKey in data.upgradeTree:
        remainingStuff=data.upgradeTree[eachKey]
        if (len(remainingStuff)==0):
            deleteList.append(eachKey)
    for eachEmpty in deleteList:
        del data.upgradeTree[eachEmpty]
    if ("front" in data.upgradeTree):
        screen.blit(data.frontWeapon,(400,800))
    if ("side" in data.upgradeTree):
        screen.blit(data.sideWeapon,(540,800))
    if ("rear" in data.upgradeTree):
        screen.blit(data.rearWeapon,(680,800))
    if (data.drawingWeapon==True): 
        if (data.drawWeaponFront==True):
            weaponRemain=data.upgradeTree["front"]
            count=0
            for each in weaponRemain:
                msg=myfont.render(each,True,data.whiteColor)
                pos=(390,770-count*30)
                screen.blit(msg,pos)
                count+=1
        elif (data.drawWeaponSide==True):
            count=0
            weaponRemain=data.upgradeTree["side"]
            for each in weaponRemain:
                msg=myfont.render(each,True,data.whiteColor)
                pos=(530,770-count*30)
                screen.blit(msg,pos)
                count+=1
        elif (data.drawWeaponRear==True):
            count=0
            weaponRemain=data.upgradeTree["rear"]
            for each in weaponRemain:
                msg=myfont.render(each,True,data.whiteColor)
                pos=(670,770-count*30)
                screen.blit(msg,pos)
                count+=1
  
def drawLeaderBoard():
    # rank the score based on sort 
    topLabel = myfont1.render("LeaderBoard",True,(220,220,220))
    screen.blit(topLabel,(800,30))
    scoreList=[]
    for eachScore in data.scoreDict:
        scoreList.append(eachScore)
    rankingScore=list(reversed(sorted(scoreList)))
    for fromTopToLow in range(len(rankingScore)):
        ranking=fromTopToLow+1 
        score=rankingScore[fromTopToLow]        
        if (data.me.score==score):
            theLabel=myfont1.render("%d %s(me) %d"%(ranking,data.me.name,data.me.score),True,data.whiteColor)
            screen.blit(theLabel,(800,30+50*ranking))
        else:
            name=data.scoreDict.get(score)
            theLabel=myfont1.render("%d %s %d"%(ranking,name,score),True,data.whiteColor)
            screen.blit(theLabel,(800,30+50*ranking))
            
def drawUpgrade():
    # draw players blood and upgrades
    if (data.me.equips<=0):
        percent=data.me.getExp()
        whiteBarLen=int(percent*3)
        data.bar4= pygame.Surface((whiteBarLen,20)) 
        data.bar4.set_alpha(70)                
        data.bar4.fill((220,220,220))
        Label26=myfont1.render(" %d %%" %percent,True,(220,220,220))
        screen.blit(Label26,(600,833))
        screen.blit(data.bar4,(450,828))
        screen.blit(data.bar3,(450,828))   
         
def drawLand():
    for eachImage in data.newImages:
        screen.blit(eachImage[0],(eachImage[1][0]+data.me.offsetX,eachImage[1][1]+data.me.offsetY))
        
def PlayerUpdate():
    # call update for each player 
    data.scoreDict=dict()
    flag=False 
    if (len(data.players)>0 and data.gameEntered==True):            
        for eachID in data.players:
            player=data.players[eachID]
            player.updatePos()
            player.updateCondition()
            if (data.readyMsg=="NotReady"):
                player.Update()
           
    
    data.me.updateCondition()
    
    if (data.pathFinding==True):
        if (data.me.destination!=None):
            data.me.solveDest()
        if (len(data.me.curveMotion)>0):
            motion=data.me.curveMotion.pop(0)
            data.me.angle=motion 
        elif (len(data.me.solutions)>0):
            flag=True 
            Moves=data.me.solutions.pop(0)
            if (Moves==(1,0) or Moves==(0,1) or Moves==(-1,0) or Moves==(0,-1)):
                if (Moves==(1,0)): data.me.angle=0
                elif (Moves==(-1,0)): data.me.angle=180
                elif (Moves==(0,-1)): data.me.angle=90
                elif (Moves==(0,1)): data.me.angle=270
                data.me.posX+=Moves[0]*data.me.curSpeed
                data.me.posY+=Moves[1]*data.me.curSpeed
            else:
                if (Moves==(1,1)): data.me.angle=315
                elif (Moves==(-1,1)): data.me.angle=225
                elif (Moves==(1,-1)): data.me.angle=45
                elif (Moves==(-1,-1)): data.me.angle=135
                data.me.posX+=Moves[0]*data.me.curSpeed*((2**0.5)/2)
                data.me.posY+=Moves[1]*data.me.curSpeed*((2**0.5)/2)
            data.me.offsetX,data.me.offsetY=620-data.me.posX,450-data.me.posY
    if (flag==False):
        data.me.updatePos()
        
    if (data.readyMsg=="NotReady" and len(data.players)>0):
        flag=False 
        for eachID in data.players:
            player=data.players[eachID]
        if (data.pathFinding==True):
            if (player.destination!=None):
                player.solveDest()
            if (len(player.curveMotion)>0):
                motion=player.curveMotion.pop(0)
                player.angle=motion 
            elif (len(player.solutions)>0):
                flag=True 
                Moves=player.solutions.pop(0)
                if (Moves==(1,0) or Moves==(0,1) or Moves==(-1,0) or Moves==(0,-1)):
                    if (Moves==(1,0)): player.angle=0
                    elif (Moves==(-1,0)): player.angle=180
                    elif (Moves==(0,-1)): player.angle=90
                    elif (Moves==(0,1)): player.angle=270
                    player.posX+=Moves[0]*player.curSpeed
                    player.posY+=Moves[1]*player.curSpeed
                else:
                    if (Moves==(1,1)): player.angle=315
                    elif (Moves==(-1,1)): player.angle=225
                    elif (Moves==(1,-1)): player.angle=45
                    elif (Moves==(-1,-1)): player.angle=135
                    player.posX+=Moves[0]*player.curSpeed*((2**0.5)/2)
                    player.posY+=Moves[1]*player.curSpeed*((2**0.5)/2)
        if (flag==False):
            player.updatePos()

def drawBullet():
    # move through each bullet in the list and draw 
    if (len(data.bullet)>0):
        for eachBul in data.bullet:
            pygame.draw.circle(screen,data.blackColor,(round(data.me.offsetX+eachBul[0][0]),
                round(data.me.offsetY+eachBul[0][1])),12,0)
    if (len(data.mines)>0):
        for eachMine in data.mines:
            x,y=eachMine[0][0],eachMine[0][1]
            pointList=[(x-12,y),(x-6,y+6*3**0.5),(x+6,y+6*3**0.5),(x+12,y),(x+6,y-6*3**0.5),(x-6,y-6*3**0.5)]
            newPointList=list(map (lambda eachPos: (round(eachPos[0]+data.me.offsetX),
            round(eachPos[1]+data.me.offsetY)),pointList))
            pygame.draw.polygon(screen,data.blackColor,newPointList,0)
 
def checkDamage():
    # check damage for each player 
    hitBullet=list(filter(lambda bul: heruistics(data.me.posX,
        data.me.posY,bul[0][0],bul[0][1])<=52 and bul[4]!=data.me.name,data.bullet))
    data.bullet=list(filter(lambda bul: bul not in hitBullet,data.bullet))
    damage=list(map(lambda x: x[3],hitBullet))
    totaldmg= reduce(lambda x,y: x + y, damage, 0)
    data.me.blood-=totaldmg
    hitMine=list(filter(lambda mn: heruistics(data.me.posX,
        data.me.posY,mn[0][0],mn[0][1])<=50 and mn[1]!=data.me.name,data.mines))
    data.mines=list(filter(lambda mn: mn not in hitMine,data.mines))
    damage=list(map(lambda x: x[2],hitMine))
    totaldmg= reduce(lambda x,y: x + y, damage, 0)
    data.me.blood-=totaldmg
    if (data.readyMsg=="Sail" and data.gameEntered==True):
        for eachID in data.players:
            player=data.players[eachID]
            hitBullet=list(filter(lambda bul: heruistics(player.posX,
                player.posY,bul[0][0],bul[0][1])<=52 and bul[4]!=player.name,data.bullet))
            data.bullet=list(filter(lambda bul: bul not in hitBullet,data.bullet))
            damage=list(map(lambda x: x[3],hitBullet))
            totaldmg= reduce(lambda x,y: x + y, damage, 0)
            player.blood-=totaldmg
            hitMine=list(filter(lambda mn: heruistics(player.posX,
                player.posY,mn[0][0],mn[0][1])<=50 and mn[1]!=player.name,data.mines))
            data.mines=list(filter(lambda mn: mn not in hitMine,data.mines))
            damage=list(map(lambda x: x[2],hitMine))
            totaldmg= reduce(lambda x,y: x + y, damage, 0)
            player.blood-=totaldmg
    
def bulletUpdate():
    # update the position for each bullet 
    if (len(data.bullet)>0):
        for eachBul in data.bullet:
            remainingMove=eachBul[2]
            if (remainingMove>0):
                bulPixelX=round(eachBul[0][0])
                bulPixelY=round(eachBul[0][1])
                direction=eachBul[1]
                eachBul[0][0]+=25*math.cos(direction)
                eachBul[0][1]-=25*math.sin(direction)
                eachBul[2]-=1
            if (bulPixelX>3000 or bulPixelY>3000 or bulPixelX<0 or bulPixelY<0 
                or eachBul[2]<=0 or (bulPixelX,bulPixelY) in data.map2 or remainingMove==0):
                data.bullet.remove(eachBul)
           
def serverUpdate(msg):
    # handle message sent from server differently based on starting string 
    if (msg.startswith("newPlayer")):
        msg = "ship %s %d %d %s\n"%(data.me.name,data.me.posX,data.me.posY,
                data.processedShips[data.color])       
        data.server.send(msg.encode())
        msg="readyState %s\n"%data.readyMsg
        data.server.send(msg.encode())
    elif (msg.startswith("inf")):
        msg=msg.split()
        pID=int(msg[1])
        pName=msg[2]
        pX,pY=int(msg[3]),int(msg[4])
        image=str(msg[5])
        
        newP=playerShip(pName,pX,pY,image)
        data.players[pID]=newP
    elif (msg.startswith("state")):
        msg=msg.split()
        pID=int(msg[1])
        state=str(msg[2])
        data.readyDict[pID]=state    
    elif (msg.startswith("coinCome")):
        msg=msg[9:]      
        data.coinList+=ast.literal_eval(msg)
    if (data.gameEntered==True):
        if (msg.startswith("sho")):
            msg=msg.split()             
            pbulX,pbulY=int(msg[2]),int(msg[3])
            pbulDir=int(msg[4])
            pbulMove=int(msg[5])
            pbulDmg=int(msg[6])
            pName=str(msg[7])
            bulData=[[pbulX,pbulY],pbulDir,pbulMove,pbulDmg,pName]
            data.bullet.append(bulData)
        elif (msg.startswith("mn")):               
            msg=msg.split()
            pMineX=int(msg[2])
            pMineY=int(msg[3])
            pName=str(msg[4])
            pDmg=int(msg[5])
            mnData=((pMineX,pMineY),pName,pDmg)
            data.mines.append(mnData)  
        elif (msg.startswith("upg")):               
            msg=msg.split()
            pID=int(msg[1])
            player=data.players[pID]
            upgrade=str(msg[2])
            if (upgrade=="Hull"): player.upgradeHull()
            elif (upgrade=="Range"): player.upgradeRange()
            elif (upgrade=="Turn"): player.upgradeTurn()
            elif (upgrade=="Speed"): player.upgradeSpeed()
            elif(upgrade=="Collision"): player.upgradeCollision()
            elif(upgrade=="Reload"): player.upgradeReload()
            elif(upgrade=="Recover"): player.upgradeRecover()
            elif (upgrade=="Damage"): player.upgradeDamage()
        elif (msg.startswith("start")):               
            msg=msg.split()
            pID=int(msg[1])
            player=data.players[pID]
            action=str(msg[2])
            if (action=="Acc"): 
                player.accler=True 
                player.decler=False    
            elif (action=="Dec"): 
                player.accler=False 
                player.decler=True   
            elif (action=="Right"):
                player.right=True 
                player.left=False  
            elif (action=="Left"): 
                player.left=True 
                player.right=False  
        elif (msg.startswith("stop")):
            msg=msg.split()
            pID=int(msg[1])
            player=data.players[pID]
            action=str(msg[2])
            if (action=="Acc"): player.accler=False 
            elif (action=="Dec"): player.decler=False   
            elif (action=="Right"): player.right=False 
            elif (action=="Left"): player.left=False 
        elif (msg.startswith("score")):
            msg=msg.split()
            pID=int(msg[1])
            type=int(msg[2])
            coin=(type,int(msg[3]),int(msg[4]))
            data.coinList.remove(coin)
            scoreIncr=data.val[int(type)]
            if (pID in data.players):
                player=data.players[pID]  
                player.score+=scoreIncr 
            else:
                data.me.score+=scoreIncr
        elif (msg.startswith("lessHealth")):
            msg=msg.split()
            pID=int(msg[1])
            newHealth=int(msg[2])
            if (pID in data.players):
                player=data.players[pID]  
                player.blood=newHealth
            else:
                data.me.health=newHealth
        elif (msg.startswith("die")):
            msg=msg.split()
            name=str(msg[1])  
            if (name==data.me.name):
                drawGameOver()
        elif (msg.startswith("pos")):
            msg=msg.split()
            pID=int(msg[1])
            newX,newY=int(msg[2]),int(msg[3])
            angle=int(msg[4])
            if (pID in data.players):
                player=data.players[pID]
                player.posX,player.posY,player.angle=newX,newY,angle
                player.rotatePlayer()
            else:
                data.me.offsetX,data.me.offsetY=620-newX,450-newY
                data.me.posX,data.me.posY,data.me.angle=newX,newY,angle
                data.me.rotatePlayer()
        elif (msg.startswith("msg")):
            msg=msg.split()
            pID=int(msg[1])
            message=""
            for eachPiece in range(len(msg)-2):
                message+=str(msg[2+eachPiece])+" "
            chatterName=data.players[pID].name
            data.displayMsg+="%s:"%chatterName+" "+message+"\n"
            
        elif (msg.startswith("leave")):
            msg=msg.split()
            pID=int(msg[1]) 
            player=data.players[pID]
            thisPersonScore=player.score
            data.leftPlayer=player.name
            del data.scoreDict[thisPersonScore]
            del data.players[pID]
def drawSettings():
    screen.fill((255,255,255))
    screen.blit(data.settingPg,(0,0))
    label=bigfont.render("settings",True,data.blackColor)
    screen.blit(label,(535,20))
    label1=myfont.render("soundEffect",True,data.blackColor)
    label2=myfont.render("music",True,data.blackColor)
    label3=myfont.render("pathFinding(Enable for Single Disable for multiplayer)",True,data.blackColor)
    label4=myfont.render("Set current name as default",True,data.blackColor)
    label5=myfont.render("Set current color as default",True,data.blackColor)
    label6=myfont.render("On",True,data.blackColor)
    label7=myfont.render("Off",True,data.blackColor)
    screen.blit(data.greenShip,(55,120))
    screen.blit(data.redShip,(285,120))
    screen.blit(data.blueShip,(515,120))
    screen.blit(data.purpleShip,(745,120))
    screen.blit(data.orangeShip,(975,120))
    screen.blit( data.back,(1100,20))
    screen.blit(label1,(35,550))
    screen.blit(label2,(35,600))
    screen.blit(label3,(35,650))
    screen.blit(label4,(35,700))
    screen.blit(label5,(35,750))
    screen.blit(label6,(940,520))
    screen.blit(label7,(1090,520))
    pygame.draw.rect(screen,data.blackColor,[950,550,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[950,600,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[950,650,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[950,700,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[950,750,20,20],0)    
    pygame.draw.rect(screen,data.blackColor,[1100,550,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[1100,600,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[1100,650,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[1100,700,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[1100,750,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[140,260,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[370,260,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[600,260,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[830,260,20,20],0)
    pygame.draw.rect(screen,data.blackColor,[1060,260,20,20],0)
    if (data.color==0): drawTick(140,260)
    elif (data.color==1): drawTick(370,260)
    elif (data.color==2): drawTick(600,260)
    elif (data.color==3): drawTick(830,260)
    elif (data.color==4): drawTick(1060,260)
    if (data.soundEffect==True): drawTick(950,550)
    else: drawTick(1100,550)
    if (data.music==True): drawTick(950,600)
    else: drawTick(1100,600)
    if (data.pathFinding==True): drawTick(950,650)
    else: drawTick(1100,650)
    if (data.nameDefault==True): drawTick(950,700)
    else: drawTick(1100,700)
    if (data.colorDefault==True): drawTick(950,750)
    else: drawTick(1100,750)
    
def drawTick(posX,posY):
    # draw the tick with two lines 
    firstLineX1,firstLineY1=posX+3,posY+10
    firstLineX2,firstLineY2=firstLineX1+math.cos(conv(45))*8,firstLineY1++math.sin(conv(45))*8
    secondLineX1,secondLineY1=firstLineX2,firstLineY2
    secondLineX2,secondLineY2=firstLineX2+math.cos(conv(55))*13,firstLineY2-math.sin(conv(55))*13
    pygame.draw.line(screen,(0,255,0),(firstLineX1,firstLineY1),(firstLineX2,firstLineY2),5)

    pygame.draw.line(screen,(0,255,0),(secondLineX1,secondLineY1),(secondLineX2,secondLineY2),5)
   
def drawCredit(): 
    screen.blit(data.gratitude,(0,0))
    screen.blit( data.back,(1100,20))
    thank=bigfont.render("Credit",True,data.blackColor)
    msg1="I would like to express my gratitude to professor Kosbie for his instruction, to my mentor Katja for her" 
    msg2="advice and guidance,to Rohan for his helpful tutorial,to all the other 15112 TAs for their instructions,"
    msg3="to Jacky Xu,SiHao Yu, MingQuan Chen,and TianLei Pan for their strong support in the last month."
    thankMsg1=myfont.render("%s"%msg1,True,data.blackColor)
    thankMsg2=myfont.render("%s"%msg2,True,data.blackColor)
    thankMsg3=myfont.render("%s"%msg3,True,data.blackColor)
    screen.blit(thank,(545,35))
    screen.blit(thankMsg1,(30,80))
    screen.blit(thankMsg2,(30,110))
    screen.blit(thankMsg3,(30,135))

def drawLobby():
    if (data.lobby==True):
        if (data.nameMsg!=""):
            data.me.name=data.nameMsg 
        screen.fill(data.blackColor)
        screen.blit( data.back,(1100,20))
        label1=myfont.render("Game Lobby",True,data.whiteColor)
        screen.blit(label1,(520,20))
        label2=myfont.render("Players",True, data.whiteColor)
        screen.blit(label2,(100,200))
        label3=myfont.render("State",True,data.whiteColor)
        label4=myfont.render("%s"%data.me.name,True,data.whiteColor)
        label6=myfont.render("%s"%data.readyMsg,True,data.whiteColor)
        if (data.readyMsg=="NotReady"):
            label5=myfont.render("Set Sail",True,data.blackColor)
            color=(0,255,0)
        else:
            label5=myfont.render("Not Ready",True,data.blackColor)
            color=(255,0,0)
        screen.blit(label3,(750,200))
        screen.blit(label4,(100,250))
        screen.blit(label6,(750,250))
        pygame.draw.rect(screen,color,(520,700,180,65),0)
        screen.blit(label5,(550,710))
        count=0
        if (len(data.readyDict)>0):
            for eachID in data.players:
                readyState=data.readyDict[eachID]
                label01=myfont.render("%s"%data.players[eachID].name,True,data.whiteColor)
                label02=myfont.render("%s"%readyState,True,data.whiteColor)
                screen.blit(label01,(100,250+(count+1)*50))
                screen.blit(label02,(750,250+(count+1)*50))
                data.front=False 
                
def checkStart():
        count=0
        if (len(data.readyDict)>0):
            for eachID in data.readyDict:
                state=data.readyDict[eachID]
                if (state=="Sail"):
                    count+=1 
        if (len(data.players)>0 and count==len(data.players) and data.readyMsg=="Sail"):
            data.scoreList=[0 for each in range(len(data.players)+2)]
            msg="game\n"
            data.server.send(bytes(msg,"UTF-8"))
            data.gameEntered=True 
            data.lobby=False 
            
def update():   
    # game major update 
    data.map=[[0]*100 for val in range(100)]
    if (data.readyMsg=="NotReady"):
        coinGenerator()
    PlayerUpdate()
    bulletUpdate()
    checkDamage()
    
def drawChat():
    #display the chat msg in multiplayer game 
    if (data.displayMsg!=""):
        msgList=data.displayMsg.split("\n")
        for eachMsgIndex in range(len(msgList)):
            position=(30,700-(len(msgList)-1-eachMsgIndex)*30)
            othersMsg=myfont1.render(msgList[eachMsgIndex],True,data.blackColor)
            screen.blit(othersMsg,position)
    if (data.leftPlayer!=""):
        print("aaaa")
        leftMsg="%s left the game,leaving you alone" % data.leftPlayer
        leftmsg=myfont1.render(leftMsg,True,data.blackColor)
        screen.blit(leftmsg,(30,750))
        
def drawGameOver():
    lose=bigfont.render("You lose",True,(255,0,0))
    instruc=bigfont.render("Press R to return",True,(255,0,0))
    screen.blit(lose,(530,400)) 
    screen.blit(instruc,(480,430)) 
    pygame.display.update()
    
def main():
    while 1:
        clock.tick(60)
        data.elapsed+=1
        data.map2=[]
        for event in pygame.event.get():
            getKeyPress(event)
            getMousePress(event)
        if (data.instructPg==True): drawInstruct()
        if (data.front==True): drawFront()
        if (data.elapsed%600==0 and data.displayMsg!=""): data.displayMsg=""
        if (data.elapsed%1000==0 and data.leftPlayer!=""): data.leftPlayer=""
        if (data.credit==True): drawCredit()
        if (data.settings==True): drawSettings()
        if (data.lobby==True): 
            drawLobby()
            checkStart()
        if (data.gameEntered==True): 
            update()
            drawGame()
        pygame.display.flip()
        
if __name__ == "__main__":
    main()

