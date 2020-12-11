import sys
import pygame as pg
import numpy as np
import random
import time

pic = np.zeros(shape=(128,64))
width = 128
height = 64
refresh_rate = 60
interval = 1 / refresh_rate

bootrom_file = "bootrom0"
rom_file = "rom"
# rom_file = "hello_world"
debug = False

pg.display.init()
display = pg.display.set_mode((width*4, height*4), flags=0, depth=8)
screen = pg.Surface((width, height), flags=0, depth=8)
pg.transform.scale(screen, (width*4, height*4), display)

def screen_update(silent=True):
    pg.transform.scale(screen, (width*4, height*4), display)
    pg.display.flip()
    if not silent:
        print("Screen Update")

def screen_clear():
    screen.fill((0,0,0))
    #screen_update()

def screen_draw_line(x, y, pixels):
    # print("----------DRAW----------")
    # print("x:",x)
    # print("y:",y)
    # print("pix:",bin(pixels))
    j = 0b10000000
    for i in range(8):
        x_pos = x + i
        y_pos = y
        if x_pos >= 0 and x_pos < width:
            if y_pos >= 0 and y_pos < height:
                if pixels & j:
                    pg.draw.rect(screen, 255, pg.Rect(x_pos,y_pos,1,1))
                else:
                    pg.draw.rect(screen, 0, pg.Rect(x_pos,y_pos,1,1))
        j = j >> 1
    #screen_update()

screen_clear()
# screen_draw_line(0,0,0b10101011)
# input()


class memByte:
    def __init__(self):
        self.value = 0x00000000
    def write(self, value):
        self.value = value & 0xff
    def readUpper(self):
        return (self.value & 0b11110000) >> 4
    def readLower(self):
        return self.value & 0b1111

class Flags:
    def __init__(self):
        self.z = 0
        self.n = 0
        self.h = 0
        self.c = 0
    def setZero(self):
        self.z = 1
    def clearZero(self):
        self.z = 0
    def setNeg(self):
        self.n = 1
    def clearNeg(self):
        self.n = 0
    def setHalf(self):
        self.h = 1
    def clearHalf(self):
        self.h = 0
    def setCarry(self):
        self.c = 1
    def clearCarry(self):
        self.c = 0
    def clearFlags(self):
        self.z = 0
        self.n = 0
        self.h = 0
        self.c = 0

class reg:
    def __init__(self):
        self.value = 0b00000000
        self.value = random.randint(0,255)
    def send(self):
        sys.stdout.write(chr(self.value))
        sys.stdout.flush()

class Dreg:
    def __init__(self, r1, r2):
        self.r1 = r1
        self.r2 = r2
    def getvalue(self):
        self.value = (self.r1.value << 8) + self.r2.value
    def setvalue(self):
        self.r1.value = self.value >> 8
        self.r2.value = self.value & 0xff


class regPC:
    def __init__(self):
        self.value = 0x0
    def inc(self, length=1):
        self.value += length
        self.value = self.value & 0xffff
    def jump(self, address):
        self.value = address & 0xffff

class regSP:
    def __init__(self):
        self.value = 0xfffe
    def inc(self):
        self.value += 2
        self.value = self.value & 0xffff
    def dec(self):
        self.value -= 2
    def setvalue(self):
        #print("SPSET:",hex(self.value))
        pass # JUST TO MAKE LDX SIMPLER

ONE_REG = reg()
ONE_REG.value = 1

FL = Flags()
halt = False
A = reg()
B = reg()
C = reg()
D = reg()
E = reg()
H = reg()
L = reg()
BC = Dreg(B, C)
DE = Dreg(D, E)
HL = Dreg(H, L)

#E.value = 0x1 # Randomness loop

PC = regPC()
SP = regSP()
memory = []
jumped = False

print("RESERVING MEMORY...")
for i in range(0x10000):
    memory.append(memByte())
print("MEMORY RESERVED.")
print("LOADING MEMORY...")
f = open(bootrom_file, "rb")
rom_data = f.read()
f.close()
for i in range(len(rom_data)):
    memory[i+0x0].value = rom_data[i]
f = open(rom_file, "rb")
rom_data = f.read()
f.close()
for i in range(len(rom_data)):
    memory[i+0x597].value = rom_data[i]
print("MEMORY LOADED.")

