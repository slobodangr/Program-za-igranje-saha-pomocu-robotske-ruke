# Импортовање основних библиотека и модула
import chess as sah
import math as math
import random as rd
import pygame as PY
import time as tm
import chess.polyglot
import chess.gaviota
from robodk import robolink     # type: ignore
from robodk import robomath     # type: ignore
RDK = robolink.Robolink()
robot=RDK.Item("robot")
brojac_pojedenih_bijele=0
brojac_pojedenih_crne=0
#-----------------------------------------------------------------------------------------------------------------------------------------Klasa sahEngine
# Класа ChessEngine
class sahEngine:
    # Konstruktor klase ChessEngine
    def __init__(self,sahovska_tabla,dubina_pretrazivanja,boja_figura):
        self.sahovska_tabla=sahovska_tabla                              
        self.dubina_pretrazivanja=dubina_pretrazivanja
        self.boja_figura=boja_figura 
#---------------------------------------------------------------------------------------------------------------
# Главна функција за евалуацију позиције
    def evaluacija_pozicije(self):
        vrijednost=0
        for i in range(64):
            vrijednost+=self.vrijednost_figura(sah.SQUARES[i])
        return vrijednost+self.provjera_mata()+0.001*rd.random()+self.provjera_centralnih_polja()+self.provjer_stalemate()
#---------------------------------------------------------------------------------------------------------------
# Функција која позива Minimax функцију са почетним параметрима
    def najboljiPotez(self):
        return self.Minimax(None, 1)
#---------------------------------------------------------------------------------------------------------------
# Функција која провјерава контролу централних поља
    def provjera_centralnih_polja(self):
        vrijednost_centralnih_polja = 0
        centralna_polja = [sah.D4, sah.E4, sah.C4, sah.F4, sah.D5, sah.C5, sah.F5, sah.E5]
        for polje in centralna_polja:
            if self.sahovska_tabla.is_attacked_by(self.boja_figura, polje):
                vrijednost_centralnih_polja += 0.05
            if self.sahovska_tabla.is_attacked_by(not self.boja_figura, polje):
                vrijednost_centralnih_polja -= 0.05
        return vrijednost_centralnih_polja
#---------------------------------------------------------------------------------------------------------------
    # Функција која враћа евалуацију позиције ако је на шаховској табли пет или мање фигура, укључујући краљеве
    def gaviot_tablebase(self):
        evaluacija=None
        putanja=r"C:\Users\Korisnik\Desktop\3-4-5"
        provjer_rohade=False
        # Провјера да ли су извршене рохаде
        if self.sahovska_tabla.has_kingside_castling_rights(chess.WHITE) or \
           self.sahovska_tabla.has_queenside_castling_rights(chess.WHITE):
            provjer_rohade=True
        elif self.sahovska_tabla.has_kingside_castling_rights(chess.BLACK) or \
             self.sahovska_tabla.has_queenside_castling_rights(chess.BLACK):
            provjer_rohade=True
        else:
            provjer_rohade=False
        if provjer_rohade==False and sah.popcount(self.sahovska_tabla.occupied)<=5:
            # Отварање датотеке са шаховским завршницама
            try:
                with chess.gaviota.open_tablebase(putanja) as tablebase:
                    # Број потеза да се оствари мат у позицији (ако је могуће)
                    rezultat = tablebase.probe_dtm(self.sahovska_tabla)
                    # Рачунање евалуације
                    if rezultat>0:
                        evaluacija=1000-rezultat
                    elif rezultat<0:
                        evaluacija=-1000-rezultat
                    else:
                        evaluacija=0
                    return evaluacija if self.sahovska_tabla.turn == self.boja_figura \
                           else -evaluacija
            except chess.gaviota.MissingTableError:
                return None
#---------------------------------------------------------------------------------------------------------------
# Функција која провјера да ли је на шаховској табли дошло до мата       
    def provjera_mata(self):
        if (self.sahovska_tabla.is_checkmate()==True):
            if(self.sahovska_tabla.turn==self.boja_figura):
                return -1000
            else:
                return 1000
        else:
            return 0
#---------------------------------------------------------------------------------------------------------------
# Функција која провјера да ли је на шаховској табли дошло до пата     
    def provjer_stalemate(self):
        if (self.sahovska_tabla.is_stalemate()==True):
            if(self.sahovska_tabla.turn==self.boja_figura):
                return 0
            else:
                return -500
        return 0
#---------------------------------------------------------------------------------------------------------------
# Функција која има улогу да врати вриједност фигуре која се налази на одређеном шаховском пољу
    def vrijednost_figura(self,polje):# Шаховско поље се просљеђује као аргумент
        vrijednost_fig=0
        #Додјељивање вриједности промјењивој vrijednost_fig у зависности од типа фигуре
        if (self.sahovska_tabla.piece_type_at(polje)==sah.PAWN):
            vrijednost_fig=1
        elif(self.sahovska_tabla.piece_type_at(polje)==sah.KNIGHT):
            vrijednost_fig=3
        elif(self.sahovska_tabla.piece_type_at(polje)==sah.BISHOP):
            vrijednost_fig=3
        elif(self.sahovska_tabla.piece_type_at(polje)==sah.ROOK):
            vrijednost_fig=5
        elif(self.sahovska_tabla.piece_type_at(polje)==sah.QUEEN):
            vrijednost_fig=9
        #Враћање позитивне вриједности у случају када боја фигуре одговара боји рачунара
        if (self.sahovska_tabla.color_at(polje))!=self.boja_figura:
            return -vrijednost_fig
        else:
            return vrijednost_fig
#---------------------------------------------------------------------------------------------------------------
# Функција Minimax служи за проналажење најбољег потеза за одређену шаховску позицију и у њој је имплеметиран минимакс алгоритам
    def Minimax(self,current_eval,dubina):
        najbolji_potez=None
        '''Bazni uslov minimaks funckije[1]'''
        if (dubina==self.dubina_pretrazivanja or self.sahovska_tabla.legal_moves.count()==0):
            return self.evaluacija_pozicije()
        lista_legalnih_poteza=list(self.sahovska_tabla.legal_moves)
        '''Naizmjenicno prebacivanje igraca i inicijalizacija promjenjive
        novi_current_eval koja ima ulogu cuvanje najbolje vrijednosti
        evaluacije za svaki nivo pretrazivanja'''
        novi_current_eval=0
        if (dubina%2!=0):
            novi_current_eval=float(-math.inf)
        else:
            novi_current_eval=float(math.inf)
        '''Simulacija igre i gradjenje stabla poteza, pri cemu se na
        svakom nivou porede najbolje vrijednosti koje se vracaju u
        roditeljski cvor'''
        for potez in lista_legalnih_poteza:
            self.sahovska_tabla.push(potez)
            evaluacija=self.Minimax(novi_current_eval,dubina+1)
            if (evaluacija>novi_current_eval and dubina%2!=0):
                if(dubina==1):
                    najbolji_potez=potez 
                novi_current_eval=evaluacija
            elif(evaluacija<novi_current_eval and dubina%2==0):
                novi_current_eval=evaluacija
            '''Optimizacija minimaks algoritma'''
            '''Igrac koji maksimizira prvi na potezu'''
            if (current_eval!=None and evaluacija<current_eval and dubina%2==0):
                self.sahovska_tabla.pop()
                break
            '''Igrac koji minimizra prvi na potezu'''
            if (current_eval!=None and evaluacija>current_eval and dubina%2!=0):
                self.sahovska_tabla.pop()
                break
            self.sahovska_tabla.pop()
        '''Povratne vrijendosti Minimax funckije'''
        if (dubina>1):
            return novi_current_eval
        else:
            return najbolji_potez
        
#---------------------------------------------------------------------------------------------------------------------------------klasa Igra  
class Igra:
# Конструктор класе Igra
# Oсновни атрибути ове класу су: шаховска табла, величина поља, димензије плоче, слике фигура и плоча. Класа садржи и једну методу, која се назива crtanje_table().
    def __init__(self,sahovska_tabla=sah.Board()):
        self.sahovska_tabla=sahovska_tabla
        self.velicina_polja=80
        self.dimenzije_ploce=self.velicina_polja*8
        self.slike=self.ucitaj_slike(self.velicina_polja)
# Функција set_mode()се користи за креирање графичког прозора (екрана) који ће представљати шаховску плочу
        self.ploca=PY.display.set_mode((self.dimenzije_ploce,self.dimenzije_ploce))
        PY.display.set_caption("Sah")
        self.crtanje_table()
#---------------------------------------------------------------------------------------------------------------
# Функција ucitaj_slike() има улогу да се направи рјечник (енг. dictionary) од учитаних слика, односно да се свакој слици придружи одговарајућа ознака (кључ)
    def ucitaj_slike(self,velicina):
        slike={} #dictionary, pravi se lista slika sa odgovarajucim kljucevima i vrijednostima
        oznake_figura=['P','N','B','R','Q','K','p','n','b','r','q','k']
        slike[oznake_figura[0]]=PY.image.load(r"C:\Users\Korisnik\Desktop\KOD_DIPLOMSKI\sah_figure\P.png")
        slike[oznake_figura[1]]=PY.image.load(r"C:\Users\Korisnik\Desktop\KOD_DIPLOMSKI\sah_figure\N.png")
        slike[oznake_figura[2]]=PY.image.load(r"C:\Users\Korisnik\Desktop\KOD_DIPLOMSKI\sah_figure\B.png")
        slike[oznake_figura[3]]=PY.image.load(r"C:\Users\Korisnik\Desktop\KOD_DIPLOMSKI\sah_figure\R.png")
        slike[oznake_figura[4]]=PY.image.load(r"C:\Users\Korisnik\Desktop\KOD_DIPLOMSKI\sah_figure\Q.png")
        slike[oznake_figura[5]]=PY.image.load(r"C:\Users\Korisnik\Desktop\KOD_DIPLOMSKI\sah_figure\K.png")
        slike[oznake_figura[6]]=PY.image.load(r"C:\Users\Korisnik\Desktop\KOD_DIPLOMSKI\sah_figure\PC.png")
        slike[oznake_figura[7]]=PY.image.load(r"C:\Users\Korisnik\Desktop\KOD_DIPLOMSKI\sah_figure\NC.png")
        slike[oznake_figura[8]]=PY.image.load(r"C:\Users\Korisnik\Desktop\KOD_DIPLOMSKI\sah_figure\BC.png")
        slike[oznake_figura[9]]=PY.image.load(r"C:\Users\Korisnik\Desktop\KOD_DIPLOMSKI\sah_figure\RC.png")
        slike[oznake_figura[10]]=PY.image.load(r"C:\Users\Korisnik\Desktop\KOD_DIPLOMSKI\sah_figure\QC.png")
        slike[oznake_figura[11]]=PY.image.load(r"C:\Users\Korisnik\Desktop\KOD_DIPLOMSKI\sah_figure\KC.png")
        for oznaka in oznake_figura:
            # Скалирање фигура на димензију поља
            slike[oznaka]=PY.transform.scale(slike[oznaka],(velicina,velicina))
        return slike
#---------------------------------------------------------------------------------------------------------------
# Функција за цртање шаховске табле
    def crtanje_table(self):
        boje_polja=[(255,255,255),(128,128,128)]
        for red in range(8):
            for kolona in range(8):
                # Окретање плоче (бијеле фигуре на доњој страни)
                novi_red=7-red
                trenutna_boja=boje_polja[(red+kolona)%2]
                # Цртање шаховског поља (функција pygame.draw.rect())
                PY.draw.rect(self.ploca,trenutna_boja,PY.Rect(kolona*self.velicina_polja,\
                red*self.velicina_polja,self.velicina_polja,self.velicina_polja))
                # Провјера да ли се фигура налази на шаховском пољу
                figura=self.sahovska_tabla.piece_at(sah.square(kolona,novi_red))
                if figura:
                    slika_figura=self.slike[str(figura)]
                    # Функција blit()служи за приказивање једног објекта преко другог (слика фигура на шаховској плочи)
                    self.ploca.blit(slika_figura,(kolona*self.velicina_polja,red*self.velicina_polja))
        # Функција flip() се користи за освјежавање комплетног приказа на екрану. Ово је кључно за приказивање промјена које су се направиле на екрану током игре.
        PY.display.flip()
#---------------------------------------------------------------------------------------------------------------
''' Функција која враћа бројчану вриједнoст (индекс) поља на којем се налази курсор миша. У chess библиотеци,
шаховска табла је представљена матрицом од 64 поља, нумерисаним од 0 до 63. Аргумент ове функије је позиција
курсора која је представљена као tuple(координатe (x,y))'''
    def detekcija_poteza(self,pozicija_kursora):
        sahovska_tabla_red=pozicija_kursora[1]//self.velicina_polja
        sahovska_tabla_kolona=pozicija_kursora[0]//self.velicina_polja
        nova_kolona,novi_red=self.transformacija_koordinata(sahovska_tabla_kolona,sahovska_tabla_red)
        # Функција sah.square() претвара колону и ред у индекс поља
        return sah.square(nova_kolona,novi_red)
#---------------------------------------------------------------------------------------------------------------
''' Функција transformacija_koordinata() служи за трансформацију координатног система графичког прозора у Pygame-у 
(почетак у горњем лијевом углу) у координатни систем шаховске табле (почетак у доњем десном углу). 
Ова трансформација је неопходна за правилно представљање шаховских потеза на графичком прозору у Pygame-у.'''
    def transformacija_koordinata(self,x, y):
        pygame_x = x
        pygame_y = 7 - y
        return pygame_x, pygame_y
