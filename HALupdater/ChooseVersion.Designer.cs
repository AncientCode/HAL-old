namespace HALupdater {
    partial class ChooseVersion {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing) {
            if (disposing && (components != null)) {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent() {
            this.label1 = new System.Windows.Forms.Label();
            this.versions = new System.Windows.Forms.ListBox();
            this.upgrade = new System.Windows.Forms.Button();
            this.skip = new System.Windows.Forms.Button();
            this.ignore = new System.Windows.Forms.CheckBox();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(12, 9);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(219, 13);
            this.label1.TabIndex = 0;
            this.label1.Text = "HAL has found updates! Please choose one.";
            // 
            // versions
            // 
            this.versions.FormattingEnabled = true;
            this.versions.Location = new System.Drawing.Point(12, 25);
            this.versions.Name = "versions";
            this.versions.Size = new System.Drawing.Size(219, 173);
            this.versions.TabIndex = 2;
            // 
            // upgrade
            // 
            this.upgrade.Location = new System.Drawing.Point(237, 175);
            this.upgrade.Name = "upgrade";
            this.upgrade.Size = new System.Drawing.Size(75, 23);
            this.upgrade.TabIndex = 3;
            this.upgrade.Text = "&Upgrade";
            this.upgrade.UseVisualStyleBackColor = true;
            this.upgrade.Click += new System.EventHandler(this.upgrade_Click);
            // 
            // skip
            // 
            this.skip.DialogResult = System.Windows.Forms.DialogResult.Cancel;
            this.skip.Location = new System.Drawing.Point(237, 146);
            this.skip.Name = "skip";
            this.skip.Size = new System.Drawing.Size(75, 23);
            this.skip.TabIndex = 4;
            this.skip.Text = "&Skip";
            this.skip.UseVisualStyleBackColor = true;
            this.skip.Click += new System.EventHandler(this.skip_Click);
            // 
            // ignore
            // 
            this.ignore.AutoSize = true;
            this.ignore.Location = new System.Drawing.Point(237, 123);
            this.ignore.Name = "ignore";
            this.ignore.Size = new System.Drawing.Size(56, 17);
            this.ignore.TabIndex = 5;
            this.ignore.Text = "&Ignore";
            this.ignore.UseVisualStyleBackColor = true;
            this.ignore.CheckedChanged += new System.EventHandler(this.ignore_CheckedChanged);
            // 
            // ChooseVersion
            // 
            this.AcceptButton = this.upgrade;
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.CancelButton = this.skip;
            this.ClientSize = new System.Drawing.Size(324, 214);
            this.Controls.Add(this.ignore);
            this.Controls.Add(this.skip);
            this.Controls.Add(this.upgrade);
            this.Controls.Add(this.versions);
            this.Controls.Add(this.label1);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "ChooseVersion";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            this.Text = "Choose a Version to Upgrade to";
            this.Load += new System.EventHandler(this.ChooseVersion_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.ListBox versions;
        private System.Windows.Forms.Button upgrade;
        private System.Windows.Forms.Button skip;
        private System.Windows.Forms.CheckBox ignore;
    }
}