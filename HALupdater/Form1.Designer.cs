namespace HALupdater {
    partial class StartWin {
        /// <summary>
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing) {
            if (disposing && (components != null)) {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows 窗体设计器生成的代码

        /// <summary>
        /// 设计器支持所需的方法 - 不要
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent() {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(StartWin));
            this.label1 = new System.Windows.Forms.Label();
            this.progress = new System.Windows.Forms.ProgressBar();
            this.skip = new System.Windows.Forms.Button();
            this.console = new System.Windows.Forms.TextBox();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(12, 9);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(122, 13);
            this.label1.TabIndex = 0;
            this.label1.Text = "Checking For Updates...";
            // 
            // progress
            // 
            this.progress.Location = new System.Drawing.Point(12, 25);
            this.progress.Name = "progress";
            this.progress.Size = new System.Drawing.Size(453, 23);
            this.progress.Style = System.Windows.Forms.ProgressBarStyle.Marquee;
            this.progress.TabIndex = 1;
            // 
            // skip
            // 
            this.skip.Location = new System.Drawing.Point(390, 221);
            this.skip.Name = "skip";
            this.skip.Size = new System.Drawing.Size(75, 23);
            this.skip.TabIndex = 2;
            this.skip.Text = "Skip";
            this.skip.UseVisualStyleBackColor = true;
            // 
            // console
            // 
            this.console.Location = new System.Drawing.Point(12, 54);
            this.console.Multiline = true;
            this.console.Name = "console";
            this.console.ReadOnly = true;
            this.console.Size = new System.Drawing.Size(453, 161);
            this.console.TabIndex = 3;
            // 
            // StartWin
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(477, 256);
            this.Controls.Add(this.console);
            this.Controls.Add(this.skip);
            this.Controls.Add(this.progress);
            this.Controls.Add(this.label1);
            this.Icon = ((System.Drawing.Icon) (resources.GetObject("$this.Icon")));
            this.Name = "StartWin";
            this.Text = "Starting HAL...";
            this.Load += new System.EventHandler(this.StartWin_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.ProgressBar progress;
        private System.Windows.Forms.Button skip;
        private System.Windows.Forms.TextBox console;
    }
}