#---------------------------------------------------------------------------------------------------------------
# Функција prikaz_legalnih_poteza() има улогу да се означе сви легални потези за селектовану фигуру
    def prikaz_legalnih_poteza(self,polje):
        legalni_potezi=list(self.sahovska_tabla.legal_moves)
        legalna_polja=[]
        for potez in legalni_potezi:
            # Провјера који легални потези почињу из селектованог поља
            # from_square враћа цјелобројни индекс почетног поља за одговарајући потез
            if potez.from_square==polje:
                # to_square враћа цјелобројни индекс који представља одредишно поље на шаховској табли за одређени потез
                legalna_polja.append(potez.to_square)
        for polje in legalna_polja:
            kolona=polje%8
            red=7-polje//8
            # Цртање круга на свим шаховским пољима на којa је могуће доћи са селектованом фигуром
            centar_kruznice=((kolona*self.velicina_polja)+self.velicina_polja//2,\
            (red*self.velicina_polja)+self.velicina_polja//2)
            PY.draw.circle(self.ploca,(102,178,255),centar_kruznice,self.velicina_polja//8)
#---------------------------------------------------------------------------------------------------------------
# Функција за одлагање поједених фигура у симулацији (софтвер RoboDK)
    def ostavljanje_pojedenih_figura(self,figura_napadnuta,pojedena_figura,koordinatni_sistem_odlaganje_bijele,koordinatni_sistem_odlaganje_crne):
        # Приступ глобалним промјењивима унутар функције (употреба кључне ријечи global)
        # Тренутни број поједених бијелих и црних фигура
        global brojac_pojedenih_bijele
        global brojac_pojedenih_crne
        # Одлагање бијелих поједених фигура
        if figura_napadnuta.color:
            # Везивање поједене фигура за жељени координатни систем помоћу функције setParent
            pojedena_figura.setParent(koordinatni_sistem_odlaganje_bijele)
            translacija_x=25*brojac_pojedenih_bijele
            brojac_pojedenih_bijele+=1
            translacija_y=11
            # Хомогена трансформациона матрица, помјерање по х оси
            matrica_translacije=robomath.Mat(   [[1, 0, 0, translacija_x], 
                                     [0, 0, -1, translacija_y], 
                                     [0, 1, 0, 1], 
                                     [0, 0, 0, 1]])
            # Функција setPose() се користи за постављање положаја и оријентације објекта у софтверу RoboDK
            pojedena_figura.setPose(matrica_translacije)
            # Одлагање црних поједених фигура
        else:
            pojedena_figura.setParent(koordinatni_sistem_odlaganje_crne)
            translacija_x=25*brojac_pojedenih_crne
            brojac_pojedenih_crne+=1
            translacija_y=11
            matrica_translacije=robomath.Mat(   [[1, 0, 0, translacija_x], 
                                     [0, 0, -1, translacija_y], 
                                     [0, 1, 0, 1], 
                                     [0, 0, 0, 1]])
            pojedena_figura.setPose(matrica_translacije)
#---------------------------------------------------------------------------------------------------------------
'''Функција за помјерање фигура помоћу роботске руке у софтверу RoboDK. 
   Аргументи ове функције су: ред и колона селектованог и жељеног поља, 
   селектована и нападнута фигура (ако је нема, вриједност је None).'''
    def pomjeranje_figura(self,red_1,kolona_1,red_2,kolona_2,figura,figura_napadnuta):
        #--------------------------------------------------------------->Lista programa  
        # Таргет представља специфичну позицију и орјентацију коју робот треба да достигне у свом радном простору
        # Tаргет за почетну позицију роботске руке (употреба методе robomath.Pose (x, y, z, rx, ry, rz))
        target_pocetna=robomath.Pose(170,85,130,180,0,-90)
        # Таргети за одлагање пјешака и тешких фигура
        target_ostavljanje_figure=robomath.Pose(165,-110,110,180,0,-90)
        target_ostavljanje_figure_spustanje_1=robomath.Pose(165,-110,38,180,0,-90)
        target_ostavljanje_figure_spustanje_2=robomath.Pose(165,-110,32,180,0,-90)
        # Координатни системи за одлагање поједених фигура
        koordinatni_sistem_odlaganje_bijele=RDK.Item("odlaganje_figura_bijele")
        koordinatni_sistem_odlaganje_crne=RDK.Item("odlaganje_figura_crne")
        # Робот и хватаљка на радној станици
        '''У софтверу RoboDK, медота RDK.Item() служи за приступање објектима из радне станице на основу њиховог имена и типа. 
        Ова метода омогућава корисницима да приступе различитим елементима радне станице, као што су роботи, алати, програми 
        и да њима манипулишу путем Python скрипте.'''
        robot=RDK.Item("robot")
        hvataljka=RDK.Item("Tool_1")
        # Листа програма за отварање и затварање хватаљке који су креирани у софтверу RoboDK
        ispustanje_figure=RDK.Item("ispustanje_figure",robolink.ITEM_TYPE_PROGRAM)
        otvorena_hvataljka_figure=RDK.Item("otvorena_hvataljka_figure",robolink.ITEM_TYPE_PROGRAM)
        zatvorena_hvataljka_12=RDK.Item("zatvorena_hvataljka_12",robolink.ITEM_TYPE_PROGRAM)
        zatvorena_hvataljka_10_5=RDK.Item("zatvorena_hvataljka_10_5",robolink.ITEM_TYPE_PROGRAM)
        zatvorena_hvataljka_14=RDK.Item("zatvorena_hvataljka_14",robolink.ITEM_TYPE_PROGRAM)
        otvorena_hvataljka_51=RDK.Item("otvorena_hvataljka_51",robolink.ITEM_TYPE_PROGRAM)
        #----------------------------------------------------------->Prilazi za pjesake
        ''' Креирање дводимензионалне листе која садржи прилазе изнад пјешаке за сва шаховска поља. 
        Сваки елемент листе садржи 6 параметара, а то су 3 транслације и 3 ротације.'''
        pjesak_prilaz=[]
        lista_prilaza_1=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=90
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_1.append(lista)
            pjesak_prilaz.append(lista_prilaza_1)
            lista_prilaza_1=[]
        #----------------------------------------------------------->Hvatanje pjesaka
        # Креирање дводимензионалне листе која садржи прилазе за пјешаке током њиховог узимања или спуштања
        pjesak_hvatanje=[]
        lista_prilaza_2=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=32
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_2.append(lista)
            pjesak_hvatanje.append(lista_prilaza_2)
            lista_prilaza_2=[]
        #----------------------------------------------------------->Prilaz figure
        # Креирање дводимензионалне листе која садржи прилазе изнад осталих фигура за сва шаховска поља
        figure_prilaz=[]
        lista_prilaza_3=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=110
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_3.append(lista)
            figure_prilaz.append(lista_prilaza_3)
            lista_prilaza_3=[]
        #----------------------------------------------------------->Hvatanje figure
        # Креирање дводимензионалне листе која садржи прилазе за остале фигуре током њиховог узимања или спуштања
        figure_hvatanje=[]
        lista_prilaza_4=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=38
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_4.append(lista)
            figure_hvatanje.append(lista_prilaza_4)
            lista_prilaza_4=[]
        #------------------------------------------------------------->podizanja za slobodna kretanja(manja visina podizanja)                                           
        '''Креирање дводимензионалне листе која садржи ниже прилазе током слободног кретања фигура (нема узимања противничке фигуреи дијагоналног помјерања), 
        како би се избацило непотребно велико подизање. Ово се односи на све фигуре осим ловца и скакача због њиховог сложенијег кретања.'''
        prilaz_slobodno_kretanja=[]
        lista_prilaza_5=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=45
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_5.append(lista)
            prilaz_slobodno_kretanja.append(lista_prilaza_5)
            lista_prilaza_5=[]
        '''Таргети за ниже прилазе током слободног кретања. Аргументи који се просљеђују методи robomath.Pose() су три транслације и ротације 
        које се налазе у дводимензионалној листи (матрици) прилаза за слободно кретања фигура. Приступ одговарајућем елементу листе се врши
        помоћу реда и колоне селектованог шаховског поља.'''
        target_mali_prilaz_1=robomath.Pose(prilaz_slobodno_kretanja[red_1][kolona_1][0],prilaz_slobodno_kretanja[red_1][kolona_1][1],prilaz_slobodno_kretanja[red_1][kolona_1][2],prilaz_slobodno_kretanja[red_1][kolona_1][3],prilaz_slobodno_kretanja[red_1][kolona_1][4],prilaz_slobodno_kretanja[red_1][kolona_1][5])
        target_mali_prilaz_2=robomath.Pose(prilaz_slobodno_kretanja[red_2][kolona_2][0],prilaz_slobodno_kretanja[red_2][kolona_2][1],prilaz_slobodno_kretanja[red_2][kolona_2][2],prilaz_slobodno_kretanja[red_2][kolona_2][3],prilaz_slobodno_kretanja[red_2][kolona_2][4],prilaz_slobodno_kretanja[red_2][kolona_2][5])   
        # Провјера да ли се узима противничка фигура (ако је нема, фигура се помјера на слободно поље)
        if figura_napadnuta is None: #---------------------------------------------------------->Pomicanje figure na slobodno polje
            # Порвјера да ли је селектована фигура пјешак
            if figura and figura.piece_type==sah.PAWN:
                # Таргети за прилаз и хватање пјешака када се помјера на слободно поље
                # Почетно (селектовано) поље
                target_prilaz_1=robomath.Pose(pjesak_prilaz[red_1][kolona_1][0],pjesak_prilaz[red_1][kolona_1][1],pjesak_prilaz[red_1][kolona_1][2],pjesak_prilaz[red_1][kolona_1][3],pjesak_prilaz[red_1][kolona_1][4],pjesak_prilaz[red_1][kolona_1][5])
                target_hvatanje_1=robomath.Pose(pjesak_hvatanje[red_1][kolona_1][0],pjesak_hvatanje[red_1][kolona_1][1],pjesak_hvatanje[red_1][kolona_1][2],pjesak_hvatanje[red_1][kolona_1][3],pjesak_hvatanje[red_1][kolona_1][4],pjesak_hvatanje[red_1][kolona_1][5])
                #Крајње (жељено) поље
                target_prilaz_2=robomath.Pose(pjesak_prilaz[red_2][kolona_2][0],pjesak_prilaz[red_2][kolona_2][1],pjesak_prilaz[red_2][kolona_2][2],pjesak_prilaz[red_2][kolona_2][3],pjesak_prilaz[red_2][kolona_2][4],pjesak_prilaz[red_2][kolona_2][5])
                target_hvatanje_2=robomath.Pose(pjesak_hvatanje[red_2][kolona_2][0],pjesak_hvatanje[red_2][kolona_2][1],pjesak_hvatanje[red_2][kolona_2][2],pjesak_hvatanje[red_2][kolona_2][3],pjesak_hvatanje[red_2][kolona_2][4],pjesak_hvatanje[red_2][kolona_2][5])
                # Дио кода којим се остварује прилаз, узимање и премјештање пјешака са почетног на жељено поље
                # МоveL() је метродa која омогућава линеарно кретање робота до задатог таргета
                robot.MoveL(target_prilaz_1)
                # Функција RunProgram() омогућава да се покрене одређени програм унутар софтвера RoboDK
                otvorena_hvataljka_51.RunProgram()
                '''Функција time.sleep() унутар while петља обезбјеђује да се хватаљка не креће током њеног
                отварања или затварња, односно да се не прелази на идући дио кода док се не изврши програм
                за затварање или отварање хватаљке.'''
                while otvorena_hvataljka_51.Busy():
                    tm.sleep(0.1)
                robot.MoveL(target_hvatanje_1)
                zatvorena_hvataljka_10_5.RunProgram()
                while zatvorena_hvataljka_10_5.Busy():
                    tm.sleep(0.1)
                # Хватање пјешака помоћу функицје AttachClosest () (омогућaва да се пјешак закачи за хватаљку у симулацији)
                hvataljka.AttachClosest()
                robot.MoveL(target_mali_prilaz_1)
                robot.MoveL(target_mali_prilaz_2)
                robot.MoveL(target_hvatanje_2)
                ispustanje_figure.RunProgram()
                otvorena_hvataljka_51.RunProgram()
                while otvorena_hvataljka_51.Busy():
                    tm.sleep(0.1)
                robot.MoveL(target_prilaz_2)
                robot.MoveL(target_pocetna)
            # Случај када се остале фигуре помјерају на слободно поље
            else:
                # Таргети за прилаз и хватање фигура када се помјерају на слободно поље
                # Почетно (селектовано) поље
                target_prilaz_1=robomath.Pose(figure_prilaz[red_1][kolona_1][0],figure_prilaz[red_1][kolona_1][1],figure_prilaz[red_1][kolona_1][2],figure_prilaz[red_1][kolona_1][3],figure_prilaz[red_1][kolona_1][4],figure_prilaz[red_1][kolona_1][5])
                target_hvatanje_1=robomath.Pose(figure_hvatanje[red_1][kolona_1][0],figure_hvatanje[red_1][kolona_1][1],figure_hvatanje[red_1][kolona_1][2],figure_hvatanje[red_1][kolona_1][3],figure_hvatanje[red_1][kolona_1][4],figure_hvatanje[red_1][kolona_1][5])
                # Крајње (жељено) поље
                target_prilaz_2=robomath.Pose(figure_prilaz[red_2][kolona_2][0],figure_prilaz[red_2][kolona_2][1],figure_prilaz[red_2][kolona_2][2],figure_prilaz[red_2][kolona_2][3],figure_prilaz[red_2][kolona_2][4],figure_prilaz[red_2][kolona_2][5])
                target_hvatanje_2=robomath.Pose(figure_hvatanje[red_2][kolona_2][0],figure_hvatanje[red_2][kolona_2][1],figure_hvatanje[red_2][kolona_2][2],figure_hvatanje[red_2][kolona_2][3],figure_hvatanje[red_2][kolona_2][4],figure_hvatanje[red_2][kolona_2][5])
                # Дио кода којим се остварује прилаз, узимање и премјештање осталих фигура са почетног на жељено поље
                robot.MoveL(target_prilaz_1)
                otvorena_hvataljka_figure.RunProgram()
                while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
                robot.MoveL(target_hvatanje_1)
                # Провјера типа фигуре која се врши због позива одговарајућег програма за затврање хватаљке.
                if figura.piece_type==sah.ROOK or figura.piece_type==sah.KING or figura.piece_type==sah.QUEEN:
                    zatvorena_hvataljka_14.RunProgram()
                    while zatvorena_hvataljka_14.Busy():
                        tm.sleep(0.1)
                elif figura.piece_type==sah.KNIGHT or figura.piece_type==sah.BISHOP:
                    zatvorena_hvataljka_12.RunProgram()
                    while zatvorena_hvataljka_12.Busy():
                        tm.sleep(0.1)
                hvataljka.AttachClosest()
                '''Провјера типа фигуре која омогућава оптимизацију кретања робота, смањујући непотребно подизање фигура. 
                У случају даме и краља, нижа подизања су обезбјеђена само за вертикално и хоризонтално помјерање, док се за дијагонално кретање користе виша подизања.'''
                if figura.piece_type==sah.ROOK or (figura.piece_type==sah.KING and (red_1==red_2 or kolona_1==kolona_2)) or (figura.piece_type==sah.QUEEN and (red_1==red_2 or kolona_1==kolona_2)):
                    robot.MoveL(target_mali_prilaz_1)
                    robot.MoveL(target_mali_prilaz_2)
                else:
                    robot.MoveL(target_prilaz_1)
                    robot.MoveL(target_prilaz_2)
                robot.MoveL(target_hvatanje_2)
                ispustanje_figure.RunProgram()
                otvorena_hvataljka_figure.RunProgram()
                while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
                robot.MoveL(target_prilaz_2)
                robot.MoveL(target_pocetna)
        # Случај када се узима противничка фигура
        else:
            # Испитивање која фигура је на потезу и која фигура је узета
            # Случај када пјешак узима пјешака
            if figura_napadnuta.piece_type==sah.PAWN:
                if figura and figura.piece_type==sah.PAWN:
                    # Таргети за прилаз и хватање пјешака (почетно и крајње поље)
                    # Почетно (селектовано) поље
                    target_prilaz_1=robomath.Pose(pjesak_prilaz[red_1][kolona_1][0],pjesak_prilaz[red_1][kolona_1][1],pjesak_prilaz[red_1][kolona_1][2],pjesak_prilaz[red_1][kolona_1][3],pjesak_prilaz[red_1][kolona_1][4],pjesak_prilaz[red_1][kolona_1][5])
                    target_hvatanje_1=robomath.Pose(pjesak_hvatanje[red_1][kolona_1][0],pjesak_hvatanje[red_1][kolona_1][1],pjesak_hvatanje[red_1][kolona_1][2],pjesak_hvatanje[red_1][kolona_1][3],pjesak_hvatanje[red_1][kolona_1][4],pjesak_hvatanje[red_1][kolona_1][5])
                    # Крајње (жељено) поље
                    target_prilaz_2=robomath.Pose(pjesak_prilaz[red_2][kolona_2][0],pjesak_prilaz[red_2][kolona_2][1],pjesak_prilaz[red_2][kolona_2][2],pjesak_prilaz[red_2][kolona_2][3],pjesak_prilaz[red_2][kolona_2][4],pjesak_prilaz[red_2][kolona_2][5])
                    target_hvatanje_2=robomath.Pose(pjesak_hvatanje[red_2][kolona_2][0],pjesak_hvatanje[red_2][kolona_2][1],pjesak_hvatanje[red_2][kolona_2][2],pjesak_hvatanje[red_2][kolona_2][3],pjesak_hvatanje[red_2][kolona_2][4],pjesak_hvatanje[red_2][kolona_2][5])
                    '''Дио кода којим се остварује прилаз и узимање поједеног пјешака, као и његово одлагање. 
                    Након одлагања пјешака, врши се помјерање пјешака са којим је извршено узимање.'''
                    robot.MoveL(target_prilaz_2)
                    otvorena_hvataljka_51.RunProgram()
                    while otvorena_hvataljka_51.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_hvatanje_2)
                    zatvorena_hvataljka_10_5.RunProgram()
                    while zatvorena_hvataljka_10_5.Busy():
                        tm.sleep(0.1)
                    # Узимање и уклањање поједеног пјешака са шаховске табле  
                    pojedena_figura=hvataljka.AttachClosest()
                    robot.MoveL(target_prilaz_2)
                    robot.MoveL(target_ostavljanje_figure)
                    robot.MoveL( target_ostavljanje_figure_spustanje_2)
                    ispustanje_figure.RunProgram()
                    otvorena_hvataljka_51.RunProgram()
                    while otvorena_hvataljka_51.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_ostavljanje_figure)
                    # Везивање поједеног пјешака за координатни систем поједених фигура
                    self.ostavljanje_pojedenih_figura(figura_napadnuta,pojedena_figura,koordinatni_sistem_odlaganje_bijele, koordinatni_sistem_odlaganje_crne)
                    # Помјерање селектованог пјешака након што је уклоњен поједени пјешак
                    robot.MoveL(target_prilaz_1)
                    robot.MoveL(target_hvatanje_1)
                    zatvorena_hvataljka_10_5.RunProgram()
                    while zatvorena_hvataljka_10_5.Busy():
                        tm.sleep(0.1)
                    hvataljka.AttachClosest()
                    robot.MoveL(target_prilaz_1)
                    robot.MoveL(target_prilaz_2)
                    robot.MoveL(target_hvatanje_2)
                    ispustanje_figure.RunProgram()
                    otvorena_hvataljka_51.RunProgram()
                    while otvorena_hvataljka_51.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_prilaz_2)
                    robot.MoveL(target_pocetna)
                # Случај када остале фигуре узимају пјешака
                else:
                    # Таргети за прилаз и хватање фигуре (почетно поље)
                    target_prilaz_1=robomath.Pose(figure_prilaz[red_1][kolona_1][0],figure_prilaz[red_1][kolona_1][1],figure_prilaz[red_1][kolona_1][2],figure_prilaz[red_1][kolona_1][3],figure_prilaz[red_1][kolona_1][4],figure_prilaz[red_1][kolona_1][5])
                    target_hvatanje_1=robomath.Pose(figure_hvatanje[red_1][kolona_1][0],figure_hvatanje[red_1][kolona_1][1],figure_hvatanje[red_1][kolona_1][2],figure_hvatanje[red_1][kolona_1][3],figure_hvatanje[red_1][kolona_1][4],figure_hvatanje[red_1][kolona_1][5])
                    # Таргети за прилаз и хватање поједеног пјешака
                    target_prilaz_2=robomath.Pose(pjesak_prilaz[red_2][kolona_2][0],pjesak_prilaz[red_2][kolona_2][1],pjesak_prilaz[red_2][kolona_2][2],pjesak_prilaz[red_2][kolona_2][3],pjesak_prilaz[red_2][kolona_2][4],pjesak_prilaz[red_2][kolona_2][5])
                    target_hvatanje_2=robomath.Pose(pjesak_hvatanje[red_2][kolona_2][0],pjesak_hvatanje[red_2][kolona_2][1],pjesak_hvatanje[red_2][kolona_2][2],pjesak_hvatanje[red_2][kolona_2][3],pjesak_hvatanje[red_2][kolona_2][4],pjesak_hvatanje[red_2][kolona_2][5])
                    # Таргети за прилаз и хватање фигуре (крајње поље)
                    target_prilaz_1_2=robomath.Pose(figure_prilaz[red_2][kolona_2][0],figure_prilaz[red_2][kolona_2][1],figure_prilaz[red_2][kolona_2][2],figure_prilaz[red_2][kolona_2][3],figure_prilaz[red_2][kolona_2][4],figure_prilaz[red_2][kolona_2][5])
                    target_hvatanje_1_2=robomath.Pose(figure_hvatanje[red_2][kolona_2][0],figure_hvatanje[red_2][kolona_2][1],figure_hvatanje[red_2][kolona_2][2],figure_hvatanje[red_2][kolona_2][3],figure_hvatanje[red_2][kolona_2][4],figure_hvatanje[red_2][kolona_2][5])
                    robot.MoveL(target_prilaz_2)
                    otvorena_hvataljka_51.RunProgram()
                    while otvorena_hvataljka_51.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_hvatanje_2)
                    zatvorena_hvataljka_10_5.RunProgram()
                    while zatvorena_hvataljka_10_5.Busy():
                        tm.sleep(0.1)
                    # Узимање и уклањање поједеног пјешака са шаховске табле
                    pojedena_figura=hvataljka.AttachClosest()
                    robot.MoveL(target_prilaz_2)
                    robot.MoveL(target_ostavljanje_figure)
                    robot.MoveL( target_ostavljanje_figure_spustanje_2)
                    ispustanje_figure.RunProgram()
                    otvorena_hvataljka_51.RunProgram()
                    while otvorena_hvataljka_51.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_ostavljanje_figure)
                    self.ostavljanje_pojedenih_figura(figura_napadnuta,pojedena_figura,koordinatni_sistem_odlaganje_bijele, koordinatni_sistem_odlaganje_crne)
                    # Помјерање фигуре са почетног на жељено поље
                    robot.MoveL(target_prilaz_1)
                    otvorena_hvataljka_figure.RunProgram()
                    while otvorena_hvataljka_figure.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_hvatanje_1)
                    if figura.piece_type==sah.ROOK or figura.piece_type==sah.KING or figura.piece_type==sah.QUEEN:
                        zatvorena_hvataljka_14.RunProgram()
                        while zatvorena_hvataljka_14.Busy():
                            tm.sleep(0.1)
                    elif figura.piece_type==sah.KNIGHT or figura.piece_type==sah.BISHOP:
                        zatvorena_hvataljka_12.RunProgram()
                        while zatvorena_hvataljka_12.Busy():
                            tm.sleep(0.1)
                    hvataljka.AttachClosest()
                    if figura.piece_type==sah.ROOK or (figura.piece_type==sah.KING and (red_1==red_2 or kolona_1==kolona_2)) or (figura.piece_type==sah.QUEEN and (red_1==red_2 or kolona_1==kolona_2)):
                        robot.MoveL(target_mali_prilaz_1)
                        robot.MoveL(target_mali_prilaz_2)
                    else:
                        robot.MoveL(target_prilaz_1)
                        robot.MoveL(target_prilaz_2)
                    robot.MoveL(target_hvatanje_1_2)#***
                    ispustanje_figure.RunProgram()
                    otvorena_hvataljka_figure.RunProgram()
                    while otvorena_hvataljka_figure.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_prilaz_1_2)
                    robot.MoveL(target_pocetna)
            # Случај када пјешак узима неку од тешких фигура
            else:
                 if figura and figura.piece_type==sah.PAWN:
                    # Таргети за прилаз и хватање пјешака (почетно поље)
                    target_prilaz_1=robomath.Pose(pjesak_prilaz[red_1][kolona_1][0],pjesak_prilaz[red_1][kolona_1][1],pjesak_prilaz[red_1][kolona_1][2],pjesak_prilaz[red_1][kolona_1][3],pjesak_prilaz[red_1][kolona_1][4],pjesak_prilaz[red_1][kolona_1][5])
                    target_hvatanje_1=robomath.Pose(pjesak_hvatanje[red_1][kolona_1][0],pjesak_hvatanje[red_1][kolona_1][1],pjesak_hvatanje[red_1][kolona_1][2],pjesak_hvatanje[red_1][kolona_1][3],pjesak_hvatanje[red_1][kolona_1][4],pjesak_hvatanje[red_1][kolona_1][5])
                    # Таргети за прилаз и испуштање пјешака (крајње поље)
                    target_prilaz_2=robomath.Pose(pjesak_prilaz[red_2][kolona_2][0],pjesak_prilaz[red_2][kolona_2][1],pjesak_prilaz[red_2][kolona_2][2],pjesak_prilaz[red_2][kolona_2][3],pjesak_prilaz[red_2][kolona_2][4],pjesak_prilaz[red_2][kolona_2][5])
                    target_hvatanje_2=robomath.Pose(pjesak_hvatanje[red_2][kolona_2][0],pjesak_hvatanje[red_2][kolona_2][1],pjesak_hvatanje[red_2][kolona_2][2],pjesak_hvatanje[red_2][kolona_2][3],pjesak_hvatanje[red_2][kolona_2][4],pjesak_hvatanje[red_2][kolona_2][5])
                    # Таргети за прилаз и хватање поједене фигуре
                    target_prilaz_1_2=robomath.Pose(figure_prilaz[red_2][kolona_2][0],figure_prilaz[red_2][kolona_2][1],figure_prilaz[red_2][kolona_2][2],figure_prilaz[red_2][kolona_2][3],figure_prilaz[red_2][kolona_2][4],figure_prilaz[red_2][kolona_2][5])
                    target_hvatanje_1_2=robomath.Pose(figure_hvatanje[red_2][kolona_2][0],figure_hvatanje[red_2][kolona_2][1],figure_hvatanje[red_2][kolona_2][2],figure_hvatanje[red_2][kolona_2][3],figure_hvatanje[red_2][kolona_2][4],figure_hvatanje[red_2][kolona_2][5])
                    robot.MoveL(target_prilaz_1_2)
                    otvorena_hvataljka_figure.RunProgram()
                    while otvorena_hvataljka_figure.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_hvatanje_1_2)
                    if figura_napadnuta.piece_type==sah.ROOK or figura_napadnuta.piece_type==sah.KING or figura_napadnuta.piece_type==sah.QUEEN:
                        zatvorena_hvataljka_14.RunProgram()
                        while zatvorena_hvataljka_14.Busy():
                            tm.sleep(0.1)
                    elif figura_napadnuta.piece_type==sah.KNIGHT or figura_napadnuta.piece_type==sah.BISHOP:
                        zatvorena_hvataljka_12.RunProgram()
                        while zatvorena_hvataljka_12.Busy():
                            tm.sleep(0.1)
                    pojedena_figura=hvataljka.AttachClosest()
                    robot.MoveL(target_prilaz_1_2)
                    robot.MoveL(target_ostavljanje_figure)
                    robot.MoveL(target_ostavljanje_figure_spustanje_1)
                    ispustanje_figure.RunProgram()
                    otvorena_hvataljka_figure.RunProgram()
                    while otvorena_hvataljka_figure.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_ostavljanje_figure)
                    self.ostavljanje_pojedenih_figura(figura_napadnuta,pojedena_figura,koordinatni_sistem_odlaganje_bijele, koordinatni_sistem_odlaganje_crne)
                    robot.MoveL(target_prilaz_1)
                    otvorena_hvataljka_51.RunProgram()
                    while otvorena_hvataljka_51.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_hvatanje_1)
                    zatvorena_hvataljka_10_5.RunProgram()
                    while zatvorena_hvataljka_10_5.Busy():
                        tm.sleep(0.1)
                    hvataljka.AttachClosest()
                    robot.MoveL(target_prilaz_1)
                    robot.MoveL(target_prilaz_2)
                    robot.MoveL(target_hvatanje_2)
                    ispustanje_figure.RunProgram()
                    otvorena_hvataljka_51.RunProgram()
                    while otvorena_hvataljka_51.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_prilaz_2)
                    robot.MoveL(target_pocetna)
                 # Случај када фигура узима фигуру (све фигуре осим пјешака)
                 else:
                    # Таргети за прилаз и узимање фигуре (почетно поље)
                    target_prilaz_1=robomath.Pose(figure_prilaz[red_1][kolona_1][0],figure_prilaz[red_1][kolona_1][1],figure_prilaz[red_1][kolona_1][2],figure_prilaz[red_1][kolona_1][3],figure_prilaz[red_1][kolona_1][4],figure_prilaz[red_1][kolona_1][5])
                    target_hvatanje_1=robomath.Pose(figure_hvatanje[red_1][kolona_1][0],figure_hvatanje[red_1][kolona_1][1],figure_hvatanje[red_1][kolona_1][2],figure_hvatanje[red_1][kolona_1][3],figure_hvatanje[red_1][kolona_1][4],figure_hvatanje[red_1][kolona_1][5])
                    # Таргети за прилаз и узимање фигуре (крајње поље)
                    target_prilaz_2=robomath.Pose(figure_prilaz[red_2][kolona_2][0],figure_prilaz[red_2][kolona_2][1],figure_prilaz[red_2][kolona_2][2],figure_prilaz[red_2][kolona_2][3],figure_prilaz[red_2][kolona_2][4],figure_prilaz[red_2][kolona_2][5])
                    target_hvatanje_2=robomath.Pose(figure_hvatanje[red_2][kolona_2][0],figure_hvatanje[red_2][kolona_2][1],figure_hvatanje[red_2][kolona_2][2],figure_hvatanje[red_2][kolona_2][3],figure_hvatanje[red_2][kolona_2][4],figure_hvatanje[red_2][kolona_2][5])
                    robot.MoveL(target_prilaz_2)
                    otvorena_hvataljka_figure.RunProgram()
                    while otvorena_hvataljka_figure.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_hvatanje_2)
                    if figura_napadnuta.piece_type==sah.ROOK or figura_napadnuta.piece_type==sah.KING or figura_napadnuta.piece_type==sah.QUEEN:
                        zatvorena_hvataljka_14.RunProgram()
                        while zatvorena_hvataljka_14.Busy():
                            tm.sleep(0.1)
                    elif figura_napadnuta.piece_type==sah.KNIGHT or figura_napadnuta.piece_type==sah.BISHOP:
                        zatvorena_hvataljka_12.RunProgram()
                        while zatvorena_hvataljka_12.Busy():
                            tm.sleep(0.1)
                    pojedena_figura=hvataljka.AttachClosest()
                    robot.MoveL(target_prilaz_2)
                    robot.MoveL(target_ostavljanje_figure)
                    robot.MoveL(target_ostavljanje_figure_spustanje_1)
                    ispustanje_figure.RunProgram()
                    otvorena_hvataljka_figure.RunProgram()
                    while otvorena_hvataljka_figure.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_ostavljanje_figure)
                    self.ostavljanje_pojedenih_figura(figura_napadnuta,pojedena_figura,koordinatni_sistem_odlaganje_bijele, koordinatni_sistem_odlaganje_crne)
                    robot.MoveL(target_prilaz_1)
                    robot.MoveL(target_hvatanje_1)
                    if figura.piece_type==sah.ROOK or figura.piece_type==sah.KING or figura.piece_type==sah.QUEEN:
                        zatvorena_hvataljka_14.RunProgram()
                        while zatvorena_hvataljka_14.Busy():
                            tm.sleep(0.1)
                    elif figura.piece_type==sah.KNIGHT or figura.piece_type==sah.BISHOP:
                        zatvorena_hvataljka_12.RunProgram()
                        while zatvorena_hvataljka_12.Busy():
                            tm.sleep(0.1)
                    hvataljka.AttachClosest()
                    if figura.piece_type==sah.ROOK or (figura.piece_type==sah.KING and (red_1==red_2 or kolona_1==kolona_2)) or (figura.piece_type==sah.QUEEN and (red_1==red_2 or kolona_1==kolona_2)):
                        robot.MoveL(target_mali_prilaz_1)
                        robot.MoveL(target_mali_prilaz_2)
                    else:
                        robot.MoveL(target_prilaz_1)
                        robot.MoveL(target_prilaz_2)
                    robot.MoveL(target_hvatanje_2)
                    ispustanje_figure.RunProgram()
                    otvorena_hvataljka_figure.RunProgram()
                    while otvorena_hvataljka_figure.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(target_prilaz_2)
                    robot.MoveL(target_pocetna)
