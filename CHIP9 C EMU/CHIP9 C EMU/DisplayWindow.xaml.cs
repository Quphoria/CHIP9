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

namespace CHIP9_C_EMU
{
    /// <summary>
    /// Interaction logic for DisplayWindow.xaml
    /// </summary>
    public partial class DisplayWindow : Window
    {
        Byte buttonstatus = 0b00000000;
        int width = 128;
        int height = 64;
        //int scale = 8;
        WriteableBitmap wbitmap;
        public byte[,] pixels;
        MainWindow parentWindow;
        public bool exiting = false;
        public DisplayWindow(MainWindow parent)
        {
            InitializeComponent();
            parentWindow = parent;

            wbitmap = new WriteableBitmap(width, height, 96, 96, PixelFormats.Gray8, null);
            pixels = new byte[height, width];

            RenderOptions.SetBitmapScalingMode(display_image, BitmapScalingMode.NearestNeighbor);
            display_image.Source = wbitmap;
            refreshScreen();
        }
        public event EventHandler<ButtonEventArgs> UpdateButtonStatus;
        public class ButtonEventArgs : EventArgs
        {
            public byte buttonStatus { get; set; }
        }
        protected virtual void OnUpdateButtonStatus(byte b_status)
        {
            ButtonEventArgs e = new ButtonEventArgs();
            e.buttonStatus = b_status;
            if (UpdateButtonStatus != null) UpdateButtonStatus(this, e);
        }

        public void refreshScreen()
        {
            byte[] pixels1d = new byte[height * width];
            int index = 0;
            for (int row = 0; row < height; row++)
            {
                for (int col = 0; col < width; col++)
                {
                    pixels1d[index++] = pixels[row, col];
                }
            }
            Int32Rect rect = new Int32Rect(0, 0, width, height);
            wbitmap.WritePixels(rect, pixels1d, width, 0);
        }
        public void clearScreen()
        {
            pixels = new byte[height, width];
        }

        private void WindowKeyUp(object sender, KeyEventArgs e)
        {
            switch (e.Key) {
                case Key.Up:
                case Key.W:
                    buttonstatus = (byte)(buttonstatus & 0b01111111);
                    break;
                case Key.Left:
                case Key.A:
                    buttonstatus = (byte)(buttonstatus & 0b10111111);
                    break;
                case Key.Down:
                case Key.S:
                    buttonstatus = (byte)(buttonstatus & 0b11011111);
                    break;
                case Key.Right:
                case Key.D:
                    buttonstatus = (byte)(buttonstatus & 0b11101111);
                    break;
                case Key.OemPeriod:
                    buttonstatus = (byte)(buttonstatus & 0b11110111);
                    break;
                case Key.OemComma:
                    buttonstatus = (byte)(buttonstatus & 0b11111011);
                    break;
                case Key.N:
                    buttonstatus = (byte)(buttonstatus & 0b11111101);
                    break;
                case Key.M:
                    buttonstatus = (byte)(buttonstatus & 0b11111110);
                    break;
            }
            OnUpdateButtonStatus(buttonstatus);
        }

        private void WindowKeyDown(object sender, KeyEventArgs e)
        {
            switch (e.Key)
            {
                case Key.Up:
                case Key.W:
                    buttonstatus = (byte)(buttonstatus | 0b10000000);
                    break;
                case Key.Left:
                case Key.A:
                    buttonstatus = (byte)(buttonstatus | 0b01000000);
                    break;
                case Key.Down:
                case Key.S:
                    buttonstatus = (byte)(buttonstatus | 0b00100000);
                    break;
                case Key.Right:
                case Key.D:
                    buttonstatus = (byte)(buttonstatus | 0b00010000);
                    break;
                case Key.OemPeriod:
                    buttonstatus = (byte)(buttonstatus | 0b00001000);
                    break;
                case Key.OemComma:
                    buttonstatus = (byte)(buttonstatus | 0b00000100);
                    break;
                case Key.N:
                    buttonstatus = (byte)(buttonstatus | 0b00000010);
                    break;
                case Key.M:
                    buttonstatus = (byte)(buttonstatus | 0b00000001);
                    break;
            }
            OnUpdateButtonStatus(buttonstatus);
        }

        private void Window_Closing_1(object sender, System.ComponentModel.CancelEventArgs e)
        {
            exiting = true;
            if (!parentWindow.exiting)
            {
                parentWindow.Close();
            }
        }
    }
}
