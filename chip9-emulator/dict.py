REGISTERS = [B, C, D, E, H, L, HL, A]
D_REGISTERS = [BC, DE, HL, SP]
LDI_R_OPCODES = [0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80, 0x90]
LDX_RR_OPCODES = [0x21, 0x31, 0x41, 0x22]
PUSH_R_OPCODES = [0x81, 0x91, 0xA1, 0xB1, 0xC1, 0xD1, 0xC0, 0xD0]
PUSH_RR_OPCODES = [0x51, 0x61, 0x71]
POP_R_OPCODES = [0x82, 0x92, 0xA2, 0xB2, 0xC2, 0xD2, 0xC3, 0xD3]
POP_RR_OPCODES = [0x52, 0x62, 0x72]
MOVB_OPCODES = [0x09, 0x19, 0x29, 0x39, 0x49, 0x59, 0x69, 0x79]
MOVC_OPCODES = [0x99, 0x99, 0xA9, 0xB9, 0xC9, 0xD9, 0xE9, 0xF9]
MOVD_OPCODES = [0x0A, 0x1A, 0x2A, 0x3A, 0x4A, 0x5A, 0x6A, 0x7A]
MOVE_OPCODES = [0x8A, 0x9A, 0xAA, 0xBA, 0xCA, 0xDA, 0xEA, 0xFA]
MOVH_OPCODES = [0x0B, 0x1B, 0x2B, 0x3B, 0x4B, 0x5B, 0x6B, 0x7B]
MOVL_OPCODES = [0x8B, 0x9B, 0xAB, 0xBB, 0xCB, 0xDB, 0xEB, 0xFB]
MOVMHL_OPCODES = [0x0C, 0x1C, 0x2C, 0x3C, 0x4C, 0x5C, 0x6C, 0x7C]
MOVA_OPCODES = [0x8C, 0x9C, 0xAC, 0xBC, 0xCC, 0xDC, 0xEC, 0xFC]
MOV_RR_OPCODES = [0xED, 0xFD]
ADD_R_OPCODES = [0x04, 0x14, 0x24, 0x34, 0x44, 0x54, 0x64, 0x74]
ADDX_RR_OPCODES = [0x83, 0x93, 0xA3]
SUB_R_OPCODES = [0x84, 0x94, 0xA4, 0xB4, 0xC4, 0xD4, 0xE4, 0xF4]
CMP_R_OPCODES = [0x86, 0x96, 0xA6, 0xB6, 0xC6, 0xD6, 0xE6, 0xF6]
INC_R_OPCODES = [0x03, 0x13, 0x23, 0x33, 0x43, 0x53, 0x63, 0x73]
INX_RR_OPCODES = [0xA8, 0xB8, 0xC8]
DEC_R_OPCODES = [0x07, 0x17, 0x27, 0x37, 0x47, 0x57, 0x67, 0x77]
AND_R_OPCODES = [0x05, 0x15, 0x25, 0x35, 0x45, 0x55, 0x65, 0x75]
OR_R_OPCODES = [0x85, 0x95, 0xA5, 0xB5, 0xC5, 0xD5, 0xE5, 0xF5]
XOR_R_OPCODES = [0x06, 0x16, 0x26, 0x36, 0x46, 0x56, 0x66, 0x76]
CMPS_R_OPCODES = [0x0D, 0x1D, 0x2D, 0x3D, 0x4D, 0x5D, 0x6D, 0x7D]
CJUMP_OPCODES = [0x1F, 0x2F, 0x3F, 0x4F, 0x5F, 0x6F, 0x7F, 0x8F]
CRJUMP_OPCODES = [0xAF, 0xBF, 0xCF, 0xDF, 0xEF, 0xFF, 0xEE, 0xFE]

# LDI R, xx
def _LDI_R(opcode):
    LDI(REGISTERS[LDI_R_OPCODES.index(opcode)], opcode == 0x80)
# LDX RR, xxyy
def _LDX_RR(opcode):
    LDX(D_REGISTERS[LDX_RR_OPCODES.index(opcode)])
# PUSH R
def _PUSH_R(opcode):
    PUSH_R(REGISTERS[PUSH_R_OPCODES.index(opcode)], opcode == 0xC0)
# PUSH RR
def _PUSH_RR(opcode):
    PUSH_RR(D_REGISTERS[PUSH_RR_OPCODES.index(opcode)])