def LDI(R, mem=False):
    PC.inc()
    if not mem:
        R.value = memory[PC.value].value
    else:
        R.getvalue()
        memory[R.value].value = memory[PC.value].value
def LDX(R):
    PC.inc()
    low = memory[PC.value].value
    PC.inc()
    R.value = low + (memory[PC.value].value << 8)
    R.setvalue()
def PUSH_R(R, mem=False):
    if not mem:
        memory[SP.value].value = R.value
    else:
        R.getvalue()
        memory[SP.value].value = memory[R.value].value
    SP.dec()
def PUSH_RR(RR):
    RR.getvalue()
    memory[SP.value].value = RR.value & 0xff
    memory[SP.value + 1].value = RR.value >> 8
    SP.dec()
def POP_R(R, mem=False):
    SP.inc()
    if not mem:
        #print(hex(SP.value))
        R.value = memory[SP.value].value
    else:
        R.getvalue()
        memory[R.value].value = memory[SP.value].value
def POP_RR(RR):
    SP.inc()
    RR.value = memory[SP.value].value + (memory[SP.value + 1].value << 8)
    RR.setvalue()
MOV_REGISTERS = [B, C, D, E, H, L, HL, A]
MOVB_OPCODES = [0x09, 0x19, 0x29, 0x39, 0x49, 0x59, 0x69, 0x79]
MOVC_OPCODES = [0x99, 0x99, 0xA9, 0xB9, 0xC9, 0xD9, 0xE9, 0xF9]
MOVD_OPCODES = [0x0A, 0x1A, 0x2A, 0x3A, 0x4A, 0x5A, 0x6A, 0x7A]
MOVE_OPCODES = [0x8A, 0x9A, 0xAA, 0xBA, 0xCA, 0xDA, 0xEA, 0xFA]
MOVH_OPCODES = [0x0B, 0x1B, 0x2B, 0x3B, 0x4B, 0x5B, 0x6B, 0x7B]
MOVL_OPCODES = [0x8B, 0x9B, 0xAB, 0xBB, 0xCB, 0xDB, 0xEB, 0xFB]
MOVMHL_OPCODES = [0x0C, 0x1C, 0x2C, 0x3C, 0x4C, 0x5C, 0x6C, 0x7C]
MOVA_OPCODES = [0x8C, 0x9C, 0xAC, 0xBC, 0xCC, 0xDC, 0xEC, 0xFC]
def MOV(R1, R2index, mem=False):
    R2 = MOV_REGISTERS[R2index]
    if not mem:
        if R2index == 6:
            R2.getvalue()
            R1.value = memory[R2.value].value
        else:
            R1.value = R2.value
    else:
        memory[R1.value].value = R2.value
        R1.setvalue()
def MOV_RR(RR1, RR2):
    RR2.getvalue()
    RR1.value = RR2.value
    RR1.setvalue()
def ADD_8(value1, value2):
    nib = (value1 & 0xf) + (value2 & 0xf)
    value = value1 + value2
    FL.clearFlags()
    if value & 0xff == 0:
        FL.setZero()
    if value & 0b10000000:
        FL.setNeg()
    if nib & 0xf0:
        FL.setHalf()
    if value >> 8:
        FL.setCarry()
    return value & 0xff
def ADD_R(R, mem=False):
    if not mem:
        value = ADD_8(A.value, R.value)
        R.value = value
    else:
        R.getvalue()
        value = ADD_8(A.value, memory[R.value].value)
        memory[R.value].value = value
def ADD_16(value1, value2):
    nib = (value1 & 0xf) + (value2 & 0xf)
    value = value1 + value2
    FL.clearFlags()
    if value & 0xffff == 0:
        FL.setZero()
    if value & 0b1000000000000000:
        FL.setNeg()
    if nib & 0xf0:
        FL.setHalf()
    if value >> 16:
        FL.setCarry()
    return value & 0xffff
def ADDX_RR(RR):
    RR.getvalue()
    value = ADD_16(A.value, RR.value)
    RR.value = value
    RR.setvalue()
def SUB_8(value1, value2):
    value = value1 - value2
    if value < 0:
        value += 0x100
    FL.clearFlags()
    if value == 0:
        FL.setZero()
    if value & 0b10000000:
        FL.setNeg()
    if (value1 & 0xf) <= (value2 & 0xf):
        FL.setHalf()
    if value1 <= value2:
        FL.setCarry()
    return value & 0xff
