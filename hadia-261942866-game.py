import pygame
import random
pygame.font.init()
pygame.init()

# x and y position and screen height and width
x = 50
y = 50
width = 650
height = 650

#load music
music = pygame.mixer.music.load('game/Fluffing-a-Duck.mp3')
pygame.mixer.music.play(-1)
#load sound effect
lostsound = pygame.mixer.Sound('game/lostgame.mp3')
hitsound = pygame.mixer.Sound('game/hit.wav')

#load images
enemy_ship_blue = pygame.image.load('game/ufoz.png')
enemy_ship_red = pygame.image.load('game/ufoz.png')
player_bullets = pygame.image.load('game/spr_bullet_strip.png')
enemy_bullets_red = pygame.image.load('game/spr_bullet_strip.png')
player_ship = pygame.image.load('game/playership.png')


 
#background
bg = pygame.transform.scale(pygame.image.load(('game/bg.png')), (width,height))

#canvas
pygame.display.set_caption(('Space Shooter'))
win = pygame.display.set_mode((width,height))

class Ship: #base class or abstract class
    slowdown = 30
    def __init__(self, x, y ,health =100):
        self.x = x
        self.y = y
        self.slow_down_counter = 0
        self.health = health
        self.ship =   None
        self.bullets = None  # compositon : ship has instance of bullets
        self.bullet_lst = []
    def getwidth(self):
        return self.ship.get_width()
    def getheight(self):
        return self.ship.get_height()
    def draw(self, win):
        win.blit(self.ship, (self.x,self.y))
        for i in self.bullet_lst:
            i.draw(win)
    
    def bulletmovements(self,vel,objz):
        self.slowdownz()
        for i in self.bullet_lst:
            i.move(vel)
            if i.out_screen(height):
                self.bullet_lst.remove(i)
            elif i.collision(objz):
                objz.health -= 10
                self.bullet_lst.remove(i)
    def shoot(self):  #abstarct method
        if self.slow_down_counter == 0:
            bullet = Bullets(self.x,self.y,self.bullets) # compositon is used as bullets class is passed as instances in ship class and is called. 
            self.bullet_lst.append(bullet)
            self.slow_down_counter = 1

    def slowdownz(self): # for not spamming the bullets
        if self.slow_down_counter >= self.slowdown:
            self.slow_down_counter = 0
        elif self.slow_down_counter >0:
            self.slow_down_counter +=1


            
class Playership(Ship): #inheritance as it inherits properties of ship class. 
    def __init__(self,x,y,health =100):
        super().__init__(x,y,health)
        self.ship = player_ship
        self.player_bullets = player_bullets  
        self.x = width//2
        self.y = height//2
        self.max_health = health
        self.mask = pygame.mask.from_surface(self.ship)
        self.score = 0
 
    def healthbar(self,win):
        pygame.draw.rect(win, (255,0,0),(self.x,self.y + self.ship.get_height() + 10, self.ship.get_width(),10))
        pygame.draw.rect(win, (0,255,0),(self.x,self.y + self.ship.get_height() + 10,self.ship.get_width() * (self.health/self.max_health),10)) 

    def draw(self,win):   #method override
        super().draw(win)
        self.healthbar(win)

    def shoot(self): #method override
        if self.slow_down_counter == 0:
            bullet = Bullets(self.x+20,self.y,self.bullets) 
            self.bullet_lst.append(bullet)
            self.slow_down_counter = 1
        

    def bulletmovements(self,vel,objp): #overrideing methods from the ship class
        self.slowdownz()
        for i in self.bullet_lst:
            i.move(vel)
            if i.out_screen(height):
                self.bullet_lst.remove(i)
            else:
                for obj in objp:
                    if  i.collision(obj):
                        objp.remove(obj)
                        self.bullet_lst.remove(i)
                        self.score += 50
                        hitsound.play()
                        



class Enemyship(Ship): #inheritance as it inherits properties of ship class.
    color_keys = {'red':(enemy_ship_red, enemy_bullets_red),
                 'blue':(enemy_ship_blue, enemy_bullets_red)
                 }
    def __init__(self,x,y,color,health=100):
        super().__init__(x,y,health)
        self.ship,self.bullets = self.color_keys[color]
        self.mask = pygame.mask.from_surface(self.ship)
    
    def move(self,velo):
        self.y += velo
    
    def shoot(self): #method override
        if self.slow_down_counter == 0:
            bullet = Bullets(self.x+20,self.y,self.bullets) 
            self.bullet_lst.append(bullet)
            self.slow_down_counter = 1
    
