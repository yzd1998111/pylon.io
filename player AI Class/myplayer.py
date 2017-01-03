import math 
import os 
import sys
import random
from heapq import * 
import time
import string 
import copy
import time 


os.chdir("/Users/yuanzhendong/desktop/tp3")
sys.path.append("/Users/yuanzhendong/desktop/tp3")
from client.myclient import *
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
        self.dmg=1.1 
        self.reload=2
        self.collision=1
        self.image=pygame.image.load(image) 
        self.newImage=pygame.transform.rotate(self.image,self.angle+90)
        self.equip=[]
        self.level=0
        self.upgrade=0
        self.equips=20
        self.recover=2
        self.collision=3
        self.fleets=0
        self.score=0
        self.coins=9999
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
        while (self.angle)<0:
            self.angle+=360
        while (self.angle)>360:
            self.angle-=360 
        if (0<=self.angle<90): return 1 
        elif (90<=self.angle<180): return 2 
        elif (180<=self.angle<270): return 3 
        elif (270<=self.angle<360): return 4 
        
    def updatePos(self):   
        tempX,tempY,tempAngle=self.posX,self.posY,self.angle
        tempOffX,tempOffY=self.offsetX,self.offsetY
        self.posY-=self.curSpeed*math.sin(conv(self.angle))
        self.posX+=self.curSpeed*math.cos(conv(self.angle))
        flag,collide=True,False  
        
        for coins in data.coinList:
            itsVal=data.val[coins[0]]
            xPos=coins[1]
            yPos=coins[2]
            dist=heruistics(xPos,yPos,self.posX,self.posY)
            if  (dist<=52):
                self.coins+=itsVal
                self.score+=itsVal
                data.coinList.remove(coins)
                        
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
                self.blood-=player.collision
                player.blood-=self.collision
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
            print("impossible")
            global failure
            failure+=1 
            data.lose=True 
            
    def drawPlayer(self):
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
        oldCenter=self.rect1.center
        self.newImage=pygame.transform.rotate(self.image,self.angle+90)
        self.rect1=self.newImage.get_rect()
        self.rect1.center=oldCenter 
        
    def checkShoot(self):
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
        self.recordSpeed=self.curSpeed 
        solutions={(True,True):4,(True,False):1,(False,True):3,(False,False):2}
        endingX,endingY=self.destination[0],self.destination[1]
        self.destination=None 
        if ((endingX,endingY) in data.map2):
            endingX,endingY=findNewPos(self.posX,self.posY,endingX,endingY,0)
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
        print(haveToMoveInDir,self.angle)
        turnRadius=calTurnRadius(self.speedLev,self.turnLev)
        if (abs(self.angle-haveToMoveInDir)>self.turn and heruistics(startX,startY,endingX,endingY)<turnRadius):
            return 
        else:
            if (abs(self.angle-haveToMoveInDir)>self.turn):
                moveOrder=[]
                self.curveMotion=[]
                print("dest",destQuadrant,"cur",curQuadrant)
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
                        result=simulateDirection(eachDirection,[(self.posX,self.posY)],self.angle,haveToMoveInDir,[])
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
            self.solutions=list(map(lambda x: (x[0],x[1]),self.astar(startX,startY,endX,endY,data.dirs)))
            
    def astar(self,startX,startY,endX,endY,dirs):
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

class finiteStateAI(playerShip):
    def __init__(self,name,posX,posY,image,enemy):
        super().__init__(name,posX,posY,image)
        startWander=wander(self)
        self.state=startWander 
        self.name=name
        self.posX=posX
        self.image=pygame.image.load(image)
        self.enemy=enemy
    def transToState(self,state):
        self.state=state
    def Update(self):
        print("zhixing",self.state)
        self.state.execute(self)
    def isStrong(self):
        if (self.upgrade-2>=self.enemy.upgrade or self.upgrade==75):
            return True   
        else: 
            return False 

class state():
    def __init__(self,AI):
        self.AI=AI
    def execute():
        pass 
        
class attack(state):
    def __init__(self,AI):
        super().__init__(AI)
    def execute(self,AI):
        dist=heruistics(data.me.posX,data.me.posY,self.AI.posX,self.AI.posY)
        if (not self.AI.enemy.blood<=30 and self.AI.blood<=40):
            startEscape=escape(self.AI)
            self.AI.transToState(startEscape)
        elif ((self.AI.isStrong() and dist>150) or "batteringRam" in AI.equip):
            startChase=chase(self.AI)
            self.AI.transToState(startChase)
        elif (self.AI.isStrong() and dist<=150):
            self.atk()
    def atk(self):
        # avoidBullet 
        if (AI.ready==True):
            if ("movingcannon" in AI.equips):
                pass
            elif ("sideCannon" or "rearCannon" or "frontCannon" in self.AI.equip):
                self.AI.checkShoot()
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
   