def SUB_R(R, compare_only, mem=False):
    if not mem:
        value = SUB_8(R.value, A.value)
        if not compare_only:
            R.value = value
    else:
        R.getvalue()
        value = SUB_8(memory[R.value].value, A.value)
        if not compare_only:
            memory[R.value].value = value
def INC(R, mem=False):
    if not mem:
        value = ADD_8(ONE_REG.value, R.value)
        R.value = value
    else:
        R.getvalue()
        value = ADD_8(ONE_REG.value, memory[R.value].value)
        memory[R.value].value = value
def DEC(R, mem=False):
    if not mem:
        value = SUB_8(R.value, ONE_REG.value)
        R.value = value
    else:
        R.getvalue()
        value = SUB_8(memory[R.value].value, ONE_REG.value)
        memory[R.value].value = value
def AND_8(value1, value2):
    value = value1 & value2
    FL.clearFlags()
    if value == 0:
        FL.setZero()
    if value & 0b10000000:
        FL.setNeg()
    return value & 0xff
def AND_R(R, mem=False):
    if not mem:
        value = AND_8(A.value, R.value)
        R.value = value
    else:
        R.getvalue()
        value = AND_8(A.value, memory[R.value].value)
        memory[R.value].value = value
def OR_8(value1, value2):
    value = value1 | value2
    FL.clearFlags()
    if value == 0:
        FL.setZero()
    if value & 0b10000000:
        FL.setNeg()
    return value & 0xff
def OR_R(R, mem=False):
    if not mem:
        value = OR_8(A.value, R.value)
        R.value = value
    else:
        R.getvalue()
        value = OR_8(A.value, memory[R.value].value)
        memory[R.value].value = value
def XOR_8(value1, value2):
    value = value1 ^ value2
    FL.clearFlags()
    if value == 0:
        FL.setZero()
    if value & 0b10000000:
        FL.setNeg()
    return value & 0xff
def XOR_R(R, mem=False):
    if not mem:
        value = XOR_8(A.value, R.value)
        R.value = value
    else:
        R.getvalue()
        value = XOR_8(A.value, memory[R.value].value)
        memory[R.value].value = value
def CMPS(R, mem=False):
    if not mem:
        Rval = R.value
        if Rval & 0b10000000:
            Rval = - ((0x100 - Rval) & 0xff)
        Aval = A.value
        if Aval & 0b10000000:
            Aval = - ((0x100 - Aval) & 0xff)
        FL.clearFlags()
        if Rval == Aval:
            FL.setZero()
        elif Rval < Aval:
            FL.setNeg()
    else:
        R.getvalue()
        Rval = memory[R.value].value
        if Rval & 0b10000000:
            Rval = - ((0x100 - Rval) & 0xff)
        Aval = A.value
        if Aval & 0b10000000:
            Aval = - ((0x100 - Aval) & 0xff)
        FL.clearFlags()
        if Rval == Aval:
            FL.setZero()
        elif Rval < Aval:
            FL.setNeg()
def JUMP():
    PC.inc()
    low = memory[PC.value].value
    PC.inc()
    high = memory[PC.value].value
    global jumped
    jumped = True
    PC.value = (high << 8) + low
    print("JUMP:",hex((high << 8) + low))
def REL_JUMP():
    PC.inc()
    value = memory[PC.value].value
    if value & 0b10000000:
        value = - ((0x100 - value) & 0xff)
    # ACCORDING TO DOCUMENTATION RELATIVE JUMPS USE THE +2 PC INC
    PC.value += value

screen_update()
last_update = time.time()

