import pygame
import os

# game setup
WIDTH = 1280	# 1280 x 720 - full is 1600x900
HEIGHT = 720
FPS      = 60
TILESIZE = 32

# colours
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
BLACK = (0,0,0)
WHITE = (255,255,255)

def import_folder(path):
    surface_list = []

    for _,__,img_files in os.walk(path):
        for image in img_files:
            full_path = path + '/' + image		
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list

def extract_number(filename):
    return int(filename.split(".")[0])

def import_folder(path):
    surface_list = []

    for root, dirs, img_files in os.walk(path): 
        sorted_file_names = sorted(img_files, key=extract_number)  

    for img_name in sorted_file_names:
        full_path = path + '/' + img_name
        image_surf = pygame.image.load(full_path).convert_alpha()
        surface_list.append(image_surf)

    return surface_list
        

monster_data = {
    "necromancer": {"health": 100, "attack_damage": 20, "roaming_speed": 2, "hunting_speed": [4,4,7,7,7], "image": pygame.image.load("necromancer/roam/0.png"), "image_scale": 1.5, "hitbox_rect": pygame.Rect(0,0,75,100), "animation_speed": 0.2, "roam_animation_speed": 0.05, "death_animation_speed": 0.12, "notice_radius": 500},
    "nightborne": {"health": 100, "attack_damage": 40, "roaming_speed": 4, "hunting_speed": [4,4,6,6,6], "image": pygame.image.load("nightborne/hunt/1.png"), "image_scale": 1.9, "hitbox_rect": pygame.Rect(0,0,75,90), "animation_speed": 0.1, "roam_animation_speed": 0.12, "death_animation_speed": 0.2, "notice_radius": 400},
}

game_stats = {
    "enemies_killed_or_removed": 0, "necromancer_death_count": 0, "nightborne_death_count": 0, "coins": 0, "health_potion_heal": 20, "current_wave": 1, "number_of_enemies": [5, 6,7], "wave_cooldown": 6000, "num_health_potions": 3
}

items = {
    "health potion": {"image": pygame.image.load("items/health potion/10.png"), "has_animation": False},
    "coin": {"image": pygame.image.load("items/coin/0.png"), "has_animation": True}

}
