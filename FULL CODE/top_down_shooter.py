
import pygame
from sys import exit
import math
from csv import reader
from settings import *
import random
from os import walk

pygame.init()

# window and text
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Zombie Game')
clock = pygame.time.Clock()

# fonts
font = pygame.font.Font("font/PublicPixel.ttf", 20)
small_font = pygame.font.Font("font/PublicPixel.ttf", 15)
title_font = pygame.font.Font("font/PublicPixel.ttf", 60)
score_font = pygame.font.Font("font/PublicPixel.ttf", 50)

# loads imgs
background = pygame.image.load("data/tmx/Map.png").convert()
plain_bg = pygame.image.load("background/black bg.png").convert()
coin_imgs = import_folder("items/coin")

#bullet_img = pygame.image.load("bullets/bluebullet.png").convert_alpha()
bullet_img = pygame.image.load("bullet/0.png").convert_alpha()

boundary_block_img = pygame.image.load("tileset/skyBlock.png").convert_alpha()

# Sounds
coin_sound = pygame.mixer.Sound("sounds/coin.wav")
health_potion_sound = pygame.mixer.Sound("sounds/health_pick_up.wav")
hurt_sound = pygame.mixer.Sound("sounds/hurt.mp3")
death_sound = pygame.mixer.Sound("sounds/death.mp3")
gun_shot_sound = pygame.mixer.Sound("sounds/gunshot.wav")
necromancer_death_sound = pygame.mixer.Sound("sounds/necromancer death.wav")
nightborne_death_sound = pygame.mixer.Sound("sounds/nightborne death.mp3")
gun_shot_sound.set_volume(0.5)
health_potion_sound.set_volume(0.3)


top_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_18.png").convert_alpha(), (1,2))
bottom_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_46.png").convert_alpha(), (1,2))
right_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_17.png").convert_alpha(), (1,2))
left_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_19.png").convert_alpha(), (1,2))
topright_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_23.png").convert_alpha(), (1,2))
topleft_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_24.png").convert_alpha(), (1,2))
left_wall_connect_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_31.png").convert_alpha(), (1,2))
right_wall_connect_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_30.png").convert_alpha(), (1,2))
topright_black_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_38.png").convert_alpha(), (1,2))
topleft_black_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_39.png").convert_alpha(), (1,2))
torch_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_39.png").convert_alpha(), (1,2))

game_active = True
beat_game = False
current_time = 0
level_over_time = 0
ready_to_spawn = False
display_countdown_time = False
first_level = True

