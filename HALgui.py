#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade HG on Tue Mar 27 18:28:57 2012

import wx
import sys
import time
import random
import os.path
import threading

from HALmain import get_main_dir, get_system_info
from HALspeak import stop_speaking
from HALBot import HAL

# begin wxGlade: extracode
# end wxGlade

class RedirectText(object):
    def __init__(self, textctrl):
        self.textctrl = textctrl
        self.max_row = 500
    def write(self, string):
        self.textctrl.AppendText(string)

class MainWin(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MainWin.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.hal_title = wx.StaticBitmap(self, -1, wx.NullBitmap)
        self.hal_icon = wx.StaticBitmap(self, -1, wx.NullBitmap)
        self.output = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)
        self.input = wx.TextCtrl(self, 5, "", style=wx.TE_PROCESS_ENTER)
        self.ask_btn = wx.Button(self, 1, _("&Ask"))
        self.mute = wx.CheckBox(self, 2, _("Mute"))
        self.stop_talking_btn = wx.Button(self, 3, _("Stop Talking!"))
        self.clear_out_btn = wx.Button(self, 4, _("Clear Output"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT_ENTER, self.input_enter, id=5)
        self.Bind(wx.EVT_BUTTON, self.Ask, id=1)
        self.Bind(wx.EVT_CHECKBOX, self.mute_changed, id=2)
        self.Bind(wx.EVT_BUTTON, self.stop_talking, id=3)
        self.Bind(wx.EVT_BUTTON, self.clear_output, id=4)
        # end wxGlade
        threading.Thread(target=self.start_hal).start()
        self.hal_title.SetBitmap(wx.Bitmap(os.path.join(get_main_dir(), 'Logo_V1.png'), wx.BITMAP_TYPE_PNG))
        self.normaleye = wx.Bitmap(os.path.join(get_main_dir(), 'Normal.png'), wx.BITMAP_TYPE_PNG)
        self.inverteye = wx.Bitmap(os.path.join(get_main_dir(), 'Buffering.png'), wx.BITMAP_TYPE_PNG)
        self.hal_icon.SetBitmap(self.normaleye)
        threading.Thread(target=self.blink).start()

    def __set_properties(self):
        # begin wxGlade: MainWin.__set_properties
        self.SetTitle(_("HAL, the Heurisic ALgorithmic Computer"))
        self.SetSize((700, 530))
        self.SetBackgroundColour(wx.Colour(240, 240, 240))
        self.hal_title.SetMinSize((392, 119))
        self.hal_icon.SetMinSize((119, 119))
        self.input.SetFocus()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MainWin.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(self.hal_title, 0, 0, 0)
        sizer_6.Add((0, 119), 1, 0, 0)
        sizer_6.Add(self.hal_icon, 0, 0, 0)
        sizer_1.Add(sizer_6, 0, wx.EXPAND, 0)
        sizer_3.Add(self.output, 1, wx.EXPAND, 0)
        sizer_4.Add(self.input, 1, wx.EXPAND, 0)
        sizer_4.Add(self.ask_btn, 0, 0, 0)
        sizer_3.Add(sizer_4, 0, wx.EXPAND, 0)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        sizer_5.Add(self.mute, 0, 0, 0)
        sizer_5.Add(self.stop_talking_btn, 0, 0, 0)
        sizer_5.Add(self.clear_out_btn, 0, 0, 0)
        sizer_2.Add(sizer_5, 0, wx.EXPAND, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade
    
    def start_hal(self):
        data = os.path.join(get_main_dir(), 'data')
        sys.stdout = RedirectText(self.output)
        print '[SYSTEM]', 'Booted on', get_system_info(), '[/SYSTEM]'
        print
        print 'Loading data files...'
        self.hal = HAL(speak=True)
        if not os.path.exists(data):
            print 'Your need a full package with the data folder'
            self.ask_btn.Enabled(False)
        print
        print '-HAL: Hello %s. I am HAL %s.'%(self.hal.user, self.hal.version)
        print
        prompt = '-%s:'%self.hal.user
        halpro = '-HAL:'
        length = max(len(prompt), len(halpro))
        if len(prompt) < length:
            prompt += ' '*(length-len(prompt))
        if len(halpro) < length:
            halpro += ' '*(length-len(halpro))
        self.prompt = prompt
        self.halpro = halpro

    def Ask(self, event):  # wxGlade: MainWin.<event_handler>
        self.input.Enable(False)
        input = self.input.GetValue()
        print self.prompt, input
        for i in self.hal.ask(input.encode('utf-8')):
            print self.halpro, i
        if not self.hal.running:
            print hal.shutdown()
            self.hal.running = True
        print
        self.input.Clear()
        self.input.Enable(True)
        self.input.SetFocus()

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
        self.Ask(event)
    
    def blink(self):
        while True:
            if not random.randint(0, 5):
                self.hal_icon.SetBitmap(self.inverteye)
                time.sleep(0.05)
                self.hal_icon.SetBitmap(self.normaleye)
            time.sleep(1)
                

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