#---------------------------------------------------------------------------------------------------------------
'''Функција promocijaPjesaka ()има улогу да изврши промоцију пјешака у жељену фигуру на шаховској плочи у софтверу RoboDK. 
   Аргументи ове функције су: ред и колона селектованог и жељеног шаховског поља, фигура која се промовише (figura_krajnja) и 
   нападнута фигура (у случају да пјешак узима противничку фигуру приликом промоције).'''           
    def promocijaPjesaka(self,red_1,kolona_1,red_2,kolona_2,figura_krajnja,figura_napadnuta):
        global brojac_pojedenih_bijele
        global brojac_pojedenih_crne
        target_pocetna=robomath.Pose(170,85,130,180,0,-90)
        target_ostavljanje_figure=robomath.Pose(165,-110,110,180,0,-90)
        target_ostavljanje_figure_spustanje_1=robomath.Pose(165,-110,38,180,0,-90)
        target_ostavljanje_figure_spustanje_2=robomath.Pose(165,-110,32,180,0,-90)
        koordinatni_sistem_odlaganje_bijele=RDK.Item("odlaganje_figura_bijele")
        koordinatni_sistem_odlaganje_crne=RDK.Item("odlaganje_figura_crne")
        robot=RDK.Item("robot")
        hvataljka=RDK.Item("Tool_1")
        ispustanje_figure=RDK.Item("ispustanje_figure",robolink.ITEM_TYPE_PROGRAM)
        otvorena_hvataljka_figure=RDK.Item("otvorena_hvataljka_figure",robolink.ITEM_TYPE_PROGRAM)
        zatvorena_hvataljka_12=RDK.Item("zatvorena_hvataljka_12",robolink.ITEM_TYPE_PROGRAM)
        zatvorena_hvataljka_10_5=RDK.Item("zatvorena_hvataljka_10_5",robolink.ITEM_TYPE_PROGRAM)
        zatvorena_hvataljka_14=RDK.Item("zatvorena_hvataljka_14",robolink.ITEM_TYPE_PROGRAM)
        otvorena_hvataljka_51=RDK.Item("otvorena_hvataljka_51",robolink.ITEM_TYPE_PROGRAM)
        #----------------------------------------------------------->Prilazi za pjesake
        pjesak_prilaz=[]
        lista_prilaza_1=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=90
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_1.append(lista)
            pjesak_prilaz.append(lista_prilaza_1)
            lista_prilaza_1=[]
        #----------------------------------------------------------->Hvatanje pjesaka
        pjesak_hvatanje=[]
        lista_prilaza_2=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=32
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_2.append(lista)
            pjesak_hvatanje.append(lista_prilaza_2)
            lista_prilaza_2=[]
         #----------------------------------------------------------->Prilaz figure
        figure_prilaz=[]
        lista_prilaza_3=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=110
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_3.append(lista)
            figure_prilaz.append(lista_prilaza_3)
            lista_prilaza_3=[]
         #----------------------------------------------------------->Hvatanje figure
        figure_hvatanje=[]
        lista_prilaza_4=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=38
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_4.append(lista)
            figure_hvatanje.append(lista_prilaza_4)
            lista_prilaza_4=[]
        #------------------------------------------------------------->podizanja za slobodna kretanja(manja visina podizanja)
        prilaz_slobodno_kretanja=[]
        lista_prilaza_5=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=45
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_5.append(lista)
            prilaz_slobodno_kretanja.append(lista_prilaza_5)
            lista_prilaza_5=[]
        # Таргети за прилаз и хватање селектованог пјешака са почетног поља
        target_prilaz_1=robomath.Pose(pjesak_prilaz[red_1][kolona_1][0],pjesak_prilaz[red_1][kolona_1][1],pjesak_prilaz[red_1][kolona_1][2],pjesak_prilaz[red_1][kolona_1][3],pjesak_prilaz[red_1][kolona_1][4],pjesak_prilaz[red_1][kolona_1][5])
        target_hvatanje_1=robomath.Pose(pjesak_hvatanje[red_1][kolona_1][0],pjesak_hvatanje[red_1][kolona_1][1],pjesak_hvatanje[red_1][kolona_1][2],pjesak_hvatanje[red_1][kolona_1][3],pjesak_hvatanje[red_1][kolona_1][4],pjesak_hvatanje[red_1][kolona_1][5])
        # Таргети за прилаз и испуштање селектованог пјешака на жељено поље
        target_prilaz_2=robomath.Pose(pjesak_prilaz[red_2][kolona_2][0],pjesak_prilaz[red_2][kolona_2][1],pjesak_prilaz[red_2][kolona_2][2],pjesak_prilaz[red_2][kolona_2][3],pjesak_prilaz[red_2][kolona_2][4],pjesak_prilaz[red_2][kolona_2][5])
        target_hvatanje_2=robomath.Pose(pjesak_hvatanje[red_2][kolona_2][0],pjesak_hvatanje[red_2][kolona_2][1],pjesak_hvatanje[red_2][kolona_2][2],pjesak_hvatanje[red_2][kolona_2][3],pjesak_hvatanje[red_2][kolona_2][4],pjesak_hvatanje[red_2][kolona_2][5])
        # Таргети за прилаз и узимање поједене фигуре, ако она постоји
        target_prilaz1_2=robomath.Pose(figure_prilaz[red_2][kolona_2][0],figure_prilaz[red_2][kolona_2][1],figure_prilaz[red_2][kolona_2][2],figure_prilaz[red_2][kolona_2][3],figure_prilaz[red_2][kolona_2][4],figure_prilaz[red_2][kolona_2][5])
        target_hvatanje1_2=robomath.Pose(figure_hvatanje[red_2][kolona_2][0],figure_hvatanje[red_2][kolona_2][1],figure_hvatanje[red_2][kolona_2][2],figure_hvatanje[red_2][kolona_2][3],figure_hvatanje[red_2][kolona_2][4],figure_hvatanje[red_2][kolona_2][5])
        # Таргети за ниже подизање пјешака
        target_mali_prilaz_1=robomath.Pose(prilaz_slobodno_kretanja[red_1][kolona_1][0],prilaz_slobodno_kretanja[red_1][kolona_1][1],prilaz_slobodno_kretanja[red_1][kolona_1][2],prilaz_slobodno_kretanja[red_1][kolona_1][3],prilaz_slobodno_kretanja[red_1][kolona_1][4],prilaz_slobodno_kretanja[red_1][kolona_1][5])
        target_mali_prilaz_2=robomath.Pose(prilaz_slobodno_kretanja[red_2][kolona_2][0],prilaz_slobodno_kretanja[red_2][kolona_2][1],prilaz_slobodno_kretanja[red_2][kolona_2][2],prilaz_slobodno_kretanja[red_2][kolona_2][3],prilaz_slobodno_kretanja[red_2][kolona_2][4],prilaz_slobodno_kretanja[red_2][kolona_2][5])
        # Случај када је узета противничка фигура током промоцје пјешака
        if figura_napadnuta is not None:
            # Узимање и одлагање противничке фигуре са шаховске табле
            robot.MoveL(target_prilaz1_2)
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                tm.sleep(0.1)
            robot.MoveL(target_hvatanje1_2)
            if figura_napadnuta.piece_type==sah.BISHOP or figura_napadnuta.piece_type==sah.KNIGHT:
                zatvorena_hvataljka_12.RunProgram()
                while zatvorena_hvataljka_12.Busy():
                    tm.sleep(0.1)
            else:
                zatvorena_hvataljka_14.RunProgram()
                while zatvorena_hvataljka_14.Busy():
                    tm.sleep(0.1) 
            pojedena_figura=hvataljka.AttachClosest()
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_ostavljanje_figure)
            robot.MoveL( target_ostavljanje_figure_spustanje_1)
            ispustanje_figure.RunProgram()
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                tm.sleep(0.1)
            robot.MoveL(target_ostavljanje_figure)
            self.ostavljanje_pojedenih_figura(figura_napadnuta,pojedena_figura,koordinatni_sistem_odlaganje_bijele, koordinatni_sistem_odlaganje_crne)
        '''Након одлагања поједене фигуре, врши се помјерање пјешака на поље промоције, а затим се тај пјешак уклања
        са шаховске табле (овај дио кода се односи и на промоцију пјешака на слободно поље).'''
        robot.MoveL(target_prilaz_1)
        otvorena_hvataljka_51.RunProgram()
        while otvorena_hvataljka_51.Busy():
            tm.sleep(0.1)
        robot.MoveL(target_hvatanje_1)
        zatvorena_hvataljka_10_5.RunProgram()
        while zatvorena_hvataljka_10_5.Busy():
            tm.sleep(0.1)
        pojedena_figura=hvataljka.AttachClosest()
        if figura_napadnuta is not None:
            robot.MoveL(target_prilaz_1)
            robot.MoveL(target_prilaz_2)
        else:
            robot.MoveL(target_mali_prilaz_1)
            robot.MoveL(target_mali_prilaz_2)
        robot.MoveL(target_hvatanje_2)
        robot.MoveL(target_prilaz_2)
        robot.MoveL(target_ostavljanje_figure)
        robot.MoveL( target_ostavljanje_figure_spustanje_2)
        ispustanje_figure.RunProgram()
        otvorena_hvataljka_51.RunProgram()
        while otvorena_hvataljka_51.Busy():
            tm.sleep(0.1)
        robot.MoveL(target_ostavljanje_figure)
        # Одлагање пјешака послије промоције
        if self.sahovska_tabla.turn==sah.BLACK:
            pojedena_figura.setParent(koordinatni_sistem_odlaganje_bijele)
            translacija_x=25*brojac_pojedenih_bijele
            brojac_pojedenih_bijele+=1
            translacija_y=11
            matrica_translacije=robomath.Mat(   [[1, 0, 0, translacija_x], 
                                     [0, 0, -1, translacija_y], 
                                     [0, 1, 0, 1], 
                                     [0, 0, 0, 1]])
            pojedena_figura.setPose(matrica_translacije)
        elif self.sahovska_tabla.turn==sah.WHITE:
            pojedena_figura.setParent(koordinatni_sistem_odlaganje_crne)
            translacija_x=25*brojac_pojedenih_crne
            brojac_pojedenih_crne+=1
            translacija_y=11
            matrica_translacije=robomath.Mat(   [[1, 0, 0, translacija_x], 
                                     [0, 0, -1, translacija_y], 
                                     [0, 1, 0, 1], 
                                     [0, 0, 0, 1]])
            pojedena_figura.setPose(matrica_translacije)
        # Провјера у коју фигуру се промовише пјешака (у софтверу RoboDK су креирне додатне фигуре за промоцију)
        # Промоција пјешака у црну даму
        if figura_krajnja.piece_type==sah.QUEEN and not figura_krajnja.color:
            robot.MoveL(robomath.Pose(292.5,290,110,180,0,-90))
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                tm.sleep(0.1)
            robot.MoveL(robomath.Pose(292.5,290,38,180,0,-90))
            zatvorena_hvataljka_14.RunProgram()
            while zatvorena_hvataljka_14.Busy():
                    tm.sleep(0.1)
            hvataljka.AttachClosest()
            robot.MoveL(robomath.Pose(292.5,290,110,180,0,-90))
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_hvatanje1_2)
            ispustanje_figure.RunProgram()
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_pocetna)
        # Промоција пјешака у бијелу даму
        elif figura_krajnja.piece_type==sah.QUEEN and figura_krajnja.color:
            robot.MoveL(robomath.Pose(152.5,290,110,180,0,-90))
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                tm.sleep(0.1)
            robot.MoveL(robomath.Pose(152.5,290,38,180,0,-90))
            zatvorena_hvataljka_14.RunProgram()
            while zatvorena_hvataljka_14.Busy():
                    tm.sleep(0.1)
            hvataljka.AttachClosest()
            robot.MoveL(robomath.Pose(152.5,290,110,180,0,-90))
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_hvatanje1_2)
            ispustanje_figure.RunProgram()
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_pocetna)
        # Промоција пјешака у црног топа
        elif figura_krajnja.piece_type==sah.ROOK and not figura_krajnja.color:
            robot.MoveL(robomath.Pose(187.5,290,110,180,0,-90))
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                tm.sleep(0.1)
            robot.MoveL(robomath.Pose(187.5,290,38,180,0,-90))
            zatvorena_hvataljka_14.RunProgram()
            while zatvorena_hvataljka_14.Busy():
                    tm.sleep(0.1)
            hvataljka.AttachClosest()
            robot.MoveL(robomath.Pose(187.5,290,110,180,0,-90))
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_hvatanje1_2)
            ispustanje_figure.RunProgram()
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_pocetna)
        # Промоција пјешака у бијелог топа
        elif figura_krajnja.piece_type==sah.ROOK and figura_krajnja.color:
            robot.MoveL(robomath.Pose(47.5,290,110,180,0,-90))
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                tm.sleep(0.1)
            robot.MoveL(robomath.Pose(47.5,290,38,180,0,-90))
            zatvorena_hvataljka_14.RunProgram()
            while zatvorena_hvataljka_14.Busy():
                    tm.sleep(0.1)
            hvataljka.AttachClosest()
            robot.MoveL(robomath.Pose(47.5,290,110,180,0,-90))
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_hvatanje1_2)
            ispustanje_figure.RunProgram()
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_pocetna)
        # Промоција пјешака у црног ловца
        elif figura_krajnja.piece_type==sah.BISHOP and not figura_krajnja.color:
            robot.MoveL(robomath.Pose(257.5,290,110,180,0,-90))
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                tm.sleep(0.1)
            robot.MoveL(robomath.Pose(257.5,290,38,180,0,-90))
            zatvorena_hvataljka_12.RunProgram()
            while zatvorena_hvataljka_12.Busy():
                    tm.sleep(0.1)
            hvataljka.AttachClosest()
            robot.MoveL(robomath.Pose(257.5,290,110,180,0,-90))
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_hvatanje1_2)
            ispustanje_figure.RunProgram()
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_pocetna)
        # Промоција пјешака у бијелог ловца
        elif figura_krajnja.piece_type==sah.BISHOP and figura_krajnja.color:
            robot.MoveL(robomath.Pose(117.5,290,110,180,0,-90))
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                tm.sleep(0.1)
            robot.MoveL(robomath.Pose(117.5,290,38,180,0,-90))
            zatvorena_hvataljka_12.RunProgram()
            while zatvorena_hvataljka_12.Busy():
                    tm.sleep(0.1)
            hvataljka.AttachClosest()
            robot.MoveL(robomath.Pose(117.5,290,110,180,0,-90))
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_hvatanje1_2)
            ispustanje_figure.RunProgram()
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_pocetna)
        # Промоција пјешака у црног скакача
        elif figura_krajnja.piece_type==sah.KNIGHT and not figura_krajnja.color:
            robot.MoveL(robomath.Pose(222.5,290,110,180,0,-90))
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                tm.sleep(0.1)
            robot.MoveL(robomath.Pose(222.5,290,38,180,0,-90))
            zatvorena_hvataljka_12.RunProgram()
            while zatvorena_hvataljka_12.Busy():
                    tm.sleep(0.1)
            hvataljka.AttachClosest()
            robot.MoveL(robomath.Pose(222.5,290,110,180,0,-90))
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_hvatanje1_2)
            ispustanje_figure.RunProgram()
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_pocetna)
        # Промоција пјешака у бијелог скакача
        elif figura_krajnja.piece_type==sah.KNIGHT and figura_krajnja.color:
            robot.MoveL(robomath.Pose(82.5,290,110,180,0,-90))
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                tm.sleep(0.1)
            robot.MoveL(robomath.Pose(82.5,290,38,180,0,-90))
            zatvorena_hvataljka_12.RunProgram()
            while zatvorena_hvataljka_12.Busy():
                    tm.sleep(0.1)
            hvataljka.AttachClosest()
            robot.MoveL(robomath.Pose(82.5,290,110,180,0,-90))
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_hvatanje1_2)
            ispustanje_figure.RunProgram()
            otvorena_hvataljka_figure.RunProgram()
            while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
            robot.MoveL(target_prilaz1_2)
            robot.MoveL(target_pocetna)
