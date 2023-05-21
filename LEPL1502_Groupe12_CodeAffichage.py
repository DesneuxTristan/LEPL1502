import pygame as py
from pygame import Rect
import serial as s
import time

class timer:

    def __init__(self,max=10) -> None:

        print('sending: Start')
        self.arduino=s.Serial(port='COM3',baudrate=9600,timeout=1)
        time.sleep(5)
        self.arduino.write('Start'.encode('utf-8'))

        self.ardBoard=[False for a in range(16)]

        self.clock= py.time.Clock()
        self.first= Timer(max)
        self.current = self.first
        self.first.other=Timer(max)
        self.first.other.other=self.first
        self.t0=None

        self.running= False
        self.window=py.display.set_mode((960,520))

        py.font.init()
        self.font=py.font.Font('arial.ttf',size=45)
        self.tend=0
        self.currentcolor='b'
        self.window=py.display.set_mode((960,640))

        self.Board= Board()

        self.BoardImage=py.Surface((514,514))
        self.BoardImage.fill('grey30',Rect(1,1,513,513))
        for b in range(8):
            for a in range(4):
                self.BoardImage.fill('beige',Rect((2*a+b%2)*64+1,b*64+1,64,64))

        self.PiecesImage=py.Surface((514,514))

        self.selected=py.Surface((64,64))
        self.selected.fill('yellow')
        self.selected.set_alpha(180)

        self.inAir=None
        self.initialcase=()
        self.selectedcase=()

    def process(self) -> None:
        
        if self.arduino.in_waiting>0:
            #b = self.arduino.read(2)
            #data = int.from_bytes(b, 'big')
            data = int.from_bytes(self.arduino.read(2),'big')
            #print(bin(data))

            for i in range(16):
                self.ardBoard[i]= ((data>>i)&1==1)
            #print(self.ardBoard)
            self.Dif(self.Board.board,self.ardBoard)


        input=False

        for event in py.event.get():

            if event.type == py.QUIT:
                self.running = True
                break

            elif event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    self.running = True
                    break
                elif event.key == py.K_RETURN:
                    input=True
        
        if self.t0 == None:
            if input==True:
                self.change()
            self.update()
            if self.initialcase and self.selectedcase:
                self.Board.change(self.initialcase,self.selectedcase)
                self.change()
                self.initialcase=()
                self.selectedcase=()

    def render(self) -> None:
        # timer text
        self.window.fill('white')
        self.text=('Blancs : '+ (str(self.current) if self.current==self.first else str(self.current.other)) )+'     ' + \
            ('Noirs : '+ (str(self.current) if self.current.other==self.first else str(self.current.other)))
        x=self.font.size(self.text)[0]
        self.window.blit(self.font.render(self.text,True,'black','white'),(self.window.get_width()/2-x/2,10))

        # board update
        self.PiecesImage.blit(self.BoardImage,(0,0))

        if self.initialcase:
            self.PiecesImage.blit(self.selected,self.initialcase)

        self.Board.render(self.PiecesImage)

        self.window.blit(self.PiecesImage,(self.window.get_size()[0]/2-self.PiecesImage.get_size()[0]/2,75))

        # end of game (à corriger)
        if self.t0!=None:
            self.end()

        py.display.flip()

    def change(self) -> None:
        self.current = self.current.other
        self.currentcolor='b' if self.currentcolor=='n' else 'n'
    
    def IsmouseInBoard(self) -> bool:
        return Rect(self.window.get_size()[0]/2-self.BoardImage.get_size()[0]/2,76,self.BoardImage.get_size()[0]-2,self.BoardImage.get_size()[1]-2).collidepoint(py.mouse.get_pos()[0],py.mouse.get_pos()[1])
    
    def getcase(self,coord) -> tuple:
        return (int((coord[0]-1)//64),int((coord[1]-1)//64))
    
    def update(self) -> None:
        if self.current.clock>0 :
            self.current.clock-=1/60
        else :
            self.t0=self.current
            self.tend=0
    
    def Dif(self,initial,final):
        print(self.inAir)
        for a in range(len(initial)):
            if initial[a]!= final[a]:
                if final[a]==None:
                    if self.inAir==None:
                        self.inAir=initial[a]
                        self.initialcase=(a//4,a%4)
                        return
                else :
                    self.Board.board[a]=self.inAir
                    self.inAir=None
                    self.selectedcase=(a//4,a%4)
                    return

class Board:
    def __init__(self) -> None:

        self.board=[None for a in range(16)]
        self.board[0]='Tourn'

        self.prevboard=self.board

        self.sprites={}

        self.sprites[None]=None
        self.sprites['Cavalierb']=py.image.load('wN.png')
        self.sprites['Cavaliern']=py.image.load('bN.png')
        self.sprites['Tourn']=py.image.load('bR.png')
        self.sprites['Tourb']=py.image.load('wR.png')
        self.sprites['Foun']=py.image.load('bB.png')
        self.sprites['Foub']=py.image.load('wB.png')
        self.sprites['Renen']=py.image.load('bQ.png')
        self.sprites['Reneb']=py.image.load('wQ.png')
        self.sprites['Roin']=py.image.load('bK.png')
        self.sprites['Roib']=py.image.load('wK.png')
        self.sprites['Pionn']=py.image.load('bP.png')
        self.sprites['Pionb']=py.image.load('wP.png')

        self.lastMoved = [None,False]

    def __eq__(self, __value: list) -> bool:
        return self.board!=__value
    
    def render(self,board: py.Surface):
        for a in range(len(self.board)):
            t=self.board[a]
            if t != None:
                board.blit(self.sprites[t],(64*(a%4),64*(a//4)))

    def change(self,initial,final):
        piece= self.getpiece(initial)
        if piece[-1]=='b':
            self.lastMoved=[final,(initial[0]==final[0] and final[1]-initial[1]==2)]
        else:
            self.lastMoved=[final,(initial[0]==final[0] and initial[1]-final[1]==2)]
        self.board[final[1]*8+final[0]]=self.board[initial[1]*8+initial[0]]
        self.board[initial[1]*8+initial[0]]=None

    def isvalid(self,initial,final,color) -> bool:
        piece=self.getpiece(initial)

        if piece[-1]!=color:
            return False
        
        if piece[:-1]=='Pion':
            if piece[-1]=='b':
                a1= (initial[0],initial[1]-1)==final and self.getpiece(final)==None
                a2= (initial[0]+1,initial[1]-1)==final and self.getpiece(final) != None and self.getpiece(final)[-1]=='n'
                a3= (initial[0]-1,initial[1]-1)==final and self.getpiece(final) != None and self.getpiece(final)[-1]=='n'
                a4= (initial[0],4)==final and self.getpiece((final[0],5))==None and self.getpiece(final)==None

                return a1 or a2 or a3 or a4
            
            else:
                a1= (initial[0],initial[1]+1)==final and self.getpiece(final)==None
                a2= (initial[0]+1,initial[1]+1)==final and self.getpiece(final) != None and self.getpiece(final)[-1]=='b'
                a3= (initial[0]-1,initial[1]+1)==final and self.getpiece(final) != None and self.getpiece(final)[-1]=='b'
                a4= (initial[0],3)==final and self.getpiece((final[0],2))==None and self.getpiece(final)==None

                return a1 or a2 or a3 or a4
            
        elif piece[:-1]=='Tour':
            if piece[-1]=='b':
                return self.collisionLigne(initial,final) and (self.getpiece(final) == None or self.getpiece(final)[-1]=='n')
            else:
                return self.collisionLigne(initial,final) and (self.getpiece(final) == None or self.getpiece(final)[-1]=='b')
        
        elif piece[:-1]=='Fou':
            if piece[-1]=='b':
                return self.collisionDiago(initial,final) and (self.getpiece(final) == None or self.getpiece(final)[-1]=='n')
            else:
                return self.collisionDiago(initial,final) and (self.getpiece(final) == None or self.getpiece(final)[-1]=='b')
        
        elif piece[:-1]=='Rene':
            if piece[-1]=='b':
                return (self.collisionDiago(initial,final) or self.collisionLigne(initial,final)) and (self.getpiece(final) == None or self.getpiece(final)[-1]=='n')
            else:
                return (self.collisionDiago(initial,final) or self.collisionLigne(initial,final)) and (self.getpiece(final) == None or self.getpiece(final)[-1]=='b')

        elif piece[:-1]=='Roi':
            if piece[-1]=='b':
                return (initial[0]-final[0])**2<=1 and (initial[1]-final[1])**2<=1 and (self.getpiece(final) == None or self.getpiece(final)[-1]=='n')
            else:
                return (initial[0]-final[0])**2<=1 and (initial[1]-final[1])**2<=1 and (self.getpiece(final) == None or self.getpiece(final)[-1]=='b')

        elif piece[:-1]=='Cavalier':
            if piece[-1]=='b':
                if (initial[0]-final[0])**2==1:
                    if (initial[1]-final[1])**2==4:
                        return (self.getpiece(final) == None or self.getpiece(final)[-1]=='n')
                if (initial[1]-final[1])**2==1:
                    if (initial[0]-final[0])**2==4:
                        return (self.getpiece(final) == None or self.getpiece(final)[-1]=='n')
            else:
                if (initial[0]-final[0])**2==1:
                    if (initial[1]-final[1])**2==4:
                        return (self.getpiece(final) == None or self.getpiece(final)[-1]=='b')
                if (initial[1]-final[1])**2==1:
                    if (initial[0]-final[0])**2==4:
                        return (self.getpiece(final) == None or self.getpiece(final)[-1]=='b')    

    def getpiece(self,coord) -> str:
        return self.board[coord[1]*4+coord[0]]
    
    def collisionLigne(self,initial,final) -> bool:
        if initial[0]==final[0]:
            if final[1]>initial[1]:
                for a in range(1,final[1]-initial[1]):
                    if self.getpiece((initial[0],initial[1]+a)):
                        return False
                return True
            elif final[1]<initial[1]:
                for a in range(1,initial[1]-final[1]):
                    if self.getpiece((initial[0],initial[1]-a)):
                        return False
                return True
        elif initial[1]==final[1]:
            if final[0]>initial[0]:
                for a in range(1,final[0]-initial[0]):
                    if self.getpiece((initial[0]+a,initial[1])):
                        return False
                return True
            elif final[0]<initial[0]:
                for a in range(1,initial[0]-final[0]):
                    if self.getpiece((initial[0]-a,initial[1])):
                        return False
                return True
            
        return False

    def collisionDiago(self,initial,final) -> bool:
        if (final[1]-initial[1])==(final[0]-initial[0]):
            if final[1]>initial[1]:
                for a in range(1,final[1]-initial[1]):
                    if self.getpiece((initial[0]+a,initial[1]+a)):
                        return False
                return True
            elif final[1]<initial[1]:
                for a in range(1,initial[1]-final[1]):
                    if self.getpiece((initial[0]-a,initial[1]-a)):
                        return False
                return True
        elif (final[1]-initial[1])==-(final[0]-initial[0]):
            if final[1]>initial[1]:
                for a in range(1,final[1]-initial[1]):
                    if self.getpiece((initial[0]-a,initial[1]+a)):
                        return False
                return True
            elif final[1]<initial[1]:
                for a in range(1,initial[1]-final[1]):
                    if self.getpiece((initial[0]+a,initial[1]-a)):
                        return False
                return True
        return False

class Timer:
    def __init__(self,max):
        self.clock=max*60
        self.other=None
    def __str__(self):
        c=self.clock
        hour=(str(int(c//3600))+":" if c//3600>0 else "")
        min= (str(int(c//60%60))+ ":" if c//60%60>=10 else ("0"+str(int(c//60%60))+':' if c%60>0 else ("00:" if hour!="" else "")))
        sec= (str(c%60%60)[:5] if c%60%60!=0 and c%60%60>10 else ("0"+str(c%60%60)[:4] if (min!="" and c%60%60>0) else "00.0")) +('0'if c-int(c)==0 else '')
        return hour+min+sec
a=0
t = timer()

while not t.running:
    a+=1
    t.render()
    t.process()
    t.clock.tick(60)

t.arduino.write('Stop'.encode('utf-8'))
time.sleep(2)
t.arduino.close()