class chase(state):
    def __init__(self,AI):
        super().__init__(AI)
        self.elpsed=0
        
    def execute(self,AI):
        self.elpsd+=1 
        dist=heruistics(self.AI.enemy.posX,self.AI.enemy.posY,self.AI.posX,self.AI.posY)
        if (self.AI.blood<50):
            startEscape=escape(self.AI)
            self.AI.transToState(startEscape)
        elif ("batteringRam" in AI.equips):
            self.track()
        elif(dist<900):
            self.AI.transToState(attack)
            
    def track(self):
        if (self.elpsedTime%3==0):
            self.AI.destination=(self.AI.enemy.posX,self.AI.enemy.posY)

class escape(state):
    def __init__(self,AI):
        super().__init__(AI)
        self.elpsed=0
    
    def execute(self,AI):
        self.elpsed+=1
        dist=heruistics(self.AI.enemy.posX,self.AI.enemy.posY,self.AI.posX,self.AI.posY)
        if (self.AI.enemy.blood<=50 and self.AI.blood>50):
            print("what")
            startAttack=attack(self.AI)
            self.AI.transToState(startAttack)
        elif (dist<=500):
            print("fk you")
            self.findSafe()
        else:
            print("fk me")
            startWander=wander(self.AI)
            self.AI.transToState(startWander)
            
    def findSafe(self):
        if (self.elpsed%3==0): 
            if (self.AI.enemy.posX>=self.AI.posX,self.AI.enemy.posY>=self.AI.posY):
                self.AI.destination=(self.AI.posX-200,self.AI.posY-200)
            elif (self.AI.enemy.posX>= self.AI.posX,self.AI.enemy.posY<self.AI.posY):
                self.AI.destination=(self.AI.posX-200,self.AI.posY+200)
            elif (self.AI.enemy.posX<self.AI.posX,self.AI.enemy.posY>=self.AI.posY):
                self.AI.destination=(self.AI.posX+200,self.AI.posY-200)
            elif (self.AI.enemy.posX<self.AI.posX,self.AI.enemy.posY>=self.AI.posY):
                self.AI.destination=(self.AI.posX+200,self.AI.posY-200)
        if ("mineDropper" in self.AI.equip and self.AI.ready==True):
            self.AI.checkShoot()

class wander(state):
    def __init__(self,AI):
        super().__init__(AI)
        self.working=False 
        self.coinToGet=None
    def execute(self,AI):
        dist=heruistics(self.AI.enemy.posX,data.me.posY,AI.posX,AI.posY)
        print(dist,self.AI.isStrong())
        if (dist>400):
            self.normal()
        elif (dist<400 and self.AI.isStrong()==False):
            startEscape=escape(self.AI)
            self.AI.transToState(startEscape)
        else:
            startAttack=attack(self.AI)
            self.AI.transToState(startAttack)
            
    def normal(self):
        if (len(self.AI.solutions)==0):
            self.working=False
        if (self.working==False):
            min=99999
            for eachCoin in data.coinList:
                dist=heruistics(eachCoin[1],eachCoin[2],self.AI.posX,self.AI.posY)
                if (dist<min):
                    min=dist
                    self.coinToGet=eachCoin
                elif (dist==min and eachCoin[0]>self.coinToGet[0]):
                    self.coinToGet=eachCoin
                    self.working=True
                else: pass
            self.AI.destination=(self.coinToGet[0],self.coinToGet[1])
            
        self.tryUpgrade()
        while (self.AI.equips>0):
            weaponList=["frontCannon","mineDropper","rearCannon",
            "sideCannon","batteringRam","movingCannon"]
            
            weaponNum=random.randint(0,5)
            weapon=weaponList[weaponNum]
            if (weapon not in self.AI.equip):
                self.AI.addEquip(weapon)
             
    def tryUpgrade(self):
        print(self.AI.equip)
        if ("batteringRam" in self.AI.equip):
            self.AI.upgradeCollision()
        if ("frontCannon" or "rearCannon" or "sideCannon" or "movingCannon" in self.AI.equip):
            self.AI.upgradeDamage()
            self.AI.upgradeRange()
            self.AI.upgradeReload()
        else: self.AI.upgradeTurn()
        self.AI.upgradeSpeed()
        self.AI.upgradeHull()
        self.AI.upgradeRecover()
       
       