#---------------------------------------------------------------------------------------------------------------
# Функција које омогућава реализацију шаховског потеза “en passant”
    def en_passant(self,red_1,kolona_1,red_2,kolona_2):
        global brojac_pojedenih_bijele
        global brojac_pojedenih_crne
        target_pocetna=robomath.Pose(170,85,130,180,0,-90)
        target_ostavljanje_figure=robomath.Pose(165,-110,110,180,0,-90)
        target_ostavljanje_figure_spustanje_1=robomath.Pose(165,-110,38,180,0,-90)
        target_ostavljanje_figure_spustanje_2=robomath.Pose(165,-110,32,180,0,-90)
        ispustanje_figure=RDK.Item("ispustanje_figure",robolink.ITEM_TYPE_PROGRAM)
        koordinatni_sistem_odlaganje_bijele=RDK.Item("odlaganje_figura_bijele")
        koordinatni_sistem_odlaganje_crne=RDK.Item("odlaganje_figura_crne")
        otvorena_hvataljka_51=RDK.Item("otvorena_hvataljka_51",robolink.ITEM_TYPE_PROGRAM)
        zatvorena_hvataljka_10_5=RDK.Item("zatvorena_hvataljka_10_5",robolink.ITEM_TYPE_PROGRAM)
        robot=RDK.Item("robot")
        hvataljka=RDK.Item("Tool_1")
        #----------------------------------------------------------->Prilazi za pjesake
        pjesak_prilaz=[]
        lista_prilaza_1=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=90
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_1.append(lista)
            pjesak_prilaz.append(lista_prilaza_1)
            lista_prilaza_1=[]
        #----------------------------------------------------------->Hvatanje pjesaka
        pjesak_hvatanje=[]
        lista_prilaza_2=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=32
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_2.append(lista)
            pjesak_hvatanje.append(lista_prilaza_2)
            lista_prilaza_2=[]
        #--------------------------------------------------------------
        target_prilaz_1=robomath.Pose(pjesak_prilaz[red_1][kolona_1][0],pjesak_prilaz[red_1][kolona_1][1],pjesak_prilaz[red_1][kolona_1][2],pjesak_prilaz[red_1][kolona_1][3],pjesak_prilaz[red_1][kolona_1][4],pjesak_prilaz[red_1][kolona_1][5])
        target_hvatanje_1=robomath.Pose(pjesak_hvatanje[red_1][kolona_1][0],pjesak_hvatanje[red_1][kolona_1][1],pjesak_hvatanje[red_1][kolona_1][2],pjesak_hvatanje[red_1][kolona_1][3],pjesak_hvatanje[red_1][kolona_1][4],pjesak_hvatanje[red_1][kolona_1][5])
        target_prilaz_2=robomath.Pose(pjesak_prilaz[red_2][kolona_2][0],pjesak_prilaz[red_2][kolona_2][1],pjesak_prilaz[red_2][kolona_2][2],pjesak_prilaz[red_2][kolona_2][3],pjesak_prilaz[red_2][kolona_2][4],pjesak_prilaz[red_2][kolona_2][5])
        target_hvatanje_2=robomath.Pose(pjesak_hvatanje[red_2][kolona_2][0],pjesak_hvatanje[red_2][kolona_2][1],pjesak_hvatanje[red_2][kolona_2][2],pjesak_hvatanje[red_2][kolona_2][3],pjesak_hvatanje[red_2][kolona_2][4],pjesak_hvatanje[red_2][kolona_2][5])
        if not self.sahovska_tabla.turn:
            target_prilaz_2_2=robomath.Pose(pjesak_prilaz[red_2-1][kolona_2][0],pjesak_prilaz[red_2-1][kolona_2][1],pjesak_prilaz[red_2-1][kolona_2][2],pjesak_prilaz[red_2-1][kolona_2][3],pjesak_prilaz[red_2-1][kolona_2][4],pjesak_prilaz[red_2-1][kolona_2][5])
            target_hvatanje_2_2=robomath.Pose(pjesak_hvatanje[red_2-1][kolona_2][0],pjesak_hvatanje[red_2-1][kolona_2][1],pjesak_hvatanje[red_2-1][kolona_2][2],pjesak_hvatanje[red_2-1][kolona_2][3],pjesak_hvatanje[red_2-1][kolona_2][4],pjesak_hvatanje[red_2-1][kolona_2][5])
        else:
            target_prilaz_2_2=robomath.Pose(pjesak_prilaz[red_2+1][kolona_2][0],pjesak_prilaz[red_2+1][kolona_2][1],pjesak_prilaz[red_2+1][kolona_2][2],pjesak_prilaz[red_2+1][kolona_2][3],pjesak_prilaz[red_2+1][kolona_2][4],pjesak_prilaz[red_2+1][kolona_2][5])
            target_hvatanje_2_2=robomath.Pose(pjesak_hvatanje[red_2+1][kolona_2][0],pjesak_hvatanje[red_2+1][kolona_2][1],pjesak_hvatanje[red_2+1][kolona_2][2],pjesak_hvatanje[red_2+1][kolona_2][3],pjesak_hvatanje[red_2+1][kolona_2][4],pjesak_hvatanje[red_2+1][kolona_2][5])
        robot.MoveL(target_prilaz_2_2)
        otvorena_hvataljka_51.RunProgram()
        while otvorena_hvataljka_51.Busy():
            tm.sleep(0.1)
        robot.MoveL(target_hvatanje_2_2)
        zatvorena_hvataljka_10_5.RunProgram()
        while zatvorena_hvataljka_10_5.Busy():
            tm.sleep(0.1)
        pojedena_figura=hvataljka.AttachClosest()
        robot.MoveL(target_prilaz_2_2)
        robot.MoveL(target_ostavljanje_figure)
        robot.MoveL(target_ostavljanje_figure_spustanje_2)
        ispustanje_figure.RunProgram()
        otvorena_hvataljka_51.RunProgram()
        while otvorena_hvataljka_51.Busy():
            tm.sleep(0.1)
        robot.MoveL(target_ostavljanje_figure)
        if self.sahovska_tabla.turn:
            pojedena_figura.setParent(koordinatni_sistem_odlaganje_bijele)
            translacija_x=25*brojac_pojedenih_bijele
            brojac_pojedenih_bijele+=1
            translacija_y=11
            matrica_translacije=robomath.Mat(   [[1, 0, 0, translacija_x], 
                                     [0, 0, -1, translacija_y], 
                                     [0, 1, 0, 1], 
                                     [0, 0, 0, 1]])
            pojedena_figura.setPose(matrica_translacije)
        else:
            pojedena_figura.setParent(koordinatni_sistem_odlaganje_crne)
            translacija_x=25*brojac_pojedenih_crne
            brojac_pojedenih_crne+=1
            translacija_y=11
            matrica_translacije=robomath.Mat(   [[1, 0, 0, translacija_x], 
                                     [0, 0, -1, translacija_y], 
                                     [0, 1, 0, 1], 
                                     [0, 0, 0, 1]])
            pojedena_figura.setPose(matrica_translacije)
        robot.MoveL(target_prilaz_1)
        otvorena_hvataljka_51.RunProgram()
        while otvorena_hvataljka_51.Busy():
            tm.sleep(0.1)
        robot.MoveL(target_hvatanje_1)
        zatvorena_hvataljka_10_5.RunProgram()
        while zatvorena_hvataljka_10_5.Busy():
            tm.sleep(0.1)
        hvataljka.AttachClosest()
        robot.MoveL(target_prilaz_1)
        robot.MoveL(target_prilaz_2)
        robot.MoveL(target_hvatanje_2)
        ispustanje_figure.RunProgram()
        otvorena_hvataljka_51.RunProgram()
        while otvorena_hvataljka_51.Busy():
            tm.sleep(0.1)
        robot.MoveL(target_prilaz_2)
        robot.MoveL(target_pocetna)