# POP R
def _POP_R(opcode):
    POP_R(REGISTERS[POP_R_OPCODES.index(opcode)], opcode == 0xC3)
# POP RR
def _POP_RR(opcode):
    POP_RR(D_REGISTERS[POP_RR_OPCODES.index(opcode)])
# MOV R1, R2
def MOVB(opcode):
    MOV(B, MOVB_OPCODES.index(opcode))
def MOVC(opcode):
    MOV(C, MOVC_OPCODES.index(opcode))
def MOVD(opcode):
    MOV(D, MOVD_OPCODES.index(opcode))
def MOVE(opcode):
    MOV(E, MOVE_OPCODES.index(opcode))
def MOVH(opcode):
    MOV(H, MOVH_OPCODES.index(opcode))
def MOVL(opcode):
    MOV(L, MOVL_OPCODES.index(opcode))
def MOVHL(opcode):
    MOV(HL, MOVMHL_OPCODES.index(b_val), mem=True)
def MOVA(opcode):
    MOV(A, MOVA_OPCODES.index(opcode))
# MOV RR1, RR2
def _MOV_RR(opcode):
    MOV_RR(HL, D_REGISTERS[MOV_RR_OPCODES.index(opcode)])
# CLRFLAG
def CLRFLAG(opcode):
    FL.clearFlags()
# SETFLAG f, x
def F_Z1(opcode):
    FL.setZero()
def F_Z0(opcode):
    FL.clearZero()
def F_N1(opcode):
    FL.setNeg()
def F_N0(opcode):
    FL.clearNeg()
def F_H1(opcode):
    FL.setHalf()
def F_H0(opcode):
    FL.clearHalf()
def F_C1(opcode):
    FL.setCarry()
def F_C0(opcode):
    FL.clearCarry()
# ADD R
def _ADD_R(opcode):
    ADD_R(REGISTERS[ADD_R_OPCODES.index(opcode)], opcode == 0x64)
# ADDI xx
def ADDI(opcode):
    PC.inc()
    value = ADD_8(A.value, memory[PC.value].value)
    A.value = value
# ADDX RR
def _ADDX_RR(opcode):
    ADDX_RR(D_REGISTERS[ADDX_RR_OPCODES.index(opcode)])
# SUB R
def _SUB_R(opcode):
    SUB_R(REGISTERS[SUB_R_OPCODES.index(opcode)], False, opcode==0xE4)
# CMP R
def CMP_R(opcode):
    SUB_R(REGISTERS[CMP_R_OPCODES.index(opcode)], True, opcode==0xE6)
# SUBI xx | CMPI xx
def SUBI_CMPI(opcode):
    PC.inc()
    value = SUB_8(A.value, memory[PC.value].value)
    if opcode == 0xB7: # SUBI xx
        A.value = value
# INC R
def INC_R(opcode):
    INC(REGISTERS[INC_R_OPCODES.index(opcode)], opcode == 0x63)
# INX RR
def INX_RR(opcode):
    RR = D_REGISTERS[INX_RR_OPCODES.index(opcode)]
    RR.getvalue()
    RR.value += 1
    RR.value & 0xffff
    RR.setvalue()
# DEC R
def DEC_R(opcode):
    DEC(REGISTERS[DEC_R_OPCODES.index(opcode)], opcode == 0x67)
# AND R
def _AND_R(opcode):
    AND_R(REGISTERS[AND_R_OPCODES.index(opcode)], opcode == 0x65)
# ANDI xx
def ANDI(opcode):
    PC.inc()
    value = AND_8(A.value, memory[PC.value].value)
    A.value = value
# OR R
def _OR_R(opcode):
    OR_R(REGISTERS[OR_R_OPCODES.index(opcode)], opcode == 0xE5)
# ORI xx
def ORI(opcode):
    PC.inc()
    value = OR_8(A.value, memory[PC.value].value)
    A.value = value
# XOR R
def _XOR_R(opcode):
    XOR_R(REGISTERS[XOR_R_OPCODES.index(opcode)], opcode == 0x66)
# ANDI xx
def XORI(opcode):
    PC.inc()
    value = XOR_8(A.value, memory[PC.value].value)
    A.value = value
