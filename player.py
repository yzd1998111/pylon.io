class Ship:
    def __init__(self,name,color):
        self.color=color
        self.name=name
        self.speed=8
        self.turn=6
        self.Hull=100
        self.recover=1
    def __hash__(self):
        return hash(self.color,self.name)
        
class battleShip(Ship):
    def __init__(self,name,color):
        super().__init__(name,color)
        self.range=3
        self.dmg=10
        self.reload=8
        self.collision=3
        
class playerShip(Ship):
    def __init__(self,name,color):
        super().__init__(name,color)
        self.equip=[]
        self.level=1
        self.exp=0
        self.upgrade=0
        self.range=20
        self.dmg=10
        self.recover=1
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
        self.speedLev=0
        self.turnLev=0
        self.collisionLev=0
        self.angle=0
        (self.posX,self.posY)=(500,500)
        self.ready=True 
        self.left,self.right=False,False
        self.destination=None
        self.solutions=[]
        self.elapsed=0
    def upgradeHull(self):
        self.Hull+=30
        self.spped-=1
    def upgradeSpeed(self):
        self.speed+=2
    def upgradeTurningSpeed(self):
        self.turn+=1
    def upgradeRecover(self):
        self.recover+=2
    def upgradeDamage(self):
        self.dmg+=5
    def upgradeReload(self):
        self.reload*=0.9
    def upgradeCollision(self):
        self.collision+=3
    def upgradeRange(self):
        self.range+=1
    def upgradeTurn(self):
        self.turn+=0.5
    def addExp(self,m):
        self.exp+=m
    def getExp(self):
        return (self.exp//(300*self.level))
    def addEquip(self,weapon):
        self.equip.append(weapon)
        
class enemey(playerShip):
    def __init__(self,name,color):
        super().__init__(name,color)
        self.state=xxxx
        
