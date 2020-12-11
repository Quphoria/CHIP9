using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CHIP9_C_EMU
{
    class InstructionInfo
    {
        public string Decode(byte b1, byte b2, byte b3)
        {
            string op = "UNKNOWN";
            switch (b1)
            {
                case 0x20:
                    op = "LDI B, 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x30:
                    op = "LDI C, 0x" + Convert.ToString(b2, 16).ToUpper();
                    break;
                case 0x40:
                    op = "LDI D, 0x" + Convert.ToString(b2, 16).ToUpper();
                    break;
                case 0x50:
                    op = "LDI E, 0x" + Convert.ToString(b2, 16).ToUpper();
                    break;
                case 0x60:
                    op = "LDI H, 0x" + Convert.ToString(b2, 16).ToUpper();
                    break;
                case 0x70:
                    op = "LDI L, 0x" + Convert.ToString(b2, 16).ToUpper();
                    break;
                case 0x80:
                    op = "LDI (HL), 0x" + Convert.ToString(b2, 16).ToUpper();
                    break;
                case 0x90:
                    op = "LDI A, 0x" + Convert.ToString(b2, 16).ToUpper();
                    break;
                case 0x21:
                    op = "LDX BC, 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x31:
                    op = "LDX DE, 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x41:
                    op = "LDX HL, 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x22:
                    op = "LDX SP, 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x81:
                    op = "PUSH B";
                    break;
                case 0x91:
                    op = "PUSH C";
                    break;
                case 0xA1:
                    op = "PUSH D";
                    break;
                case 0xB1:
                    op = "PUSH E";
                    break;
                case 0xC1:
                    op = "PUSH H";
                    break;
                case 0xD1:
                    op = "PUSH L";
                    break;
                case 0xC0:
                    op = "PUSH (HL)";
                    break;
                case 0xD0:
                    op = "PUSH A";
                    break;
                case 0x51:
                    op = "PUSH BC";
                    break;
                case 0x61:
                    op = "PUSH DE";
                    break;
                case 0x71:
                    op = "PUSH HL";
                    break;
                case 0x82:
                    op = "POP B";
                    break;
                case 0x92:
                    op = "POP C";
                    break;
                case 0xA2:
                    op = "POP D";
                    break;
                case 0xB2:
                    op = "POP E";
                    break;
                case 0xC2:
                    op = "POP H";
                    break;
                case 0xD2:
                    op = "POP L";
                    break;
                case 0xC3:
                    op = "POP (HL)";
                    break;
                case 0xD3:
                    op = "POP A";
                    break;
                case 0x52:
                    op = "POP BC";
                    break;
                case 0x62:
                    op = "POP DE";
                    break;
                case 0x72:
                    op = "POP HL";
                    break;
                case 0x09:
                    op = "MOV B, B";
                    break;
                case 0x19:
                    op = "MOV B, C";
                    break;
                case 0x29:
                    op = "MOV B, D";
                    break;
                case 0x39:
                    op = "MOV B, E";
                    break;
                case 0x49:
                    op = "MOV B, H";
                    break;
                case 0x59:
                    op = "MOV B, L";
                    break;
                case 0x69:
                    op = "MOV B, (HL)";
                    break;
                case 0x79:
                    op = "MOV B, A";
                    break;
                case 0x89:
                    op = "MOV C, B";
                    break;
                case 0x99:
                    op = "MOV C, C";
                    break;
                case 0xA9:
                    op = "MOV C, D";
                    break;
                case 0xB9:
                    op = "MOV C, E";
                    break;
                case 0xC9:
                    op = "MOV C, H";
                    break;
                case 0xD9:
                    op = "MOV C, L";
                    break;
                case 0xE9:
                    op = "MOV C, (HL)";
                    break;
                case 0xF9:
                    op = "MOV C, A";
                    break;
                case 0x0A:
                    op = "MOV D, B";
                    break;
                case 0x1A:
                    op = "MOV D, C";
                    break;
                case 0x2A:
                    op = "MOV D, D";
                    break;
                case 0x3A:
                    op = "MOV D, E";
                    break;
                case 0x4A:
                    op = "MOV D, H";
                    break;
                case 0x5A:
                    op = "MOV D, L";
                    break;
                case 0x6A:
                    op = "MOV D, (HL)";
                    break;
                case 0x7A:
                    op = "MOV D, A";
                    break;
                case 0x8A:
                    op = "MOV E, B";
                    break;
                case 0x9A:
                    op = "MOV E, C";
                    break;
                case 0xAA:
                    op = "MOV E, D";
                    break;
                case 0xBA:
                    op = "MOV E, E";
                    break;
                case 0xCA:
                    op = "MOV E, H";
                    break;
                case 0xDA:
                    op = "MOV E, L";
                    break;
                case 0xEA:
                    op = "MOV E, (HL)";
                    break;
                case 0xFA:
                    op = "MOV E, A";
                    break;
                case 0x0B:
                    op = "MOV H, B";
                    break;
                case 0x1B:
                    op = "MOV H, C";
                    break;
                case 0x2B:
                    op = "MOV H, D";
                    break;
                case 0x3B:
                    op = "MOV H, E";
                    break;
                case 0x4B:
                    op = "MOV H, H";
                    break;
                case 0x5B:
                    op = "MOV H, L";
                    break;
                case 0x6B:
                    op = "MOV H, (HL)";
                    break;
                case 0x7B:
                    op = "MOV H, A";
                    break;
                case 0x8B:
                    op = "MOV L, B";
                    break;
                case 0x9B:
                    op = "MOV L, C";
                    break;
                case 0xAB:
                    op = "MOV L, D";
                    break;
                case 0xBB:
                    op = "MOV L, E";
                    break;
                case 0xCB:
                    op = "MOV L, H";
                    break;
                case 0xDB:
                    op = "MOV L, L";
                    break;
                case 0xEB:
                    op = "MOV L, (HL)";
                    break;
                case 0xFB:
                    op = "MOV L, A";
                    break;
                case 0x0C:
                    op = "MOV (HL), B";
                    break;
                case 0x1C:
                    op = "MOV (HL), C";
                    break;
                case 0x2C:
                    op = "MOV (HL), D";
                    break;
                case 0x3C:
                    op = "MOV (HL), E";
                    break;
                case 0x4C:
                    op = "MOV (HL), H";
                    break;
                case 0x5C:
                    op = "MOV (HL), L";
                    break;
                case 0x6C:
                    op = "HALT and CATCH FIRE";
                    break;
                case 0x7C:
                    op = "MOV (HL), A";
                    break;
                case 0x8C:
                    op = "MOV A, B";
                    break;
                case 0x9C:
                    op = "MOV A, C";
                    break;
                case 0xAC:
                    op = "MOV A, D";
                    break;
                case 0xBC:
                    op = "MOV A, E";
                    break;
                case 0xCC:
                    op = "MOV A, H";
                    break;
                case 0xDC:
                    op = "MOV A, L";
                    break;
                case 0xEC:
                    op = "MOV A, (HL)";
                    break;
                case 0xFC:
                    op = "MOV A, A";
                    break;
                case 0xED:
                    op = "MOV HL, BC";
                    break;
                case 0xFD:
                    op = "MOV HL, DE";
                    break;
                case 0x08:
                    op = "CLRFLAG";
                    break;
                case 0x18:
                    op = "SETFLAG Z, 1";
                    break;
                case 0x28:
                    op = "SETFLAG Z, 0";
                    break;
                case 0x38:
                    op = "SETFLAG N, 1";
                    break;
                case 0x48:
                    op = "SETFLAG N, 0";
                    break;
                case 0x58:
                    op = "SETFLAG H, 1";
                    break;
                case 0x68:
                    op = "SETFLAG H, 0";
                    break;
                case 0x78:
                    op = "SETFLAG C, 1";
                    break;
                case 0x88:
                    op = "SETFLAG C, 0";
                    break;
                case 0x04:
                    op = "ADD B";
                    break;
                case 0x14:
                    op = "ADD C";
                    break;
                case 0x24:
                    op = "ADD D";
                    break;
                case 0x34:
                    op = "ADD E";
                    break;
                case 0x44:
                    op = "ADD H";
                    break;
                case 0x54:
                    op = "ADD L";
                    break;
                case 0x64:
                    op = "ADD (HL)";
                    break;
                case 0x74:
                    op = "ADD A";
                    break;
                case 0xA7:
                    op = "ADDI 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x83:
                    op = "ADDX BC";
                    break;
                case 0x93:
                    op = "ADDX DE";
                    break;
                case 0xA3:
                    op = "ADDX HL";
                    break;
                case 0x84:
                    op = "SUB B";
                    break;
                case 0x94:
                    op = "SUB C";
                    break;
                case 0xA4:
                    op = "SUB D";
                    break;
                case 0xB4:
                    op = "SUB E";
                    break;
                case 0xC4:
                    op = "SUB H";
                    break;
                case 0xD4:
                    op = "SUB L";
                    break;
                case 0xE4:
                    op = "SUB (HL)";
                    break;
                case 0xF4:
                    op = "SUB A";
                    break;
                case 0xB7:
                    op = "SUBI 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x03:
                    op = "INC B";
                    break;
                case 0x13:
                    op = "INC C";
                    break;
                case 0x23:
                    op = "INC D";
                    break;
                case 0x33:
                    op = "INC E";
                    break;
                case 0x43:
                    op = "INC H";
                    break;
                case 0x53:
                    op = "INC L";
                    break;
                case 0x63:
                    op = "INC (HL)";
                    break;
                case 0x73:
                    op = "INC A";
                    break;
                case 0xA8:
                    op = "INX BC";
                    break;
                case 0xB8:
                    op = "INX DE";
                    break;
                case 0xC8:
                    op = "INX HL";
                    break;
                case 0x07:
                    op = "DEC B";
                    break;
                case 0x17:
                    op = "DEC C";
                    break;
                case 0x27:
                    op = "DEC D";
                    break;
                case 0x37:
                    op = "DEC E";
                    break;
                case 0x47:
                    op = "DEC H";
                    break;
                case 0x57:
                    op = "DEC L";
                    break;
                case 0x67:
                    op = "DEC (HL)";
                    break;
                case 0x77:
                    op = "DEC A";
                    break;
                case 0x05:
                    op = "AND B";
                    break;
                case 0x15:
                    op = "AND C";
                    break;
                case 0x25:
                    op = "AND D";
                    break;
                case 0x35:
                    op = "AND E";
                    break;
                case 0x45:
                    op = "AND H";
                    break;
                case 0x55:
                    op = "AND L";
                    break;
                case 0x65:
                    op = "AND (HL)";
                    break;
                case 0x75:
                    op = "AND A";
                    break;
                case 0xC7:
                    op = "ANDI 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x85:
                    op = "OR B";
                    break;
                case 0x95:
                    op = "OR C";
                    break;
                case 0xA5:
                    op = "OR D";
                    break;
                case 0xB5:
                    op = "OR E";
                    break;
                case 0xC5:
                    op = "OR H";
                    break;
                case 0xD5:
                    op = "OR L";
                    break;
                case 0xE5:
                    op = "OR (HL)";
                    break;
                case 0xF5:
                    op = "OR A";
                    break;
                case 0xD7:
                    op = "ORI 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x06:
                    op = "XOR B";
                    break;
                case 0x16:
                    op = "XOR C";
                    break;
                case 0x26:
                    op = "XOR D";
                    break;
                case 0x36:
                    op = "XOR E";
                    break;
                case 0x46:
                    op = "XOR H";
                    break;
                case 0x56:
                    op = "XOR L";
                    break;
                case 0x66:
                    op = "XOR (HL)";
                    break;
                case 0x76:
                    op = "XOR A";
                    break;
                case 0xE7:
                    op = "XORI 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x86:
                    op = "CMP B";
                    break;
                case 0x96:
                    op = "CMP C";
                    break;
                case 0xA6:
                    op = "CMP D";
                    break;
                case 0xB6:
                    op = "CMP E";
                    break;
                case 0xC6:
                    op = "CMP H";
                    break;
                case 0xD6:
                    op = "CMP L";
                    break;
                case 0xE6:
                    op = "CMP (HL)";
                    break;
                case 0xF6:
                    op = "CMP A";
                    break;
                case 0xF7:
                    op = "CMPI A 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x0D:
                    op = "CMPS B";
                    break;
                case 0x1D:
                    op = "CMPS C";
                    break;
                case 0x2D:
                    op = "CMPS D";
                    break;
                case 0x3D:
                    op = "CMPS E";
                    break;
                case 0x4D:
                    op = "CMPS H";
                    break;
                case 0x5D:
                    op = "CMPS L";
                    break;
                case 0x6D:
                    op = "CMPS (HL)";
                    break;
                case 0x7D:
                    op = "CMPS A";
                    break;
                case 0xE0:
                    op = "SIN";
                    break;
                case 0xE1:
                    op = "SOUT";
                    break;
                case 0xF0:
                    op = "CLRSCR";
                    break;
                case 0xF1:
                    op = "DRAW";
                    break;
                case 0x0F:
                    op = "JMP 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x1F:
                    op = "JMPZ 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x2F:
                    op = "JMPNZ 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x3F:
                    op = "JMPN 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x4F:
                    op = "JMPNN 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x5F:
                    op = "JMPH 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x6F:
                    op = "JMPNH 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x7F:
                    op = "JMPC 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x8F:
                    op = "JMPNC 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x9F:
                    op = "JMP 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0xAF:
                    op = "JMPZ 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0xBF:
                    op = "JMPNZ 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0xCF:
                    op = "JMPN 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0xDF:
                    op = "JMPNN 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0xEF:
                    op = "JMPH 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0xFF:
                    op = "JMPNH 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0xEE:
                    op = "JMPC 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0xFE:
                    op = "JMPNC 0x" + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x1E:
                    op = "CALL 0x" + Convert.ToString(b3, 16).ToUpper().PadLeft(2, '0') + Convert.ToString(b2, 16).ToUpper().PadLeft(2, '0');
                    break;
                case 0x0E:
                    op = "RET";
                    break;
                case 0x00:
                    op = "NOP";
                    break;
                default:
                    op += " " + Convert.ToString(b1, 16).ToUpper().PadLeft(2, '0');
                    break;
            }
            return op;
        }
    }
}
