using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Runtime.InteropServices;

namespace HALupdater {
    public partial class ChooseVersion : Form {
        const int MF_BYPOSITION = 0x400;

        [DllImport("User32")]
        private static extern int RemoveMenu(IntPtr hMenu, int nPosition, int wFlags);

        [DllImport("User32")]
        private static extern IntPtr GetSystemMenu(IntPtr hWnd, bool bRevert);

        [DllImport("User32")]
        private static extern int GetMenuItemCount(IntPtr hWnd);

        public ChooseVersion() {
            InitializeComponent();
        }

        public decimal latest, current;
        public bool is_installed = false;

        private void ChooseVersion_Load(object sender, EventArgs e) {
            // Remove Close Button
            IntPtr hMenu = GetSystemMenu(this.Handle, false);
            int menuItemCount = GetMenuItemCount(hMenu);
            RemoveMenu(hMenu, menuItemCount - 1, MF_BYPOSITION);

            if (!is_installed) {
                skip.Enabled = false;
                upgrade.Text = "Install";
            }
            for (decimal version = current+0.001m; version <= latest; version += 0.001m)
                versions.Items.Add(version);
            versions.SelectedItem = latest;
        }

        private void ignore_CheckedChanged(object sender, EventArgs e) {
            upgrade.Enabled = !ignore.Checked;
        }

        public decimal? chosen = null;

        private void upgrade_Click(object sender, EventArgs e) {
            /*if (versions.SelectedItem == null) {
                MessageBox.Show("You must select a version" + (is_installed ? " or skip upgrade" : ""),
                                "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }*/
            chosen = (decimal)versions.SelectedItem;
            Close();
        }

        private void skip_Click(object sender, EventArgs e) {
            Close();
        }
    }
}
