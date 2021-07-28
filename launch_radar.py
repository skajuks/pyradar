import sys
import pymem
import pymem.process
import pygame as pg
import os
import time
import pathlib
from fetch_offsets_to_dict import fetchOffsets

# fetch offsets from hazeddumper
offsets = fetchOffsets(1) # 0 -> debug off

process_name = "csgo.exe"
game_name = "Counter-Strike: Global Offensive"

try:
    memory = pymem.Pymem(process_name)  # get process handle
    gameModule = pymem.process.module_from_name(memory.process_handle, "client.dll").lpBaseOfDll
    engineModule = pymem.process.module_from_name(memory.process_handle, "engine.dll").lpBaseOfDll
except:
    print(f"[Error] cannot find process handle for {process_name}, check if {game_name} is running")
    sys.exit() # terminate script if no process if found

def VECTOR3(localPlayer):
    return {
        "x" : round(float(memory.read_float(localPlayer + int(offsets["m_vecOrigin"], 16))), 2),
        "y" : round(float(memory.read_float(localPlayer + int(offsets["m_vecOrigin"], 16) + 4)), 2),  #   add 4 bytes for next value
        "z" : float(0) #	leave z empty for now, because 2D pos logging is used
    }

def healthToColor(health):
    return (int(round(255 - (health * 2.55))), int(round(health * 2.55)), 0)

def getPlayerName(i, items):
    name = memory.read_string(memory.read_int((items + 0x28) + (i * 0x34)) + 0x10)
    return str(name)

weapon_list = {
    1: "Desert Eagle",
    2: "Dual Berettas",
    3: "Five-SeveN",
    4: "Glock-18",
    7: "AK-47",
    8: "AUG",
    9: "AWP",
    10: "FAMAS",
    11: "G3SG1",
    13: "Galil AR",
    14: "M249",
    16: "M4A4",
    17: "MAC-10",
    19: "P90",
    20: "Repulsor Device",
    23: "MP5-SD",
    24: "UMP-45",
    25: "XM1014",
    26: "PP-Bizon",
    27: "MAG-7",
    28: "Negev",
    29: "Sawed-Off",
    30: "Tec-9",
    31: "Zeus x27",
    32: "P2000",
    33: "MP7",
    34: "MP9",
    35: "Nova",
    36: "P250",
    37: "Ballistic Shield",
    38: "SCAR-20",
    39: "SG 553",
    40: "SSG 08",
    41: "Knife",
    42: "Knife",
    43: "Flashbang",
    44: "High Explosive Grenade",
    45: "Smoke Grenade",
    46: "Molotov",
    47: "Decoy Grenade",
    48: "Incendiary Grenade",
    49: "C4 Explosive",
    50: "Kevlar Vest",
    51: "Kevlar + Helmet",
    52: "Heavy Assault Suit",
    54: "item_nvg",
    55: "Defuse Kit",
    56: "Rescue Kit",
    57: "Medi-Shot",
    58: "Music Kit",
    59: "Knife",
    60: "M4A1-S",
    61: "USP-S",
    63: "CZ75-Auto",
    64: "R8 Revolver",
    68: "Tactical Awareness Grenade",
    69: "Bare Hands",
    70: "Breach Charge",
    72: "Tablet",
    75: "Axe",
    76: "Hammer",
    78: "Wrench",
    80: "Spectral Shiv",
    81: "Fire Bomb",
    82: "Diversion Device",
    83: "Frag Grenade",
    84: "Snowball",
    85: "Bump Mine"
}

def getWeaponName(index):
    print(index)
    for key, value in weapon_list.items():
        if index == key:
            return value
    return "Unknown"       