#---------------------------------------------------------------------------------------------------------------
'''Функција којa омогућава потез играча oдносно кориснички унос помоћу периферног уређаја (миша).
   Такође, унутар ове функције се врше позиви функција за реализацију шаховског потеза у симулацији у зависности од његовог типа.'''
    def potezIgraca(self):
        tip_rohade=""
        zeljeno_polje = None
        # Бесконачна петља (омогућава унос све док се не дође до легалног потеза)
        while True:
            # Провјера корисничког уноса
            for event in PY.event.get():
                if event.type == PY.QUIT:
                    PY.quit()
                    pocetna_pozicija=RDK.Item("pocetna_pozicija",robolink.ITEM_TYPE_PROGRAM)
                    '''Повратак елеменатау почетни положај на радној станици у софтверу RoboDK приликом 
                    затвварања графичког прозора (pocetna_pozicija.RunProgram())'''
                    pocetna_pozicija.RunProgram()
                    return
                elif event.type == PY.MOUSEBUTTONDOWN:
                    selektovano_polje = self.detekcija_poteza(PY.mouse.get_pos())
                    if zeljeno_polje is None:
                        figura = self.sahovska_tabla.piece_at(selektovano_polje)
                        if figura and figura.color == self.sahovska_tabla.turn:
                            zeljeno_polje = selektovano_polje
                            self.crtanje_table()
                            self.prikaz_legalnih_poteza(zeljeno_polje)
                            PY.display.update()
                    else:
                        # Креирање шаховског потеза на основу индекса почетног и крајњег поља (класа chess.Move())
                        potez = sah.Move(zeljeno_polje, selektovano_polje)
                        figura=self.sahovska_tabla.piece_at(zeljeno_polje)
                        figura_uzimanje=self.sahovska_tabla.piece_at(selektovano_polje)
                        # Рачунање редова и колона поља на основу његовог индекса
                        kolona_zeljeno = zeljeno_polje % 8
                        red_zeljeno = zeljeno_polje // 8
                        kolona_selektovano = selektovano_polje % 8
                        red_selektovano = selektovano_polje // 8
                        
                        # Тип потеза (промоција)
                        if (figura and figura.piece_type==sah.PAWN and selektovano_polje//8==7 and \
                            self.sahovska_tabla.turn==sah.WHITE and zeljeno_polje//8==6) or (figura and \
                            figura.piece_type==sah.PAWN and selektovano_polje//8==0 and \
                            self.sahovska_tabla.turn==sah.BLACK and zeljeno_polje//8==1):
                            print("Promocija pjesaka!")
                            # Позив функције promocija_pjesaka()
                            self.promocija_pjesaka(potez)
                            return
                        # Тип потеза (en passant)
                        elif potez in self.sahovska_tabla.legal_moves and self.sahovska_tabla.is_en_passant(potez):
                            self.sahovska_tabla.push(potez)
                            print(f"Igrac je odigrao potez: {potez}")
                            self.crtanje_table()
                            PY.display.update()
                            # Позив функције en_passant()
                            self.en_passant(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano)
                            return
                        # Тип потеза (рохада)
                        elif potez in self.sahovska_tabla.legal_moves and self.sahovska_tabla.is_castling(potez):
                            self.sahovska_tabla.push(potez)
                            print(f"Igrac je odigrao potez: {potez}")
                            self.crtanje_table()
                            PY.display.update()
                            # Провјера типа рохаде
                            if potez.to_square==sah.G1 or potez.to_square==sah.G8:
                                tip_rohade="mala"
                            else:
                                tip_rohade="velika"
                            # Позив функције rohada()
                            self.rohada(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano,tip_rohade)
                            return
                        # Тип потеза (помјерање фигуре на слободно поља или узимање противничке фигуре)
                        elif potez in self.sahovska_tabla.legal_moves:
                            self.sahovska_tabla.push(potez)
                            print(f"Igrac je odigrao potez: {potez}")
                            self.crtanje_table()
                            PY.display.update()
                            self.pomjeranje_figura(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano,figura,figura_uzimanje)
                            return
                        # Замјена почетне (селектоване) фигуре
                        elif self.sahovska_tabla.color_at(selektovano_polje)==self.sahovska_tabla.turn:
                            zeljeno_polje=selektovano_polje
                            self.crtanje_table()
                            self.prikaz_legalnih_poteza(zeljeno_polje)
                            PY.display.update()
                        # Nelegalan potez
                        else:
                            print("Nelegalan potez. Pokušajte ponovo.")
#---------------------------------------------------------------------------------------------------------------
# Функција rohada() обезбјеђује релизацију мале и велике рохаде у симулацији
    def rohada(self,red_1,kolona_1,red_2,kolona_2,tip_rohade):
        robot=RDK.Item("robot")
        hvataljka=RDK.Item("Tool_1")
        ispustanje_figure=RDK.Item("ispustanje_figure",robolink.ITEM_TYPE_PROGRAM)
        otvorena_hvataljka_figure=RDK.Item("otvorena_hvataljka_figure",robolink.ITEM_TYPE_PROGRAM)
        target_pocetna=robomath.Pose(170,85,130,180,0,-90)
        zatvorena_hvataljka_14=RDK.Item("zatvorena_hvataljka_14",robolink.ITEM_TYPE_PROGRAM)
        #------------------------------------------------------------>Prilaz figuri
        figure_prilaz=[]
        lista_prilaza_3=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=110
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_3.append(lista)
            figure_prilaz.append(lista_prilaza_3)
            lista_prilaza_3=[]
         #----------------------------------------------------------->Hvatanje figure
        figure_hvatanje=[]
        lista_prilaza_4=[]
        for i in range(8):
            x=47.5+35*i
            for j in range(8):
                y=207.5-j*35
                z=38
                rot_x=180
                rot_y=0
                rot_z=-90
                lista=[x,y,z,rot_x,rot_y,rot_z]
                lista_prilaza_4.append(lista)
            figure_hvatanje.append(lista_prilaza_4)
            lista_prilaza_4=[]
            
        # Таргети за прилаз и хватање бијлог топа (мала рохада)
        #---------------------------------------------
        top_bijeli_mala_hvatanje_1=robomath.Pose(figure_hvatanje[0][7][0],figure_hvatanje[0][7][1],figure_hvatanje[0][7][2],figure_hvatanje[0][7][3],figure_hvatanje[0][7][4],figure_hvatanje[0][7][5])
        top_bijeli_mala_prilaz_1=robomath.Pose(figure_prilaz[0][7][0],figure_prilaz[0][7][1],figure_prilaz[0][7][2],figure_prilaz[0][7][3],figure_prilaz[0][7][4],figure_prilaz[0][7][5])
        top_bijeli_mala_hvatanje_2=robomath.Pose(figure_hvatanje[0][5][0],figure_hvatanje[0][5][1],figure_hvatanje[0][5][2],figure_hvatanje[0][5][3],figure_hvatanje[0][5][4],figure_hvatanje[0][5][5])
        top_bijeli_mala_prilaz_2=robomath.Pose(figure_prilaz[0][5][0],figure_prilaz[0][5][1],figure_prilaz[0][5][2],figure_prilaz[0][5][3],figure_prilaz[0][5][4],figure_prilaz[0][5][5])
        
        # Таргети за прилаз и хватање бијлог топа (велика рохада)
        #---------------------------------------------
        top_bijeli_velika_hvatanje_1_1=robomath.Pose(figure_hvatanje[0][0][0],figure_hvatanje[0][0][1],figure_hvatanje[0][0][2],figure_hvatanje[0][0][3],figure_hvatanje[0][0][4],figure_hvatanje[0][0][5])
        top_bijeli_velika_prilaz_1_1=robomath.Pose(figure_prilaz[0][0][0],figure_prilaz[0][0][1],figure_prilaz[0][0][2],figure_prilaz[0][0][3],figure_prilaz[0][0][4],figure_prilaz[0][0][5])
        top_bijeli_velika_hvatanje_2_2=robomath.Pose(figure_hvatanje[0][3][0],figure_hvatanje[0][3][1],figure_hvatanje[0][3][2],figure_hvatanje[0][3][3],figure_hvatanje[0][3][4],figure_hvatanje[0][3][5])
        top_bijeli_velika_prilaz_2_2=robomath.Pose(figure_prilaz[0][3][0],figure_prilaz[0][3][1],figure_prilaz[0][3][2],figure_prilaz[0][3][3],figure_prilaz[0][3][4],figure_prilaz[0][3][5])
        
        # Таргети за прилаз и хватање црног топа (мала рохада)
        #---------------------------------------------
        top_crni_mala_hvatanje_1=robomath.Pose(figure_hvatanje[7][7][0],figure_hvatanje[7][7][1],figure_hvatanje[7][7][2],figure_hvatanje[7][7][3],figure_hvatanje[7][7][4],figure_hvatanje[7][7][5])
        top_crni_mala_prilaz_1=robomath.Pose(figure_prilaz[7][7][0],figure_prilaz[7][7][1],figure_prilaz[7][7][2],figure_prilaz[7][7][3],figure_prilaz[7][7][4],figure_prilaz[7][7][5])
        top_crni_mala_hvatanje_2=robomath.Pose(figure_hvatanje[7][5][0],figure_hvatanje[7][5][1],figure_hvatanje[7][5][2],figure_hvatanje[7][5][3],figure_hvatanje[7][5][4],figure_hvatanje[7][5][5])
        top_crni_mala_prilaz_2=robomath.Pose(figure_prilaz[7][5][0],figure_prilaz[7][5][1],figure_prilaz[7][5][2],figure_prilaz[7][5][3],figure_prilaz[7][5][4],figure_prilaz[7][5][5])
        
        # Таргети за прилаз и хватање црног топа (велика рохада)
        #---------------------------------------------
        top_crni_velika_hvatanje_1_1=robomath.Pose(figure_hvatanje[7][0][0],figure_hvatanje[7][0][1],figure_hvatanje[7][0][2],figure_hvatanje[7][0][3],figure_hvatanje[7][0][4],figure_hvatanje[7][0][5])
        top_crni_velika_prilaz_1_1=robomath.Pose(figure_prilaz[7][0][0],figure_prilaz[7][0][1],figure_prilaz[7][0][2],figure_prilaz[7][0][3],figure_prilaz[7][0][4],figure_prilaz[7][0][5])
        top_crni_velika_hvatanje_2_2=robomath.Pose(figure_hvatanje[7][3][0],figure_hvatanje[7][3][1],figure_hvatanje[7][3][2],figure_hvatanje[7][3][3],figure_hvatanje[7][3][4],figure_hvatanje[7][3][5])
        top_crni_velika_prilaz_2_2=robomath.Pose(figure_prilaz[7][3][0],figure_prilaz[7][3][1],figure_prilaz[7][3][2],figure_prilaz[7][3][3],figure_prilaz[7][3][4],figure_prilaz[7][3][5])
        #---------------------------------
        # Таргети за прилаз и хватање краља
        target_prilaz_1=robomath.Pose(figure_prilaz[red_1][kolona_1][0],figure_prilaz[red_1][kolona_1][1],figure_prilaz[red_1][kolona_1][2],figure_prilaz[red_1][kolona_1][3],figure_prilaz[red_1][kolona_1][4],figure_prilaz[red_1][kolona_1][5])
        target_hvatanje_1=robomath.Pose(figure_hvatanje[red_1][kolona_1][0],figure_hvatanje[red_1][kolona_1][1],figure_hvatanje[red_1][kolona_1][2],figure_hvatanje[red_1][kolona_1][3],figure_hvatanje[red_1][kolona_1][4],figure_hvatanje[red_1][kolona_1][5])
        target_prilaz_2=robomath.Pose(figure_prilaz[red_2][kolona_2][0],figure_prilaz[red_2][kolona_2][1],figure_prilaz[red_2][kolona_2][2],figure_prilaz[red_2][kolona_2][3],figure_prilaz[red_2][kolona_2][4],figure_prilaz[red_2][kolona_2][5])
        target_hvatanje_2=robomath.Pose(figure_hvatanje[red_2][kolona_2][0],figure_hvatanje[red_2][kolona_2][1],figure_hvatanje[red_2][kolona_2][2],figure_hvatanje[red_2][kolona_2][3],figure_hvatanje[red_2][kolona_2][4],figure_hvatanje[red_2][kolona_2][5])
        if not self.sahovska_tabla.turn:
                robot.MoveL(target_prilaz_1)
                otvorena_hvataljka_figure.RunProgram()
                while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
                robot.MoveL(target_hvatanje_1)
                zatvorena_hvataljka_14.RunProgram()
                while zatvorena_hvataljka_14.Busy():
                    tm.sleep(0.1)
                hvataljka.AttachClosest()
                robot.MoveL(target_prilaz_1)
                robot.MoveL(target_prilaz_2)
                robot.MoveL(target_hvatanje_2)
                ispustanje_figure.RunProgram()
                otvorena_hvataljka_figure.RunProgram()
                while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
                robot.MoveL(target_prilaz_2)
                # Мала рохада (бијеле фигуре)
                if tip_rohade=="mala":
                    robot.MoveL(top_bijeli_mala_prilaz_1)
                    robot.MoveL(top_bijeli_mala_hvatanje_1)
                    zatvorena_hvataljka_14.RunProgram()
                    while zatvorena_hvataljka_14.Busy():
                        tm.sleep(0.1)
                    hvataljka.AttachClosest()
                    robot.MoveL(top_bijeli_mala_prilaz_1)
                    robot.MoveL(top_bijeli_mala_prilaz_2)
                    robot.MoveL(top_bijeli_mala_hvatanje_2)
                    ispustanje_figure.RunProgram()
                    otvorena_hvataljka_figure.RunProgram()
                    while otvorena_hvataljka_figure.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(top_bijeli_mala_prilaz_2)
                # Велика рохада (бијеле фигуре)
                else:
                    robot.MoveL(top_bijeli_velika_prilaz_1_1)
                    robot.MoveL(top_bijeli_velika_hvatanje_1_1)
                    zatvorena_hvataljka_14.RunProgram()
                    while zatvorena_hvataljka_14.Busy():
                        tm.sleep(0.1)
                    hvataljka.AttachClosest()
                    robot.MoveL(top_bijeli_velika_prilaz_1_1)
                    robot.MoveL(top_bijeli_velika_prilaz_2_2)
                    robot.MoveL(top_bijeli_velika_hvatanje_2_2)
                    ispustanje_figure.RunProgram()
                    otvorena_hvataljka_figure.RunProgram()
                    while otvorena_hvataljka_figure.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(top_bijeli_velika_prilaz_2_2)
                robot.MoveL(target_pocetna)
        else:
                robot.MoveL(target_prilaz_1)
                otvorena_hvataljka_figure.RunProgram()
                while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
                robot.MoveL(target_hvatanje_1)
                zatvorena_hvataljka_14.RunProgram()
                while zatvorena_hvataljka_14.Busy():
                    tm.sleep(0.1)
                hvataljka.AttachClosest()
                robot.MoveL(target_prilaz_1)
                robot.MoveL(target_prilaz_2)
                robot.MoveL(target_hvatanje_2)
                ispustanje_figure.RunProgram()
                otvorena_hvataljka_figure.RunProgram()
                while otvorena_hvataljka_figure.Busy():
                    tm.sleep(0.1)
                robot.MoveL(target_prilaz_2)
                # Мала рохада (црне фигуре)
                if tip_rohade=="mala":
                    robot.MoveL(top_crni_mala_prilaz_1)
                    robot.MoveL(top_crni_mala_hvatanje_1)
                    zatvorena_hvataljka_14.RunProgram()
                    while zatvorena_hvataljka_14.Busy():
                        tm.sleep(0.1)
                    hvataljka.AttachClosest()
                    robot.MoveL(top_crni_mala_prilaz_1)
                    robot.MoveL(top_crni_mala_prilaz_2)
                    robot.MoveL(top_crni_mala_hvatanje_2)
                    ispustanje_figure.RunProgram()
                    otvorena_hvataljka_figure.RunProgram()
                    while otvorena_hvataljka_figure.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(top_crni_mala_prilaz_2)
                # Велика рохада (црне фигуре)
                else:
                    robot.MoveL(top_crni_velika_prilaz_1_1)
                    robot.MoveL(top_crni_velika_hvatanje_1_1)
                    zatvorena_hvataljka_14.RunProgram()
                    while zatvorena_hvataljka_14.Busy():
                        tm.sleep(0.1)
                    hvataljka.AttachClosest()
                    robot.MoveL(top_crni_velika_prilaz_1_1)
                    robot.MoveL(top_crni_velika_prilaz_2_2)
                    robot.MoveL(top_crni_velika_hvatanje_2_2)
                    ispustanje_figure.RunProgram()
                    otvorena_hvataljka_figure.RunProgram()
                    while otvorena_hvataljka_figure.Busy():
                        tm.sleep(0.1)
                    robot.MoveL(top_crni_velika_prilaz_2_2)
                robot.MoveL(target_pocetna)
#---------------------------------------------------------------------------------------------------------------
# Функција promocija_pjesaka()обезбјеђује избор типа фигуре у коју се пјешак промовише
    def promocija_pjesaka(self,potez):
        odabir_promocije=None
        while odabir_promocije not in [1,2,3,4]:
            #Избор промоције
            odabir_promocije=int(input("Unesite zeljenu promociju,1(top),2(konj),3(lovac),4(dama):"))
        if odabir_promocije==1:
            nova_figura=sah.ROOK
        elif odabir_promocije==2:
            nova_figura=sah.KNIGHT
        elif odabir_promocije==3:
            nova_figura=sah.BISHOP
        elif odabir_promocije==4:
            nova_figura=sah.QUEEN
        zapis_poteza=str(potez)
        polje_napadnuto=zapis_poteza[2:]
        figura_napadnuta=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(polje_napadnuto)])
        # Креирање шаховског потеза (као трећи аргумент конструктору класе chess.Move() просљеђује се изабрана фигура)
        promjena_figure=sah.Move(potez.from_square,potez.to_square,promotion=nova_figura)
        print(promjena_figure)
        self.sahovska_tabla.push(promjena_figure)
        promocija=str(promjena_figure)
        self.crtanje_table()
        PY.display.update()
        pocetno_polje=promocija[:2]
        krajnje_polje=promocija[2:4]
        figura_promocija=promocija[4]
        figura_pocetna=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(pocetno_polje)])
        figura_krajnja=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(krajnje_polje)])
        # Конверзија алгебарског записа у индексе поља
        pocetno_polje_indeks=sah.parse_square(pocetno_polje)
        zeljeno_polje_indeks=sah.parse_square(krajnje_polje)
        # Ред и колона почетног и крајњег поља
        kolona_zeljeno = pocetno_polje_indeks % 8
        red_zeljeno = pocetno_polje_indeks // 8
        kolona_selektovano = zeljeno_polje_indeks % 8
        red_selektovano = zeljeno_polje_indeks // 8
        # Позив функције promocijaPjesaka()
        self.promocijaPjesaka(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano,figura_krajnja,figura_napadnuta)