def hitbox_collide(sprite1, sprite2):
    return sprite1.base_zombie_rect.colliderect(sprite2.rect)

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("player/0.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.35)
        self.base_player_image = self.image

        self.pos = pos
        self.vec_pos = pygame.math.Vector2(pos)
        self.base_player_rect = self.base_player_image.get_rect(center = pos)
        self.rect = self.base_player_rect.copy()

        self.player_speed = 10 
        self.shoot = False
        self.shoot_cooldown = 0

        self.health = 100

        self.gun_barrel_offset = pygame.math.Vector2(45,20)
        

    def player_turning(self): 
        self.mouse_coords = pygame.mouse.get_pos() 

        self.x_change_mouse_player = (self.mouse_coords[0] - (WIDTH // 2))
        self.y_change_mouse_player = (self.mouse_coords[1] - (HEIGHT // 2))
        self.angle = int(math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player)))
        self.angle = (self.angle) % 360 # if this stop working add 360 in the brackets

        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center = self.base_player_rect.center)


    def player_input(self):   
        self.velocity_x = 0
        self.velocity_y = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.velocity_y = -self.player_speed
        if keys[pygame.K_s]:
            self.velocity_y = self.player_speed
        if keys[pygame.K_d]:
            self.velocity_x = self.player_speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.player_speed
            
        if self.velocity_x != 0 and self.velocity_y != 0: # moving diagonally
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)

        if pygame.mouse.get_pressed() == (1, 0, 0) or keys[pygame.K_SPACE]: 
            self.shoot = True
            self.is_shooting() 
                    
        else:
            self.shoot = False

        if event.type == pygame.KEYUP:
            if pygame.mouse.get_pressed() == (1, 0, 0):
                self.shoot = False

    def move(self):
        self.base_player_rect.centerx += self.velocity_x
        self.check_collision("horizontal")

        self.base_player_rect.centery += self.velocity_y
        self.check_collision("vertical")

        self.rect.center = self.base_player_rect.center 
        
        self.vec_pos = (self.base_player_rect.centerx, self.base_player_rect.centery)
        
    def is_shooting(self):
        if self.shoot_cooldown == 0 and self.shoot:
            gun_shot_sound.play()
            spawn_bullet_pos = self.vec_pos + self.gun_barrel_offset.rotate(self.angle)
            self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            self.shoot_cooldown = 10
            bullet_group.add(self.bullet)
            all_sprites_group.add(self.bullet)
   
    def get_damage(self, amount):
        if ui.current_health > 0:
            ui.current_health -= amount
            self.health -= amount
            if ui.current_health > 0:
                hurt_sound.play()
            else:
                death_sound.play()
        if ui.current_health <= 0: # dead
            ui.current_health = 0
            self.health = 0
            
        
    def increase_health(self, amount):
        if ui.current_health < ui.maximum_health:
            ui.current_health += amount
            self.health += amount
        if ui.current_health >= ui.maximum_health:
            ui.current_health = ui.maximum_health
            self.health = ui.maximum_health

    def check_collision(self, direction):
        for sprite in obstacles_group:
            if sprite.rect.colliderect(self.base_player_rect):
                if direction == "horizontal":
                    if self.velocity_x > 0:
                        self.base_player_rect.right = sprite.rect.left
                    if self.velocity_x < 0:
                        self.base_player_rect.left = sprite.rect.right
                
                if direction == "vertical":
                    if self.velocity_y < 0:
                        self.base_player_rect.top = sprite.rect.bottom
                    if self.velocity_y > 0:
                        self.base_player_rect.bottom = sprite.rect.top
           
    def update(self):     
        self.player_turning()
        self.player_input()    
        self.move()

        # pygame.draw.rect(screen, "red", self.base_player_rect, width=2)
        # pygame.draw.rect(screen, "yellow", self.rect, width=2)

        if self.shoot_cooldown > 0: # Just shot a bullet
            self.shoot_cooldown -= 1
        if self.shoot:
            self.is_shooting()

class Enemy(pygame.sprite.Sprite): 
    def __init__(self, name, position):
        super().__init__(enemy_group, all_sprites_group)
        self.alive = True
        self.position = pygame.math.Vector2(position) 
        self.direction_index = random.randint(0, 3)
        self.steps = random.randint(3, 6) * TILESIZE
        self.name = name

        enemy_info = monster_data[self.name]
        self.health = enemy_info["health"]
        self.roaming_speed = enemy_info["roaming_speed"]
        self.hunting_speed = random.choice(enemy_info["hunting_speed"])
        self.image_scale = enemy_info["image_scale"]
        self.image = enemy_info["image"].convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, self.image_scale)
        self.animation_speed = enemy_info["animation_speed"]
        self.roam_animation_speed = enemy_info["roam_animation_speed"]
        self.death_animation_speed = enemy_info["death_animation_speed"]
        self.notice_radius = enemy_info["notice_radius"]
        self.attack_damage = enemy_info["attack_damage"]
        self.import_graphics(name)

        self.current_index = 0

        self.image.set_colorkey((0,0,0))
        #self.base_zombie_image = self.image
        
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        self.hitbox_rect = enemy_info["hitbox_rect"]
        self.base_zombie_rect = self.hitbox_rect.copy()
        self.base_zombie_rect.center = self.rect.center
             
        self.velocity = pygame.math.Vector2()
        self.direction = pygame.math.Vector2()
        self.direction_list = [(1,1), (1,-1), (-1,1), (-1,-1)] # [(-1, 0), (1, 0), (0, -1), (0, 1), (1,1), (1,-1), (-1,1), (-1,-1)]

        self.collide = False

        self.coin_dropped = False

    def check_alive(self): # checks if enemy dies
        if self.health <= 0:
            self.alive = False
            if self.name == "necromancer":
                necromancer_death_sound.play()
                game_stats["necromancer_death_count"] += 1
            if self.name == "nightborne":
                nightborne_death_sound.play()
                game_stats["nightborne_death_count"] += 1
            game_stats["enemies_killed_or_removed"] += 1
        
    def roam(self):
        self.direction.x, self.direction.y = self.direction_list[self.direction_index] # gets a random direction
        self.velocity = self.direction * self.roaming_speed
        self.position += self.velocity
        
        self.base_zombie_rect.centerx = self.position.x
        self.check_collision("horizontal", "roam")

        self.base_zombie_rect.centery = self.position.y
        self.check_collision("vertical", "roam")
        
        self.rect.center = self.base_zombie_rect.center
        self.position = (self.base_zombie_rect.centerx, self.base_zombie_rect.centery)

        self.steps -= 1

        if self.steps == 0:
            self.get_new_direction_and_distance()

    def get_new_direction_and_distance(self):
        self.direction_index = random.randint(0, len(self.direction_list)-1)
        self.steps = random.randint(3, 6) * TILESIZE
                        
    def check_collision(self, direction, move_state):
        for sprite in obstacles_group:
            if sprite.rect.colliderect(self.base_zombie_rect):
                self.collide = True
                if direction == "horizontal":
                    if self.velocity.x > 0:
                        self.base_zombie_rect.right = sprite.rect.left
                    if self.velocity.x < 0:
                        self.base_zombie_rect.left = sprite.rect.right 
                if direction == "vertical":
                    if self.velocity.y < 0:
                        self.base_zombie_rect.top = sprite.rect.bottom
                    if self.velocity.y > 0:
                        self.base_zombie_rect.bottom = sprite.rect.top
                if move_state == "roam":
                    self.get_new_direction_and_distance()

    def hunt_player(self):  
        if self.velocity.x > 0:
            self.current_movement_sprite = 0
        else:
            self.current_movement_sprite = 1
        
        player_vector = pygame.math.Vector2(player.base_player_rect.center)
        enemy_vector = pygame.math.Vector2(self.base_zombie_rect.center)
        distance = self.get_vector_distance(player_vector, enemy_vector)

        if distance > 0:
            self.direction = (player_vector - enemy_vector).normalize()
        else:
            self.direction = pygame.math.Vector2()

        self.velocity = self.direction * self.hunting_speed
        self.position += self.velocity

        self.base_zombie_rect.centerx = self.position.x
        self.check_collision("horizontal", "hunt")

        self.base_zombie_rect.centery = self.position.y
        self.check_collision("vertical", "hunt")

        self.rect.center = self.base_zombie_rect.center

        self.position = (self.base_zombie_rect.centerx, self.base_zombie_rect.centery)

    def get_vector_distance(self, vector_1, vector_2):
        return (vector_1 - vector_2).magnitude()
    
    def import_graphics(self,name):
        self.animations = {'roam':[],'death':[],'hunt':[]}
        
        main_path = f'{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def animate(self, index, animation_speed, sprite, type):
        index += animation_speed

        if index >= len(sprite): # animation over
            index = 0
            if type == "death":
                self.kill()
    
        self.image = sprite[int(index)]
        self.image = pygame.transform.rotozoom(self.image, 0, self.image_scale)

        if type == "hunt" or type == "idle" or "death":
            if self.velocity.x < 0:
                self.image = pygame.transform.flip(self.image, flip_x = 180, flip_y = 0)

        return index

    def check_player_collision(self):          
        if pygame.Rect.colliderect(self.base_zombie_rect, player.base_player_rect): # player and enemy collides
            self.kill()
            player.get_damage(self.attack_damage)
            game_stats["enemies_killed_or_removed"] += 1
            # scream_sound.play()

    def draw_enemy_health(self, x, y):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.base_zombie_rect.width * self.health / 100)
        pygame.draw.rect(screen, col, (x - 40 - game_level.offset.x, y - 45 - game_level.offset.y, width, 5))

    def update(self):
        
        self.draw_enemy_health(self.position[0], self.position[1])
    
        if self.alive:
            self.check_alive()
            if self.get_vector_distance(pygame.math.Vector2(player.base_player_rect.center), 
                                        pygame.math.Vector2(self.base_zombie_rect.center)) < 100:
                self.check_player_collision()
                
            if self.get_vector_distance(pygame.math.Vector2(player.base_player_rect.center), 
                                        pygame.math.Vector2(self.base_zombie_rect.center)) < self.notice_radius:    # nightborne 400, necromancer 500
                self.hunt_player()
                self.current_index = self.animate(self.current_index, self.animation_speed, self.animations["hunt"], "hunt")
            else:
                self.roam()
                if self.get_vector_distance(pygame.math.Vector2(player.base_player_rect.center), pygame.math.Vector2(self.base_zombie_rect.center)) < 700:    
                    self.current_index = self.animate(self.current_index, self.roam_animation_speed, self.animations["roam"], "idle")
        else: # drop coin and play death animation
            if not self.coin_dropped:
                self.coin_dropped = True
                Item(self.position, "coin")
            self.current_index = self.animate(self.current_index, self.death_animation_speed, self.animations["death"], "death")

