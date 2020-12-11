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
    /// Interaction logic for ConsoleWindow.xaml
    /// </summary>
    public partial class ConsoleWindow : Window
    {
        MainWindow parentWindow;
        public bool exiting = false;
        public ConsoleWindow(MainWindow parent)
        {
            InitializeComponent();
            parentWindow = parent;
        }
        public event EventHandler<ConsoleEventArgs> UpdateSIN;
        public class ConsoleEventArgs : EventArgs
        {
            public char letter { get; set; }
        }
        protected virtual void OnUpdateSIN(char letter)
        {
            ConsoleEventArgs e = new ConsoleEventArgs();
            e.letter = letter;
            if (UpdateSIN != null) UpdateSIN(this, e);
        }

        private void textBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            while (textBox.Text.Length > 0)
            {
                OnUpdateSIN(textBox.Text[0]);
                textBox.Text = textBox.Text.Remove(0, 1);
            }
        }

        private void Window_Closing_2(object sender, System.ComponentModel.CancelEventArgs e)
        {
            exiting = true;
            if (!parentWindow.exiting)
            {
                parentWindow.Close();
            }
        }

        private Boolean AutoScroll = true;
        private void ScrollViewer_ScrollChanged(object sender, ScrollChangedEventArgs e)
        {
            // User scroll event : set or unset auto-scroll mode
            if (e.ExtentHeightChange == 0)
            {   // Content unchanged : user scroll event
                if (textScrollViewer.VerticalOffset == textScrollViewer.ScrollableHeight)
                {   // Scroll bar is in bottom
                    // Set auto-scroll mode
                    AutoScroll = true;
                }
                else
                {   // Scroll bar isn't in bottom
                    // Unset auto-scroll mode
                    AutoScroll = false;
                }
            }

            // Content scroll event : auto-scroll eventually
            if (AutoScroll && e.ExtentHeightChange != 0)
            {   // Content changed and auto-scroll mode set
                // Autoscroll
                textScrollViewer.ScrollToVerticalOffset(textScrollViewer.ExtentHeight);
            }
        }
    }
}