#---------------------------------------------------------------------------------------------------------------
# Функција otvaranje() обезбјеђује потезе рачунара у фази шаховског отварања
    def otvaranje(self):
        # Књиге за шаховска отварања
        pocetna_otvaranja_1=r"C:\Users\Korisnik\Desktop\M11.2_bin\M11.2.bin"
        pocetna_otvaranja_2=r"C:\Users\Korisnik\Desktop\Eman_bin.book\Eman.bin"
        pocetna_otvaranja_3=r"C:\Users\Korisnik\Desktop\AdrianOliva.bin.Book\AdrianOliva.bin"
        pocetna_otvaranja_4=r"C:\Users\Korisnik\Desktop\Terk.bin\Terk.bin"
        lista_otvaranja=[pocetna_otvaranja_1,pocetna_otvaranja_2,pocetna_otvaranja_3,pocetna_otvaranja_4]
        for knjiga_otvaranja in lista_otvaranja:
            try:
                with chess.polyglot.open_reader(knjiga_otvaranja) as rd:
                    move = rd.get(self.sahovska_tabla)
                    if move:
                        print("Potez je uzet iz knjige:",knjiga_otvaranja)
                        return move.move
            except Exception as e:
                print(f"Greška prilikom učitavanja iz baze otvaranja: {e}")
        return None
