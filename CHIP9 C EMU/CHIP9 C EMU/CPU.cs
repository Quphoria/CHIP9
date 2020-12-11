using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel;
using System.Threading;
using System.Windows;

namespace CHIP9_C_EMU
{
    class PCreg
    {
        public UInt16 value = 0x0;
        public void Inc(byte length = 1)
        {
            value += length;
        }
        public void Jump(UInt16 address)
        {
            value = address;
        }
    }
    class SPreg
    {
        public UInt16 value = 0xfffe;
        public void Inc()
        {
            value += 2;
        }
        public void Dec()
        {
            value -= 2;
        }
    }
    struct Flags
    {
        public bool z, n, h, c;
        public void Clear()
        {
            z = false;
            n = false;
            h = false;
            c = false;
        }
    }
    class CPU
    {
        public Thread CPUThread;
        public byte A, B, C, D, E, H, L;
        public Flags F;
        public UInt16 BC, DE, HL;
        public PCreg PC;
        public SPreg SP;
        public byte[] memory;
        public bool loadError, romloaded, running, pause, step, halted, jumped, SerialWait, ClearScreen, NewPixels, refreshdelay;
        public byte b1, b2, b3;
        public UInt16 last_instr;
        private byte lower;
        public List<byte[]> pixeldata;
        public List<char> sindata, soutdata;
        public byte buttonstatus;
        int width = 128;
        int height = 64;
        public byte[,] pixels;
        public List<UInt16> breakpoints;
        public int slowdown;
        public CPU()
        {
            A = B = C = D = E = H = L = 0x0;
            F = new Flags();
            BC = 0x0;
            DE = 0x0;
            HL = 0x0;
            PC = new PCreg();
            SP = new SPreg();
            memory = new byte[0x10000];
            pixeldata = new List<byte[]>();
            sindata = new List<char>();
            soutdata = new List<char>();
            buttonstatus = 0x0;
            last_instr = 0x0;
            loadError = false;
            romloaded = false;
            running = false;
            pause = false;
            step = false;
            halted = false;
            jumped = false;
            SerialWait = false;
            ClearScreen = false;
            pixels = new byte[height, width];
            NewPixels = true;
            breakpoints = new List<UInt16>();
            refreshdelay = true;
            slowdown = 15;
            Console.WriteLine("CPU Loaded.");
        }
        public void getBC()
        {
            BC = (UInt16)((B << 8) + C);
        }
        public void setBC()
        {
            B = (byte)(BC >> 8);
            C = (byte)(BC & 0xff);
        }
        public void getDE()
        {
            DE = (UInt16)((D << 8) + E);
        }
        public void setDE()
        {
            D = (byte)(DE >> 8);
            E = (byte)(DE & 0xff);
        }
        public void getHL()
        {
            HL = (UInt16)((H << 8) + L);
        }
        public void setHL()
        {
            H = (byte)(HL >> 8);
            L = (byte)(HL & 0xff);
        }
        public void Kill()
        {
            if (running & !halted)
            {
                //backgroundWorker.CancelAsync();
                halted = true;
                CPUThread.Abort();
            }
        }
        public void RunCPU()
        {
            if (!running & romloaded)
            {
                running = true;
                LaunchThread();
            } else if (!running & !romloaded)
            {
                MessageBoxResult errorBox = MessageBox.Show("Please Load The ROM Files.", "An Error Occurred", MessageBoxButton.OK, MessageBoxImage.Exclamation);
            } else if (running & pause)
            {
                pause = false;
            }
        }
        public void StepCPU()
        {
            if (pause & running)
            {

            } else if (!running)
            {
                pause = true;
                step = true;
                RunCPU();
            }
        }
        public void ClearROM()
        {
            memory = new byte[0x10000];
        }
        public void LoadROM(byte[] rom, UInt16 start_address)
        {
            if (!running & !loadError)
            {
                for (int i = 0; i < rom.Length; i++)
                {
                    int address = start_address + i;
                    if (address >= 0 & address < 0x10000)
                    {
                        memory[address] = rom[i];
                    }
                }
                romloaded = !loadError;
            }
        }
        public void LaunchThread()
        {
            CPUThread = new Thread(this.cpu_thread);
            CPUThread.IsBackground = true;
            CPUThread.Start();
        }
        public void cpu_thread()
        {
            Console.WriteLine("CPU Thread Started.");
            sindata.Clear();
            try
            {
                last_instr = PC.value;
                while (!halted)
                {
                    // Slow it down a bit
                    if (slowdown > 0)
                    {
                        Thread.SpinWait(15*slowdown*slowdown);
                    }
                    step = false;
                    while (pause & !step & !halted)
                    {
                        System.Threading.Thread.Sleep(50);
                    }
                    if (breakpoints.Contains(PC.value))
                    {
                        pause = true;
                    }
                    last_instr = PC.value;
                    b1 = memory[PC.value];
                    //Console.WriteLine(Convert.ToString(b1, 16).ToUpper());
                    if (PC.value + 1 <= 0xffff)
                    {
                        b2 = memory[PC.value + 1];
                        if (PC.value + 2 <= 0xffff)
                        {
                            b3 = memory[PC.value + 2];
                        }
                        else
                        {
                            b3 = 0x0;
                        }
                    }
                    else
                    {
                        b2 = 0x0;
                        b3 = 0x0;
                    }

                    memory[0xf000] = buttonstatus;
                    
                    jumped = false;

                    switch (b1)
                    {
                        case 0x20:
                            PC.Inc();
                            B = memory[PC.value];
                            break;
                        case 0x30:
                            PC.Inc();
                            C = memory[PC.value];
                            break;
                        case 0x40:
                            PC.Inc();
                            D = memory[PC.value];
                            break;
                        case 0x50:
                            PC.Inc();
                            E = memory[PC.value];
                            break;
                        case 0x60:
                            PC.Inc();
                            H = memory[PC.value];
                            break;
                        case 0x70:
                            PC.Inc();
                            L = memory[PC.value];
                            break;
                        case 0x80:
                            PC.Inc();
                            getHL();
                            memory[HL] = memory[PC.value];
                            break;
                        case 0x90:
                            PC.Inc();
                            A = memory[PC.value];
                            break;
                        case 0x21:
                            PC.Inc();
                            lower = memory[PC.value];
                            PC.Inc();
                            BC = (UInt16)((memory[PC.value] << 8) + lower);
                            setBC();
                            break;
                        case 0x31:
                            PC.Inc();
                            lower = memory[PC.value];
                            PC.Inc();
                            DE = (UInt16)((memory[PC.value] << 8) + lower);
                            setDE();
                            break;
                        case 0x41:
                            PC.Inc();
                            lower = memory[PC.value];
                            PC.Inc();
                            HL = (UInt16)((memory[PC.value] << 8) + lower);
                            setHL();
                            break;
                        case 0x22:
                            PC.Inc();
                            lower = memory[PC.value];
                            PC.Inc();
                            SP.value = (UInt16)((memory[PC.value] << 8) + lower);
                            break;
                        case 0x81:
                            memory[SP.value] = B;
                            SP.Dec();
                            break;
                        case 0x91:
                            memory[SP.value] = C;
                            SP.Dec();
                            break;
                        case 0xA1:
                            memory[SP.value] = D;
                            SP.Dec();
                            break;
                        case 0xB1:
                            memory[SP.value] = E;
                            SP.Dec();
                            break;
                        case 0xC1:
                            memory[SP.value] = H;
                            SP.Dec();
                            break;
                        case 0xD1:
                            memory[SP.value] = L;
                            SP.Dec();
                            break;
                        case 0xC0:
                            getHL();
                            memory[SP.value] = memory[HL];
                            SP.Dec();
                            break;
                        case 0xD0:
                            memory[SP.value] = A;
                            SP.Dec();
                            break;
                        case 0x51:
                            memory[SP.value] = C;
                            memory[SP.value + 1] = B;
                            SP.Dec();
                            break;
                        case 0x61:
                            memory[SP.value] = E;
                            memory[SP.value + 1] = D;
                            SP.Dec();
                            break;
                        case 0x71:
                            memory[SP.value] = L;
                            memory[SP.value + 1] = H;
                            SP.Dec();
                            break;
                        case 0x82:
                            SP.Inc();
                            B = memory[SP.value];
                            break;
                        case 0x92:
                            SP.Inc();
                            C = memory[SP.value];
                            break;
                        case 0xA2:
                            SP.Inc();
                            D = memory[SP.value];
                            break;
                        case 0xB2:
                            SP.Inc();
                            E = memory[SP.value];
                            break;
                        case 0xC2:
                            SP.Inc();
                            H = memory[SP.value];
                            break;
                        case 0xD2:
                            SP.Inc();
                            L = memory[SP.value];
                            break;
                        case 0xC3:
                            getHL();
                            SP.Inc();
                            memory[HL] = memory[SP.value];
                            break;
                        case 0xD3:
                            SP.Inc();
                            A = memory[SP.value];
                            break;
                        case 0x52:
                            SP.Inc();
                            C = memory[SP.value];
                            B = memory[SP.value + 1];
                            break;
                        case 0x62:
                            SP.Inc();
                            E = memory[SP.value];
                            D = memory[SP.value + 1];
                            break;
                        case 0x72:
                            SP.Inc();
                            L = memory[SP.value];
                            H = memory[SP.value + 1];
                            break;
                        case 0x09:
                            // MOV B, B
                            break;
                        case 0x19:
                            B = C;
                            break;
                        case 0x29:
                            B = D;
                            break;
                        case 0x39:
                            B = E;
                            break;
                        case 0x49:
                            B = H;
                            break;
                        case 0x59:
                            B = L;
                            break;
                        case 0x69:
                            getHL();
                            B = memory[HL];
                            break;
                        case 0x79:
                            B = A;
                            break;
                        case 0x89:
                            C = B;
                            break;
                        case 0x99:
                            // MOV C, C
                            break;
                        case 0xA9:
                            C = D;
                            break;
                        case 0xB9:
                            C = E;
                            break;
                        case 0xC9:
                            C = H;
                            break;
                        case 0xD9:
                            C = L;
                            break;
                        case 0xE9:
                            getHL();
                            C = memory[HL];
                            break;
                        case 0xF9:
                            C = A;
                            break;
                        case 0x0A:
                            D = B;
                            break;
                        case 0x1A:
                            D = C;
                            break;
                        case 0x2A:
                            // MOV D, D
                            break;
                        case 0x3A:
                            D = E;
                            break;
                        case 0x4A:
                            D = H;
                            break;
                        case 0x5A:
                            D = L;
                            break;
                        case 0x6A:
                            getHL();
                            D = memory[HL];
                            break;
                        case 0x7A:
                            D = A;
                            break;
                        case 0x8A:
                            E = B;
                            break;
                        case 0x9A:
                            E = C;
                            break;
                        case 0xAA:
                            E = D;
                            break;
                        case 0xBA:
                            // MOV E, E
                            break;
                        case 0xCA:
                            E = H;
                            break;
                        case 0xDA:
                            E = L;
                            break;
                        case 0xEA:
                            getHL();
                            E = memory[HL];
                            break;
                        case 0xFA:
                            E = A;
                            break;
                        case 0x0B:
                            H = B;
                            break;
                        case 0x1B:
                            H = C;
                            break;
                        case 0x2B:
                            H = D;
                            break;
                        case 0x3B:
                            H = E;
                            break;
                        case 0x4B:
                            // MOV H, H
                            break;
                        case 0x5B:
                            H = L;
                            break;
                        case 0x6B:
                            getHL();
                            H = memory[HL];
                            break;
                        case 0x7B:
                            H = A;
                            break;
                        case 0x8B:
                            L = B;
                            break;
                        case 0x9B:
                            L = C;
                            break;
                        case 0xAB:
                            L = D;
                            break;
                        case 0xBB:
                            L = E;
                            break;
                        case 0xCB:
                            L = H;
                            break;
                        case 0xDB:
                            // MOV L, L
                            break;
                        case 0xEB:
                            getHL();
                            L = memory[HL];
                            break;
                        case 0xFB:
                            L = A;
                            break;
                        case 0x0C:
                            getHL();
                            memory[HL] = B;
                            break;
                        case 0x1C:
                            getHL();
                            memory[HL] = C;
                            break;
                        case 0x2C:
                            getHL();
                            memory[HL] = D;
                            break;
                        case 0x3C:
                            getHL();
                            memory[HL] = E;
                            break;
                        case 0x4C:
                            getHL();
                            memory[HL] = H;
                            break;
                        case 0x5C:
                            getHL();
                            memory[HL] = L;
                            break;
                        case 0x6C:
                            halted = true;
                            break;
                        case 0x7C:
                            getHL();
                            memory[HL] = A;
                            break;
                        case 0x8C:
                            A = B;
                            break;
                        case 0x9C:
                            A = C;
                            break;
                        case 0xAC:
                            A = D;
                            break;
                        case 0xBC:
                            A = E;
                            break;
                        case 0xCC:
                            A = H;
                            break;
                        case 0xDC:
                            A = L;
                            break;
                        case 0xEC:
                            getHL();
                            A = memory[HL];
                            break;
                        case 0xFC:
                            // MOV A, A
                            break;
                        case 0xED:
                            getBC();
                            HL = BC;
                            setHL();
                            break;
                        case 0xFD:
                            getDE();
                            HL = DE;
                            setHL();
                            break;
                        case 0x08:
                            F.Clear();
                            break;
                        case 0x18:
                            F.z = true;
                            break;
                        case 0x28:
                            F.z = false;
                            break;
                        case 0x38:
                            F.n = true;
                            break;
                        case 0x48:
                            F.n = false;
                            break;
                        case 0x58:
                            F.h = true;
                            break;
                        case 0x68:
                            F.h = false;
                            break;
                        case 0x78:
                            F.c = true;
                            break;
                        case 0x88:
                            F.c = false;
                            break;
                        case 0x04:
                            B = Add(A, B);
                            break;
                        case 0x14:
                            C = Add(A, C);
                            break;
                        case 0x24:
                            D = Add(A, D);
                            break;
                        case 0x34:
                            E = Add(A, E);
                            break;
                        case 0x44:
                            H = Add(A, H);
                            break;
                        case 0x54:
                            L = Add(A, L);
                            break;
                        case 0x64:
                            getHL();
                            memory[HL] = Add(A, memory[HL]);
                            break;
                        case 0x74:
                            A = Add(A, A);
                            break;
                        case 0xA7:
                            PC.Inc();
                            A = Add(A, memory[PC.value]);
                            break;
                        case 0x83:
                            getBC();
                            BC = Add16(BC, A);
                            setBC();
                            break;
                        case 0x93:
                            getDE();
                            DE = Add16(DE, A);
                            setDE();
                            break;
                        case 0xA3:
                            getHL();
                            HL = Add16(HL, A);
                            setHL();
                            break;
                        case 0x84:
                            B = Sub(B, A);
                            break;
                        case 0x94:
                            C = Sub(C, A);
                            break;
                        case 0xA4:
                            D = Sub(D, A);
                            break;
                        case 0xB4:
                            E = Sub(E, A);
                            break;
                        case 0xC4:
                            H = Sub(H, A);
                            break;
                        case 0xD4:
                            L = Sub(L, A);
                            break;
                        case 0xE4:
                            getHL();
                            memory[HL] = Sub(memory[HL], A);
                            break;
                        case 0xF4:
                            A = Sub(A, A);
                            break;
                        case 0xB7:
                            PC.Inc();
                            A = Sub(A, memory[PC.value]);
                            break;
                        case 0x03:
                            B = Inc(B);
                            break;
                        case 0x13:
                            C = Inc(C);
                            break;
                        case 0x23:
                            D = Inc(D);
                            break;
                        case 0x33:
                            E = Inc(E);
                            break;
                        case 0x43:
                            H = Inc(H);
                            break;
                        case 0x53:
                            L = Inc(L);
                            break;
                        case 0x63:
                            getHL();
                            memory[HL] = Inc(memory[HL]);
                            break;
                        case 0x73:
                            A = Inc(A);
                            break;
                        case 0xA8:
                            getBC();
                            BC = Inc16(BC);
                            setBC();
                            break;
                        case 0xB8:
                            getDE();
                            DE = Inc16(DE);
                            setDE();
                            break;
                        case 0xC8:
                            getHL();
                            HL = Inc16(HL);
                            setHL();
                            break;
                        case 0x07:
                            B = Dec(B);
                            break;
                        case 0x17:
                            C = Dec(C);
                            break;
                        case 0x27:
                            D = Dec(D);
                            break;
                        case 0x37:
                            E = Dec(E);
                            break;
                        case 0x47:
                            H = Dec(H);
                            break;
                        case 0x57:
                            L = Dec(L);
                            break;
                        case 0x67:
                            getHL();
                            memory[HL] = Dec(memory[HL]);
                            break;
                        case 0x77:
                            A = Dec(A);
                            break;
                        case 0x05:
                            B = And8(A, B);
                            break;
                        case 0x15:
                            C = And8(A, C);
                            break;
                        case 0x25:
                            D = And8(A, D);
                            break;
                        case 0x35:
                            E = And8(A, E);
                            break;
                        case 0x45:
                            H = And8(A, H);
                            break;
                        case 0x55:
                            L = And8(A, L);
                            break;
                        case 0x65:
                            getHL(); ;
                            memory[HL] = And8(A, memory[HL]);
                            break;
                        case 0x75:
                            A = And8(A, A);
                            break;
                        case 0xC7:
                            PC.Inc();
                            A = And8(A, memory[PC.value]);
                            break;
                        case 0x85:
                            B = Or8(A, B);
                            break;
                        case 0x95:
                            C = Or8(A, C);
                            break;
                        case 0xA5:
                            D = Or8(A, D);
                            break;
                        case 0xB5:
                            E = Or8(A, E);
                            break;
                        case 0xC5:
                            H = Or8(A, H);
                            break;
                        case 0xD5:
                            L = Or8(A, L);
                            break;
                        case 0xE5:
                            getHL();
                            memory[HL] = Or8(A, memory[HL]);
                            break;
                        case 0xF5:
                            A = Or8(A, A);
                            break;
                        case 0xD7:
                            PC.Inc();
                            A = Or8(A, memory[PC.value]);
                            break;
                        case 0x06:
                            B = Xor8(A, B);
                            break;
                        case 0x16:
                            C = Xor8(A, C);
                            break;
                        case 0x26:
                            D = Xor8(A, D);
                            break;
                        case 0x36:
                            E = Xor8(A, E);
                            break;
                        case 0x46:
                            H = Xor8(A, H);
                            break;
                        case 0x56:
                            L = Xor8(A, L);
                            break;
                        case 0x66:
                            getHL();
                            memory[HL] = Xor8(A, memory[HL]);
                            break;
                        case 0x76:
                            A = Xor8(A, A);
                            break;
                        case 0xE7:
                            PC.Inc();
                            A = Xor8(A, memory[PC.value]);
                            break;
                        case 0x86:
                            Sub(B, A);
                            break;
                        case 0x96:
                            Sub(C, A);
                            break;
                        case 0xA6:
                            Sub(D, A);
                            break;
                        case 0xB6:
                            Sub(E, A);
                            break;
                        case 0xC6:
                            Sub(H, A);
                            break;
                        case 0xD6:
                            Sub(L, A);
                            break;
                        case 0xE6:
                            getHL();
                            Sub(memory[HL], A);
                            break;
                        case 0xF6:
                            Sub(A, A);
                            break;
                        case 0xF7:
                            PC.Inc();
                            Sub(A, memory[PC.value]);
                            break;
                        case 0x0D:
                            CMPS(A, B);
                            break;
                        case 0x1D:
                            CMPS(A, C);
                            break;
                        case 0x2D:
                            CMPS(A, D);
                            break;
                        case 0x3D:
                            CMPS(A, E);
                            break;
                        case 0x4D:
                            CMPS(A, H);
                            break;
                        case 0x5D:
                            CMPS(A, L);
                            break;
                        case 0x6D:
                            getHL();
                            CMPS(A, memory[HL]);
                            break;
                        case 0x7D:
                            CMPS(A, A);
                            break;
                        case 0xE0:
                            SerialWait = true;
                            while (sindata.Count == 0 & !halted)
                            {
                                System.Threading.Thread.Sleep(50);
                            }
                            SerialWait = false;
                            A = (byte)(sindata[0]);
                            sindata.RemoveAt(0);
                            break;
                        case 0xE1:
                            soutdata.Add((char)(A & 0xff));
                            //if (A == 0x07)
                            //{
                            //    foreach (char l in "[BELL]") {
                            //        soutdata.Add(l);
                            //    }
                            //}
                            System.Threading.Thread.Sleep(5);
                            break;
                        case 0xF0:
                            ClearScreen = true;
                            while (ClearScreen & !halted)
                            {
                                System.Threading.Thread.Sleep(1);
                            }
                            clearScreen();
                            if (refreshdelay)
                            {
                                System.Threading.Thread.Sleep(15);
                            }
                            break;
                        case 0xF1:
                            //pixeldata.Add(new byte[] { C, B, A });
                            drawByte((sbyte)C, (sbyte)B, A);
                            NewPixels = true;
                            break;
                        case 0x0F:
                            Jump();
                            break;
                        case 0x1F:
                            if (F.z)
                            {
                                Jump();
                            }
                            else
                            {
                                PC.Inc(2);
                            }
                            break;
                        case 0x2F:
                            if (!F.z)
                            {
                                Jump();
                            }
                            else
                            {
                                PC.Inc(2);
                            }
                            break;
                        case 0x3F:
                            if (F.n)
                            {
                                Jump();
                            }
                            else
                            {
                                PC.Inc(2);
                            }
                            break;
                        case 0x4F:
                            if (!F.n)
                            {
                                Jump();
                            }
                            else
                            {
                                PC.Inc(2);
                            }
                            break;
                        case 0x5F:
                            if (F.h)
                            {
                                Jump();
                            }
                            else
                            {
                                PC.Inc(2);
                            }
                            break;
                        case 0x6F:
                            if (!F.h)
                            {
                                Jump();
                            }
                            else
                            {
                                PC.Inc(2);
                            }
                            break;
                        case 0x7F:
                            if (F.c)
                            {
                                Jump();
                            }
                            else
                            {
                                PC.Inc(2);
                            }
                            break;
                        case 0x8F:
                            if (!F.c)
                            {
                                Jump();
                            }
                            else
                            {
                                PC.Inc(2);
                            }
                            break;
                        case 0x9F:
                            RelJump();
                            break;
                        case 0xAF:
                            if (F.z)
                            {
                                RelJump();
                            } else
                            {
                                PC.Inc();
                            }
                            break;
                        case 0xBF:
                            if (!F.z)
                            {
                                RelJump();
                            }
                            else
                            {
                                PC.Inc();
                            }
                            break;
                        case 0xCF:
                            if (F.n)
                            {
                                RelJump();
                            }
                            else
                            {
                                PC.Inc();
                            }
                            break;
                        case 0xDF:
                            if (!F.n)
                            {
                                RelJump();
                            }
                            else
                            {
                                PC.Inc();
                            }
                            break;
                        case 0xEF:
                            if (F.h)
                            {
                                RelJump();
                            }
                            else
                            {
                                PC.Inc();
                            }
                            break;
                        case 0xFF:
                            if (!F.h)
                            {
                                RelJump();
                            }
                            else
                            {
                                PC.Inc();
                            }
                            break;
                        case 0xEE:
                            if (F.c)
                            {
                                RelJump();
                            }
                            else
                            {
                                PC.Inc();
                            }
                            break;
                        case 0xFE:
                            if (!F.c)
                            {
                                RelJump();
                            }
                            else
                            {
                                PC.Inc();
                            }
                            break;
                        case 0x1E:
                            memory[SP.value] = (byte)((PC.value + 3) & 0xff);
                            memory[SP.value + 1] = (byte)((PC.value + 3) >> 8);
                            SP.Dec();
                            Jump();
                            break;
                        case 0x0E:
                            SP.Inc();
                            PC.value = (UInt16)((memory[SP.value + 1] << 8) + memory[SP.value]);
                            jumped = true;
                            break;
                        case 0x00:
                            // NOP
                            break;
                        default:
                            //Console.WriteLine("Unknown Instruction: 0x" + Convert.ToString(b1, 16).ToUpper());
                            break;
                    }

                    if (!jumped)
                    {
                        PC.Inc();
                    }
                }
            }
            catch (ThreadAbortException)
            {
                Console.WriteLine("CPU Thread Closed.");
                Thread.ResetAbort();
                halted = true;
            }
        }

