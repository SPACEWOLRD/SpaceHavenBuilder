from settings import *
from tools import *
from current_langage import OBJ_NAME, CAT_NAME
import pygame as pg


class Object:
    def __init__(self, grid:list, center:tuple, obj_id:int, path:str, name:str, display_name: bool = True) -> None:
        self.name = name
        self.obj_id = obj_id
        self.display_name = display_name
        self.grid = grid
        self.img_path = path
        self.masks = create_masks(grid)
        self.grid = grid
        self.angle = 0
        rect = pg.image.load(path).get_rect()
        self.surf = pg.surface.Surface((rect.width, rect.height))

    def rotate(self, angle:int=90) -> None:
        self.angle = (self.angle+90)%360
        # self.img = pg.transform.rotate(self.img, angle)
        self.masks = (pg.transform.rotate(self.masks[0], angle), pg.transform.rotate(self.masks[1], angle))

    def place(self, group:pg.sprite.Group, pos:tuple, action:list) -> None:
        for prop in group:
            prop:Props
            if check_masks_collision(self.masks, prop.masks, get_offset(prop.rect.topleft, pos)):
                print('Collision')
                break
        else:
            action.append(Props(group, pos, self.grid, self.img_path, self.angle, self.obj_id, self.display_name))
            print('place')

    def draw(self, screen:pg.Surface, pos:tuple, group:pg.sprite.Group) -> None:
        # check if collide
        self.surf.fill(BLACK)
        for prop in group:
            prop:Props

            if check_masks_collision(self.masks, prop.masks, get_offset(prop.rect.topleft, pos)):
                for y, row in enumerate(self.grid):
                    for x, value in enumerate(row):
                        if value == 1:
                            pg.draw.rect(self.surf, RED, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                        elif value == -1:
                            pg.draw.rect(self.surf, LIGHT_RED, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                break
        else:
            for y, row in enumerate(self.grid):
                for x, value in enumerate(row):
                    if value == 1:
                        pg.draw.rect(self.surf, GREEN, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    elif value == -1:
                        pg.draw.rect(self.surf, LIGHT_GREEN, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        self.surf.set_colorkey((0, 0, 0))
        screen.blit(pg.transform.rotate(self.surf, self.angle), pos)


class Props(pg.sprite.Sprite):
    def __init__(self, group:pg.sprite.Group, pos:tuple, grid:list, path:str, angle:int, obj_id:int, display_name:bool) -> None:
        super().__init__(group)
        self.masks = [pg.transform.rotate(mask, angle) for mask in create_masks(grid)]
        self.image = image_alpha_mask(pg.transform.rotate(pg.image.load(path), angle), self.masks[1])
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        if display_name:
            self.create_id(grid, obj_id, angle)

        # info need in load save
        self.angle = angle
        self.grid = grid
        self.path = path
        self.pos = pos
        self.obj_id = obj_id
        self.display_name = display_name

    def draw(self, screen:pg.Surface, ids:bool=True, display_masks:int=0) -> None:
        surf = self.image.copy()
        if ids and self.display_name:
            surf.blit(self.text_surf, self.text_rect)
        if display_masks == 0:
            screen.blit(surf, self.rect)
        elif display_masks == 1:
            screen.blit(self.masks[0], self.rect)
        elif display_masks == 2:
            screen.blit(self.masks[1], self.rect)

    def create_id(self, grid:list, obj_id:int, angle:int):
        xt, yt, widtht, heightt = largest_rectangle_in_grid(grid)

        # position the id on the surface nicely
        if angle == 0:
            x = xt*TILE_SIZE
            y = yt*TILE_SIZE
            width = widtht*TILE_SIZE
            height = heightt*TILE_SIZE
        elif angle == 90:
            y = self.rect.height - xt*TILE_SIZE - widtht*TILE_SIZE
            x = yt*TILE_SIZE
            width = heightt*TILE_SIZE
            height = widtht*TILE_SIZE
        elif angle == 180:
            x = self.rect.width - xt*TILE_SIZE - widtht*TILE_SIZE
            y = self.rect.height - yt*TILE_SIZE - heightt*TILE_SIZE
            width = widtht*TILE_SIZE
            height = heightt*TILE_SIZE
        elif angle == 270:
            y = xt*TILE_SIZE
            x = self.rect.width - yt*TILE_SIZE - heightt*TILE_SIZE
            width = heightt*TILE_SIZE
            height = widtht*TILE_SIZE

        text = render_text(str(obj_id), BLACK, None, 20)
        rect = text.get_rect()
        self.text_surf = pg.transform.scale_by(text, min(width/rect.width, height/rect.height))
        self.text_rect = self.text_surf.get_rect()
        self.text_rect.topleft = (x, y)


### DATA ###
OBJ_DICT = {
    CAT_NAME[0]: [
        Object([[1]], (0, 0), 101, 'source/coque.png', OBJ_NAME[CAT_NAME[0]][0], False),
        Object([[1]], (0, 0), 102, 'source/mur.png', OBJ_NAME[CAT_NAME[0]][1], False),
        Object([[-1, 1, -1]], (1, 0), 103, 'source/porte X1.png', OBJ_NAME[CAT_NAME[0]][2], False),
        Object([[-1, 1, -1], [-1, 1, -1]], (1, 0), 104, 'source/porte X2.png', OBJ_NAME[CAT_NAME[0]][3], False),
        Object([[0, -1, 0], [-1, 1, -1], [0, 1, 0]], (1, 1), 105, 'source/porte_scaphandre.png', OBJ_NAME[CAT_NAME[0]][4], False),
        Object([[0, -1, 0], [-1, 1, -1], [0, 1, 0], [0, -1, 0]], (1, 1), 106, 'source/ecoutille.png', OBJ_NAME[CAT_NAME[0]][5], False)
    ],
    CAT_NAME[1]: [
        Object([[1, 1]], (0, 0), 201, 'source/lit.png', OBJ_NAME[CAT_NAME[1]][0]),
        Object([[1]], (0, 0), 202, 'source/table_de_nuit.png', OBJ_NAME[CAT_NAME[1]][1]),
        Object([[1]], (0, 0), 203, 'source/table.png', OBJ_NAME[CAT_NAME[1]][2]),
        Object([[1, 1]], (0, 0), 204, 'source/canape X1.png', OBJ_NAME[CAT_NAME[1]][3]),
        Object([[1, 1, 1], [1, 0, 1]], (1, 0), 205, 'source/canape X2.png', OBJ_NAME[CAT_NAME[1]][4])
    ],
    CAT_NAME[2]: [
        Object([[1, 1, -1], [1, 1, -1], [1, 1, -1]], (1, 1), 301, 'source/terminal.png', OBJ_NAME[CAT_NAME[2]][0]),
        Object([[1, 1], [-1, -1]], (1, 0), 302, 'source/paillasse.png', OBJ_NAME[CAT_NAME[2]][1]),
        Object([[1, -1], [1, 1]], (0, 0), 303, 'source/capsule.png', OBJ_NAME[CAT_NAME[2]][2]),
        Object([[1, -1]], (0, 0), 304, 'source/cuve.png', OBJ_NAME[CAT_NAME[2]][4]),
        Object([[1, -1], [1, 1]], (0, 0), 305, 'source/medical_bed.png', OBJ_NAME[CAT_NAME[2]][5]),
        Object([[1, -1], [1, 0]], (0, 0), 306, 'source/toilette.png', OBJ_NAME[CAT_NAME[2]][6]),
        Object([[1, -1]], (0, 0), 307, 'source/jukebox.png', OBJ_NAME[CAT_NAME[2]][7]),
        Object([[1, -1], [1, -1]], (0, 0), 308, 'source/lit_augmentation.png', OBJ_NAME[CAT_NAME[2]][8]),
        Object([[1, 0], [1, -1]], (0, 0), 309, 'source/oxygene.png', OBJ_NAME[CAT_NAME[2]][9]),
        Object([[1, -1]], (0, 0), 310, 'source/epuratrice.png', OBJ_NAME[CAT_NAME[2]][10]),
        Object([[1]], (0, 0), 311, 'source/chauffage.png', OBJ_NAME[CAT_NAME[2]][1])
    ],
    CAT_NAME[3]: [
        Object([[1, 1, 1, -1], [1, 1, 1, -1]], (0, 0), 401, 'source/generatrice.png', OBJ_NAME[CAT_NAME[3]][0]),
        Object([[1]], (0, 0), 402, 'source/petit_noeud.png', OBJ_NAME[CAT_NAME[3]][1]),
        Object([[1, 1]], (0, 0), 403, 'source/grand_noeud.png', OBJ_NAME[CAT_NAME[3]][2]),
        Object([[1, 1]], (0, 0), 404, 'source/batterie.png', OBJ_NAME[CAT_NAME[3]][3]),
        Object([[1, 1]], (0, 0), 405, 'source/secour.png', OBJ_NAME[CAT_NAME[3]][4]),
        Object([[1, 1, 1, -1], [1, 1, 1, -1]], (1, 0), 406, 'source/generatrice_X1.png', OBJ_NAME[CAT_NAME[3]][5]),
        Object([[1, 1, 1, -1], [1, 1, 1, -1], [1, 1, 1, -1]], (1, 0), 407, 'source/generatrice_X2.png', OBJ_NAME[CAT_NAME[3]][6]),
        Object([[1, 1, 1, -1], [1, 1, 1, -1], [1, 1, 1, -1], [1, 1, 1, -1]], (1, 1), 408, 'source/generatrice_X3.png', OBJ_NAME[CAT_NAME[3]][7]),
        Object([[1, 1, 1], [1, 1, 1], [1, 1, 1]], (1, 1), 409, 'source/panneau.png', OBJ_NAME[CAT_NAME[3]][8])
    ],
    CAT_NAME[4]: [
        Object([[1, -1], [1, -1]], (0, 0), 501, 'source/etablie.png', OBJ_NAME[CAT_NAME[4]][0]),
        Object([[1, -1], [1, -1]], (0, 0), 502, 'source/outilleuse.png', OBJ_NAME[CAT_NAME[4]][1]),
        Object([[1, -1], [1, -1]], (0, 0), 503, 'source/purificatrice.png', OBJ_NAME[CAT_NAME[4]][2]),
        Object([[1, -1]], (0, 0), 504, 'source/deshumidificatrice.png', OBJ_NAME[CAT_NAME[4]][3]),
        Object([[1, 1, 1, 1, 1, -1], [1, 1, 1, 1, 1, -1]], (2, 0), 505, 'source/trieuse.png', OBJ_NAME[CAT_NAME[4]][4]),
        Object([[1, 1, -1, -1], [1, 1, 1, -1], [1, 1, 1, -1]], (1, 1), 506, 'source/recycleuse.png', OBJ_NAME[CAT_NAME[4]][5]),
        Object([[1, 1, -1], [1, 1, -1]], (1, 0), 507, 'source/composteur.png', OBJ_NAME[CAT_NAME[4]][6]),
        Object([[1, -1], [1, -1]], (0, 0), 508, 'source/imprimante.png', OBJ_NAME[CAT_NAME[4]][7]),
        Object([[1, 1, 1, 1], [1, 1, 1, 1], [-1, -1, -1, -1]], (1, 1), 509, 'source/convertisseuse_metaux.png', OBJ_NAME[CAT_NAME[4]][8]),
        Object([[1, 1, 1], [-1, -1, -1]], (1, 0), 510, 'source/tisseuse.png', OBJ_NAME[CAT_NAME[4]][9]),
        Object([[1, 1, 1], [1, 1, 1], [-1, -1, -1]], (1, 0), 511, 'source/assembleuse.png', OBJ_NAME[CAT_NAME[4]][10]),
        Object([[1, 1, 1], [1, 1, 1], [1, 1, 1], [-1, -1, -1]], (1, 1), 512, 'source/convertisseuse_energie.png', OBJ_NAME[CAT_NAME[4]][11]),
        Object([[1, 1, 1], [1, 1, 1], [-1, -1, -1]], (1, 1), 513, 'source/convertisseuse_chimique.png', OBJ_NAME[CAT_NAME[4]][12]),
        Object([[1, 1, 1], [-1, 1, 1], [-1, -1, -1]], (1, 1), 514, 'source/imprimante_optronique.png', OBJ_NAME[CAT_NAME[4]][13]),
        Object([[1, 1, 1], [1, 1, 1], [1, 1, 1],[-1, -1, -1]], (1, 1), 514, 'source/assembleuse_avancee.png', OBJ_NAME[CAT_NAME[4]][14])
    ],
    CAT_NAME[5]: [
        Object([[1, 1], [-1, -1]], (0, 0), 601, 'source/algue.png', OBJ_NAME[CAT_NAME[5]][0]),
        Object([[1, 1, 1], [-1, -1, -1]], (1, 0), 602, 'source/cuisine.png', OBJ_NAME[CAT_NAME[5]][1]),
        Object([[1, 1], [-1, -1]], (0, 0), 603, 'source/alcool.png', OBJ_NAME[CAT_NAME[5]][2]),
        Object([[1, 1], [-1, -1]], (0, 0), 604, 'source/cultivatrice_x1.png', OBJ_NAME[CAT_NAME[5]][3]),
        Object([[1, 1, 1], [-1, -1, -1]], (0, 0), 605, 'source/cultivatrice_x2.png', OBJ_NAME[CAT_NAME[5]][4]),
        Object([[-1, -1, -1, -1], [-1, 1, 1, -1], [-1, 1, 1, -1], [-1, 1, 1, -1], [-1, -1, -1, -1]], (2, 1), 606, 'source/cultivatrice_x3.png', OBJ_NAME[CAT_NAME[5]][5]),
        Object([[1, -1]], (0, 0), 607, 'source/productrice_O2.png', OBJ_NAME[CAT_NAME[5]][6]),
        Object([[-1, -1], [1, 1], [-1, -1]], (1, 0), 608, 'source/autopsie.png', OBJ_NAME[CAT_NAME[5]][7]),
    ],
    CAT_NAME[6]: [
        Object([[1, 1, -1]], (1, 0), 701, 'source/petit_stockage.png', OBJ_NAME[CAT_NAME[6]][0]),
        Object([[1, 1, 0], [1, 1, -1], [1, 1, 0]], (1, 1), 702, 'source/grand_stockage.png', OBJ_NAME[CAT_NAME[6]][1]),
        Object([[1, 1], [1, 1], [-1, -1]], (1, 0), 703, 'source/morgue.png', OBJ_NAME[CAT_NAME[6]][2]),
        Object([[0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1], [-1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1], [0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1]], (5, 3), 704, 'source/port_amarrage.png', OBJ_NAME[CAT_NAME[6]][3], False),
        # Port d'amarrage de station
    ],
    CAT_NAME[7]: [
        Object([[1, 1, -1]], (0, 0), 801, 'source/vestiaire.png', OBJ_NAME[CAT_NAME[7]][0]),
        Object([[0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1], [0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1], [-1, 1, 1, 0, -1, -1, -1, -1, -1, -1, -1], [-1, -1, 1, 1, -1, -1, -1, -1, -1, -1, -1], [-1, 1, 1, 0, -1, -1, -1, -1, -1, -1, -1], [0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1], [0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1]], (3, 2), 802, 'source/sas.png', OBJ_NAME[CAT_NAME[7]][1]),
        Object([[1, 1, 1], [1, 1, 1], [1, 1, 1], [-1, -1, -1]], (1, 1), 803, 'source/nacelle.png', OBJ_NAME[CAT_NAME[7]][2]),
        Object([[-1, -1, -1, -1, -1, -1], [-1, 1, 1, 1, 1, -1], [-1, 1, 1, 1, 1, -1], [-1, 1, 1, 1, 1, -1], [-1, 1, 1, 1, 1, -1], [-1, 1, 1, 1, 1, -1], [-1, -1, -1, -1, -1, -1]], (3, 2), 804, 'source/navette.png', OBJ_NAME[CAT_NAME[7]][3])
    ],
    CAT_NAME[8]: [
        Object([[1, 1], [1, 1], [-1, -1]], (0, 0), 901, 'source/noyau_x1.png', OBJ_NAME[CAT_NAME[8]][0]),
        Object([[1, 1, 1], [1, 1, 1], [-1, -1, -1]], (0, 0), 902, 'source/noyau_x2.png', OBJ_NAME[CAT_NAME[8]][1]),
        Object([[1, 1, 1, 1], [1, 1, 1, 1], [-1, -1, -1, -1]], (0, 0), 903, 'source/noyau_x3.png', OBJ_NAME[CAT_NAME[8]][2]),
        Object([[1, 1], [-1, -1]], (0, 0), 904, 'source/stabilisateur_coque.png', OBJ_NAME[CAT_NAME[8]][3]),
        Object([[1, 1, 1], [1, 1, 1], [0, -1, 0]], (1, 1), 905, 'source/console.png', OBJ_NAME[CAT_NAME[8]][4]),
        Object([[1, 1, 1], [1, 1, 1], [0, -1, 0]], (1, 1), 906, 'source/console.png', OBJ_NAME[CAT_NAME[8]][5]),
        Object([[1, 1, 1], [1, 1, 1], [0, -1, 0]], (1, 1), 907, 'source/console.png', OBJ_NAME[CAT_NAME[8]][6]),
        Object([[1, 1, 1], [1, 1, 1], [0, -1, 0]], (1, 1), 908, 'source/console.png', OBJ_NAME[CAT_NAME[8]][7]),
        Object([[-1, 1, 1, -1], [-1, 1, 1, -1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], (2, 1), 909, 'source/hypermoteur.png', OBJ_NAME[CAT_NAME[8]][8]), # without the nope zone to note interacte with the border, may do this with the sas or rework the border system
        Object([[-1, 1, 1, -1], [-1, 1, 1, -1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], (2, 1), 910, 'source/hypermoteur.png', OBJ_NAME[CAT_NAME[8]][9]),
        Object([[1, 1], [1, 1]], (0, 0), 911, 'source/petit_bouclier.png', OBJ_NAME[CAT_NAME[8]][10]),
        Object([[1, 1, 1], [1, 1, 1], [1, 1, 1], [0, -1, 0]], (1, 1), 912, 'source/bouclier.png', OBJ_NAME[CAT_NAME[8]][11]),
        Object([[1, 1], [1, 1]], (0, 0), 913, 'source/tourelle_2x.png', OBJ_NAME[CAT_NAME[8]][12]),
        Object([[1, 1], [1, 1]], (0, 0), 914, 'source/tourelle_2x.png', OBJ_NAME[CAT_NAME[8]][13]),
        Object([[1, 1, 1], [1, 1, 1], [1, 1, 1], [0, -1, 0]], (1, 1), 915, 'source/tourelle_3x.png', OBJ_NAME[CAT_NAME[8]][14]),
        Object([[1, 1, 1], [1, 1, 1], [1, 1, 1], [0, -1, 0]], (1, 1), 916, 'source/tourelle_3x.png', OBJ_NAME[CAT_NAME[8]][15]),
        Object([[1, 1, 1], [1, 1, 1], [1, 1, 1]], (1, 1), 917, 'source/scanneuse.png', OBJ_NAME[CAT_NAME[8]][16]),
        Object([[1, 1, 1], [1, 1, 1], [1, 1, 1], [0, -1, 0]], (1, 1), 918, 'source/brouilleur.png', OBJ_NAME[CAT_NAME[8]][17])
    ]
    # robot, station
}

CAT_LIST = list(OBJ_DICT.keys())
