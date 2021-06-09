import pygame
import os
import random
import csv
pygame.init()

root_x = 800
root_y = int(root_x * 1)

root = pygame.display.set_mode((root_x, root_y))
pygame.display.set_caption("SFEB")

clock = pygame.time.Clock()                                                      
fps = 60

gravity = 0.75
rows = 16
cols = 150
tile_size = root_y // rows
tile_types = 21
level = 1

moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

img_list = []
for x in range(tile_types):
    img = pygame.image.load(f'sprites/tile/{x}.png')
    img = pygame.transform.scale(img, (tile_size, tile_size))
    img_list.append(img)

#пуля
bullet_img = pygame.image.load("sprites/icons/bullet.png").convert_alpha()
#граната
grenade_img = pygame.image.load("sprites/icons/grenade.png").convert_alpha()
#коробки
health_box_img = pygame.image.load("sprites/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("sprites/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("sprites/icons/grenade_box.png").convert_alpha()

item_boxes = {
    'Health'    :health_box_img,
    'Ammo'      :ammo_box_img,
    'Grenade'   :grenade_box_img

}

BG = (123, 102, 102)
red = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    root.blit(img, (x, y))

def draw_bg():
    root.fill(BG)
    pygame.draw.line(root, red, (0,400), (root_x,400))


class Solder(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 200, 20)
        self.idling = False
        self.idling_counter = 0

        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f"sprites/{self.char_type}/{animation}"))

            for i in range(num_of_frames):
                img = pygame.image.load(f"sprites/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        #gravity_jump
        self.vel_y += gravity
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        if self.rect.bottom + dy > 400:
            dy = 400 - self.rect.bottom
            self.in_air = False
        
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > tile_size:
                    	self.direction *= -1
                    	self.move_counter *= -1
                else:
                	self.idling_counter -= 1
                	if self.idling_counter <= 0:
                		self.idling = False

    def update_animation(self):
        animation_coldown = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_coldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) -1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3) 

    def draw(self):
        root.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                img = img_list[tile]
                img_rect = img.get_rect()
                img_rect.x = x * tile_size
                img_rect.y = y * tile_size
                tile_data = (img, img_rect)
                
                if tile >= 0 and tile <= 8:
                    self.obstacle_list.append(tile_data)
                elif tile >= 9 and tile <= 10:
                    water = Water(img, x * tile_size, y * tile_size)
                    water_group.add(water)
                elif tile >= 11 and tile <= 14:
                    decoration = Decoration(img, x * tile_size, y * tile_size)
                    decoration_group.add(water)
                elif tile == 15: #персонаж
                    player = Solder('player', x * tile_size, y * tile_size, 1.65, 5, 20, 5)
                    health_bar = HealthBar(10, 10, player.health, player.health)
                elif tile == 16: #персонаж
                    enemy = Solder('enemy', x * tile_size, y * tile_size, 1.65, 5, 20, 5) #если что убрать гранаты если сломается!!!!!!!!!!!!!!
                    enemy_group.add(enemy)
                elif tile == 17:
                    item_box = ItemBox('Ammo', x * tile_size, y * tile_size)
                    item_box_group.add(item_box)
                elif tile == 18:
                    item_box = ItemBox('Grenade', x * tile_size, y * tile_size)
                    item_box_group.add(item_box)
                elif tile == 19:
                    item_box = ItemBox('Health', x * tile_size, y * tile_size)
                    item_box_group.add(item_box)
                elif tile == 20:
                    exit = Exit(img, x * tile_size, y * tile_size)
                    exit_group.add(exit)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            root.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y +(tile_size - self.image.get_height()))

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y +(tile_size - self.image.get_height()))

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y +(tile_size - self.image.get_height()))

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(root, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(root, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(root, GREEN, (self.x,self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction

    def update(self):
        #движение пули
        self.rect.x += (self.direction * self.speed)
        #коллизия пули
        if self.rect.right < 0 or self.rect.left > root_x:
            self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -=1
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

class ItemBox(pygame.sprite.Sprite):
    def __init__(self,item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y +(tile_size - self.image.get_height()))

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health

            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3

            self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction

    def update(self):
        self.vel_y += gravity
        dx = self.direction * self.speed
        dy = self.vel_y

        if self.rect.bottom + dy > 400:
            dy = 400 - self.rect.bottom
            self.speed = 0

        if self.rect.left + dx < 0 or self.rect.right + dx > root_x:
            self.direction *= -1
            dx = self.direction * self.speed

        self.rect.x += dx
        self.rect.y += dy

        #таймер до взрыва
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            if abs(self.rect.centerx - player.rect.centerx) < tile_size * 2 and abs(self.rect.centery - player.rect.centery) < tile_size * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < tile_size * 2 and abs(self.rect.centery - enemy.rect.centery) < tile_size * 2:
                    enemy.health -= 50

   
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f'sprites/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0


	def update(self):
		EXPLOSION_SPEED = 4
		self.counter += 1

		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]


enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

item_box = ItemBox('Health', 100, 363)
item_box_group.add(item_box)
item_box = ItemBox('Ammo', 400, 363)
item_box_group.add(item_box)
item_box = ItemBox('Grenade', 600, 363)
item_box_group.add(item_box)

player = Solder('player', 200, 200, 1.65, 5, 10, 10)
health_bar = HealthBar(10, 10, player.health, player.health)

enemy = Solder('enemy', 500, 200, 1.65, 2, 20, 0)
enemy2 = Solder('enemy', 300, 200, 1.65, 2, 20, 0)

enemy_group.add(enemy)
enemy_group.add(enemy2)


run = True
while run:

    clock.tick(fps)

    draw_bg()

    health_bar.draw(player.health)

    draw_text("AMMO: ",font, WHITE, 10, 35)
    for x in range(player.ammo):
        root.blit(bullet_img, (90+(x*10), 40))
    
    draw_text("GRENADES: ",font, WHITE, 10, 60)
    for x in range(player.grenades):
        root.blit(grenade_img, (135+(x*15), 60))

    player.update()
    player.draw()

    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    item_box_group.update()

    bullet_group.draw(root)
    grenade_group.draw(root)
    explosion_group.draw(root)
    item_box_group.draw(root)
    
    if player.alive:
        if shoot:
            player.shoot()
        elif grenade and grenade_thrown == False and player.grenades > 0:
            grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), player.rect.top, player.direction)
            grenade_group.add(grenade)
            player.grenades -= 1
            grenade_thrown = True

        if player.in_air:
            player.update_action(2) #jump
        elif moving_left or moving_right:
            player.update_action(1) # run
        else:
            player.update_action(0) # idle
        player.move(moving_left, moving_right)

    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            run = False

        if i.type == pygame.KEYDOWN:
            if i.key == pygame.K_a:
                moving_left = True
            if i.key == pygame.K_d:
                moving_right = True
            if i.key == pygame.K_SPACE and player.alive:
                player.jump = True
            if i.key == pygame.K_r:
                grenade = True
            if i.key == pygame.K_f:
                shoot = True
            if i.key == pygame.K_ESCAPE:
                run = False

        if i.type == pygame.KEYUP:
            if i.key == pygame.K_a:
                moving_left = False
            if i.key == pygame.K_d:
                moving_right = False
            if i.key == pygame.K_f:
                shoot = False
            if i.key == pygame.K_r:
                grenade = False
                grenade_thrown = False


    pygame.display.update()

pygame.quit()
quit()