class UI(): 
    def __init__(self): 
        self.current_health = 100
        self.maximum_health = 100
        self.health_bar_length = 100
        self.health_ratio = self.maximum_health / self.health_bar_length 
        self.current_colour = None

    def display_health_bar(self): 
        pygame.draw.rect(screen, BLACK, (10, 15, self.health_bar_length * 3, 20)) # black

        if self.current_health >= 75:
            pygame.draw.rect(screen, GREEN, (10, 15, self.current_health * 3, 20)) # green    
            self.current_colour = GREEN
        elif self.current_health >= 25:
            pygame.draw.rect(screen, YELLOW, (10, 15, self.current_health * 3, 20)) # yellow
            self.current_colour = YELLOW 
        elif self.current_health >= 0:
            pygame.draw.rect(screen, RED, (10, 15, self.current_health * 3, 20)) # red 
            self.current_colour = RED

        pygame.draw.rect(screen, WHITE, (10, 15, self.health_bar_length * 3, 20), 4) # white border

    def display_health_text(self):
        health_surface = font.render(f"{player.health} / {self.maximum_health}", False, self.current_colour) 
        health_rect = health_surface.get_rect(center = (410, 25))
        screen.blit(health_surface, health_rect)

    def display_wave_text(self):
        wave_surface = font.render(f"Wave: {game_stats['current_wave']}", False, GREEN) 
        wave_rect = wave_surface.get_rect(center = (745, 28))
        screen.blit(wave_surface, wave_rect)

    def display_coin(self):
        coin_image = pygame.image.load("items/coin/0.png").convert_alpha()
        coin_image = pygame.transform.scale_by(coin_image, 3)
        coin_image_rect = coin_image.get_rect(center = (1162,30))
        coin_text = font.render(f"x {game_stats['coins']}", True, (255,223,91))
        screen.blit(coin_text, (1200, 20))
        screen.blit(coin_image, coin_image_rect)

    def display_countdown(self, time):
        text_1 = font.render(f"Enemies spawning in {int(time/1000)} seconds!",True, RED)
        screen.blit(text_1, (400, 100))

    def display_enemy_count(self):
        text_1 = font.render(f"Enemies: {game_stats['number_of_enemies'][game_stats['current_wave'] - 1] - game_stats['enemies_killed_or_removed']}",True, GREEN)
        screen.blit(text_1, (855, 18))

    def update(self): 
        self.display_health_bar()
        self.display_health_text()
        self.display_coin()
        self.display_wave_text()
        self.display_enemy_count()

