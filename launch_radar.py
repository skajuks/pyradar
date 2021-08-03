import sys
import pymem
import pymem.process
import pygame as pg
import os
import time
import struct
import pathlib
from fetch_offsets_to_dict import fetchOffsets
from structs import *


# fetch offsets from hazeddumper
offsets = fetchOffsets(1) # 0 -> debug off

process_name = "csgo.exe"
game_name = "Counter-Strike: Global Offensive"

d_counter_terrorist_team = 3
d_terrorist_team = 2

try:
    memory = pymem.Pymem(process_name)  # get process handle
    gameModule = pymem.process.module_from_name(memory.process_handle, "client.dll").lpBaseOfDll
    engineModule = pymem.process.module_from_name(memory.process_handle, "engine.dll").lpBaseOfDll
except:
    print(f"[Error] cannot find process handle for {process_name}, check if {game_name} is running")
    sys.exit() # terminate script if no process if found

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

ci = [ClientInfo() for _ in range(64)]
e = [Entity() for _ in range(64)]

def healthToColor(health):
    return (int(round(255 - (health * 2.55))), int(round(health * 2.55)), 0)

def getPlayerName(i):
    playerinfo = memory.read_int(memory.read_int(engineModule + int(offsets["dwClientState"], 16)) + int(offsets["dwClientState_PlayerInfo"], 16))
    playerinfo_items = memory.read_int(memory.read_int(playerinfo + 0x40) + 0xC)
    name = memory.read_string(memory.read_int((playerinfo_items + 0x28) + (i * 0x34)) + 0x10)
    return str(name)

def getWeaponName(index):
    print(index)
    for key, value in weapon_list.items():
        if index == key:
            return value
    return "Unknown"

def VECTOR3(arr): # redo
    vector_base = int(offsets["m_vecOrigin"], 16)
    return {
        "x" : round(float(struct.unpack('<f', bytearray(arr[vector_base:vector_base + 4]))[0]), 2),
        "y" : round(float(struct.unpack('<f', bytearray(arr[vector_base + 4:vector_base + 8]))[0]), 2),  #   add 4 bytes for next value
        "z" : float(0) #	leave z empty for now, because 2D pos logging is used
    }

def vectorToScreen(vector):
    vector["x"] = (vector["x"] + 1838) / 4.1
    vector["y"] = (vector["y"] - 1858) / 4.1

def drawCircleWithOutline(screen, color, x ,y):
    pg.draw.circle(screen, (0,0,0), [x, abs(y)], 10)
    pg.draw.circle(screen, color, [x, abs(y)], 8)
class Radar:
    def __init__(self):
        pg.init()
        pg.display.set_caption("chadys external python radar")
        self.screen = pg.display.set_mode((1024, 1024))
        self.run_radar = True
        self.load_radar_image()

    def run(self):
        self.update_radar_info()
        self.draw()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

    def update_radar_info(self):

        # add eye angles to draw line where player is looking



        self.screen.blit(self.office_radar, [0,0])
        entityIndex = 0
        while True:
            if(entityIndex >= 64):
                 break # ensure that we dont go pass 64 entities
            ci[entityIndex].entity = memory.read_int(gameModule + int(offsets["dwEntityList"], 16) + entityIndex * 0x10)
            if(ci[entityIndex].entity == 0): 
                break  # break if cannot find next entity
            EntityObject = memory.read_bytes(ci[entityIndex].entity, 400)
            e[entityIndex].health = EntityObject[int(offsets["m_iHealth"], 16)]
            e[entityIndex].team = EntityObject[int(offsets["m_iTeamNum"], 16)]
            e[entityIndex].vecOrigin = VECTOR3(EntityObject)
            vectorToScreen(e[entityIndex].vecOrigin)
            if(e[entityIndex].health > 0):
                if(e[entityIndex].team == d_counter_terrorist_team):
                    drawCircleWithOutline(self.screen, (0,255,255),e[entityIndex].vecOrigin["x"], e[entityIndex].vecOrigin["y"])
                else: 
                    drawCircleWithOutline(self.screen, (255,0,40),e[entityIndex].vecOrigin["x"], e[entityIndex].vecOrigin["y"])
                    self.draw_text(getPlayerName(entityIndex), 10, (255,255,255), e[entityIndex].vecOrigin["x"], abs(e[entityIndex].vecOrigin["y"] - 10))  
            entityIndex +=1

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