import pygame
import os
import time
import random
pygame.font.init()

# Game window
Width,Height = 720, 720
WIN = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Space Shooters")

# load images
Red_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
Green_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
Blue_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
# player player
Yellow_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))
# laser
Red_laser = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
Green_laser = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
Blue_laser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
Yellow_laser = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
# background
BG = pygame.image.load(os.path.join("assets", "background-black.png"))
BG = pygame.transform.scale(BG, (Width, Height))

# paren class ship
class Ship:
    COOLDOWN = 30
    def __init__(self,x,y,health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()

    # a way to move ship laser(used mainly by enemy ships as it is overwritten for the player ship)
    def move_laser(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(Height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter >0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

# player object that inherits from Ship
class Player(Ship):
    def __init__(self, x,y, health=100):
        super().__init__(x, y, health)
        self.ship_img = Yellow_space_ship
        self.laser_img = Yellow_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    # a function to move the laser of the player and check whether it hist enemy ships or not
    def move_laser(self,vel,objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(Height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
    # over writes the draw function of the parent class ship, by copying the same stuff but adding a life bar
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window,(255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(),10))
        pygame.draw.rect(window,(0,255,0),(self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width()*(self.health/self.max_health), 10))

# enemy object that inherits from Ship
class Enemy(Ship):
    Color_Map = {
            "red": (Red_space_ship,Red_laser),
            "green": (Green_space_ship, Green_laser),
            "blue":(Blue_space_ship, Blue_laser)
    }
    def __init__(self,x,y,color,health= 100):
        super().__init__(x, y, health)
        self.ship_img,self.laser_img = self.Color_Map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    # movement
    def move(self, vel):
         self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

# Laser object
class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self,vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)

def collide(obj1,obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5
    player = Player(300, 605)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    # a function that draws everything
    def redraw_window():
        WIN.blit(BG, (0,0))
        # drawing texts
        lives_label = main_font.render(f"Lives:{lives}",1,(255,255,255))
        level_label = main_font.render(f"Level:{level}", 1, (255, 255, 255))
        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (Width - level_label.get_width()-10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255,255,255))
            WIN.blit(lost_label, (Width/2 - lost_label.get_width()/2,350))

        pygame.display.update()

    # a function that moves and runes every thing based on the FPS
    while run:
        clock.tick(FPS)
        redraw_window()
        
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        # lost message counter/ pauses the gam once life(player health) hits zero
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
                
        # creates the enemies and puts them in a list
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, Width-100), random.randrange(-1500, 100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        # pressing x in the right corner quits the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                quit()

        # player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: #left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < Width: #right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: #up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < Height: #down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        player.move_laser(-laser_vel, enemies)

        # enemy movement and shooting
        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel,player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > Height:
                lives -=1
                enemies.remove(enemy)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 40)
    run = True
    while run:
        WIN.blit(BG,(0,0))
        title_lable = title_font.render("Press the Mouse to Beign...",1,(255,255,255))
        WIN.blit(title_lable,(Width/2 - title_lable.get_width()/2,350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

if __name__ == '__main__':
    main_menu()