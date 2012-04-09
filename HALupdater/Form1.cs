using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Net;

namespace HALupdater  {
    public partial class StartWin : Form {
        public StartWin() {
            InitializeComponent();
        }

        //public List<decimal> versions = new List<decimal>();
        decimal latest, current;
#if PORTABLE
        string urlformat = "http://dl.halbot.co.cc/HAL_PE_{0:F3}.7z";
#else
        string urlformat = "http://dl.halbot.co.cc/HAL_SE_{0:F3}.7z";
#endif
        string url, file;

        private void StartWin_Load(object sender, EventArgs e) {
            Directory.CreateDirectory(appPath);
            var thread = new Thread(HALupdate_thread);
            thread.Start();
        }

        private void HALupdate_thread() {
            current = GetHALVersion();
            /*while (true) {
                if (http_file_exists(string.Format(urlformat, version))) {
                    version += 0.001m;
                } else {
                    version -= 0.001m;
                    break;
                }
            }*/
            WebClient client = new WebClient();
            Action error = () => {
                MessageBox.Show("Problem with server, please contact author", "Fatal Error",
                                MessageBoxButtons.OK, MessageBoxIcon.Error);
                Environment.Exit(2);
            };
            try {
                string ver = client.DownloadString("http://dl.halbot.co.cc/latest.update");
                latest = decimal.Parse(ver);
            } catch (FormatException) {
                error();
            } catch (WebException) {
                error();
            }
            this.Invoke((MethodInvoker)delegate {
                console.Text = "Found update " + latest + "...\n";
                progress.Style = ProgressBarStyle.Continuous;
                download_update(latest, current);
            });
        }

        private void download_update(decimal version, decimal current) {
            if (version <= current)
                StartHAL();
            ChooseVersion version_dialog = new ChooseVersion();
            version_dialog.current = current;
            version_dialog.is_installed = File.Exists(Path.Combine(appPath, "Version.halconfig"));
            version_dialog.latest = latest;
            version_dialog.ShowDialog();
            decimal chosen = version_dialog.chosen ?? 0;
            if (chosen == 0)
                StartHAL();
            url = string.Format(urlformat, chosen);
            //file = Path.Combine(Path.GetTempPath(), url.Split('/').Last<string>());
            file = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString()+".7z");
            console.AppendText("Downloading file: " + url + "\n");
            label1.Text = "Downloading...";
            WebClient webClient = new WebClient();
            webClient.DownloadFileCompleted += new AsyncCompletedEventHandler(Completed);
            webClient.DownloadProgressChanged += new DownloadProgressChangedEventHandler(ProgressChanged);
            webClient.DownloadFileAsync(new Uri(url), file);
        }

        private void ProgressChanged(object sender, DownloadProgressChangedEventArgs e) {
            progress.Value = e.ProgressPercentage;
        }

        private void Completed(object sender, AsyncCompletedEventArgs e) {
            progress.Style = ProgressBarStyle.Marquee;
            label1.Text = "Extracting...";
            Process process = new Process();
            process.StartInfo.FileName = Path.Combine(appPath, "extract.exe");
            process.StartInfo.Arguments = "\"" + file + "\"";
            process.StartInfo.WorkingDirectory = appPath;
            process.StartInfo.CreateNoWindow = true;
            process.StartInfo.RedirectStandardOutput = true;
            process.StartInfo.UseShellExecute = false;
            process.EnableRaisingEvents = true;
            process.OutputDataReceived += extract_output;
            process.Exited += new EventHandler(extract_exited);
            try {
                process.Start();
                process.BeginOutputReadLine();
            } catch (Win32Exception) {
                MessageBox.Show("Please check if you download was complete and you have write access to the this directory",
                                "Fatal Error!", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            //new Thread(extract_thread).Start(file);
        }

        private void extract_exited(object sender, EventArgs e) {
            StartHAL();
        }

        private void extract_output(object sender, DataReceivedEventArgs e) {
            this.Invoke((MethodInvoker) delegate {
                /*if (e.Data == null)
                    return extract_exited(null, null);*/
                console.AppendText(e.Data ?? "");
                console.AppendText("\n");
            });
        }

        /*private void extract_thread(object file_) {
            string file = (string) file_;
            SevenZipExtractor.SetLibraryPath(Path.Combine(appPath, "7zxa.dll"));
            using (SevenZipExtractor tmp = new SevenZipExtractor(file)) {
                this.Invoke((MethodInvoker) delegate {
                    progress.Value = 0;
                    progress.Maximum = tmp.ArchiveFileData.Count;
                });
                for (int i = 0; i < tmp.ArchiveFileData.Count; i++) {
                    tmp.ExtractFiles(appPath, tmp.ArchiveFileData[i].Index);
                    this.Invoke((MethodInvoker) delegate {
                        console.AppendText("Extracting " + tmp.ArchiveFileNames[i] + "... " + (i / tmp.ArchiveFileData.Count * 100).ToString("F2") + "\n");
                        progress.Value += 1;
                    });
                }
            }
            File.Delete(file);
            console.AppendText("Done!\n");
            Thread.Sleep(1000);
        }*/

        private bool http_file_exists(string url) {
            try {
                HttpWebRequest req = (HttpWebRequest) WebRequest.Create(url);
                req.Method = "HEAD";
                HttpWebResponse response = (HttpWebResponse) req.GetResponse();
                bool result;
                result = response.StatusCode == HttpStatusCode.OK;
                response.Close();
                return result;
            } catch (WebException) {
                return false;
            }
        }

        private decimal GetHALVersion() {
            try {
                string data = File.ReadAllText(Path.Combine(appPath, "Version.halconfig"));
                decimal version;
                if (decimal.TryParse(data, out version))
                    return version;
                else
                    throw new FileNotFoundException();
            } catch (FileNotFoundException) {
                this.Invoke((MethodInvoker) delegate {
                    skip.Enabled = false;
                    skip.Text = "(Installing...)";
                    label1.Text = "Checking for latest version to prepare for installation...";
                });
                return 0.010m;
            }
        }

        //public static string appPath = Path.Combine(Path.GetDirectoryName(Application.ExecutablePath), "HAL");
        public static string appPath = Path.GetDirectoryName(Application.ExecutablePath);

        private void StartHAL(bool exit = true) {
            var process = new Process();
#if PORTABLE
            process.StartInfo.FileName = Path.Combine(appPath, "HALgui.exe");
            if (!File.Exists(process.StartInfo.FileName))
                process.StartInfo.FileName = Path.Combine(appPath, "HAL.exe");
            if (!File.Exists(process.StartInfo.FileName)) {
                MessageBox.Show("Invalid Installation!", "Fatal Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                Environment.Exit(2);
            }
#else
            process.StartInfo.FileName = "pythonw";
            process.StartInfo.Arguments = "-O \"" + Path.Combine(appPath, "HALgui.pyw") + "\"";
#endif
            process.Start();
            if (exit)
                Environment.Exit(0);
        }
    }
}