#---------------------------------------------------------------------------------------------------------------
# Функција ispisvanje_rezultat()служи да испише исход шаховске партије на графичком екрану
    def ispisivanje_rezultata(self,tekst):
        PY.font.init()
        font_teksta=PY.font.SysFont("Arial",35)
        font_teksta.set_bold(True)
        pozadina_teksta=font_teksta.render(tekst,True,(0,0,0))
        tekst_mjesto=pozadina_teksta.get_rect(center=(300,300))
        pravougaonik = PY.Rect(
        tekst_mjesto.left - 10, tekst_mjesto.top - 10,
        tekst_mjesto.width + 20, tekst_mjesto.height + 20)
        PY.draw.rect(self.ploca,(255,0,0),pravougaonik)
        self.ploca.blit(pozadina_teksta,tekst_mjesto)
        PY.display.update()
#---------------------------------------------------------------------------------------------------------------
# Функција за провјеру мата у наредом потезу   
    def mat_provjera(self):
        lista_legalnih=list(self.sahovska_tabla.legal_moves)
        for potez in lista_legalnih:
            self.sahovska_tabla.push(potez)
            if self.sahovska_tabla.is_checkmate():
                self.sahovska_tabla.pop()
                return potez
            self.sahovska_tabla.pop()
        return None
#---------------------------------------------------------------------------------------------------------------
'''Функција potezRacunara()обезбјеђује функционално играње од стране рачунара. 
   Аргументи који се просљеђују ово функцији су максимална дубина претраживања и боја фигура.'''
    def potezRacunara(self,max_dubina,boja_figura):
        racunar=sahEngine(self.sahovska_tabla,max_dubina,boja_figura)
        # Случај када се потез добија помоћу функције mat_provjera()
        najbolji_potez=self.mat_provjera()
        if najbolji_potez!=None:
            # Tип потеза (промоција)
            if najbolji_potez.promotion is not None:
                pomocna=str(najbolji_potez)
                pocetno_polje=pomocna[:2]
                zeljeno_polje=pomocna[2:4]
                promocija_polje=pomocna[4]
                if promocija_polje=="q":
                    figura_krajnja=sah.Piece(sah.QUEEN,sah.BLACK)
                elif promocija_polje=="Q":
                    figura_krajnja=sah.Piece(sah.QUEEN,sah.WHITE)
                elif  promocija_polje=="r":
                    figura_krajnja=sah.Piece(sah.ROOK,sah.BLACK)
                elif  promocija_polje=="R":
                    figura_krajnja=sah.Piece(sah.ROOK,sah.WHITE)
                elif  promocija_polje=="N":
                    figura_krajnja=sah.Piece(sah.KNIGHT,sah.WHITE)
                elif  promocija_polje=="n":
                    figura_krajnja=sah.Piece(sah.KNIGHT,sah.BLACK)
                elif  promocija_polje=="b":
                    figura_krajnja=sah.Piece(sah.BISHOP,sah.BLACK)
                elif  promocija_polje=="B":
                    figura_krajnja=sah.Piece(sah.BISHOP,sah.WHITE)
                figura_pocetna=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(pocetno_polje)])
                figura_napadnuta=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(zeljeno_polje)])
                pocetno_polje_indeks=sah.parse_square(pocetno_polje)
                zeljeno_polje_indeks=sah.parse_square(zeljeno_polje)
                kolona_zeljeno = pocetno_polje_indeks % 8
                red_zeljeno = pocetno_polje_indeks // 8
                kolona_selektovano = zeljeno_polje_indeks % 8
                red_selektovano = zeljeno_polje_indeks // 8
                print(f"Potez računara je (minimax algoritam): {najbolji_potez}")
                self.sahovska_tabla.push(najbolji_potez)
                self.crtanje_table()
                # Позив функције promocijaPjesaka()
                self.promocijaPjesaka(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano,figura_krajnja,figura_napadnuta)
            else:
                pomocna=str(najbolji_potez)
                pocetno_polje=pomocna[:2]
                zeljeno_polje=pomocna[2:]
                figura_pocetna=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(pocetno_polje)])
                figura_krajnja=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(zeljeno_polje)])
                pocetno_polje_indeks=sah.parse_square(pocetno_polje)
                zeljeno_polje_indeks=sah.parse_square(zeljeno_polje)
                kolona_zeljeno = pocetno_polje_indeks % 8
                red_zeljeno = pocetno_polje_indeks // 8
                kolona_selektovano = zeljeno_polje_indeks % 8
                red_selektovano = zeljeno_polje_indeks // 8
                print(f"Potez računara je (minimax algoritam): {najbolji_potez}")
                # Tип потеза (рохада)
                if  najbolji_potez in self.sahovska_tabla.legal_moves and self.sahovska_tabla.is_castling(najbolji_potez):
                    self.sahovska_tabla.push(najbolji_potez)
                    self.crtanje_table()
                    if najbolji_potez.to_square==sah.G1 or najbolji_potez.to_square==sah.G8:
                        tip_rohade="mala"
                    else:
                        tip_rohade="velika"
                    # Позив функције rohada()
                    self.rohada(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano,tip_rohade)
                # Тип потеза (еn_passant)
                elif najbolji_potez in self.sahovska_tabla.legal_moves and self.sahovska_tabla.is_en_passant(najbolji_potez):
                    self.sahovska_tabla.push(najbolji_potez)
                    self.crtanje_table()
                    self.en_passant(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano)
                else:
                    self.sahovska_tabla.push(najbolji_potez)
                    self.crtanje_table()
                    self.pomjeranje_figura(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano,figura_pocetna,figura_krajnja)
            # Испис тренутне евалуације позиције у терминалу
            if boja_figura == sah.WHITE:
                print("Trenutna evaluacija pozicije (-)-crni ima prednost, (+)-bijeli ima prednost):",racunar.evaluacija_pozicije())
            else:
                print("Trenutna evaluacija pozicije (-)-crni ima prednost, (+)-bijeli ima prednost):",-racunar.evaluacija_pozicije())
            PY.display.update()
            return
        # Случај када се потез добија из базе отварања (провјера типа потеза је иста као и за прошли случај)
        else:    
            potez_iz_baze = self.otvaranje()
            if potez_iz_baze:
                najbolji_potez=potez_iz_baze
                if najbolji_potez.promotion is not None:
                    pomocna=str(najbolji_potez)
                    pocetno_polje=pomocna[:2]
                    zeljeno_polje=pomocna[2:4]
                    promocija_polje=pomocna[4]
                    if promocija_polje=="q":
                        figura_krajnja=sah.Piece(sah.QUEEN,sah.BLACK)
                    elif promocija_polje=="Q":
                        figura_krajnja=sah.Piece(sah.QUEEN,sah.WHITE)
                    elif  promocija_polje=="r":
                        figura_krajnja=sah.Piece(sah.ROOK,sah.BLACK)
                    elif  promocija_polje=="R":
                        figura_krajnja=sah.Piece(sah.ROOK,sah.WHITE)
                    elif  promocija_polje=="N":
                        figura_krajnja=sah.Piece(sah.KNIGHT,sah.WHITE)
                    elif  promocija_polje=="n":
                        figura_krajnja=sah.Piece(sah.KNIGHT,sah.BLACK)
                    elif  promocija_polje=="b":
                        figura_krajnja=sah.Piece(sah.BISHOP,sah.BLACK)
                    elif  promocija_polje=="B":
                        figura_krajnja=sah.Piece(sah.BISHOP,sah.WHITE)
                    figura_pocetna=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(pocetno_polje)])
                    figura_napadnuta=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(zeljeno_polje)])
                    pocetno_polje_indeks=sah.parse_square(pocetno_polje)
                    zeljeno_polje_indeks=sah.parse_square(zeljeno_polje)
                    kolona_zeljeno = pocetno_polje_indeks % 8
                    red_zeljeno = pocetno_polje_indeks // 8
                    kolona_selektovano = zeljeno_polje_indeks % 8
                    red_selektovano = zeljeno_polje_indeks // 8
                    print(f"Potez računara je (minimax algoritam): {najbolji_potez}")
                    self.sahovska_tabla.push(najbolji_potez)
                    self.crtanje_table()
                    self.promocijaPjesaka(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano,figura_krajnja,figura_napadnuta)
                else:
                    pomocna=str(najbolji_potez)
                    pocetno_polje=pomocna[:2]
                    zeljeno_polje=pomocna[2:]
                    figura_pocetna=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(pocetno_polje)])
                    figura_krajnja=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(zeljeno_polje)])
                    pocetno_polje_indeks=sah.parse_square(pocetno_polje)
                    zeljeno_polje_indeks=sah.parse_square(zeljeno_polje)
                    kolona_zeljeno = pocetno_polje_indeks % 8
                    red_zeljeno = pocetno_polje_indeks // 8
                    kolona_selektovano = zeljeno_polje_indeks % 8
                    red_selektovano = zeljeno_polje_indeks // 8
                    print(f"Potez računara je (baza otvaranja): {najbolji_potez}")
                    if  najbolji_potez in self.sahovska_tabla.legal_moves and self.sahovska_tabla.is_castling(najbolji_potez):
                        self.sahovska_tabla.push(najbolji_potez)
                        self.crtanje_table()
                        if najbolji_potez.to_square==sah.G1 or najbolji_potez.to_square==sah.G8:
                            tip_rohade="mala"
                        else:
                            tip_rohade="velika"
                        self.rohada(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano,tip_rohade)
                    elif najbolji_potez in self.sahovska_tabla.legal_moves and self.sahovska_tabla.is_en_passant(najbolji_potez):
                        self.sahovska_tabla.push(najbolji_potez)
                        self.crtanje_table()
                        self.en_passant(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano)
                    else:
                        self.sahovska_tabla.push(najbolji_potez)
                        self.crtanje_table()
                        self.pomjeranje_figura(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano,figura_pocetna,figura_krajnja)
                if boja_figura == sah.WHITE:
                    print("Trenutna evaluacija pozicije (-)-crni ima prednost, (+)-bijeli ima prednost):",racunar.evaluacija_pozicije())
                else:
                    print("Trenutna evaluacija pozicije (-)-crni ima prednost, (+)-bijeli ima prednost):",-racunar.evaluacija_pozicije())
                    PY.display.update()
                return
            # Случај када се потез добија помоћу минимакс алгоритма 
            else:
                najbolji_potez= racunar.najboljiPotez()
                if najbolji_potez.promotion is not None:
                    pomocna=str(najbolji_potez)
                    pocetno_polje=pomocna[:2]
                    zeljeno_polje=pomocna[2:4]
                    promocija_polje=pomocna[4]
                    if promocija_polje=="q":
                        figura_krajnja=sah.Piece(sah.QUEEN,sah.BLACK)
                    elif promocija_polje=="Q":
                        figura_krajnja=sah.Piece(sah.QUEEN,sah.WHITE)
                    elif  promocija_polje=="r":
                        figura_krajnja=sah.Piece(sah.ROOK,sah.BLACK)
                    elif  promocija_polje=="R":
                        figura_krajnja=sah.Piece(sah.ROOK,sah.WHITE)
                    elif  promocija_polje=="N":
                        figura_krajnja=sah.Piece(sah.KNIGHT,sah.WHITE)
                    elif  promocija_polje=="n":
                        figura_krajnja=sah.Piece(sah.KNIGHT,sah.BLACK)
                    elif  promocija_polje=="b":
                        figura_krajnja=sah.Piece(sah.BISHOP,sah.BLACK)
                    elif  promocija_polje=="B":
                        figura_krajnja=sah.Piece(sah.BISHOP,sah.WHITE)
                    figura_pocetna=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(pocetno_polje)])
                    figura_napadnuta=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(zeljeno_polje)])
                    pocetno_polje_indeks=sah.parse_square(pocetno_polje)
                    zeljeno_polje_indeks=sah.parse_square(zeljeno_polje)
                    kolona_zeljeno = pocetno_polje_indeks % 8
                    red_zeljeno = pocetno_polje_indeks // 8
                    kolona_selektovano = zeljeno_polje_indeks % 8
                    red_selektovano = zeljeno_polje_indeks // 8
                    print(f"Potez računara je (minimax algoritam): {najbolji_potez}")
                    self.sahovska_tabla.push(najbolji_potez)
                    self.crtanje_table()
                    self.promocijaPjesaka(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano,figura_krajnja,figura_napadnuta)
                else:
                    pomocna=str(najbolji_potez)
                    pocetno_polje=pomocna[:2]
                    zeljeno_polje=pomocna[2:]
                    figura_pocetna=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(pocetno_polje)])
                    figura_krajnja=self.sahovska_tabla.piece_at(sah.SQUARES[sah.parse_square(zeljeno_polje)])
                    pocetno_polje_indeks=sah.parse_square(pocetno_polje)
                    zeljeno_polje_indeks=sah.parse_square(zeljeno_polje)
                    kolona_zeljeno = pocetno_polje_indeks % 8
                    red_zeljeno = pocetno_polje_indeks // 8
                    kolona_selektovano = zeljeno_polje_indeks % 8
                    red_selektovano = zeljeno_polje_indeks // 8
                    print(f"Potez racunara je (minimax algoritam):{najbolji_potez}")
                    if  najbolji_potez in self.sahovska_tabla.legal_moves and self.sahovska_tabla.is_castling(najbolji_potez):
                        self.sahovska_tabla.push(najbolji_potez)
                        self.crtanje_table()
                        if najbolji_potez.to_square==sah.G1 or najbolji_potez.to_square==sah.G8:
                            tip_rohade="mala"
                        else:
                            tip_rohade="velika"
                        self.rohada(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano,tip_rohade)
                    elif najbolji_potez in self.sahovska_tabla.legal_moves and self.sahovska_tabla.is_en_passant(najbolji_potez):
                        self.sahovska_tabla.push(najbolji_potez)
                        self.crtanje_table()
                        self.en_passant(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano)
                    else:
                        self.sahovska_tabla.push(najbolji_potez)
                        self.crtanje_table()
                        self.pomjeranje_figura(red_zeljeno,kolona_zeljeno,red_selektovano,kolona_selektovano,figura_pocetna,figura_krajnja)
                if boja_figura == sah.WHITE:
                    print("Trenutna evaluacija pozicije (-)-crni ima prednost, (+)-bijeli ima prednost):",racunar.evaluacija_pozicije())
                else:
                    print("Trenutna evaluacija pozicije (-)-crni ima prednost, (+)-bijeli ima prednost):",-racunar.evaluacija_pozicije())
                    PY.display.update()