class Bullet(pygame.sprite.Sprite): 
    def __init__(self, x, y, angle): 
        super().__init__()
        self.image = bullet_img
        self.image = pygame.transform.rotozoom(self.image, 0, 0.5)
        #self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.speed = 50
        self.angle = angle
        self.x_vel = math.cos(self.angle * (2*math.pi/360)) * self.speed
        self.y_vel = math.sin(self.angle * (2*math.pi/360)) * self.speed
        self.bullet_lifetime = 750
        self.spawn_time = pygame.time.get_ticks() # gets the specific time that the bullet was created, stays static
        

    def bullet_movement(self): 
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime: 
            self.kill()

    
        
    def bullet_collisions(self): 
        hits = pygame.sprite.groupcollide(enemy_group, bullet_group, False, True, hitbox_collide)

        for hit in hits:
            hit.health -= 10
        
                
        if pygame.sprite.spritecollide(self, obstacles_group, False): # wall collisions
            self.kill()

    def update(self):
        self.bullet_movement()
        self.bullet_collisions()

class Item(pygame.sprite.Sprite):
    def __init__(self, pos, item_name):
        self.groups = all_sprites_group, items_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        item_info = items[item_name]
        self.image = item_info["image"].convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 2.5)
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.item_name = item_name
        self.current_index = 0
        self.has_animation = item_info["has_animation"]

    def animate(self, index, animation_speed, sprite):
        index += animation_speed       
        if index >= len(sprite): # animation over
            index = 0
        self.image = sprite[int(index)]
        self.image = pygame.transform.rotozoom(self.image, 0, 2.5)
        return index
    
    def check_player_collision(self):
        if pygame.Rect.colliderect(self.rect, player.base_player_rect): # player picks up item
            self.kill()
            if self.item_name == "coin":
                game_stats["coins"] += 1
                coin_sound.play()
            if self.item_name == "health potion":
                player.increase_health(game_stats["health_potion_heal"])
                health_potion_sound.play()  
                Item(random.choice(game_level.health_spawn_pos), "health potion")
                   
                    
                
    def update(self):
        if self.has_animation:
            self.current_index = self.animate(self.current_index, 0.25, coin_imgs)
        self.check_player_collision()       

