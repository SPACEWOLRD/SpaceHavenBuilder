from settings import *
from current_langage import SELECTED
import pygame as pg
import csv
import os

def render_text(text:str, color:tuple, bg_color:tuple, size:int) -> pg.Surface:
    font = pg.font.Font(None, size)
    return font.render(text, True, color, bg_color)

def create_masks(grid:list) -> tuple[pg.mask.Mask]:
    '''take a grid and tranform it into 2 mask'''
    width, height = len(grid[0])*TILE_SIZE, len(grid)*TILE_SIZE
    soft_mask = pg.surface.Surface((width, height))
    hard_mask = pg.surface.Surface((width, height))

    # soft mask grid: (1, -1) -> WHITE, (0) -> BLACK
    # hard mask grid: (1) -> WHITE, (0, -1) -> BLACK
    for y, row in enumerate(grid):
        for x, value in enumerate(row):
            # soft mask
            if value == 1:
                pg.draw.rect(soft_mask, WHITE, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif value in (0, -1):
                pg.draw.rect(soft_mask, BLACK, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            # hard mask
            if value in (1, -1):
                pg.draw.rect(hard_mask, WHITE, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif value == 0:
                pg.draw.rect(hard_mask, BLACK, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
    soft_mask.set_colorkey((0, 0, 0))
    hard_mask.set_colorkey((0, 0, 0))
    return (soft_mask, hard_mask)

def check_masks_collision(masks_1:list, masks_2:list, offset:tuple) -> bool:
    soft_1, hard_1 = masks_1
    soft_2, hard_2 = masks_2
    soft_1, hard_1 =  [pg.mask.from_surface(soft_1), pg.mask.from_surface(hard_1)]
    soft_2, hard_2 =  [pg.mask.from_surface(soft_2), pg.mask.from_surface(hard_2)]
    soft_1:pg.Mask
    soft_2:pg.Mask
    return soft_2.overlap(hard_1, offset) or hard_2.overlap(soft_1, offset)

def mask_point_collision(mask:pg.Surface, offset:tuple) -> bool:
    mask = pg.mask.from_surface(mask)
    if 0 <= offset[0] < mask.get_size()[0] and 0 <= offset[1] < mask.get_size()[1]:
        if mask.get_at(offset):
            return True
    return False


def get_offset(pos1:tuple, pos2:tuple):
    x1, y1 = pos1
    x2, y2 = pos2
    delta_x = x2 - x1
    delta_y = y2 - y1
    return (delta_x, delta_y)

def create_grid(grid_size:tuple, size:int, width:int, height:int) -> pg.Surface:
    surf = pg.surface.Surface(grid_size)
    color = [COL1, COL2]
    for x in range(width):
        for y in range(height):
            pg.draw.rect(surf, color[(x+y)%2], (x*size, y*size, size, size))
    return surf

def pos_to_grid(pos:tuple) -> tuple:
    x, y = pos
    x_grid = (x//TILE_SIZE) * TILE_SIZE
    y_grid = (y//TILE_SIZE) * TILE_SIZE
    return (x_grid, y_grid)

def display_selected_object_info(surface:pg.Surface, object, categorie:str, energie:float):
    surface.fill((200, 200, 200))  # Efface la surface précédente
    # Affiche les détails de l'objet sélectionné
    font = pg.font.Font(None, 36)
    text = font.render(f"{SELECTED}: {object.name} ({categorie})", True, (0, 0, 0))
    energie_text = font.render(f'energie: {round(energie, 1)}', True, GREEN if energie >= 0 else RED)
    surface.blit(text, (10, 10))
    surface.blit(energie_text, (surface.get_width()-(energie_text.get_width() + ENERGIE_OFFSET), 10))

def image_alpha_mask(image:pg.Surface, mask:pg.Mask) -> pg.Surface:
    # Parcourir les pixels du masque pour rendre l'image transparente là où le masque est noir
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            # Obtenir la couleur du pixel dans le masque
            mask_pixel = mask.get_at((x, y))

            # Si le masque est noir (ou proche), on rend le pixel transparent
            if mask_pixel.r == 0 and mask_pixel.g == 0 and mask_pixel.b == 0:
                image.set_at((x, y), (0, 0, 0, 0))  # Rendre ce pixel transparent
    return image

def save(name: str, group: pg.sprite.Group) -> bool:
    if name!='' and not os.path.exists(f'data/{name}.csv'):
        with open(f'data/{name}.csv', 'w', encoding='utf-8', newline='') as f:
            # Créer l'écrivain avec les noms des colonnes
            fieldnames = ['pos', 'grid', 'path', 'angle', 'obj_id', 'display_name' , 'energie']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            # Sauvegarder chaque sprite
            for sprite in group:
                writer.writerow({
                    'pos': sprite.pos,  # Assurez-vous que sprite.pos est sérialisable
                    'grid': sprite.grid,
                    'path': sprite.path,
                    'angle': sprite.angle,
                    'obj_id': sprite.obj_id,
                    'display_name': sprite.display_name,
                    'energie': sprite.energie,
                })
        return True
    else:
        print(f'already a file: {name}')
        return False

def load(name: str, group: pg.sprite.Group, Props) -> bool:
    if name!='' and os.path.exists(f'data/{name}.csv'):
        group.empty()
        with open(f'data/{name}.csv', 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Convertir les données du CSV en types appropriés si nécessaire
                pos = eval(row['pos'])  # Par exemple, si pos est un tuple ou une liste
                grid = eval(row['grid'])  # Assurez-vous que c'est le bon type
                path = row['path']  # path est probablement une chaîne de caractères
                angle = float(row['angle'])  # Convertir angle en float
                obj_id = int(row['obj_id'])
                display_name = eval(row['display_name'])
                energie = float(row['energie'])

                # Recréer le sprite avec Props
                Props(group, pos, grid, path, angle, obj_id, display_name, energie)
        return True
    else:
        print(f'no file: {name}')
        return False

def largest_rectangle_in_histogram(heights):
    stack = []
    max_area = 0
    left, right, height = 0, 0, 0
    
    for i, h in enumerate(heights):
        start = i
        while stack and stack[-1][1] > h:
            index, height = stack.pop()
            area = height * (i - index)
            if area > max_area:
                max_area = area
                left, right, height = index, i - index, height
            start = index
        stack.append((start, h))
    
    for i, h in stack:
        area = h * (len(heights) - i)
        if area > max_area:
            max_area = area
            left, right, height = i, len(heights) - i, h
    
    return max_area, left, right, height


def largest_rectangle_in_grid(grid) -> list[int]:
    if not grid or not grid[0]:
        return 0, 0, 0, 0
    
    max_area = 0
    result = (0, 0, 0, 0)
    heights = [0] * len(grid[0])
    
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            heights[x] = heights[x] + 1 if grid[y][x] == 1 else 0
        
        area, left, width, height = largest_rectangle_in_histogram(heights)
        if area > max_area:
            max_area = area
            result = (left, y - height + 1, width, height)
    
    return result

def render_surface(name:str, surface:pg.Surface) -> bool:
    if name!='':
        if os.path.exists(f'img/{name}.png'):
            k = 0
            while os.path.exists(f'img/{name}_{k}.png'):
                k += 1
                if k >= 100:
                    return False
            pg.image.save(surface, f'img/{name}_{k}.png')
            return True
        else:
            pg.image.save(surface, f'img/{name}.png')
            return True
    else:
        return False