class Bullets:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.bullet_image = enemy_bullets_red
        self.mask = pygame.mask.from_surface(self.bullet_image)
    
    def draw(self,win): 
        win.blit(self.bullet_image, [self.x,self.y])
    
    def move(self,vel): 
        self.y += vel
    def out_screen(self,height ): # when obj is out of screen
        return not(self.y <=height and self.y >= 0)
    def collision(self,obj):
        return collide(self,obj)
    
def collide(obj1,obj2):
        offset_x = obj2.x - obj1.x
        offset_y = obj2.y - obj1.y
        return obj1.mask.overlap(obj2.mask,(offset_x, offset_y)) != None

def main():
    run = True
    frame_rate = 60
    lives = 6
    levels = 0  
    player_velo = 5
    bullet_velo = 4
    enemyz =[]
    wave_length = 3
    enemy_velo = 1
    lost = False
    lost_time = 0
    highscore = 0
    
    font = pygame.font.SysFont('arial', 40)
    main_fonts = pygame.font.SysFont('arial', 40)
    lost_fonts = pygame.font.SysFont('arial', 40) 
    player = Playership(300,630) 


    clock = pygame.time.Clock()
    

    def drawGameWindow( ):
        win.blit(bg, (0,0))
        #draw text
        lives_label = main_fonts.render(f'Lives: {lives}',1,(255,255,255))
        level_label = main_fonts.render(f'Level: {levels}',1,(255,255,255))
        highscore_label = main_fonts.render(f"High Score: {highscore}", 1, (255,255,255))
        score_label = main_fonts.render(f"Score: {player.score}", 1, "white")
        win.blit(score_label,(10,60))
        win.blit(highscore_label,(10, height - 60))
        win.blit(lives_label,(10,10))
        win.blit(level_label, (width - level_label.get_width() -10, 10))
        
        for enemy in enemyz:
            enemy.draw(win)
        player.draw(win)
        if lost:  # when game is lost text
            lost_label = lost_fonts.render("YOU LOST!!", 1,(255,0,0))
            win.blit(lost_label,(width/2 - lost_label.get_width()/2, 350))
            lostsound.play()
           
        pygame.display.update()
    

    while run:
        clock.tick(frame_rate)
        drawGameWindow()
        
        
        if len(enemyz) == 0:
            levels +=1
            wave_length +=1
            enemy_velo +=1
            for i in range(wave_length):
                enemy = Enemyship(random.randrange(100, width-100), random.randrange(-1500,-100),random.choice(['red', 'blue']))
                enemyz.append(enemy)

        if lives <= 0 or player.health <= 0:
            lost = True
            highscore = player.score
            lost_time +=1 
        if lost: # after when game is lost
            if lost_time > frame_rate * 3:
                run = False
            else:
                continue
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit()
        
          # key functions
        userinput = pygame.key.get_pressed()
        if userinput[pygame.K_LEFT] and player.x - player_velo >0:
            player.x -= player_velo
        if userinput[pygame.K_RIGHT] and player.x + player_velo + 100 <  width:
            player.x += player_velo
        if userinput[pygame.K_UP] and player.y - player_velo > 0:
            player.y -= player_velo
        if userinput[pygame.K_DOWN] and player.y + player_velo + 100 < height:
            player.y += player_velo
        if userinput[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemyz[:]:
            enemy.move(enemy_velo)
            enemy.bulletmovements(bullet_velo, player) # bullets will from enemy to player
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            
            if collide(enemy,player):
                player.health-= 10
                enemyz.remove(enemy)
                player.score += 30
                

            elif enemy.y + enemy.getheight() > height:
                lives -= 1
                enemyz.remove(enemy)

        player.bulletmovements(-bullet_velo, enemyz) #bullets will move from player to enemy



#menu
def menu():
    menu_font = pygame.font.SysFont('comicsans', 50)
    run = True
    while run:
        win.blit(bg,(0,0))
        menu_label = menu_font.render('Press mouse to play...', 1, (255,255,255))
        win.blit(menu_label, (width/2 - menu_label.get_width()/2, 350)) 
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    quit()
menu()
