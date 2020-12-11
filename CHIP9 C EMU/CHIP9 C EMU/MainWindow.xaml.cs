using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.Collections.ObjectModel;
using System.Windows.Threading;
using Microsoft.Win32;
using System.IO;
using System.Timers;
using System.Media;

namespace CHIP9_C_EMU
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        ConsoleWindow CW;
        DisplayWindow DW;
        InstructionInfo IInfo;
        CPU emuCPU;
        Timer updateTimer = new Timer(5);
        ObservableCollection<RomFile> roms = new ObservableCollection<RomFile>();
        ObservableCollection<Breakpoint> breakpoints = new ObservableCollection<Breakpoint>();
        Brush releasedBrush = new SolidColorBrush(Color.FromArgb(0xff, 0xdd, 0xdd, 0xdd));
        Brush pressedBrush = new SolidColorBrush(Color.FromArgb(0xff, 0xad, 0xad, 0xad));
        Brush onBrush = new SolidColorBrush(Color.FromArgb(0xff, 0x1c, 0xcd, 0x00));
        public bool exiting = false;
        public class RomFile
        {
            public string Name { get; set; }
            public string StartAddress { get; set; }
            public UInt16 Size { get; set; }
            public string Path { get; set; }
        }
        public class Breakpoint
        {
            public string Address { get; set; }
        }

        public MainWindow()
        {
            InitializeComponent();
            ClearMonitor();
            roms.Add(new RomFile() { Name = "bootrom", StartAddress = "0x0000", Size = 779, Path = "bootrom" });
            roms.Add(new RomFile() { Name = "rom", StartAddress = "0x0597", Size = 3072, Path = "rom" });
            romList.ItemsSource = roms;
            breakpointList.ItemsSource = breakpoints;
            emuCPU = new CPU();
            CW = new ConsoleWindow(this);
            DW = new DisplayWindow(this);
            IInfo = new InstructionInfo();
            DW.UpdateButtonStatus += update_buttonstatus;
            CW.UpdateSIN += update_sin;
            CW.Show();
            DW.Show();
            updateTimer.Elapsed += updateCPU;
            updateTimer.AutoReset = true;
            updateTimer.Start();
        }
        private byte[] StreamFile(string filename)
        {
            FileStream fs = new FileStream(filename, FileMode.Open, FileAccess.Read);

            // Create a byte array of file stream length
            byte[] ImageData = new byte[fs.Length];

            //Read block of bytes from stream into the byte array
            fs.Read(ImageData, 0, System.Convert.ToInt32(fs.Length));

            //Close the File Stream
            fs.Close();
            return ImageData; //return the byte data
        }
        public void LoadRoms()
        {
            emuCPU.loadError = false;
            emuCPU.ClearROM();
            foreach (RomFile rom in roms)
            {
                Console.WriteLine("Loading ROM: " + rom.Name + " @ " + rom.StartAddress);
                string filename = rom.Path;
                try
                {
                    emuCPU.LoadROM(StreamFile(rom.Path), UInt16.Parse(rom.StartAddress.Substring(2), System.Globalization.NumberStyles.HexNumber));
                }
                catch (FileNotFoundException e)
                {
                    MessageBoxResult errorBox = MessageBox.Show("Unable to load " + rom.Name + ", Error: File not found." + e.ToString(), "An Error Occurred", MessageBoxButton.OK, MessageBoxImage.Error);
                    emuCPU.loadError = true;
                }
                catch (Exception e)
                {
                    MessageBoxResult errorBox = MessageBox.Show("Unable to load " + rom.Name + ", Error: " + e.ToString(), "An Error Occurred", MessageBoxButton.OK, MessageBoxImage.Error);
                    emuCPU.loadError = true;
                }
                //emuCPU.LoadROM();
                //FileStream fs = new FileStream(filename, FileMode.Open, FileAccess.Read);
            }
        }

        private void RomUp_Click(object sender, RoutedEventArgs e)
        {
            var selectedIndex = romList.SelectedIndex;

            if (selectedIndex > 0)
            {
                RomFile itemToMoveUp = roms[selectedIndex];
                roms.RemoveAt(selectedIndex);
                roms.Insert(selectedIndex - 1, itemToMoveUp);
                romList.SelectedIndex = selectedIndex - 1;
            }

            
        }

        private void RomDown_Click(object sender, RoutedEventArgs e)
        {
            var selectedIndex = romList.SelectedIndex;

            if (selectedIndex + 1 < roms.Count & selectedIndex >= 0)
            {
                RomFile itemToMoveDown = roms[selectedIndex];
                roms.RemoveAt(selectedIndex);
                roms.Insert(selectedIndex + 1, itemToMoveDown);
                romList.SelectedIndex = selectedIndex + 1;
            }
        }

        private void RomLoad_Click(object sender, RoutedEventArgs e)
        {
            LoadRoms();
        }

        private void RomRun_Click(object sender, RoutedEventArgs e)
        {
            emuCPU.RunCPU();
        }

        private void RESETbutton_Click(object sender, RoutedEventArgs e)
        {
            bool keep_pause = emuCPU.pause;
            emuCPU.Kill();
            emuCPU = new CPU();
            CW.textBlock.Text = "";
            DW.clearScreen();
            DW.refreshScreen();
            emuCPU.pause = keep_pause;
            UpdateBreakpoints();
            emuCPU.slowdown = (int)speedslider.Value;
            emuCPU.refreshdelay = RefreshDelaycheckBox.IsChecked == true;
        }
        
        public void update_buttonstatus(object sender, DisplayWindow.ButtonEventArgs e)
        {
            emuCPU.buttonstatus = e.buttonStatus;
        }

        public void update_sin(object sender, ConsoleWindow.ConsoleEventArgs e)
        {
            emuCPU.sindata.Add(e.letter);
        }

        public void updateCPU(object sender, ElapsedEventArgs e) //  EventArgs e
        {
            try
            {
                this.Dispatcher.Invoke(RunUpdateCPU);
            }
            catch (Exception err)
            {
                Console.WriteLine("Update Timer Error: " + err.ToString());
            }
        }
        public void RunUpdateCPU()
        {
            try
            {
                while (emuCPU.soutdata.Count > 0)
                {
                    char letter = emuCPU.soutdata[0];
                    emuCPU.soutdata.RemoveAt(0);
                    if (letter == 0x07)
                    {
                        SystemSounds.Beep.Play();
                    }
                    CW.textBlock.Text += letter;
                }
                if (emuCPU.NewPixels & DisplayRefreshBox.IsChecked == true)
                {
                    emuCPU.NewPixels = false;
                    DW.pixels = emuCPU.pixels;
                    DW.refreshScreen();
                }
                if (emuCPU.ClearScreen)
                {
                    if (emuCPU.NewPixels)
                    {
                        emuCPU.NewPixels = false;
                        DW.pixels = emuCPU.pixels;
                        if (DisplayRefreshBox.IsChecked == true)
                        {
                            DW.refreshScreen();
                        }
                    }
                    DW.refreshScreen();
                    emuCPU.ClearScreen = false;
                }
                UpdateStatusFlags();
                if (emuCPU.pause)
                {
                    UpdateMonitor();
                    // Set Debug Outputs
                } else
                {
                    ClearMonitor();
                }
            } catch (Exception err)
            {
                Console.WriteLine("Update Error: " + err.ToString());
            }
        }

        private void Window_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            emuCPU.halted = true;
            emuCPU.Kill();
            exiting = true;
            if (!DW.exiting)
            {
                try
                {
                    DW.Close();
                }
                catch { }
            }
            if (!CW.exiting)
            {
                try
                {
                    CW.Close();
                }
                catch { }
            }
        }

        private void romDelete_Click(object sender, RoutedEventArgs e)
        {
            var selectedIndex = romList.SelectedIndex;

            if (selectedIndex < roms.Count & selectedIndex >= 0)
            {
                roms.RemoveAt(selectedIndex);
            }
        }

        private void romAdd_Click(object sender, RoutedEventArgs e)
        {
            string addrtext = addressBox.Text.ToUpper();
            string outtext = "";
            char[] validchars = new char[] { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F' };
            for (int i = addrtext.Length - 1; i >= 0; i--)
            {
                if (validchars.Contains(addrtext[i]))
                {
                    outtext += addrtext[i];
                }
            }
            char[] outarr = outtext.ToCharArray();
            Array.Reverse(outarr);
            outtext = new string(outarr);
            for (int i = 0; i < 4 - outtext.Length; i++)
            {
                outtext = "0" + outtext;
            }
            OpenFileDialog romOpen = new OpenFileDialog();
            if (romOpen.ShowDialog() == true)
            {
                string path = romOpen.FileName;
                string name = System.IO.Path.GetFileName(path);
                
                UInt16 length = (UInt16)(new System.IO.FileInfo(path).Length);
                roms.Add(new RomFile() { Name = name, StartAddress = "0x" + outtext, Size = length, Path = path });
            }
        }

        private void addressBox_Key(object sender, KeyEventArgs e)
        {
            string addrtext = addressBox.Text.ToUpper();
            string outtext = "";
            char[] validchars = new char[] { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F' };
            for (int i = addrtext.Length - 1; i >= 0; i--)
            {
                if (validchars.Contains(addrtext[i]) & outtext.Length < 4)
                {
                    outtext += addrtext[i];
                }
            }
            char[] outarr = outtext.ToCharArray();
            Array.Reverse(outarr);
            outtext = new string(outarr);
            for (int i = 0; i < 4 - outtext.Length; i++)
            {
                outtext = "0" + outtext;
            }
            if (addrtext != outtext)
            {
                addressBox.Text = outtext;
                addressBox.CaretIndex = 4;
            }
        }

        private void PauseButton_Click(object sender, RoutedEventArgs e)
        {
            if (emuCPU.pause)
            {
                emuCPU.pause = false;
                StepButton.IsEnabled = false;
                PauseButton.Background = releasedBrush;
            } else
            {
                emuCPU.pause = true;
                StepButton.IsEnabled = true;
                PauseButton.Background = pressedBrush;
            }
        }

        private void StepButton_Click(object sender, RoutedEventArgs e)
        {
            if (emuCPU.pause)
            {
                emuCPU.step = true;
            }
        }
        private void ClearMonitor()
        {
            StepButton.IsEnabled = false;
            PauseButton.Background = releasedBrush;
            B_B.Text = "--------";
            C_B.Text = "--------";
            D_B.Text = "--------";
            E_B.Text = "--------";
            H_B.Text = "--------";
            L_B.Text = "--------";
            A_B.Text = "--------";
            PC_B.Text = "----------------";
            SP_B.Text = "----------------";
            B_H.Text = "--";
            C_H.Text = "--";
            D_H.Text = "--";
            E_H.Text = "--";
            H_H.Text = "--";
            L_H.Text = "--";
            A_H.Text = "--";
            PC_H.Text = "------";
            SP_H.Text = "------";
            CUR_INSTR.Text = "------";
            Z_Frame.Background = releasedBrush;
            N_Frame.Background = releasedBrush;
            H_Frame.Background = releasedBrush;
            C_Frame.Background = releasedBrush;
            InstructionBox.Text = "Instructions Appear Here";
        }
        private void UpdateMonitor()
        {
            StepButton.IsEnabled = true;
            PauseButton.Background = pressedBrush;
            B_B.Text = Convert.ToString(emuCPU.B, 2).PadLeft(8, '0');
            C_B.Text = Convert.ToString(emuCPU.C, 2).PadLeft(8, '0');
            D_B.Text = Convert.ToString(emuCPU.D, 2).PadLeft(8, '0');
            E_B.Text = Convert.ToString(emuCPU.E, 2).PadLeft(8, '0');
            H_B.Text = Convert.ToString(emuCPU.H, 2).PadLeft(8, '0');
            L_B.Text = Convert.ToString(emuCPU.L, 2).PadLeft(8, '0');
            A_B.Text = Convert.ToString(emuCPU.A, 2).PadLeft(8, '0');
            PC_B.Text = Convert.ToString(emuCPU.PC.value, 2).PadLeft(16, '0');
            SP_B.Text = Convert.ToString(emuCPU.SP.value, 2).PadLeft(16, '0');
            B_H.Text = Convert.ToString(emuCPU.B, 16).ToUpper().PadLeft(2, '0');
            C_H.Text = Convert.ToString(emuCPU.C, 16).ToUpper().PadLeft(2, '0');
            D_H.Text = Convert.ToString(emuCPU.D, 16).ToUpper().PadLeft(2, '0');
            E_H.Text = Convert.ToString(emuCPU.E, 16).ToUpper().PadLeft(2, '0');
            H_H.Text = Convert.ToString(emuCPU.H, 16).ToUpper().PadLeft(2, '0');
            L_H.Text = Convert.ToString(emuCPU.L, 16).ToUpper().PadLeft(2, '0');
            A_H.Text = Convert.ToString(emuCPU.A, 16).ToUpper().PadLeft(2, '0');
            PC_H.Text = "0x" + Convert.ToString(emuCPU.PC.value, 16).ToUpper().PadLeft(4, '0');
            SP_H.Text = "0x" + Convert.ToString(emuCPU.SP.value, 16).ToUpper().PadLeft(4, '0');
            CUR_INSTR.Text = "0x" + Convert.ToString(emuCPU.last_instr, 16).ToUpper().PadLeft(4, '0');
            if (emuCPU.F.z)
            {
                Z_Frame.Background = onBrush;
            }
            else
            {
                Z_Frame.Background = releasedBrush;
            }
            if (emuCPU.F.n)
            {
                N_Frame.Background = onBrush;
            }
            else
            {
                N_Frame.Background = releasedBrush;
            }
            if (emuCPU.F.h)
            {
                H_Frame.Background = onBrush;
            }
            else
            {
                H_Frame.Background = releasedBrush;
            }
            if (emuCPU.F.c)
            {
                C_Frame.Background = onBrush;
            }
            else
            {
                C_Frame.Background = releasedBrush;
            }
            InstructionBox.Text = IInfo.Decode(emuCPU.b1, emuCPU.b2, emuCPU.b3);
        }
        private void UpdateStatusFlags()
        {
            if (emuCPU.romloaded)
            {
                ROM_Frame.Background = onBrush;
            } else
            {
                ROM_Frame.Background = releasedBrush;
            }
            if (emuCPU.running)
            {
                RUN_Frame.Background = onBrush;
            } else
            {
                RUN_Frame.Background = releasedBrush;
            }
            if (emuCPU.pause)
            {
                PAUSE_Frame.Background = onBrush;
            } else
            {
                PAUSE_Frame.Background = releasedBrush;
            }
            if (emuCPU.halted)
            {
                HALT_Frame.Background = onBrush;
            } else
            {
                HALT_Frame.Background = releasedBrush;
            }
            if (emuCPU.SerialWait)
            {
                SIN_Frame.Background = onBrush;
            } else
            {
                SIN_Frame.Background = releasedBrush;
            }
        }
        public void UpdateBreakpoints()
        {
            List<UInt16> brks = new List<UInt16>();
            foreach (Breakpoint brk in breakpoints)
            {
                brks.Add(UInt16.Parse(brk.Address.Substring(2), System.Globalization.NumberStyles.HexNumber));
            }
            emuCPU.breakpoints = brks;
        }

        private void BRKaddressBox_Key(object sender, KeyEventArgs e)
        {
            string addrtext = BRKaddressBox.Text.ToUpper();
            string outtext = "";
            char[] validchars = new char[] { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F' };
            for (int i = addrtext.Length - 1; i >= 0; i--)
            {
                if (validchars.Contains(addrtext[i]) & outtext.Length < 4)
                {
                    outtext += addrtext[i];
                }
            }
            char[] outarr = outtext.ToCharArray();
            Array.Reverse(outarr);
            outtext = new string(outarr);
            for (int i = 0; i < 4 - outtext.Length; i++)
            {
                outtext = "0" + outtext;
            }
            if (addrtext != outtext)
            {
                BRKaddressBox.Text = outtext;
                BRKaddressBox.CaretIndex = 4;
            }
        }

        private void BRKAdd_Click(object sender, RoutedEventArgs e)
        {
            string addrtext = BRKaddressBox.Text.ToUpper();
            string outtext = "";
            char[] validchars = new char[] { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F' };
            for (int i = addrtext.Length - 1; i >= 0; i--)
            {
                if (validchars.Contains(addrtext[i]) & outtext.Length < 4)
                {
                    outtext += addrtext[i];
                }
            }
            char[] outarr = outtext.ToCharArray();
            Array.Reverse(outarr);
            outtext = new string(outarr);
            for (int i = 0; i < 4 - outtext.Length; i++)
            {
                outtext = "0" + outtext;
            }
            breakpoints.Add(new Breakpoint() { Address = "0x" + outtext });
            UpdateBreakpoints();
        }

        private void BRKDelete_Click(object sender, RoutedEventArgs e)
        {
            var selectedIndex = breakpointList.SelectedIndex;

            if (selectedIndex < breakpoints.Count & selectedIndex >= 0)
            {
                breakpoints.RemoveAt(selectedIndex);
            }
            UpdateBreakpoints();
        }

        private void BRKClear_Click(object sender, RoutedEventArgs e)
        {
            breakpoints.Clear();
            UpdateBreakpoints();
        }

        private void Slider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (emuCPU != null)
            {
                emuCPU.slowdown = (int)speedslider.Value;
            }
        }

        private void RefreshDelaycheckBox_Click(object sender, RoutedEventArgs e)
        {
            emuCPU.refreshdelay = RefreshDelaycheckBox.IsChecked == true;
        }
    }
}
