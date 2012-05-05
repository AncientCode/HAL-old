#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade HG on Tue Mar 27 18:28:57 2012

import wx
import sys
import time
import random
import os.path
import threading
import wx.lib.newevent

from HALmain import get_main_dir, get_system_info
from HALspeak import stop_speaking
from HALBot import HAL

# begin wxGlade: extracode
# end wxGlade

GuiPrintEvent, EVT_GUI_PRINT_EVENT = wx.lib.newevent.NewEvent()

class Done(Exception): pass

class HALOptions(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: HALOptions.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.options_tabs = wx.Notebook(self, -1, style=0)
        self.speech_tab = wx.Panel(self.options_tabs, -1)
        self.advspeak = wx.CheckBox(self.speech_tab, -1, _("Use Advanced Speech Engine"))
        self.mute = wx.CheckBox(self.speech_tab, 1, _("Mute"))
        self.gender = wx.RadioBox(self.speech_tab, -1, _("Gender"), choices=[_("Male"), _("Female")], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.label_3 = wx.StaticText(self.speech_tab, -1, _("Volume: "))
        self.volume = wx.Slider(self.speech_tab, -1, 100, 0, 200, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.label_4 = wx.StaticText(self.speech_tab, -1, _("Speed:"))
        self.speed = wx.Slider(self.speech_tab, -1, 175, 80, 450, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.apply_btn = wx.Button(self.speech_tab, 2, _("&Apply"))
        self.save_btn = wx.Button(self.speech_tab, 3, _("&Save"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.apply, id=2)
        # end wxGlade
        self.parent = self.GetParent()
        self.__init_values()

    def __init_values(self):
        self.volume.SetValue(self.parent.hal.speak_opt['volume'])
        self.speed.SetValue(self.parent.hal.speak_opt['speed'])
        self.gender.SetSelection(0 if self.parent.hal.speak_opt['gender'] else 1)
        self.mute.SetValue(not self.parent.hal.speak)
        self.advspeak.SetValue(self.parent.hal.advspeak)
    
    def __set_properties(self):
        # begin wxGlade: HALOptions.__set_properties
        self.SetTitle(_("HAL Options"))
        self.SetSize((400, -1))
        self.gender.SetMinSize((-1, 60))
        self.gender.SetSelection(0)
        self.label_3.SetMinSize((42, -1))
        self.volume.SetMinSize((-1, 50))
        self.label_4.SetMinSize((42, -1))
        self.speed.SetMinSize((-1, 50))
        self.save_btn.Enable(False)
        self.save_btn.Hide()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: HALOptions.__do_layout
        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        sizer_15 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_14 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_13 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11 = wx.BoxSizer(wx.VERTICAL)
        sizer_11.Add(self.advspeak, 0, 0, 0)
        sizer_11.Add(self.mute, 0, 0, 0)
        sizer_10.Add(sizer_11, 1, wx.EXPAND, 0)
        sizer_10.Add(self.gender, 0, 0, 0)
        sizer_8.Add(sizer_10, 0, wx.EXPAND, 0)
        sizer_13.Add(self.label_3, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_13.Add(self.volume, 1, 0, 0)
        sizer_8.Add(sizer_13, 0, wx.EXPAND, 0)
        sizer_14.Add(self.label_4, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_14.Add(self.speed, 1, 0, 0)
        sizer_8.Add(sizer_14, 0, wx.EXPAND, 0)
        sizer_15.Add((0, 0), 1, wx.EXPAND, 0)
        sizer_15.Add(self.apply_btn, 0, 0, 0)
        sizer_15.Add(self.save_btn, 0, 0, 0)
        sizer_8.Add(sizer_15, 0, wx.EXPAND, 0)
        self.speech_tab.SetSizer(sizer_8)
        self.options_tabs.AddPage(self.speech_tab, _("Speech"))
        sizer_7.Add(self.options_tabs, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_7)
        self.Layout()
        # end wxGlade

    def apply(self, event):  # wxGlade: HALOptions.<event_handler>
        self.parent.hal.speak_opt['volume'] = self.volume.GetValue()
        self.parent.hal.speak_opt['speed']  = self.speed.GetValue()
        self.parent.hal.speak_opt['gender'] = not self.gender.GetSelection()
        self.parent.hal.speak = not self.mute.GetValue()
        self.parent.hal.advspeak = self.advspeak.GetValue()

# end of class HALOptions
if os.name == 'nt':
    # On Windows is ok to acess a TextCtrl from multiple threads
    class RedirectText(object):
        def __init__(self, textctrl, id, frame):
            self.textctrl = textctrl
        def write(self, string):
            self.textctrl.AppendText(string)
else:
    class RedirectText(object):
        def __init__(self, textctrl, id, frame):
            self.textctrl = textctrl
            self.thread_id = id
            self.frame = frame
        def write(self, string):
            if threading.current_thread() is self.thread_id:
                self.textctrl.AppendText(string)
            else:
                wx.PostEvent(self.frame, GuiPrintEvent(string=string))

class MainWin(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MainWin.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.label_1 = wx.StaticText(self, -1, _("HAL"), style=wx.ALIGN_CENTRE)
        self.datetime = wx.TextCtrl(self, -1, _("Date: (Unknown)\nTime: (Unknown)"), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.output = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)
        self.input = wx.TextCtrl(self, 6, "", style=wx.TE_PROCESS_ENTER)
        self.ask_btn = wx.Button(self, 1, _("&Ask"))
        self.stop_talking_btn = wx.Button(self, 3, _("Stop Talking!"))
        self.clear_out_btn = wx.Button(self, 4, _("Clear Output"))
        self.save_btn = wx.Button(self, 7, _("Save Output"))
        self.options_btn = wx.Button(self, 5, _("&Options"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.Ask, id=1)
        self.Bind(wx.EVT_BUTTON, self.stop_talking, id=3)
        self.Bind(wx.EVT_BUTTON, self.clear_output, id=4)
        self.Bind(wx.EVT_BUTTON, self.save_output, id=7)
        self.Bind(wx.EVT_BUTTON, self.open_options, id=5)
        # end wxGlade
        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, 'Consolas')
        self.output.SetFont(font)
        self.input.SetFont(font)
        thread = threading.Thread(target=self.start_hal)
        thread.daemon = True
        thread.start()
        
        self.time_lock = threading.Lock()
        thread = threading.Thread(target=self.timer)
        thread.start()
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(EVT_GUI_PRINT_EVENT, self.ThreadPrint)

    def ThreadPrint(self, event):
        self.output.AppendText(event.string)
    
    def OnCloseWindow(self, event):
        try:
            self.closewindowstarted
        except AttributeError:
            self.closewindowstarted = True
            self.time_lock.acquire()
            self.Destroy()
    
    def timer(self):
        while True:
            if not self.time_lock.acquire(0):
                break
            self.datetime.SetValue(time.strftime('Date: %B %d, %Y\nTime: %H:%M:%S'))
            if hasattr(self, 'lasttalk') and not self.working and time.time()-self.lasttalk > 60:
                msg = self.hal.autotalk()
                print self.halpro, msg
                print
                self.lasttalk = time.time()
                self.hal.do_speech(msg)
            time.sleep(1)
            self.time_lock.release()
    
    def __set_properties(self):
        # begin wxGlade: MainWin.__set_properties
        self.SetTitle(_("HAL"))
        self.SetSize((700, 530))
        self.SetBackgroundColour(wx.Colour(240, 240, 240))
        self.label_1.SetForegroundColour(wx.Colour(0, 0, 255))
        self.label_1.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD, 0, ""))
        self.datetime.SetMinSize((150, 40))
        self.input.SetFocus()
        self.ask_btn.Enable(False)
        self.options_btn.Enable(False)
        # end wxGlade
        self.label_1.SetFont(wx.Font(25, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "Consolas"))
        sys.stdout = RedirectText(self.output, threading.current_thread(), self)

    def __do_layout(self):
        # begin wxGlade: MainWin.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(self.label_1, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_6.Add(self.datetime, 0, 0, 0)
        sizer_1.Add(sizer_6, 0, wx.EXPAND, 0)
        sizer_3.Add(self.output, 1, wx.EXPAND, 0)
        sizer_4.Add(self.input, 1, wx.EXPAND, 0)
        sizer_4.Add(self.ask_btn, 0, 0, 0)
        sizer_3.Add(sizer_4, 0, wx.EXPAND, 0)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        sizer_5.Add(self.stop_talking_btn, 0, 0, 0)
        sizer_5.Add(self.clear_out_btn, 0, 0, 0)
        sizer_5.Add(self.save_btn, 0, 0, 0)
        sizer_5.Add((0, 0), 1, wx.EXPAND, 0)
        sizer_5.Add(self.options_btn, 0, wx.EXPAND, 0)
        sizer_2.Add(sizer_5, 0, wx.EXPAND, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade
    
    def start_hal(self):
        data = os.path.join(get_main_dir(), 'data')
        print '[SYSTEM]', 'Booted on', get_system_info(), '[/SYSTEM]'
        print
        print 'Loading data files...'
        self.hal = HAL(speak=True, write=True)
        if not os.path.exists(data):
            print 'Your need a full package with the data folder'
        prompt = '-%s:'%self.hal.user
        halpro = '-HAL:'
        length = max(len(prompt), len(halpro))
        self.prompt = prompt.ljust(length)
        self.halpro = halpro.ljust(length)
        self.output.SetValue('')
        print self.halpro, 'Hello %s. I am HAL %s.'%(self.hal.user, self.hal.version)
        print
        self.options_btn.Enable(True)
        self.ask_btn.Enable(True)
        self.working = True
        self.Bind(wx.EVT_TEXT_ENTER, self.input_enter, id=6)
        self.lasttalk = time.time()

    def Ask(self, event):  # wxGlade: MainWin.<event_handler>
        self.input.Enable(False)
        self.working = True
        input = self.input.GetValue()
        try:
            if not input.strip():
                event.Skip()
                raise Done
            print self.prompt, input
            for i in self.hal.ask(input.encode('utf-8')):
                print self.halpro, i
            if not self.hal.running:
                print self.halpro, self.hal.shutdown()
                self.hal.running = True
            print
            raise Done
        except Done:
            self.working = False
            self.input.Clear()
            self.input.Enable(True)
            self.input.SetFocus()
        self.lasttalk = time.time()

    def mute_changed(self, event):  # wxGlade: MainWin.<event_handler>
        if self.mute.IsChecked():
            self.hal.speak = False
            self.stop_talking(None)
        else:
            self.hal.speak = True

    def stop_talking(self, event):  # wxGlade: MainWin.<event_handler>
        stop_speaking(self.hal.sphandle)

    def clear_output(self, event):  # wxGlade: MainWin.<event_handler>
        self.output.Clear()

    def input_enter(self, event):  # wxGlade: MainWin.<event_handler>
        if self.working:
            event.Skip()
        self.Ask(event)

    def open_options(self, event):  # wxGlade: MainWin.<event_handler>
        HALOptions(self).Show()

    def save_output(self, event):  # wxGlade: MainWin.<event_handler>
        dialog = wx.FileDialog(self, "Save Output...", "", "",
                               "Text File (*.txt)|*.txt", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        
        with open(dialog.GetPath(), 'w') as f:
            f.write(self.output.GetValue())

# end of class MainWin
class HALGUI(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        mainwin = MainWin(None, -1, "")
        self.SetTopWindow(mainwin)
        mainwin.Show()
        return 1

# end of class HALGUI

def main():
    import gettext
    gettext.install("hal_gui") # replace with the appropriate catalog name

    hal_gui = HALGUI(0)
    hal_gui.MainLoop()

if __name__ == "__main__":
    main()