while not halt:
    b_up = memory[PC.value].readUpper()
    b_down = memory[PC.value].readLower()
    b_val = memory[PC.value].value

    jumped = False

    if time.time() > last_update + interval:
        screen_update()
        last_update = time.time()

    # Handle pygame events
    for event in pg.event.get():
        # print("EVENT:",event.type)
        # input()
        pass

    if debug:
        pass#input()
    if debug or False:
        print(hex(PC.value), hex(b_val))

    # if b_val in [0x86, 0x96, 0xA6, 0xB6, 0xC6, 0xD6, 0xE6, 0xF6]:
    #     print("CMP R")
    #     input()
    # if b_val == 0xF7:
    #     print("CMPI")
    #     input()

    # HCF (HALT)
    if b_val == 0x6C:
        halt = True
    # LDI R, xx
    if b_val == 0x20:
        LDI(B)
    elif b_val == 0x30:
        LDI(C)
    elif b_val == 0x40:
        LDI(D)
    elif b_val == 0x50:
        LDI(E)
    elif b_val == 0x60:
        LDI(H)
    elif b_val == 0x70:
        LDI(L)
    elif b_val == 0x80:
        LDI(HL, mem=True)
    elif b_val == 0x90:
        LDI(A)
    # LDX RR, xxyy
    elif b_val == 0x21:
        LDX(BC)
    elif b_val == 0x31:
        LDX(DE)
    elif b_val == 0x41:
        LDX(HL)
    elif b_val == 0x22:
        LDX(SP)
    # PUSH R
    elif b_val == 0x81:
        PUSH_R(B)
    elif b_val == 0x91:
        PUSH_R(C)
    elif b_val == 0xA1:
        PUSH_R(D)
    elif b_val == 0xB1:
        PUSH_R(E)
    elif b_val == 0xC1:
        PUSH_R(H)
    elif b_val == 0xD1:
        PUSH_R(L)
    elif b_val == 0xC0:
        PUSH_R(HL, mem=True)
    elif b_val == 0xD0:
        PUSH_R(A)
    # PUSH RR
    elif b_val == 0x51:
        PUSH_RR(BC)
    elif b_val == 0x61:
        PUSH_RR(DE)
    elif b_val == 0x71:
        PUSH_RR(HL)
    # POP R
    elif b_val == 0x82:
        POP_R(B)
    elif b_val == 0x92:
        POP_R(C)
    elif b_val == 0xA2:
        POP_R(D)
    elif b_val == 0xB2:
        POP_R(E)
    elif b_val == 0xC2:
        POP_R(H)
    elif b_val == 0xD2:
        POP_R(L)
    elif b_val == 0xC3:
        POP_R(HL, mem=True)
    elif b_val == 0xD3:
        POP_R(A)
    # POP RR
    elif b_val == 0x52:
        POP_RR(BC)
    elif b_val == 0x62:
        POP_RR(DE)
    elif b_val == 0x72:
        POP_RR(HL)
    # MOV R1, R2
    elif b_val in MOVB_OPCODES:
        MOV(B, MOVB_OPCODES.index(b_val))
    elif b_val in MOVC_OPCODES:
        MOV(C, MOVC_OPCODES.index(b_val))
    elif b_val in MOVD_OPCODES:
        MOV(D, MOVD_OPCODES.index(b_val))
    elif b_val in MOVE_OPCODES:
        MOV(E, MOVE_OPCODES.index(b_val))
    elif b_val in MOVH_OPCODES:
        MOV(H, MOVH_OPCODES.index(b_val))
    elif b_val in MOVL_OPCODES:
        MOV(L, MOVL_OPCODES.index(b_val))
    elif b_val in MOVMHL_OPCODES:
        MOV(HL, MOVMHL_OPCODES.index(b_val), mem=True)
    elif b_val in MOVA_OPCODES:
        MOV(A, MOVA_OPCODES.index(b_val))
    # MOV RR1, RR2
    elif b_val == 0xED:
        MOV_RR(HL, BC)
    elif b_val == 0xFD:
        MOV_RR(HL, DE)
    # CLRFLAG
    elif b_val == 0x08:
        FL.clearFlags()
    # SETFLAG f, x
    elif b_val == 0x18:
        FL.setZero()
    elif b_val == 0x28:
        FL.clearZero()
    elif b_val == 0x38:
        FL.setNeg()
    elif b_val == 0x48:
        FL.clearNeg()
    elif b_val == 0x58:
        FL.setHalf()
    elif b_val == 0x68:
        FL.clearHalf()
    elif b_val == 0x78:
        FL.setCarry()
    elif b_val == 0x88:
        FL.clearCarry()
    # ADD R
    elif b_val == 0x04:
        ADD_R(B)
    elif b_val == 0x14:
        ADD_R(C)
    elif b_val == 0x24:
        ADD_R(D)
    elif b_val == 0x34:
        ADD_R(E)
    elif b_val == 0x44:
        ADD_R(H)
    elif b_val == 0x54:
        ADD_R(L)
    elif b_val == 0x64:
        ADD_R(HL, mem=True)
    elif b_val == 0x74:
        ADD_R(A)
    # ADDI xx
    elif b_val == 0xA7:
        PC.inc()
        value = ADD_8(A.value, memory[PC.value].value)
        A.value = value
    # ADDX RR
    elif b_val == 0x83:
        ADDX_RR(BC)
    elif b_val == 0x93:
        ADDX_RR(DE)
    elif b_val == 0xA3:
        ADDX_RR(HL)
    # SUB R | CMP R
    elif b_val == 0x84 or b_val == 0x86:
        SUB_R(B, b_val == 0x86)
    elif b_val == 0x94 or b_val == 0x96:
        SUB_R(C, b_val == 0x96)
    elif b_val == 0xA4 or b_val == 0xA6:
        SUB_R(D, b_val == 0xA6)
    elif b_val == 0xB4 or b_val == 0xB6:
        SUB_R(E, b_val == 0xB6)
    elif b_val == 0xC4 or b_val == 0xC6:
        SUB_R(H, b_val == 0xC6)
    elif b_val == 0xD4 or b_val == 0xD6:
        SUB_R(L, b_val == 0xD6)
    elif b_val == 0xE4 or b_val == 0xE6:
        SUB_R(HL, b_val == 0xE6, mem=True)
    elif b_val == 0xF4 or b_val == 0xF6:
        SUB_R(A, b_val == 0xF6)
    # SUBI xx | CMPI xx
    elif b_val == 0xB7 or b_val == 0xF7:
        PC.inc()
        value = SUB_8(A.value, memory[PC.value].value)
        if b_val == 0xB7: # SUBI xx
            A.value = value
    # INC R
    elif b_val == 0x03:
        INC(B)
    elif b_val == 0x13:
        INC(C)
    elif b_val == 0x23:
        INC(D)
    elif b_val == 0x33:
        INC(E)
    elif b_val == 0x43:
        INC(H)
    elif b_val == 0x53:
        INC(L)
    elif b_val == 0x63:
        INC(HL, mem=True)
    elif b_val == 0x73:
        INC(A)
    # INX RR
    elif b_val == 0xA8:
        BC.getvalue()
        BC.value += 1
        BC.value & 0xffff
        BC.setvalue()
    elif b_val == 0xB8:
        DE.getvalue()
        DE.value += 1
        DE.value & 0xffff
        DE.setvalue()
    elif b_val == 0xC8:
        HL.getvalue()
        HL.value += 1
        HL.value & 0xffff
        HL.setvalue()
    # DEC R
    elif b_val == 0x07:
        DEC(B)
    elif b_val == 0x17:
        DEC(C)
    elif b_val == 0x27:
        DEC(D)
    elif b_val == 0x37:
        DEC(E)
    elif b_val == 0x47:
        DEC(H)
    elif b_val == 0x57:
        DEC(L)
    elif b_val == 0x67:
        DEC(HL, mem=True)
    elif b_val == 0x77:
        DEC(A)
    # AND R
    elif b_val == 0x05:
        AND_R(B)
    elif b_val == 0x15:
        AND_R(C)
    elif b_val == 0x25:
        AND_R(D)
    elif b_val == 0x35:
        AND_R(E)
    elif b_val == 0x45:
        AND_R(H)
    elif b_val == 0x55:
        AND_R(L)
    elif b_val == 0x65:
        AND_R(HL, mem=True)
    elif b_val == 0x75:
        AND_R(A)
    # ANDI xx
    elif b_val == 0xC7:
        PC.inc()
        value = AND_8(memory[PC.value].value, A.value)
        A.value = value
    # OR R
    elif b_val == 0x85:
        OR_R(B)
    elif b_val == 0x95:
        OR_R(C)
    elif b_val == 0xA5:
        OR_R(D)
    elif b_val == 0xB5:
        OR_R(E)
    elif b_val == 0xC5:
        OR_R(H)
    elif b_val == 0xD5:
        OR_R(L)
    elif b_val == 0xE5:
        OR_R(HL, mem=True)
    elif b_val == 0xF5:
        OR_R(A)
    # ORI xx
    elif b_val == 0xD7:
        PC.inc()
        value = OR_8(memory[PC.value].value, A.value)
        A.value = value
    # XOR R
    elif b_val == 0x06:
        XOR_R(B)
    elif b_val == 0x16:
        XOR_R(C)
    elif b_val == 0x26:
        XOR_R(D)
    elif b_val == 0x36:
        XOR_R(E)
    elif b_val == 0x46:
        XOR_R(H)
    elif b_val == 0x56:
        XOR_R(L)
    elif b_val == 0x66:
        XOR_R(HL, mem=True)
    elif b_val == 0x76:
        XOR_R(A)
    # XORI xx
    elif b_val == 0xE7:
        PC.inc()
        value = XOR_8(memory[PC.value].value, A.value)
        A.value = value
    # CMPS R
    elif b_val == 0x0D:
        CMPS(B)
    elif b_val == 0x1D:
        CMPS(C)
    elif b_val == 0x2D:
        CMPS(D)
    elif b_val == 0x3D:
        CMPS(E)
    elif b_val == 0x4D:
        CMPS(H)
    elif b_val == 0x5D:
        CMPS(L)
    elif b_val == 0x6D:
        CMPS(HL, mem=True)
    elif b_val == 0x7D:
        CMPS(A)
    # SIN
    elif b_val == 0xE0:
        A.value = ord(sys.stdin.buffer.read(1)) & 0xff
        pass
    # SOUT
    elif b_val == 0xE1:
        print(chr(A.value),end="",flush=True)
        if A.value == 7:
            print("[BELL]")
        pass
    # CLRSCR
    elif b_val == 0xF0:
        screen_clear()
    # DRAW
    elif b_val == 0xF1:
        x = C.value
        if x & 0b10000000:
            x = - ((0x100 - x) & 0xff)
        y = B.value
        if y & 0b10000000:
            y = - ((0x100 - y) & 0xff)
        screen_draw_line(x, y, A.value & 0xff)
    # JMP xxyy
    elif b_val == 0x0F:
        JUMP()
    # JMPcc xxyy
    elif b_val == 0x1F:
        if FL.z:
            JUMP()
        else:
            PC.inc(2)
    elif b_val == 0x2F:
        if not FL.z:
            JUMP()
        else:
            PC.inc(2)
    elif b_val == 0x3F:
        if FL.n:
            JUMP()
        else:
            PC.inc(2)
    elif b_val == 0x4F:
        if not FL.n:
            JUMP()
        else:
            PC.inc(2)
    elif b_val == 0x5F:
        if FL.h:
            JUMP()
    elif b_val == 0x6F:
        if not FL.h:
            JUMP()
        else:
            PC.inc(2)
    elif b_val == 0x7F:
        if FL.c:
            JUMP()
        else:
            PC.inc(2)
    elif b_val == 0x8F:
        if not FL.c:
            JUMP()
        else:
            PC.inc(2)
    # JMP xx
    elif b_val == 0x9F:
        REL_JUMP()
    # JMPcc xx
    elif b_val == 0xAF:
        if FL.z:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xBF:
        if not FL.z:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xCF:
        if FL.n:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xDF:
        if not FL.n:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xEF:
        if FL.h:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xFF:
        if not FL.h:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xEE:
        if FL.c:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xFE:
        if not FL.c:
            REL_JUMP()
        else:
            PC.inc()
    # CALL xxyy
    elif b_val == 0x1E:
        memory[SP.value].value = (PC.value+3) & 0xff
        memory[SP.value + 1].value = (PC.value+3) >> 8
        SP.dec()
        JUMP()
    # RET
    elif b_val == 0x0E:

        SP.inc()
        PC.value = memory[SP.value].value + (memory[SP.value + 1].value << 8)
        jumped = True
    # NOP
    elif b_val == 0x00:
        pass
    else:
        pass
        print("UNKNOWN:",hex(b_val),"@",hex(PC.value))

    if debug:
        BC.getvalue()
        DE.getvalue()
        HL.getvalue()
        print("A:",hex(A.value),"B:",hex(B.value),"C:",hex(C.value),"D:",hex(D.value),"E:",hex(E.value),"H:",hex(H.value),
                "L:",hex(L.value),"BC:",hex(BC.value),"DE:",hex(DE.value),"HL:",hex(HL.value),"PC:",hex(PC.value),"SP:",hex(SP.value))

    if not jumped:
        PC.inc()
    else:
        pass
        #print("JUMPED")