#---------------------------------------------------------------------------------------------------------------
'''Функција pocetakIgre() омогућава уношење почетних параметара игре, наизмјенично позивање функција potezIgraca() и 
potezRacunara() (играч против рачунара) или само функције potezIgraca() (играч против играча), све док се не дође до неког од коначних исхода.'''
    def pocetakIgre(self):
        boja_igraca=None
        maks_dubina=None
        modIgre=None
        # Избор типа игре (против играча или рачунара)
        while(modIgre!="igrac" and modIgre!="racunar"):
            modIgre=input("Unesite da li zelite igrati protiv igraca ili racunara (igrac ili racunar):").lower()
        # Случај када играч игра против рачунара 
        if modIgre=="racunar":
            self.crtanje_table()
            while(boja_igraca!="b" and boja_igraca!="c"):
                boja_igraca=input("Unesite boju igraca:").lower()
            while True:
                try:
                    maks_dubina=int(input("Unesite maksimalnu dubinu pretrage:"))
                    break
                except ValueError:
                    print("Unesena vrednost nije broj! Pokušajte ponovo.")
            pocetna_pozicija=RDK.Item("pocetna_pozicija",robolink.ITEM_TYPE_PROGRAM)
            pocetna_pozicija.RunProgram()
            # Случај када играч има црне фигуре
            if boja_igraca=="c":
                '''while петља омогућава да се одвија игра све док се не дође до неког од коначних исхода, 
                када се излази из петље употребом кључне ријечи break'''
                while(True):
                    # Приказивање шаховске табле у терминалу (конзоли)
                    print(self.sahovska_tabla)
                    print("Racunar je na potezu")
                    self.potezRacunara(maks_dubina,sah.WHITE)
                    '''Провјера да ли је на шаховској табли дошло до мата након потеза рачунара
                    (ако јесте, на екрану се исписује порука да је рачунар побједио)'''
                    if(self.sahovska_tabla.is_checkmate()==True):
                        print("Racunar je pobjedio")
                        self.ispisivanje_rezultata("Racunar je pobjedio")
                        break
                    # Провјера да ли је на шаховској табли дошло до пата послије потеза рачунара
                    elif(self.sahovska_tabla.is_stalemate()==True):
                        print("Rezultat je nerjesen (stalemate)!")
                        self.ispisivanje_rezultata("Rezultat je nerjesen (stalemate)!")
                        break
                    # Провјера да ли је одређена позиција поновљена 5 пута (функција is_fivefold_repetition())
                    elif (self.sahovska_tabla.is_fivefold_repetition()==True):
                        print("Rezultat je nerjesen (fivefold repetition)!")
                        self.ispisivanje_rezultata("Rezultat je nerjesen (fivefold repetition)!")
                        break
                    '''Провјера да ли je на шаховској табли остало довољно материјала 
                    (ако нема довољно материјала, партија завршава ремијем)'''
                    elif (self.sahovska_tabla.is_insufficient_material()==True):
                        print("Rezultat je nerjesen (nedovoljno materijala na tabli)")
                        self.ispisivanje_rezultata("Rezultat je nerjesen (nedovoljno materijala na tabli)")
                        break
                    else:
                        print(self.sahovska_tabla)
                        print("Igrac je na potezu")
                        self.potezIgraca()
                        if (self.sahovska_tabla.is_checkmate()==True):
                            print("Igrac je pobjedio!")
                            self.ispisivanje_rezultata("Igrac je pobjedio!")
                            break
                        elif (self.sahovska_tabla.is_stalemate()==True):
                            print("Rezultat je nerjesen (stalemate)!")
                            self.ispisivanje_rezultata("Rezultat je nerjesen (stalemate)!")
                            break
                        elif (self.sahovska_tabla.is_fivefold_repetition()==True):
                            print("Rezultat je nerjesen (fivefold repetition)!")
                            self.ispisivanje_rezultata("Rezultat je nerjesen (fivefold repetition)!")
                            break
                        elif (self.sahovska_tabla.is_insufficient_material()==True):
                            print("Rezultat je nerjesen (nedovoljno materijala na tabli)")
                            self.ispisivanje_rezultata("Rezultat je nerjesen (nedovoljno materijala na tabli)")
                            break 
                print(self.sahovska_tabla)
                # Исписивање резултата у конзоли
                print(self.sahovska_tabla.outcome())
            # Случај када играч има бијеле фигуре
            elif boja_igraca=="b":
                while(True):
                    print(self.sahovska_tabla)
                    print("Igrac je na potezu")
                    self.potezIgraca()
                    if (self.sahovska_tabla.is_checkmate()==True):
                        print("Igrac je pobjedio!")
                        self.ispisivanje_rezultata("Igrac je pobjedio")
                        break
                    elif(self.sahovska_tabla.is_stalemate()==True):
                        print("Rezultat je nerjesen (stalemate)!")
                        self.ispisivanje_rezultata("Rezultat je nerjesen (stalemate)!")
                        break
                    elif (self.sahovska_tabla.is_fivefold_repetition()==True):
                        print("Rezultat je nerjesen (fivefold repetition)!")
                        self.ispisivanje_rezultata("Rezultat je nerjesen (fivefold repetition)!")
                        break
                    elif (self.sahovska_tabla.is_insufficient_material()==True):
                        print("Rezultat je nerjesen (nedovoljno materijala na tabli)")
                        self.ispisivanje_rezultata("Rezultat je nerjesen (nedovoljno materijala na tabli)")
                        break
                    else:
                        print(self.sahovska_tabla)
                        print("Racunar je na potezu")
                        self.potezRacunara(maks_dubina,sah.BLACK)
                        if (self.sahovska_tabla.is_checkmate()==True):
                            print("Racunar je pobjedio!")
                            self.ispisivanje_rezultata("Racunar je pobjedio!")
                            break
                        elif (self.sahovska_tabla.is_stalemate()==True):
                            print("Rezultat je nerjesen (stalemate)!")
                            self.ispisivanje_rezultata("Rezultat je nerjesen (stalemate)!")
                            break
                        elif (self.sahovska_tabla.is_fivefold_repetition()==True):
                            print("Rezultat je nerjesen (fivefold repetition)!")
                            self.ispisivanje_rezultata("Rezultat je nerjesen (fivefold repetition)!")
                            break
                        elif (self.sahovska_tabla.is_insufficient_material()==True):
                            print("Rezultat je nerjesen (nedovoljno materijala na tabli)")
                            self.ispisivanje_rezultata("Rezultat je nerjesen (nedovoljno materijala na tabli)")
                            break 
                print(self.sahovska_tabla)
                print(self.sahovska_tabla.outcome())
            self.sahovska_tabla.reset()
            # Позив функције pocetakIgre() (уколико желимо играти нову партију)
            self.pocetakIgre()
        # Случај када играч игра против другог играча
        elif modIgre=="igrac":
            pocetna_pozicija=RDK.Item("pocetna_pozicija",robolink.ITEM_TYPE_PROGRAM)
            pocetna_pozicija.RunProgram()
            self.crtanje_table()
            while(True):
                print("------------------------------")
                print(self.sahovska_tabla)
                print("-----------------------")
                print("BIJELI IGRAC NA POTEZU!")
                print("-----------------------")
                print("Lista legalnih poteza")
                print("-----------------------")
                # Испис свих легалних потеза за тренутног играча у конзоли
                print(list(self.sahovska_tabla.legal_moves))
                print("------------------------------")
                self.potezIgraca()
                if (self.sahovska_tabla.is_checkmate()==True):
                    print("Bijeli igrac je pobjedio!")
                    self.ispisivanje_rezultata("Bijeli igrac je pobjedio!")
                    break
                elif (self.sahovska_tabla.is_stalemate()==True):
                    print("Rezultat je nerjesen (stalemate)!")
                    self.ispisivanje_rezultata("Rezultat je nerjesen (stalemate)!")
                    break
                elif (self.sahovska_tabla.is_fivefold_repetition()==True):
                    print("Rezultat je nerjesen (fivefold repetition)!")
                    self.ispisivanje_rezultata("Rezultat je nerjesen (fivefold repetition)!")
                    break
                elif (self.sahovska_tabla.is_insufficient_material()==True):
                        print("Rezultat je nerjesen (nedovoljno materijala na tabli)")
                        self.ispisivanje_rezultata("Rezultat je nerjesen (nedovoljno materijala na tabli)")
                        break
                else:
                    print("------------------------------")
                    print(self.sahovska_tabla)
                    print("-----------------------")
                    print("CRNI IGRAC JE NA POTEZU!")
                    print("-----------------------")
                    print("Lista legalnih poteza")
                    print("-----------------------")
                    print(list(self.sahovska_tabla.legal_moves))
                    print("------------------------------")
                    self.potezIgraca()
                    if (self.sahovska_tabla.is_checkmate()==True):
                        print("Crni igrac je pobjedio!")
                        self.ispisivanje_rezultata("Crni igrac je pobjedio!")
                        break
                    elif (self.sahovska_tabla.is_stalemate()==True):
                        print("Rezultat je nerjesen (stalemate)!")
                        self.ispisivanje_rezultata("Rezultat je nerjesen (stalemate)!")
                        break
                    elif (self.sahovska_tabla.is_fivefold_repetition()==True):
                        print("Rezultat je nerjesen (fivefold repetition)!")
                        self.ispisivanje_rezultata("Rezultat je nerjesen (fivefold repetition)!")    
                        break
                    elif (self.sahovska_tabla.is_insufficient_material()==True):
                        print("Rezultat je nerjesen (nedovoljno materijala na tabli)")
                        self.ispisivanje_rezultata("Rezultat je nerjesen (nedovoljno materijala na tabli)")
                        break
            print(self.sahovska_tabla)
            print(self.sahovska_tabla.outcome())  
            self.sahovska_tabla.reset()
            self.pocetakIgre()
# Провјера успјешности конекције са роботом
if robot.Connect()>0:
    # Аутоматско добијање почетне позиције робота
    robot.Joints()
    print("Uspjelo je povezivanje sa robotom")
else:
    raise Exception("Nije uspjelo povezivanje sa robotom")
# Креирање објекта шаховске табле
sahovska_tabla=sah.Board()
# Креирање објекта класе Igra
Sahovska_igra=Igra(sahovska_tabla)
# Позив функције pocetakIgre()
Sahovska_igra.pocetakIgre()



