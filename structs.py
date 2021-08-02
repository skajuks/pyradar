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
        self.filler = bytearray(8)
        self.nextEntity = int(0)

class Entity:   # size 0x0104
    def __init__(self):
        self.pad_0000 = bytearray(244)
        self.team = int(0)
        self.pad_0001 = bytearray(8)
        self.health = int(0)
        self.flags = int(0)
        self.vecViewOffset = VECTOR()
        self.vecVelocity = VECTOR()
        self.pad_0002 = bytearray(22)
        self.vecOrigin = VECTOR()