class Radar:
    def __init__(self):
        pg.init()
        pg.display.set_caption("chadys external python radar")
        self.screen = pg.display.set_mode((1024, 1024))
        self.run_radar = True
        self.load_radar_image()

    def run(self):
        self.update()
        self.draw()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

    def update(self):
        self.screen.blit(self.office_radar, [0,0])

        self.localPlayer = memory.read_int(gameModule + int(offsets["dwLocalPlayer"], 16)) # read localplayer offset

        self.localPlayer_health = memory.read_int(self.localPlayer + int(offsets["m_iHealth"], 16))

        if(self.localPlayer_health > 0): # if player is alive

            self.playerinfo = memory.read_int(memory.read_int(engineModule + int(offsets["dwClientState"], 16)) + int(offsets["dwClientState_PlayerInfo"], 16))
            self.playerinfo_items = memory.read_int(memory.read_int(self.playerinfo + 0x40) + 0xC)
            self.localplayer_vecOrigin = VECTOR3(self.localPlayer)

            self.localplayer_team = memory.read_int(self.localPlayer + int(offsets["m_iTeamNum"], 16))
            
            self.localplayer_vecOrigin["x"] = (self.localplayer_vecOrigin["x"] + 1838) / 4.1
            self.localplayer_vecOrigin["y"] = (self.localplayer_vecOrigin["y"] - 1858) / 4.1

            for entity in range(32):    # loop trough entities
                try:
                    player_entity = memory.read_int(gameModule + int(offsets["dwEntityList"], 16) + entity * 0x10)

                    player_entity_health = memory.read_int(player_entity + int(offsets["m_iHealth"], 16))

                    if(player_entity_health > 0):

                        player_entity_vecOrigin = VECTOR3(player_entity)

                        player_entity_vecOrigin["x"] = (player_entity_vecOrigin["x"] + 1838) / 4.1
                        player_entity_vecOrigin["y"] = (player_entity_vecOrigin["y"] - 1858) / 4.1

                        player_entity_team = memory.read_int(player_entity + int(offsets["m_iTeamNum"], 16))
                        player_name = getPlayerName(entity, self.playerinfo_items)
                        
                        if(player_entity_team == self.localplayer_team):
                            pg.draw.circle(self.screen, (0,0,0), [player_entity_vecOrigin["x"], abs(player_entity_vecOrigin["y"])], 10)
                            pg.draw.circle(self.screen, (40,0,255), [player_entity_vecOrigin["x"], abs(player_entity_vecOrigin["y"])], 8)
                        else:
                            weapon_id = memory.read_int(player_entity + int(offsets["m_hActiveWeapon"], 16))
                            weapon_entity = memory.read_int(int(offsets["dwEntityList"], 16) + ((weapon_id & 0xFFF) - 1) * 0x10)
                            if(weapon_entity):
                                weapon_id_n = memory.read_int(weapon_entity + int(offsets["m_iItemDefinitionIndex"], 16))
                                weapon_name = getWeaponName(weapon_id_n)
                                print(weapon_id_n)
                                self.draw_text(weapon_name, 10, (255,255,255), player_entity_vecOrigin["x"], abs(player_entity_vecOrigin["y"]) + 15)

                            color = healthToColor(player_entity_health)
                            pg.draw.circle(self.screen, (0,0,0), [player_entity_vecOrigin["x"], abs(player_entity_vecOrigin["y"])], 10)
                            pg.draw.circle(self.screen, color, [player_entity_vecOrigin["x"], abs(player_entity_vecOrigin["y"])], 8) 
                        self.draw_text(player_name, 10, (255,255,255), player_entity_vecOrigin["x"], abs(player_entity_vecOrigin["y"]) - 25)          
                except:
                    pass

                pg.draw.circle(self.screen, (0,0,0), [self.localplayer_vecOrigin["x"], abs(self.localplayer_vecOrigin["y"])], 10)
                pg.draw.circle(self.screen, (255,0,120), [self.localplayer_vecOrigin["x"], abs(self.localplayer_vecOrigin["y"])], 8)

    def draw(self):
        pg.display.flip()

    def load_radar_image(self):
        self.dir = str(pathlib.Path(__file__).parent.resolve()) + r"\maps"
        self.office_radar = pg.image.load(os.path.join(self.dir, "office.png"))

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(r"C:\Windows\Fonts\Arial.ttf",size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

r = Radar()
while r.run_radar:
    r.run()
    time.sleep(0.1)

pymem.process.close_handle(memory.process_handle)    
pg.quit()