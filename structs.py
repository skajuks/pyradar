#!/usr/bin/env python

# Structs file used to minimize rpm calls


class VECTOR:
    def __init__(self):
        self.x = float(0)
        self.y = float(0)
        self.z = float(0)

class ClientInfo:   # size 0x0010   16 bytes
    def __init__(self):
        self.entity = int(0)
class Entity:   # size 0x0104
    def __init__(self):
        self.team = int(0)
        self.health = int(0)
        self.flags = int(0)
        self.vecOrigin = VECTOR()
        self.eyeAngles = VECTOR()