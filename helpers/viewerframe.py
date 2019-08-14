#!/usr/bin/python
# File Name : ViewerFrame.py
# Purpose :
# Creation Date : 06-18-2012
# Last Modified : Tue 19 Jun 2012 10:22:49 AM MDT
# Created By : Nathan Gilbert
#
import sys
import wx
import os

from pyconcile import annotation_set
from pyconcile import reconcile

ID_RESP = wx.NewId()

class ViewerFrame(wx.Frame):
    '''
    classdocs
    '''
    def __init__(self, parent, title):
        self.dirName = "/home/ngilbert/xspace/data/profile_tuning"
        self.fileName = ""
        self.response_chains = None
        self.gold_chains = None

        wx.Frame.__init__(self, parent, title=title, size=(600, 800))
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text_box_left = wx.TextCtrl(self, size=wx.Size(500, 400),
                              style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)

        self.text_box_middle = wx.TextCtrl(self, size=wx.Size(100, 400), style=wx.TE_MULTILINE | wx.TE_RICH)
        self.text_box_middle.SetBackgroundColour("lightgray")

        self.text_box_right = wx.TextCtrl(self, size=wx.Size(100, 400), style=wx.TE_MULTILINE | wx.TE_RICH)
        self.text_box_right.SetBackgroundColour("lightgray")

        self.text_box_sizer.Add(self.text_box_left, 1, wx.GROW)
        self.text_box_sizer.Add(self.text_box_middle, 1, wx.GROW)
        self.text_box_sizer.Add(self.text_box_right, 1, wx.GROW)
        self.main_sizer.Add(self.text_box_sizer, 1, wx.GROW)
        self.SetSizerAndFit(self.main_sizer)

        # Set up the menu.
        filemenu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        txtFile = filemenu.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Open the text")
        filemenu.AppendSeparator()
        respFile = filemenu.Append(ID_RESP, "Open the response file")
        filemenu.AppendSeparator()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")

        self.Bind(wx.EVT_MENU, self.OnFileOpen, txtFile)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.ReadInResponse, respFile)

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)

    def ReadInResponse(self, e):
        self.response_dir = ""
        dlg = wx.DirDialog(self, "Choose response directory", self.dirName)
        if (dlg.ShowModal() == wx.ID_OK):
            self.response_dir = dlg.GetPath().replace(self.dirName, "")
        dlg.Destroy()

        self.response_chains = reconcile.getResponseChains(self.dirName,
                self.response_dir)

        out = ""
        for chain in self.response_chains.keys():
            if len(self.response_chains[chain]) > 1:
                out += "-"*100 + "\n"
                for mention in self.response_chains[chain]:
                    out += "\t%s\n"  % (mention.ppprint())
                out += "-"*100 + "\n\n"
        self.text_box_middle.SetValue(out)


        out = ""
        for chain in self.gold_chains.keys():
            if len(self.gold_chains[chain]) > 1:
                out += "-"*100 + "\n"
                for mention in self.gold_chains[chain]:
                    out += "\t%s\n"  % (mention.ppprint())
                out += "-"*100 + "\n\n"
        self.text_box_right.SetValue(out)


    def OnFileOpen(self, e):
        """ File|Open event - Open dialog box. """
        dlg = wx.FileDialog(self, "Open", self.dirName, self.fileName,
                           "Text Files (*.txt)|*.txt|All Files|*.*", wx.OPEN)
        if (dlg.ShowModal() == wx.ID_OK):
            self.fileName = dlg.GetFilename()
            self.dirName = dlg.GetDirectory()
            f = file(os.path.join(self.dirName, self.fileName), 'r')
            self.fullText = ''.join(f.readlines())
            self.text_box_left.SetValue(self.fullText)
            f.close()
        dlg.Destroy()

        self.gold_chains = reconcile.getGoldChains(self.dirName)

    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "A program for viewing Reconcile's mistakes", "Reconcile Response Viewer", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self, e):
        self.Close(True)  # Close the frame.