        public void Jump()
        {
            PC.Inc();
            byte low = memory[PC.value];
            PC.Inc();
            byte high = memory[PC.value];
            jumped = true;
            PC.value = (UInt16)((high << 8) + low);
        }
        public void RelJump()
        {
            PC.Inc();
            sbyte diff = (sbyte)memory[PC.value];
            PC.value = (UInt16)(PC.value + diff);
        }
        public byte Add(byte value1, byte value2)
        {
            int nib = (value1 & 0xf) + (value2 & 0xf);
            int value = value1 + value2;
            F.Clear();
            if ((value & 0xff) == 0)
            {
                F.z = true;
            }
            if ((value & 0b10000000) > 0)
            {
                F.n = true;
            }
            if ((nib & 0xf0) > 0)
            {
                F.h = true;
            }
            if ((value >> 8) > 0)
            {
                F.c = true;
            }
            return (byte)value;
        }
        public UInt16 Add16(UInt16 value1, UInt16 value2)
        {
            int nib = (value1 & 0xf) + (value2 & 0xf);
            int value = value1 + value2;
            F.Clear();
            if ((value & 0xffff) == 0)
            {
                F.z = true;
            }
            if ((value & 0b1000000000000000) > 0)
            {
                F.n = true;
            }
            if ((nib & 0xf0) > 0)
            {
                F.h = true;
            }
            if ((value >> 16) > 0)
            {
                F.c = true;
            }
            return (UInt16)value;
        }
        public byte Sub(byte value1, byte value2)
        {
            int value = value1 - value2;
            if (value < 0)
            {
                value = value + 0x100;
            }
            F.Clear();
            if ((value & 0xff) == 0)
            {
                F.z = true;
            }
            if ((value & 0b10000000) > 0)
            {
                F.n = true;
            }
            if ((value1 & 0xf) <= (value2 & 0xf))
            {
                F.h = true;
            }
            if (value1 <= value2)
            {
                F.c = true;
            }
            return (byte)value;
        }
        public byte Inc(byte value)
        {
            return Add(value, 1);
        }
        public UInt16 Inc16(UInt16 value)
        {
            return (UInt16)(value + 1);
        }
        public byte Dec(byte value)
        {
            return Sub(value, 1);
        }
        public byte And8(byte value1, byte value2)
        {
            byte value = (byte)(value1 & value2);
            F.Clear();
            if (value == 0)
            {
                F.z = true;
            }
            if ((value & 0b10000000) > 0)
            {
                F.n = true;
            }
            return value;
        }
        public byte Or8(byte value1, byte value2)
        {
            byte value = (byte)(value1 | value2);
            F.Clear();
            if (value == 0)
            {
                F.z = true;
            }
            if ((value & 0b10000000) > 0)
            {
                F.n = true;
            }
            return value;
        }
        public byte Xor8(byte value1, byte value2)
        {
            byte value = (byte)(value1 ^ value2);
            F.Clear();
            if (value == 0)
            {
                F.z = true;
            }
            if ((value & 0b10000000) > 0)
            {
                F.n = true;
            }
            return value;
        }
        public void CMPS(byte value1, byte value2)
        {
            sbyte v1 = (sbyte)value1;
            sbyte v2 = (sbyte)value2;
            F.Clear();
            if (v1 == v2)
            {
                F.z = true;
            } else if (v1 > v2)
            {
                F.n = true;
            }
        }
        public void drawPixel(int x, int y, bool on)
        {
            if (on)
            {
                pixels[y, x] = 0xff;
            }
            else
            {
                pixels[y, x] = 0;
            }
        }
        public void drawByte(sbyte x, sbyte y, byte b)
        {
            for (int i = 0; i < 8; i++)
            {
                if (x + i >= 0 & x + i < width & y >= 0 & y < height)
                {
                    drawPixel(x + i, y, ((b >> 7 - i) & 0b1) == 0b1);
                }
            }
        }
        public void clearScreen()
        {
            pixels = new byte[height, width];
        }
    }
}
