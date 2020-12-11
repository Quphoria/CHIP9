import sys
import pygame as pg
import random

width = 128
height = 64
scale = 4

bootrom_file = "bootrom0"
rom_file = "rom"
debug = False
stepwise = False

pg.display.init()
display = pg.display.set_mode((width*scale, height*scale), flags=0, depth=8)
screen = pg.Surface((width, height), flags=0, depth=8)
pg.transform.scale(screen, (width*scale, height*scale), display)

def screen_update():
    pg.transform.scale(screen, (width*scale, height*scale), display)
    pg.display.update()
    print("Screen Update")

def screen_clear():
    screen.fill((0,0,0))
    screen_update()

def screen_draw_line(x, y, pixels):
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
    screen_update()

screen.fill((0,0,0))
screen_update()


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
        self.calc_str()
    def setZero(self):
        self.z = 1
        self.calc_str()
    def clearZero(self):
        self.z = 0
        self.calc_str()
    def setNeg(self):
        self.n = 1
        self.calc_str()
    def clearNeg(self):
        self.n = 0
        self.calc_str()
    def setHalf(self):
        self.h = 1
        self.calc_str()
    def clearHalf(self):
        self.h = 0
        self.calc_str()
    def setCarry(self):
        self.c = 1
        self.calc_str()
    def clearCarry(self):
        self.c = 0
        self.calc_str()
    def clearFlags(self):
        self.z = 0
        self.n = 0
        self.h = 0
        self.c = 0
        self.calc_str()
    def calc_str(self):
        self.str = ("Z"*self.z) + ("N"*self.n) + ("H"*self.h) + ("C"*self.c)

class reg:
    def __init__(self):
        self.value = 0b00000000
        #self.value = random.randint(0,255)
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
        # FL.clearFlags()
        FL.clearZero()
        FL.clearNeg()
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
        # FL.clearFlags()
        FL.clearZero()
        FL.clearNeg()
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
def REL_JUMP():
    PC.inc()
    value = memory[PC.value].value
    if value & 0b10000000:
        value = - ((0x100 - value) & 0xff)
    # ACCORDING TO DOCUMENTATION RELATIVE JUMPS USE THE +2 PC INC
    PC.value += value