# CMPS R
def CMPS_R(opcode):
    CMPS(REGISTERS[CMPS_R_OPCODES.index(opcode)], opcode == 0x6D)
# SIN
def SIN(opcode):
    A.value = ord(sys.stdin.buffer.read(1)) & 0xff
# SOUT
def SOUT(opcode):
    print(chr(A.value),end="",flush=True)
# CLRSCR
def CLRSCR(opcode):
    screen_clear()
# DRAW
def DRAW(opcode):
    x = C.value
    if x & 0b10000000:
        x = - ((0x100 - x) & 0xff)
    y = B.value
    if y & 0b10000000:
        y = - ((0x100 - y) & 0xff)
    screen_draw_line(x, y, A.value & 0xff)
# JMP xxyy
def _JUMP(opcode):
    JUMP()
# JMPcc xxyy
def CJUMP(opcode):
    conditions = [FL.z, not FL.z, FL.n, not FL.n, FL.h, not FL.h, FL.c, not FL.c]
    if conditions[CJUMP_OPCODES.index(opcode)]:
        JUMP()
    else:
        PC.inc(2)
# JMP xx
def _RJUMP(opcode):
    REL_JUMP()
# JMPcc xx
def CRJUMP(opcode):
    conditions = [FL.z, not FL.z, FL.n, not FL.n, FL.h, not FL.h, FL.c, not FL.c]
    if conditions[CRJUMP_OPCODES.index(opcode)]:
        REL_JUMP()
    else:
        PC.inc()
# CALL xxyy
def CALL(opcode):
    memory[SP.value].value = (PC.value+3) & 0xff
    memory[SP.value + 1].value = (PC.value+3) >> 8
    SP.dec()
    JUMP()
# RET
def RET(opcode):
    SP.inc()
    PC.value = memory[SP.value].value + (memory[SP.value + 1].value << 8)
    global jumped
    jumped = True
# NOP
def NOP(opcode):
    pass
# UNKNOWN_OPCODE
def UNKNOWN_OPCODE(opcode):
    pass