class GameLevel(pygame.sprite.Group): 
    def __init__(self):
        super().__init__()
        self.offset = pygame.math.Vector2()
        self.floor_rect = background.get_rect(topleft = (0,0))
        self.enemy_spawn_pos = []
        self.health_spawn_pos = []
        self.create_map()

    def create_map(self):
        layouts = {"boundary": self.import_csv_layout("data/csvfiles/Map_boundary.csv"),
                   "walls": self.import_csv_layout("data/csvfiles/Map_Walls.csv"),
                   "enemies": self.import_csv_layout("data/csvfiles/Map_enemies.csv"),
                   "health potions": self.import_csv_layout("data/csvfiles/Map_health potion.csv")
                  }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != "-1":
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == "boundary":
                            Tile((x,y), [obstacles_group], "boundary", col)
                        if style == "walls":
                            Tile((x,y), [all_sprites_group], "walls", col)  
                        if style == "enemies":
                            self.enemy_spawn_pos.append((x, y))
                        if style == "health potions":
                            self.health_spawn_pos.append((x, y))
        self.spawn_enemies()
        self.spawn_health_potions()

    def spawn_enemies(self):
        self.number_of_enemies = game_stats["number_of_enemies"][game_stats["current_wave"]-1]
        enemy_name = ["necromancer", "nightborne"]
        num_of_enemies_spawned = 0
        while num_of_enemies_spawned < self.number_of_enemies:
            Enemy(random.choice(enemy_name), random.choice(self.enemy_spawn_pos))
            num_of_enemies_spawned += 1

    def spawn_health_potions(self):            
        for i in range(game_stats["num_health_potions"]):# spawns 3 potions
            Item(random.choice(self.health_spawn_pos), "health potion")

    def import_csv_layout(self, path):
        terrain_map = []
        with open(path) as level_map:
            layout = reader(level_map, delimiter=",")
            for row in layout:
                terrain_map.append(list(row))
            return terrain_map
    
    def custom_draw(self): 
        self.offset.x = player.rect.centerx - (WIDTH // 2) # gotta blit the player rect not base rect
        self.offset.y = player.rect.centery - (HEIGHT // 2)

        #draw the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        screen.blit(background, floor_offset_pos)

        # draw the PLAYER'S rectangles for demonstration purposes
        # base_rect = player.base_player_rect.copy().move(-self.offset.x, -self.offset.y)
        # pygame.draw.rect(screen, "red", base_rect, width=2)
        # rect = player.rect.copy().move(-self.offset.x, -self.offset.y)
        # pygame.draw.rect(screen, "yellow", rect, width=2)

        # # draw the ZOMBIE'S rectangles for demonstration purposes
        # base_rect = necromancer.base_zombie_rect.copy().move(-self.offset.x, -self.offset.y)
        # pygame.draw.rect(screen, "red", base_rect, width=2)
        # rect = necromancer.rect.copy().move(-self.offset.x, -self.offset.y)
        # pygame.draw.rect(screen, "yellow", rect, width=2)   

        # print(base_rect.x, base_rect.y)


        for sprite in all_sprites_group: 
            offset_pos = sprite.rect.topleft - self.offset
            screen.blit(sprite.image, offset_pos)

class Tile(pygame.sprite.Sprite): 
    def __init__(self, pos, groups, type, unique_id):
        super().__init__(groups)
        # self.image = boundary_block_img
        if type == "boundary":
            self.image = boundary_block_img
        elif type == "walls":
            if unique_id == "19":
                self.image = top_wall_img
            if unique_id == "55":
                self.image = bottom_wall_img
            if unique_id == "20":
                self.image = left_wall_img
            if unique_id == "18":
                self.image = right_wall_img
            if unique_id == "27":
                self.image = topright_wall_img
            if unique_id == "29":
                self.image = topleft_wall_img
            if unique_id == "38":
                self.image = left_wall_connect_img
            if unique_id == "36":
                self.image = right_wall_connect_img
            if unique_id == "45":
                self.image = topright_black_wall_img
            if unique_id == "47":
                self.image = topleft_black_wall_img

        # if type == "props":
        #     self.image = torch_img
        
        self.rect = self.image.get_rect(topleft = pos) 

# Groups
all_sprites_group = pygame.sprite.Group()
obstacles_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
items_group = pygame.sprite.Group() 

game_level = GameLevel()

player = Player((1000,900))
all_sprites_group.add(player)

ui = UI()

necromancer_image = pygame.image.load("necromancer/sprites/sprite_00.png").convert_alpha()
necromancer_image = pygame.transform.rotozoom(necromancer_image ,0, 1.5)
necromancer_image_rect = necromancer_image.get_rect(center = (190,225))

nightborne_image = pygame.image.load("nightborne/sprites/00.png").convert_alpha()
nightborne_image = pygame.transform.rotozoom(nightborne_image,0,2)
nightborne_image_rect = nightborne_image.get_rect(center = (220,340))

coin_image = pygame.image.load("items/coin/0.png").convert_alpha()
coin_image = pygame.transform.rotozoom(coin_image, 0, 4)
coin_image_rect = coin_image.get_rect(center = (215,540))

start_time = 0

def calculate_score():
    current_time = int((pygame.time.get_ticks() - start_time)) # resets score when player dies
    return current_time

def display_end_screen():
    screen.fill((40,40,40))
    screen.blit(necromancer_image, necromancer_image_rect)
    screen.blit(nightborne_image, nightborne_image_rect)
    screen.blit(coin_image, coin_image_rect)
    if beat_game:
        beat_game_surface = font.render("You beat the game! Thanks for playing!", True, WHITE)
        screen.blit(beat_game_surface, (300, 50))
    else:
        game_over_surface = title_font.render("GAME OVER", True, WHITE)
        screen.blit(game_over_surface, (350, 50))
    text_surface = font.render("> Press 'P' to play again", True, WHITE)
    text_1 = font.render(f"You killed:", True, WHITE)
    text_2 = font.render(f"{game_stats['necromancer_death_count']} x", True, WHITE) 
    text_3 = font.render(f"{game_stats['nightborne_death_count']} x", True, WHITE)
    text_4 = font.render(f"You collected:", True, WHITE)
    text_5 = font.render(f"{game_stats['coins']} x",True, WHITE)
    
    screen.blit(text_surface, (WIDTH / 2 - 70, HEIGHT * 7 / 8))
    screen.blit(text_1, (100, 150))
    screen.blit(text_2, (100, 250))
    screen.blit(text_3, (100, 350))
    screen.blit(text_4, (100, 450))
    screen.blit(text_5, (100, 530))
    score_text_1 = font.render(f"Your score:", False, WHITE)
    score_text_2 = score_font.render(f"{score:,}", False, WHITE)
    screen.blit(score_text_1, (550,150))
    screen.blit(score_text_2, (550,250))

def end_game():
    global game_active 
    game_active = False
    for item in items_group:
        item.kill()
    for enemy in enemy_group:
        enemy.kill()
    enemy_group.empty() 
    items_group.empty()  
    

while True: 
    current_time = pygame.time.get_ticks()
    if player.health <= 0:
        end_game()

    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if not game_active and keys[pygame.K_p]:
            player.health, ui.current_health = 100, 100
            game_active = True
            game_stats["current_wave"] = 1
            start_time = pygame.time.get_ticks()            
            
            game_stats["necromancer_death_count"] = 0
            game_stats["nightborne_death_count"] = 0
            game_stats["enemies_killed_or_removed"] = 0
            game_stats["coins"] = 0
            
            game_level.spawn_enemies()    
            game_level.spawn_health_potions()

    if game_active:
        screen.blit(plain_bg, (0,0))
        game_level.custom_draw()
        all_sprites_group.update()
        ui.update()

        if game_stats['enemies_killed_or_removed'] == game_stats["number_of_enemies"][game_stats["current_wave"] - 1]: # level over  
            display_countdown_time = True 
            ready_to_spawn = True 
            level_over_time = pygame.time.get_ticks()
            game_stats["enemies_killed_or_removed"] = 0 
            game_stats["current_wave"] += 1        
            if game_stats["current_wave"] == len(game_stats["number_of_enemies"]) + 1: # beat game
                beat_game = True
                end_game()
            else:
                beat_game = False

        if current_time - level_over_time > game_stats["wave_cooldown"] and ready_to_spawn and not beat_game:
            game_level.spawn_enemies()
            ready_to_spawn = False
        if current_time - level_over_time < game_stats["wave_cooldown"] and display_countdown_time and not game_stats["current_wave"] == 1:
            ui.display_countdown(game_stats["wave_cooldown"] - (current_time - level_over_time))
            if current_time - level_over_time > game_stats["wave_cooldown"]:
                display_countdown_time = False
                                                                
        score = calculate_score()
        # pygame.display.set_caption(f"({player.base_player_rect.centerx}, {player.base_player_rect.centery})")
        pygame.display.set_caption(f"{clock.get_fps()}")
    else:
        end_game()
        display_end_screen()

    pygame.display.update()
    clock.tick(FPS)

    