while not halt:
    b_up = memory[PC.value].readUpper()
    b_down = memory[PC.value].readLower()
    b_val = memory[PC.value].value

    jumped = False

    # Handle pygame events
    for event in pg.event.get():
        # print("EVENT:",event.type)
        # input()
        pass

    if debug and stepwise:
        input()
    if debug or True:
        print(hex(PC.value), hex(b_val))

    # if b_val in [0x86, 0x96, 0xA6, 0xB6, 0xC6, 0xD6, 0xE6, 0xF6]:
    #     print("CMP R")
    #     input()
    # if b_val == 0xF7:
    #     print("CMPI")
    #     input()

    # HCF (HALT)
    if b_val == 0x6C:
        print("HALT")
        halt = True
    # LDI R, xx
    if b_val == 0x20:
        print("LDI B", hex(memory[PC.value + 1].value))
        LDI(B)
    elif b_val == 0x30:
        print("LDI C", hex(memory[PC.value + 1].value))
        LDI(C)
    elif b_val == 0x40:
        print("LDI D", hex(memory[PC.value + 1].value))
        LDI(D)
    elif b_val == 0x50:
        print("LDI E", hex(memory[PC.value + 1].value))
        LDI(E)
    elif b_val == 0x60:
        print("LDI H", hex(memory[PC.value + 1].value))
        LDI(H)
    elif b_val == 0x70:
        print("LDI L", hex(memory[PC.value + 1].value))
        LDI(L)
    elif b_val == 0x80:
        print("LDI (HL)", hex(H.value) + hex(L.value)[2:], hex(memory[PC.value + 1].value))
        LDI(HL, mem=True)
    elif b_val == 0x90:
        print("LDI A", hex(memory[PC.value + 1].value))
        LDI(A)
    # LDX RR, xxyy
    elif b_val == 0x21:
        print("LDX BC", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        LDX(BC)
    elif b_val == 0x31:
        print("LDX DE", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        LDX(DE)
    elif b_val == 0x41:
        print("LDX HL", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        LDX(HL)
    elif b_val == 0x22:
        print("LDX SP", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        LDX(SP)
    # PUSH R
    elif b_val == 0x81:
        print("PUSH B")
        PUSH_R(B)
    elif b_val == 0x91:
        print("PUSH C")
        PUSH_R(C)
    elif b_val == 0xA1:
        print("PUSH D")
        PUSH_R(D)
    elif b_val == 0xB1:
        print("PUSH E")
        PUSH_R(E)
    elif b_val == 0xC1:
        print("PUSH H")
        PUSH_R(H)
    elif b_val == 0xD1:
        print("PUSH L")
        PUSH_R(L)
    elif b_val == 0xC0:
        print("PUSH (HL)", hex(H.value) + hex(L.value)[2:])
        PUSH_R(HL, mem=True)
    elif b_val == 0xD0:
        print("PUSH A")
        PUSH_R(A)
    # PUSH RR
    elif b_val == 0x51:
        print("PUSH BC")
        PUSH_RR(BC)
    elif b_val == 0x61:
        print("PUSH DE")
        PUSH_RR(DE)
    elif b_val == 0x71:
        print("PUSH HL")
        PUSH_RR(HL)
    # POP R
    elif b_val == 0x82:
        print("POP B")
        POP_R(B)
    elif b_val == 0x92:
        print("POP C")
        POP_R(C)
    elif b_val == 0xA2:
        print("POP D")
        POP_R(D)
    elif b_val == 0xB2:
        print("POP E")
        POP_R(E)
    elif b_val == 0xC2:
        print("POP H")
        POP_R(H)
    elif b_val == 0xD2:
        print("POP L")
        POP_R(L)
    elif b_val == 0xC3:
        print("POP (HL)", hex(H.value) + hex(L.value)[2:])
        POP_R(HL, mem=True)
    elif b_val == 0xD3:
        print("POP A")
        POP_R(A)
    # POP RR
    elif b_val == 0x52:
        print("POP BC")
        POP_RR(BC)
    elif b_val == 0x62:
        print("POP DE")
        POP_RR(DE)
    elif b_val == 0x72:
        print("POP HL")
        POP_RR(HL)
    # MOV R1, R2
    elif b_val in MOVB_OPCODES:
        print("MOV B, R2")
        MOV(B, MOVB_OPCODES.index(b_val))
    elif b_val in MOVC_OPCODES:
        print("MOV C, R2")
        MOV(C, MOVC_OPCODES.index(b_val))
    elif b_val in MOVD_OPCODES:
        print("MOV D, R2")
        MOV(D, MOVD_OPCODES.index(b_val))
    elif b_val in MOVE_OPCODES:
        print("MOV E, R2")
        MOV(E, MOVE_OPCODES.index(b_val))
    elif b_val in MOVH_OPCODES:
        print("MOV H, R2")
        MOV(H, MOVH_OPCODES.index(b_val))
    elif b_val in MOVL_OPCODES:
        print("MOV L, R2")
        MOV(L, MOVL_OPCODES.index(b_val))
    elif b_val in MOVMHL_OPCODES:
        print("MOV (HL), R2", hex(H.value) + hex(L.value)[2:])
        MOV(HL, MOVMHL_OPCODES.index(b_val), mem=True)
    elif b_val in MOVA_OPCODES:
        print("MOV A, R2")
        MOV(A, MOVA_OPCODES.index(b_val))
    # MOV RR1, RR2
    elif b_val == 0xED:
        print("MOV HL, BC")
        MOV_RR(HL, BC)
    elif b_val == 0xFD:
        print("MOV HL, DE")
        MOV_RR(HL, DE)
    # CLRFLAG
    elif b_val == 0x08:
        print("CLRFLAG")
        FL.clearFlags()
    # SETFLAG f, x
    elif b_val == 0x18:
        print("SETFLAG Z, 1")
        FL.setZero()
    elif b_val == 0x28:
        print("SETFLAG Z, 0")
        FL.clearZero()
    elif b_val == 0x38:
        print("SETFLAG N, 1")
        FL.setNeg()
    elif b_val == 0x48:
        print("SETFLAG N, 0")
        FL.clearNeg()
    elif b_val == 0x58:
        print("SETFLAG H, 1")
        FL.setHalf()
    elif b_val == 0x68:
        print("SETFLAG H, 0")
        FL.clearHalf()
    elif b_val == 0x78:
        print("SETFLAG C, 1")
        FL.setCarry()
    elif b_val == 0x88:
        print("SETFLAG C, 0")
        FL.clearCarry()
    # ADD R
    elif b_val == 0x04:
        print("ADD B")
        ADD_R(B)
    elif b_val == 0x14:
        print("ADD C")
        ADD_R(C)
    elif b_val == 0x24:
        print("ADD D")
        ADD_R(D)
    elif b_val == 0x34:
        print("ADD E")
        ADD_R(E)
    elif b_val == 0x44:
        print("ADD H")
        ADD_R(H)
    elif b_val == 0x54:
        print("ADD L")
        ADD_R(L)
    elif b_val == 0x64:
        print("ADD (HL)", hex(H.value) + hex(L.value)[2:])
        ADD_R(HL, mem=True)
    elif b_val == 0x74:
        print("ADD A")
        ADD_R(A)
    # ADDI xx
    elif b_val == 0xA7:
        PC.inc()
        print("ADDI xx", hex(memory[PC.value].value))
        value = ADD_8(A.value, memory[PC.value].value)
        A.value = value
    # ADDX RR
    elif b_val == 0x83:
        print("ADDX BC")
        ADDX_RR(BC)
    elif b_val == 0x93:
        print("ADDX DE")
        ADDX_RR(DE)
    elif b_val == 0xA3:
        print("ADDX HL")
        ADDX_RR(HL)
    # SUB R | CMP R
    elif b_val == 0x84 or b_val == 0x86:
        if b_val == 0x84:
            print("SUB B")
        else:
            print("CMP B")
        SUB_R(B, b_val == 0x86)
    elif b_val == 0x94 or b_val == 0x96:
        if b_val == 0x94:
            print("SUB C")
        else:
            print("CMP C")
        SUB_R(C, b_val == 0x96)
    elif b_val == 0xA4 or b_val == 0xA6:
        if b_val == 0xA4:
            print("SUB D")
        else:
            print("CMP D")
        SUB_R(D, b_val == 0xA6)
    elif b_val == 0xB4 or b_val == 0xB6:
        if b_val == 0xB4:
            print("SUB E")
        else:
            print("CMP E")
        SUB_R(E, b_val == 0xB6)
    elif b_val == 0xC4 or b_val == 0xC6:
        if b_val == 0xC4:
            print("SUB H")
        else:
            print("CMP H")
        SUB_R(H, b_val == 0xC6)
    elif b_val == 0xD4 or b_val == 0xD6:
        if b_val == 0xD4:
            print("SUB L")
        else:
            print("CMP L")
        SUB_R(L, b_val == 0xD6)
    elif b_val == 0xE4 or b_val == 0xE6:
        if b_val == 0xE4:
            print("SUB (HL)", hex(H.value) + hex(L.value)[2:])
        else:
            print("CMP (HL)", hex(H.value) + hex(L.value)[2:])
        SUB_R(HL, b_val == 0xE6, mem=True)
    elif b_val == 0xF4 or b_val == 0xF6:
        if b_val == 0xF4:
            print("SUB A")
        else:
            print("CMP A")
        SUB_R(A, b_val == 0xF6)
    # SUBI xx | CMPI xx
    elif b_val == 0xB7 or b_val == 0xF7:
        PC.inc()
        if b_val == 0xB7:
            print("SUBI xx", hex(memory[PC.value].value))
        else:
            print("CMPI xx", hex(memory[PC.value].value))
        value = SUB_8(A.value, memory[PC.value].value)
        if b_val == 0xB7: # SUBI xx
            A.value = value
    # INC R
    elif b_val == 0x03:
        print("INC B")
        INC(B)
    elif b_val == 0x13:
        print("INC C")
        INC(C)
    elif b_val == 0x23:
        print("INC D")
        INC(D)
    elif b_val == 0x33:
        print("INC E")
        INC(E)
    elif b_val == 0x43:
        print("INC H")
        INC(H)
    elif b_val == 0x53:
        print("INC L")
        INC(L)
    elif b_val == 0x63:
        print("INC (HL)", hex(H.value) + hex(L.value)[2:])
        INC(HL, mem=True)
    elif b_val == 0x73:
        print("INC A")
        INC(A)
    # INX RR
    elif b_val == 0xA8:
        print("INX BC")
        BC.getvalue()
        BC.value += 1
        BC.value = BC.value & 0xffff
        BC.setvalue()
    elif b_val == 0xB8:
        print("INX DE")
        DE.getvalue()
        DE.value += 1
        DE.value = DE.value & 0xffff
        DE.setvalue()
    elif b_val == 0xC8:
        print("INX HL")
        HL.getvalue()
        HL.value += 1
        HL.value = HL.value & 0xffff
        HL.setvalue()
    # DEC R
    elif b_val == 0x07:
        print("DEC B")
        DEC(B)
    elif b_val == 0x17:
        print("DEC C")
        DEC(C)
    elif b_val == 0x27:
        print("DEC D")
        DEC(D)
    elif b_val == 0x37:
        print("DEC E")
        DEC(E)
    elif b_val == 0x47:
        print("DEC H")
        DEC(H)
    elif b_val == 0x57:
        print("DEC L")
        DEC(L)
    elif b_val == 0x67:
        print("DEC (HL)", hex(H.value) + hex(L.value)[2:])
        DEC(HL, mem=True)
    elif b_val == 0x77:
        print("DEC A")
        DEC(A)
    # AND R
    elif b_val == 0x05:
        print("AND B")
        AND_R(B)
    elif b_val == 0x15:
        print("AND C")
        AND_R(C)
    elif b_val == 0x25:
        print("AND D")
        AND_R(D)
    elif b_val == 0x35:
        print("AND E")
        AND_R(E)
    elif b_val == 0x45:
        print("AND H")
        AND_R(H)
    elif b_val == 0x55:
        print("AND L")
        AND_R(L)
    elif b_val == 0x65:
        print("AND (HL)", hex(H.value) + hex(L.value)[2:])
        AND_R(HL, mem=True)
    elif b_val == 0x75:
        print("AND A")
        AND_R(A)
    # ANDI xx
    elif b_val == 0xC7:
        PC.inc()
        print("ANDI xx", hex(memory[PC.value].value))
        value = AND_8(memory[PC.value].value, A.value)
        A.value = value
    # OR R
    elif b_val == 0x85:
        print("OR B")
        OR_R(B)
    elif b_val == 0x95:
        print("OR C")
        OR_R(C)
    elif b_val == 0xA5:
        print("OR D")
        OR_R(D)
    elif b_val == 0xB5:
        print("OR E")
        OR_R(E)
    elif b_val == 0xC5:
        print("OR H")
        OR_R(H)
    elif b_val == 0xD5:
        print("OR L")
        OR_R(L)
    elif b_val == 0xE5:
        print("OR (HL)", hex(H.value) + hex(L.value)[2:])
        OR_R(HL, mem=True)
    elif b_val == 0xF5:
        print("OR A")
        OR_R(A)
    # ORI xx
    elif b_val == 0xD7:
        PC.inc()
        print("ORI xx", hex(memory[PC.value].value))
        value = OR_8(memory[PC.value].value, A.value)
        A.value = value
    # XOR R
    elif b_val == 0x06:
        print("XOR B")
        XOR_R(B)
    elif b_val == 0x16:
        print("XOR C")
        XOR_R(C)
    elif b_val == 0x26:
        print("XOR D")
        XOR_R(D)
    elif b_val == 0x36:
        print("XOR E")
        XOR_R(E)
    elif b_val == 0x46:
        print("XOR H")
        XOR_R(H)
    elif b_val == 0x56:
        print("XOR L")
        XOR_R(L)
    elif b_val == 0x66:
        print("XOR (HL)", hex(H.value) + hex(L.value)[2:])
        XOR_R(HL, mem=True)
    elif b_val == 0x76:
        print("XOR A")
        XOR_R(A)
    # XORI xx
    elif b_val == 0xE7:
        PC.inc()
        print("XORI xx", hex(memory[PC.value].value))
        value = XOR_8(memory[PC.value].value, A.value)
        A.value = value
    # CMPS R
    elif b_val == 0x0D:
        print("CMPS B")
        CMPS(B)
    elif b_val == 0x1D:
        print("CMPS C")
        CMPS(C)
    elif b_val == 0x2D:
        print("CMPS D")
        CMPS(D)
    elif b_val == 0x3D:
        print("CMPS E")
        CMPS(E)
    elif b_val == 0x4D:
        print("CMPS H")
        CMPS(H)
    elif b_val == 0x5D:
        print("CMPS L")
        CMPS(L)
    elif b_val == 0x6D:
        print("CMPS (HL)", hex(H.value) + hex(L.value)[2:])
        CMPS(HL, mem=True)
    elif b_val == 0x7D:
        print("CMPS A")
        CMPS(A)
    # SIN
    elif b_val == 0xE0:
        print("SIN")
        # TODO: IMPLEMENT SERIAL IN (maybe sockets)
        pass
    # SOUT
    elif b_val == 0xE1:
        print("SOUT")
        # TODO: IMPLEMENT SERIAL OUT (maybe sockets)
        print(chr(A.value))
        pass
    # CLRSCR
    elif b_val == 0xF0:
        print("CLRSCR")
        screen_clear()
    # DRAW
    elif b_val == 0xF1:
        print("DRAW")
        x = C.value
        if x & 0b10000000:
            x = - ((0x100 - x) & 0xff)
        y = B.value
        if y & 0b10000000:
            y = - ((0x100 - y) & 0xff)
        screen_draw_line(x, y, A.value & 0xff)
    # JMP xxyy
    elif b_val == 0x0F:
        print("JMP xxyy", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        JUMP()
    # JMPcc xxyy
    elif b_val == 0x1F:
        print("JMPZ xxyy", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        if FL.z:
            JUMP()
        else:
            PC.inc(2)
    elif b_val == 0x2F:
        print("JMPNZ xxyy", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        if not FL.z:
            JUMP()
        else:
            PC.inc(2)
    elif b_val == 0x3F:
        print("JMPN xxyy", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        if FL.n:
            JUMP()
        else:
            PC.inc(2)
    elif b_val == 0x4F:
        print("JMPNN xxyy", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        if not FL.n:
            JUMP()
        else:
            PC.inc(2)
    elif b_val == 0x5F:
        print("JMPH xxyy", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        if FL.h:
            JUMP()
    elif b_val == 0x6F:
        print("JMPNH xxyy", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        if not FL.h:
            JUMP()
        else:
            PC.inc(2)
    elif b_val == 0x7F:
        print("JMPC xxyy", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        if FL.c:
            JUMP()
        else:
            PC.inc(2)
    elif b_val == 0x8F:
        print("JMPNC xxyy", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        if not FL.c:
            JUMP()
        else:
            PC.inc(2)
    # JMP xx
    elif b_val == 0x9F:
        print("JMP xx", hex(memory[PC.value+1].value))
        REL_JUMP()
    # JMPcc xx
    elif b_val == 0xAF:
        print("JMPZ xx", hex(memory[PC.value+1].value))
        if FL.z:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xBF:
        print("JMPNZ xx", hex(memory[PC.value+1].value))
        if not FL.z:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xCF:
        print("JMPN xx", hex(memory[PC.value+1].value))
        if FL.n:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xDF:
        print("JMPNN xx", hex(memory[PC.value+1].value))
        if not FL.n:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xEF:
        print("JMPH xx", hex(memory[PC.value+1].value))
        if FL.h:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xFF:
        print("JMPNH xx", hex(memory[PC.value+1].value))
        if not FL.h:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xEE:
        print("JMPC xx", hex(memory[PC.value+1].value))
        if FL.c:
            REL_JUMP()
        else:
            PC.inc()
    elif b_val == 0xFE:
        print("JMPNC xx", hex(memory[PC.value+1].value))
        if not FL.c:
            REL_JUMP()
        else:
            PC.inc()
    # CALL xxyy
    elif b_val == 0x1E:
        print("CALL xxyy", hex(memory[PC.value + 2].value) + hex(memory[PC.value + 1].value)[2:])
        memory[SP.value].value = (PC.value+3) & 0xff
        memory[SP.value + 1].value = (PC.value+3) >> 8
        SP.dec()
        JUMP()
    # RET
    elif b_val == 0x0E:
        print("RET")
        SP.inc()
        PC.value = memory[SP.value].value + (memory[SP.value + 1].value << 8)
        jumped = True
    # NOP
    elif b_val == 0x00:
        print("NOP")
        pass
    else:
        print("UNKNOWN:",hex(b_val),"@",hex(PC.value))
        input()

    if debug:
        BC.getvalue()
        DE.getvalue()
        HL.getvalue()
        print("A:",hex(A.value),"B:",hex(B.value),"C:",hex(C.value),"D:",hex(D.value),"E:",hex(E.value),"H:",hex(H.value),
                "L:",hex(L.value),"BC:",hex(BC.value),"DE:",hex(DE.value),"HL:",hex(HL.value),"PC:",hex(PC.value),"SP:",hex(SP.value),"F:",FL.str)

    if not jumped:
        PC.inc()
    else:
        pass
        #print("JUMPED")
