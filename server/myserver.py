import socket 
from queue import Queue 
import threading  
import random
import os 
import pygame 
import sys
import select 
import time

os.chdir("/Users/yuanzhendong/desktop/tp3")
sys.path.append("/Users/yuanzhendong/desktop/tp3")
from client.myclient import * 

class Struct(object): pass
data1 = Struct()


##############credit to Rohan for his tutorial 

def init(data1):    
    data1.start=True 
    data1.elapsed=0
BACKLOG=4
host =""
port =50003

init(data1)
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
server.listen(BACKLOG)
print('wait for connection')

class gameServer():
    def __init__(self):
        self.bullet=[]
        self.players=dict()
        self.serverCoin=[]
        self.moreCoin=[]
        self.mines=[]
        self.val=[10,20,30,50,100,500]
        self.leftClient=[]
        # generate coin for all players 
    def coinGen(self):
        self.moreCoin=[]
        playerNum=len(clients)
        coins=playerNum*25
        if (len(self.serverCoin)==coins):
            pass
        else:
            lacking=coins-len(self.serverCoin)
            if (lacking>0):
                for eachLack in range(lacking):
                    randomX,randomY=random.randint(200,2800),random.randint(200,2800)
                    randVal=random.randint(0,100)
                    if (randVal<35): type=0
                    elif (randVal<=60): type=1
                    elif (randVal<=75): type=2
                    elif (randVal<=90): type=3
                    elif (randVal<=98): type=4
                    else: type=5
                    self.moreCoin.append((type,randomX,randomY))
                for clientID in clients:
                    sendMsg="coinCome"+" "+str(self.moreCoin)+"\n"
                    clients[clientID].send(bytes(sendMsg,"UTF-8"))
                self.serverCoin+=self.moreCoin
        #central position and condition update for each player 
    def centralPos(self):
        pygame.time.delay(55)
        for eachID in self.players:
            player=self.players[eachID]
            tempX,tempY,tempAngle=player.posX,player.posY,player.angle
            player.posY-=player.curSpeed*math.sin(conv(player.angle))
            player.posX+=player.curSpeed*math.cos(conv(player.angle))
            flag=True 
            for x in range(-40,41,1):
                for y in range(-40,41,1):
                    posX,posY=round(player.posX+y),round(player.posY+x)
                    if ((posX,posY) in data.map2):                   
                        player.blood-=3
                        flag=False  
            if not (39<=player.posY<=2961 and  39<=player.posX<=2961):
               
                flag=False 
          
            for eachID2 in self.players:
                player2=self.players[eachID2]
                if (eachID2!=eachID and heruistics(player.posX,player.posY,player2.posX,player2.posY)<80):
                    flag=False 
            if (flag==False):
                player.posY=tempY
                player.posX=tempX
                player.curSpeed=4
        if (len(self.bullet)>0):
            for eachBul in self.bullet:
                remainingMove=eachBul[2]
                if (remainingMove>0):
                    bulPixelX=round(eachBul[0][0])
                    bulPixelY=round(eachBul[0][1])
                    direction=eachBul[1]
                    eachBul[0][0]+=25*math.cos(direction)
                    eachBul[0][1]-=25*math.sin(direction)
                    eachBul[2]-=1
                if (bulPixelX>3000 or bulPixelY>3000 or bulPixelX<0 or bulPixelY<0 or 
                        eachBul[2]<=0 or (bulPixelX,bulPixelY) in data.map2 or remainingMove==0):
                    self.bullet.remove(eachBul)
                    
    def centralCondition(self):
        pygame.time.delay(55)
        for eachID in self.players:
            player=self.players[eachID]
            if (player.blood+player.recover>=player.Hull):
                player.blood=player.Hull
            else:
                player.blood+=player.recover
            if   (player.left==True): 
                player.angle+=player.turn
            elif (player.right==True): 
                player.angle-=player.turn  
            if (player.accler==True):
                if(player.curSpeed +2 <player.speed):
                    player.curSpeed+=2 
                else:
                    player.curSpeed=player.speed
            if (player.decler==True) :
                if (player.curSpeed-2 >data.minSpeed):
                    player.curSpeed-=2 
                else:
                    player.curSpeed=data.minSpeed
            if (player.blood<=0):
                del self.players[eachID]
                for clientID in clients:
                    sendMsg="die"+" "+str(player.name)+"\n"
                    clients[clientID].send(bytes(sendMsg,"UTF-8"))
                
    def collisionCheck(self):
        # if not divine shield 
        pygame.time.delay(30)
        for eachCoin in self.serverCoin:
            for eachID in self.players:
                eachPlayer=self.players[eachID]
                xpos,ypos=eachPlayer.posX,eachPlayer.posY
                if (heruistics(eachCoin[1],eachCoin[2],xpos,ypos)<52):
                    eachPlayer.score+=self.val[eachCoin[0]]
                    for clientID in clients:
                        sendMsg="score"+" "+str(eachID)+" "+"%d %d %d"%(eachCoin[0],eachCoin[1],eachCoin[2])+"\n"
                        clients[clientID].send(bytes(sendMsg,"UTF-8"))
                    self.serverCoin.remove(eachCoin)
                        
        for eachBul in self.bullet:
            bulX,bulY,dmg=eachBul[0][0],eachBul[0][1],eachBul[3]
            for eachID in self.players:
                eachPlayer=self.players[eachID]
                xpos,ypos=eachPlayer.posX,eachPlayer.posY
                if (heruistics(xpos,ypos,bulX,bulY)<52):
                    eachPlayer.blood-=eachBul[3]
                    for clientID in clients:
                        sendMsg="lessHealth"+" "+str(eachID)+" "+str(eachPlayer.blood)+"\n"
                        clients[clientID].send(bytes(sendMsg,"UTF-8"))
                    self.bullet.remove(eachBul)
                    
        for eachMine in self.mines:          
            mX,mY=eachMine[0][0],eachMine[0][1]
            for eachID in self.players:
                eachPlayer=self.players[eachID]
                xpos,ypos=eachPlayer.posX,eachPlayer.posY
                if (heruistics(mX,mY,xpos,ypos)<52):
                    dmg=eachMine[2]
                    eachPlayer.blood-=dmg
                    for clientID in clients:
                        sendMsg="lessHealth"+" "+str(eachID)+" "+str(eachPlayer.blood)+"\n"
                        clients[clientID].send(bytes(sendMsg,"UTF-8"))
                    self.mines.remove(eachMine)
    #                 
    #     for eachID in self.players:
    #         player1=self.players[eachID]
    #         for eachID2 in self.players:
    #             if (eachID2!=eachID):
    #                 player2=self.players[eachID]
    #             if (heuristics(player1.posX,player1.posY,player2.posX,player.posY)<80):
    #                 player2.health-=player1.collision
    #                 for client in clients:
    #                     sendMsg="lessHealth"+" "+str(eachID2)+" "+str(eachPlayer.health)+"\n"
    #                     clients[clientID].send(bytes(sendMsg,"UTF-8"))
    #             
    
    
    #receive the messsage from the client and process to send back         
    def threaded_client(self,client,channel,clientID,clients):
        msg=""
        client.setblocking(1)
        while True:
            rlist,wlist,xlist=select.select([client],[],[])
            if (len(rlist)>0):
                try:
                    msg+=client.recv(512).decode('UTF-8')
                    actualMsg=msg.split("\n")
                
                
                    while (len(actualMsg)>1):
                        readyMsg=actualMsg[0]
                        msg="\n".join(actualMsg[1:])
                        serverChannel.put(str(clientID)+"_"+readyMsg)
                        actualMsg=msg.split("\n")
                        
                except:
                    clients.pop(clientID)
                    return
                    
                    
    def sendToAll(self):
        posMsg=""
        for eachID in self.players:
            player=self.players[eachID]
            posMsg+="pos %d"%eachID+" "+"%d %d %d"%(player.posX,player.posY,player.angle)+"\n"
        for clientID in clients:
            clients[clientID].send(bytes(posMsg,"UTF-8"))
        
    def serverThread(self,clients,serverChannel):
        while True:
            msg=serverChannel.get(True,None)
            msgProcess=msg.split("_")
            senderID=int(msgProcess[0])
            useless=len(msgProcess[0])+1
            realMsg=msg[useless:]
            self.leftClient=[]
            if (msg):
                for clientID in clients:
                    if (clientID!=senderID):
                        if (data1.start==True):
                            if (realMsg.startswith("readyState")):
                                sendMsg="state" +" "+str(senderID)+" " +realMsg[11:]+"\n"
                                clients[clientID].send(bytes(sendMsg,"UTF-8"))
                            elif (realMsg.startswith("ship")):
                                sendMsg="inf" +" "+str(senderID)+" " +realMsg[5:]+"\n"
                                clients[clientID].send(bytes(sendMsg,"UTF-8"))
                                # info=realMsg.split(" ")
                                # name,posX,posY,image=str(info[1]),int(info[2]),int(info[3]),str(info[4])
                                # self.players[senderID]=playerShip(name,posX,posY,image)
                            elif (realMsg.startswith("game")):
                                data1.start=False 
                        else:
                            if (realMsg.startswith("Start")):
                               
                                real=realMsg[6:]
                                
                                sendMsg="start" +" "+str(senderID)+" " +real+"\n"
                                clients[clientID].send(bytes(sendMsg,"UTF-8")) 
                                # player=self.players[senderID]
                                # real=real.split()
                                # action=str(real[0])
                           
                                # if (action=="Acc"):
                                #  
                                #     player.accler=True 
                                #     player.decler=False 
                                #     
                                # elif (action=="Dec"): 
                                #     player.accler=False 
                                #     player.decler=True   
                                # elif (action=="Right"):
                                # 
                                #     player.right=True 
                                #     player.left=False  
                                #  
                                # elif (action=="Left"): 
                                #     player.left=True 
                                #     player.right=False
                            elif (realMsg.startswith("Stop")):
                                real=realMsg[5:]
                                sendMsg="stop" +" "+str(senderID)+" " +real+"\n"
                                clients[clientID].send(bytes(sendMsg,"UTF-8"))
                                # player=self.players[senderID]
                                # real=real.split()
                                # action=str(real[0])
                             
  #                             #   if (action=="Acc"): 
                                #    
                                #     player.accler=False 
                                # elif (action=="Dec"): player.decler=False   
                                # elif (action=="Right"): player.right=False 
                                # elif (action=="Left"): player.left=False 
                                # 
                                
                                
                            elif (realMsg.startswith("Upgrade")):
                                real=realMsg[8:]
                                sendMsg="upg" +" "+str(senderID)+" " +real+"\n"
                                clients[clientID].send(bytes(sendMsg,"UTF-8"))
                                # player=self.players[senderID]
                                # real=real.split()
                                # upgrade=str(real[0])
                                # if (upgrade=="Hull"): player.upgradeHull()
                                # elif (upgrade=="Range"): player.upgradeRange()
                                # elif (upgrade=="Turn"): player.upgradeTurn()
                                # elif (upgrade=="Speed"): player.upgradeSpeed()
                                # elif(upgrade=="Collision"): player.upgradeCollision()
                                # elif(upgrade=="Reload"): player.upgradeReload()
                                # elif(upgrade=="Recover"): player.upgradeRecover()
                                # elif (upgrade=="Damage"): player.upgradeDamage()
                                # 
                                
                            elif (realMsg.startswith("Shoot")):                 
                                sendMsg = "sho "+" "+str(senderID) + " " + realMsg[6:] + "\n"
                                clients[clientID].send(bytes(sendMsg,"UTF-8"))
                                realMsg=realMsg.split()             
                                # pbulX,pbulY=int(realMsg[1]),int(realMsg[2])
                                # pbulDir=int(realMsg[3])
                                # pbulMove=int(realMsg[4])
                                # pbulDmg=int(realMsg[5])
                                # pName=str(realMsg[6])
                                # buldata1=[[pbulX,pbulY],pbulDir,pbulMove,pbulDmg,pName]
                                # self.bullet.append(buldata1)
                                
                            elif (realMsg.startswith("chat")):
                                sendMsg="msg"+" "+ str(senderID) + " "+realMsg[5:]+"\n"
                                clients[clientID].send(bytes(sendMsg,"UTF-8"))
                               
                            elif (realMsg.startswith("Mine")):
                                sendMsg = "mn "+" "+str(senderID) + " " + realMsg[5:] + "\n"
                                clients[clientID].send(bytes(sendMsg,"UTF-8"))   
                                realMsg=realMsg.split()
                                # pMineX=int(realMsg[1])
                                # pMineY=int(realMsg[2])
                                # pName=str(realMsg[3])
                                # pDmg=int(realMsg[4])
                                # mndata1=((pMineX,pMineY),pName,pDmg)
                                # self.mines.append(mndata1)  
                            elif (realMsg.startswith("leave")):
                                sendMsg = "leave" +" " +str(senderID) + " "+realMsg[5:]+"\n"
                                clients[clientID].send(bytes(sendMsg,"UTF-8"))   
                                realMsg=realMsg.split()
                                self.leftClient.append(int(senderID))
            for each in self.leftClient:
                del clients[each]
            serverChannel.task_done()
            
            
            
myserver=gameServer()     
clients={}
curID=0  
serverChannel=Queue(100)

threading.Thread(target = myserver.serverThread,args = (clients, serverChannel)).start()
# get player information 
def clientThread(curID,clients,serverChannel):
    while True:
        client,addr=server.accept()
        for clientID in clients:
            client.send(("newPlayer %d\n"%clientID).encode())
            clients[clientID].send(("newPlayer %d\n"%curID).encode())
        clients[curID]=client 
    
        threading.Thread(target = myserver.threaded_client, args = 
                            (client ,serverChannel, curID, clients)).start()
        curID+=1 

threading.Thread(target = clientThread,args = (curID,clients,serverChannel)).start()

def main():
    while True: 
        clock.tick(60)
        if (data1.start==False):
            #game server events 
            data1.elapsed+=1 
            # myserver.sendToAll()
            myserver.coinGen()
            # myserver.centralPos()
            # myserver.centralCondition()
            # myserver.collisionCheck()
if __name__ == '__main__':
    main()
