from settings import *
from tools import *
from ui import Line, Button, Text_Zone
from data import Props, OBJ_DICT, CAT_LIST
from current_langage import MENUS
import pygame as pg
pg.init()
pg.font.init()

# display
screen = pg.display.set_mode(SIZE)
clock = pg.time.Clock()
pg.display.set_caption('SpaceHavenBuilder (InBuild)')

# grid
x, y = 0, 0
velx, vely = 0, 0
game_surf = pg.surface.Surface(GRID_SIZE)
grid = create_grid((TILE_SIZE*27*NBR_CELLS[0], TILE_SIZE*27*NBR_CELLS[1]), TILE_SIZE, 27*NBR_CELLS[0], 27*NBR_CELLS[1])

# scaling
scale = 1
MAX_SCALE = 4
MIN_SCALE = 0.5

# lines
lines = []
for xt in range(1, NBR_CELLS[0]):
    lines.append(Line((27*25*xt, 0), (27*25*xt, 54*25*NBR_CELLS[1])))
for yt in range(1, NBR_CELLS[1]):
    lines.append(Line((0, 27*25*yt), (27*25*NBR_CELLS[1], 27*25*yt)))

# Création de la surface pour afficher les détails de l'objet sélectionné
info_surface = pg.Surface((SCREEN_WIDTH, 50))

# obj
ids = True
object_group = pg.sprite.Group()
obj_index = 0
cat_index = 0
current_obj = OBJ_DICT[CAT_LIST[cat_index]][obj_index]

# energie
energie = 0

# undo
action = []

# mouse
mouse_pressed = False