opcode_dict = { 0x20:_LDI_R, 0x30:_LDI_R, 0x40:_LDI_R, 0x50:_LDI_R,
                0x60:_LDI_R, 0x70:_LDI_R, 0x80:_LDI_R, 0x90:_LDI_R,
                0x21:_LDX_RR, 0x31:_LDX_RR, 0x41:_LDX_RR, 0x22:_LDX_RR,
                0x81:_PUSH_R, 0x91:_PUSH_R, 0xA1:_PUSH_R, 0xB1:_PUSH_R,
                0xC1:_PUSH_R, 0xD1:_PUSH_R, 0xC0:_PUSH_R, 0xD0:_PUSH_R,
                0x51:_PUSH_RR, 0x61:_PUSH_RR, 0x71:_PUSH_RR,
                0x82:_POP_R, 0x92:_POP_R, 0xA2:_POP_R, 0xB2:_POP_R,
                0xC2:_POP_R, 0xD2:_POP_R, 0xC3:_POP_R, 0xD3:_POP_R,
                0x52:_POP_RR, 0x62:_POP_RR, 0x72:_POP_RR, 0x72:_POP_RR,
                0x09:MOVB, 0x19:MOVB, 0x29:MOVB, 0x39:MOVB,
                0x49:MOVB, 0x59:MOVB, 0x69:MOVB, 0x79:MOVB,
                0x99:MOVC, 0x99:MOVC, 0xA9:MOVC, 0xB9:MOVC,
                0xC9:MOVC, 0xD9:MOVC, 0xE9:MOVC, 0xF9:MOVC,
                0x0A:MOVD, 0x1A:MOVD, 0x2A:MOVD, 0x3A:MOVD,
                0x4A:MOVD, 0x5A:MOVD, 0x6A:MOVD, 0x7A:MOVD,
                0x8A:MOVE, 0x9A:MOVE, 0xAA:MOVE, 0xBA:MOVE,
                0xCA:MOVE, 0xDA:MOVE, 0xEA:MOVE, 0xFA:MOVE,
                0x0B:MOVH, 0x1B:MOVH, 0x2B:MOVH, 0x3B:MOVH,
                0x4B:MOVH, 0x5B:MOVH, 0x6B:MOVH, 0x7B:MOVH,
                0x8B:MOVL, 0x9B:MOVL, 0xAB:MOVL, 0xBB:MOVL,
                0xCB:MOVL, 0xDB:MOVL, 0xEB:MOVL, 0xFB:MOVL,
                0x0C:MOVHL, 0x1C:MOVHL, 0x2C:MOVHL, 0x3C:MOVHL,
                0x4C:MOVHL, 0x5C:MOVHL, 0x6C:MOVHL, 0x7C:MOVHL,
                0x8C:MOVA, 0x9C:MOVA, 0xAC:MOVA, 0xBC:MOVA,
                0xCC:MOVA, 0xDC:MOVA, 0xEC:MOVA, 0xFC:MOVA,
                0xED:_MOV_RR, 0xFD:_MOV_RR,
                0x08:CLRFLAG,
                0x18:F_Z1, 0x28:F_Z0, 0x38:F_N1, 0x48:F_N0,
                0x58:F_H1, 0x68:F_H0, 0x78:F_C1, 0x88:F_C0,
                0x04:_ADD_R, 0x14:_ADD_R, 0x24:_ADD_R, 0x34:_ADD_R,
                0x44:_ADD_R, 0x54:_ADD_R, 0x64:_ADD_R, 0x74:_ADD_R,
                0xA7:ADDI,
                0x83:_ADDX_RR, 0x93:_ADDX_RR, 0xA3:_ADDX_RR,
                0x84:_SUB_R, 0x94:_SUB_R, 0xA4:_SUB_R, 0xB4:_SUB_R,
                0xC4:_SUB_R, 0xD4:_SUB_R, 0xE4:_SUB_R, 0xF4:_SUB_R,
                0x86:CMP_R, 0x96:CMP_R, 0xA6:CMP_R, 0xB6:CMP_R,
                0xC6:CMP_R, 0xD6:CMP_R, 0xE6:CMP_R, 0xF6:CMP_R,
                0xB7:SUBI_CMPI, 0xF7:SUBI_CMPI,
                0x03:INC_R, 0x13:INC_R, 0x23:INC_R, 0x33:INC_R,
                0x43:INC_R, 0x53:INC_R, 0x63:INC_R, 0x73:INC_R,
                0xA8:INX_RR, 0xB8:INX_RR, 0xC8:INX_RR,
                0x07:DEC_R, 0x17:DEC_R, 0x27:DEC_R, 0x37:DEC_R,
                0x47:DEC_R, 0x57:DEC_R, 0x67:DEC_R, 0x77:DEC_R,
                0x05:_AND_R, 0x15:_AND_R, 0x25:_AND_R, 0x35:_AND_R,
                0x45:_AND_R, 0x55:_AND_R, 0x65:_AND_R, 0x75:_AND_R,
                0xC7:ANDI,
                0x85:_OR_R, 0x95:_OR_R, 0xA5:_OR_R, 0xB5:_OR_R,
                0xC5:_OR_R, 0xD5:_OR_R, 0xE5:_OR_R, 0xF5:_OR_R,
                0xD7:ORI,
                0x06:_XOR_R, 0x16:_XOR_R, 0x26:_XOR_R, 0x36:_XOR_R,
                0x46:_XOR_R, 0x56:_XOR_R, 0x66:_XOR_R, 0x76:_XOR_R,
                0xE7:XORI,
                0x0D:CMPS_R, 0x1D:CMPS_R, 0x2D:CMPS_R, 0x3D:CMPS_R,
                0x4D:CMPS_R, 0x5D:CMPS_R, 0x6D:CMPS_R, 0x7D:CMPS_R,
                0xE0:SIN,
                0xE1:SOUT,
                0xF0:CLRSCR,
                0xF1:DRAW,
                0x0F:_JUMP,
                0x1F:CJUMP, 0x2F:CJUMP, 0x3F:CJUMP, 0x4F:CJUMP,
                0x5F:CJUMP, 0x6F:CJUMP, 0x7F:CJUMP, 0x8F:CJUMP,
                0x9F:_RJUMP,
                0xAF:CRJUMP, 0xBF:CRJUMP, 0xCF:CRJUMP, 0xDF:CRJUMP,
                0xEF:CRJUMP, 0xFF:CRJUMP, 0xEE:CRJUMP, 0xFE:CRJUMP,
                0x1E:CALL,
                0x0E:RET,
                0x00:NOP
                }