# menu
querry = ''
menu = [0]
buttons = pg.sprite.Group()
text_zone = Text_Zone((SCREEN_WIDTH//2, 200), (500, 50), 40, BLACK, GREY, (10, 12))
load_button = Button(buttons, (SCREEN_WIDTH//2, 300), (500, 50), MENUS[0], LIGHT_GREEN, GREY, 40, lambda x: print('load') if load(x[0], x[1], x[2]) else None, True)
save_button = Button(buttons, (SCREEN_WIDTH//2, 400), (500, 50), MENUS[1], LIGHT_BLUE, GREY, 40, lambda x: print('save') if save(x[0], x[1]) else None, True)
render_button = Button(buttons, (SCREEN_WIDTH//2, 500), (500, 50), MENUS[2], YELLOW, GREY, 40, lambda x: print('render') if render_surface(x[0], x[3]) else print(f'to much img: {x[0]}'), True)
exit_button = Button(buttons, (SCREEN_WIDTH//2, 600), (500, 50), MENUS[3], LIGHT_RED, GREY, 40, lambda: (pg.quit(), quit()))

# DEBUG
display_masks = 0

# game loop
run = True
while run:

    clock.tick(FPS)

    # mouse
    m_x, m_y = pg.mouse.get_pos()
    mouse_pos = ((m_x-x)/scale, (m_y-y)/scale)
    mouse_b = False
    if pg.mouse.get_pressed()[0]:
        mouse_pressed = True
    if not pg.mouse.get_pressed()[0]:
        if mouse_pressed == True:
            mouse_b = True
            if not menu[0]:
                if current_obj.place(object_group, pos_to_grid(mouse_pos), action): energie += current_obj.energie
        mouse_pressed = False
        
    # event
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN:

            # toggle menu
            if event.key == pg.K_ESCAPE:
                if menu[0]: menu[0] = 0
                else: 
                    menu[0] = 1
                    querry = ''
                    # clear the cursor for render
                    # draw grid
                    game_surf.blit(grid, (0, 0))
                    # draw object
                    for obj in object_group:
                        obj:Props
                        obj.draw(game_surf)
                    # draw lines
                    for line in lines:
                        line.draw(game_surf)

            if not menu[0]:
                # toggle display masks
                if event.key == pg.K_i:
                    display_masks = (display_masks+1)%3
                # toggle ids
                if event.key == pg.K_g:
                    if ids: ids = False
                    else: ids = True
                # undo
                if event.key == pg.K_u:
                    if len(action) > 0:
                        energie -= action[-1].energie
                        action[-1].kill()
                        action.pop()
                        print('undo action')

                # scale
                if event.key == pg.K_z:
                    if not scale == MAX_SCALE:
                        scale *= 2
                if event.key == pg.K_s:
                    if not scale == MIN_SCALE:
                        scale /= 2
                
                # move the surface
                if event.key == pg.K_UP:
                    vely -= 1
                if event.key == pg.K_DOWN:
                    vely += 1
                if event.key == pg.K_LEFT:
                    velx -= 1
                if event.key == pg.K_RIGHT:
                    velx += 1

                # cycle in the objects
                if event.key == pg.K_e:
                    obj_index = (obj_index + 1)%len(OBJ_DICT[CAT_LIST[cat_index]])
                    current_obj = OBJ_DICT[CAT_LIST[cat_index]][obj_index]
                if event.key == pg.K_a:
                    obj_index = (obj_index - 1)%len(OBJ_DICT[CAT_LIST[cat_index]])
                    current_obj = OBJ_DICT[CAT_LIST[cat_index]][obj_index]
                if event.key == pg.K_d:
                    cat_index = (cat_index + 1)%len (CAT_LIST)
                    obj_index = 0
                    current_obj = OBJ_DICT[CAT_LIST[cat_index]][obj_index]
                if event.key == pg.K_q:
                    cat_index = (cat_index - 1)%len (CAT_LIST)
                    obj_index = 0
                    current_obj = OBJ_DICT[CAT_LIST[cat_index]][obj_index]

                # rotate / delete object
                if event.key == pg.K_r:
                    current_obj.rotate()
                    print('rotate')
                if event.key == pg.K_x:
                    for obj in object_group: 
                        offset = get_offset(obj.rect.topleft, pos_to_grid(mouse_pos))
                        if mask_point_collision(obj.masks[0], offset):
                            if not len(action) == 0: 
                                try: 
                                    action.remove(obj)
                                except: 
                                    pass
                            energie -= obj.energie
                            obj.kill()
                            print('delete')

            else:
                # (a-z)
                if 97 <= event.key <= 122:
                    querry += chr(event.key)
                # (0-9)
                if 1073741913 <= event.key <= 1073741922:
                    querry += str((event.key-1073741912)%10)
                if event.key == 56:
                    querry += '_'
                if event.key == pg.K_BACKSPACE:
                    if not querry == '':
                        querry = querry[:-1]

        if event.type == pg.KEYUP:
            if not menu[0]:
                # move surface
                if event.key == pg.K_UP:
                    vely += 1
                if event.key == pg.K_DOWN:
                    vely -= 1
                if event.key == pg.K_LEFT:
                    velx += 1
                if event.key == pg.K_RIGHT:
                    velx -= 1

    if not menu[0]:
        # movement
        x -= velx * SPEED * scale
        y -= vely * SPEED * scale
                    
        # display
        screen.fill(LIGHT_DARK)
        # draw grid
        game_surf.blit(grid, (0, 0))
        # draw object
        for obj in object_group:
            obj:Props
            obj.draw(game_surf, ids, display_masks)
        # draw lines
        for line in lines:
            line.draw(game_surf)
        # draw cursor object
        current_obj.draw(game_surf, pos_to_grid(mouse_pos), object_group)

        # display on screen
        screen.blit(pg.transform.scale_by(game_surf, scale), (x, y))

        # draw info
        display_selected_object_info(info_surface, current_obj, CAT_LIST[cat_index], energie)
        screen.blit(info_surface, (0, 0))
    else:
        screen.fill(LIGHT_DARK)
        buttons.draw(screen)
        text_zone.draw(screen, querry)
        buttons.update(mouse_b, menu, [querry, object_group, Props, game_surf])
    pg.display.update()

pg.quit()
