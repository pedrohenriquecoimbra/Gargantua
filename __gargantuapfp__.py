"""Required libraries"""

import datetime
import multiprocessing
import threading
import ast
import importlib
import pandas as pd
import numpy as np
import random
from collections import OrderedDict
from io import StringIO
import queue
import inspect
import ntpath
from PIL import ImageTk, Image, ImageDraw

#from tkinter import *
from tkinter import ttk
from tkinter.messagebox import askyesnocancel, askquestion
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames, asksaveasfilename
import tkinter as tk

import matplotlib
matplotlib.use("QT5Agg")
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from __scripts__.PyFluxPro.scripts import cfg, pfp_compliance, pfp_gui, pfp_io, pfp_log, pfp_threading, pfp_top_level, pfp_utils

import art
from __scripts__ import gargantua as gg, common as gt, tk_commons as tktt, versions
import sys
import threading, multiprocessing, queue
import warnings
import time
import pathlib
import copy
import os
import re
import uuid
import glob
# for full_menu and actvate_menu
#from .common import readable_file, LazyCallable


pcd = pathlib.Path(__file__).parent.resolve()
LIMIT_TIME_OUT = 30*60 # in seconds
_fcs = {}

def import_lib(lib):
    _fcs = gt.importlib_to_globals(os.path.join(pcd, "Lib", lib, "main.py"))
    #print(globals().keys())
    #print(_fcs)
    return


def dummy_call(*args, fc=print, **kwargs):
    fc('---')
    fc(args)
    fc(kwargs)
    time.sleep(5)
    return


def menufromfile(path, *args):
	# GET SETUP
    #setup = gg.readable_file(path).safe_load().to_refdict()
    setup = gg.readable_file(path).safe_load().to_dict()
    for add in args:
        setup = gt.update_nested_dict(
            setup, gg.readable_file(add).safe_load().to_dict())
    return setup


def menuupdate(setup, _ref=True, _kinit=True, **kwargs):
    setup = gt.update_nested_dict(setup, kwargs)
    if _ref:
        setup = gg.referencedictionary(setup, kinit=_kinit)
    return setup

def api(*args, path=None, setup=None, _fc_=None, block=[], nproc=1, nthread=1, **kwargs):
    # UPDATE SETUP 
    if path:
        if isinstance(path, str):
            path = [path]
        setup = menufromfile(*path)
    setup = menuupdate(setup, **kwargs)
    #setup = gt.update_nested_dict(setup, kwargs)
    #setup = gg.referencedictionary(setup, kinit=True)
    
    # RUN
    def api_run(*args, nthread=nthread, nproc=nproc, **kwargs):
        jobs = []
        #print("nthread", nthread, "nproc", nproc)
        for fc, kw in args:
            print(f'¤ {fc.__name__}')
            try:
                if nthread > 1:
                    jobs += [threading.Thread(target=fc, kwargs=kw)]
                    jobs[-1].start()
                elif nproc > 1:
                    jobs += [multiprocessing.Process(target=fc, kwargs=kw)]
                    jobs[-1].start()
                else:
                    fc(**kw)
            except Exception as e:
                warnings.warn(e)
        
        for job in jobs:
            job.join()

    if _fc_ is None:
        _fc_ = {f: {'fc': gg.LazyCallable(gt.trygetfromdict(setup, [f, '__init__', 'path'], setup['__init__']['main']),
                                          gt.trygetfromdict(setup, [f, '__init__', 'function'], f)).__get__().fc,
            'kw': {k: v for k, v in setup[f].items() if k.startswith('__')*k.endswith('__') == False}}
            for f, _ in setup.items() if f.startswith('__')*f.endswith('__') == False and f in gt.flist(block)}

    for r in block:
        if isinstance(r, str):
            api_run([_fc_[r][k] for k in ["fc", "kw"]])
        else:
            print(_fc_.keys())
            # run in parallel and wait end of execution
            api_run(*[[_fc_[el][k] for k in ["fc", "kw"]]
                    for el in gt.flist([r])])
            #for c in r:
               #for el in c:
                   #print(el)
    return

#globals().update({_as: gg.LazyCallable(os.path.join(pathlib.Path(__file__).parent.resolve(), _md)).__get__().fc for _md, _as in [(, tktt)]})

SYSTEM_KEYS = ['__init__', '__routine__']
DEFAULT_FILE_TYPES = (("yaml file (.yaml)", "*.yaml"),
                      ("Text file (.txt)", "*.txt"),
                      ("Setup file (.setup)", "*.setup"),
                      ("Meta file (.meta)", "*.meta"),
                      ("Addon file (.stppls)", "*.stppls"),
                      ("All files (.*)", "*.*"))
MEMORY_DATAFRAME = pd.DataFrame()


def running_message(fc, md, par=None, nt=None, message="", start="¤ Running\n", end="\n"):
    rm = start + f"Thread: {fc}\nModule: {md}"
    if par:
        rm += f"\nMode: {par}"
    if nt:
        rm += f"\nParallel: {nt}"
    rm += f"\nStart: {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M')}"
    if message:
        rm += f"\n{message}"
    return rm + end


def update_nested_dict(d, u):
    d = d if isinstance(d, dict) else {}
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = update_nested_dict(d.get(k, {}), v)
        else:
            if isinstance(d, dict):
                d[k] = v
            else:
                d = {k: v}
    return d


def rename_nested_dict(d, u):
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = rename_nested_dict(
                d.get(k, {}) if isinstance(d, dict) else {}, v)
        else:
            d[v] = d.pop(k, None)
    return d


def trygetfromdict(d, keys, default=None):
    try:
        d_ = d
        for k in keys:
            d_ = d_[k]
        return d_
    except:
        return default


def full_menu(*args, wait=True, waitimg="", waittxt="", **kwargs):
    def wait_page(root, wait=True, waitimg="", waittxt=""):
        # Create a new window
        root.wait = tk.Toplevel()
        root.wait.resizable(width=False, height=False)
        root.wait.attributes('-topmost', True)
        root.wait.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
        #root.wait.attributes('-topmost', False)

        # get the screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # set the window size
        top_width = 800
        top_height = 450
        root.wait.geometry(f"{top_width}x{top_height}")

        # calculate the position to center the window
        x = (screen_width // 2) - (top_width // 2)
        y = (screen_height // 2) - (top_height // 2)

        # set the window position
        root.wait.geometry("+{}+{}".format(x, y))

        # Remove the title bar
        root.wait.overrideredirect(True)

        # create a canvas to display the photo image
        canvas = tk.Canvas(root.wait, width=top_width, height=top_height)
        canvas.pack()

        credits = ''

        if waitimg and os.path.isdir(waitimg):
            if os.path.exists(os.path.join(waitimg, 'credits.txt')):
                with open(os.path.join(waitimg, 'credits.txt')) as input_file:
                    credits = input_file.readline()
            waitimg = random.choice([os.path.join(waitimg, f) for f in os.listdir(
                waitimg) if f.endswith(('.jpg', '.jpeg', '.png', '.webp', '.ico'))])
            if os.path.exists(waitimg.rsplit('.', 1)[0] + '.credits'):
                with open(waitimg.rsplit('.', 1)[0] + '.credits') as input_file:
                    credits = input_file.readline()
        if waitimg and os.path.exists(waitimg):
            # Load the image
            image = Image.open(waitimg)
            width, height = image.size
            if width/height > top_width/top_height:
                image = image.resize(
                    (int(width * (top_height / height)), top_height), Image.Resampling.LANCZOS)
            else:
                image = image.resize(
                    (top_width, int(height * (top_width / width))), Image.Resampling.LANCZOS)
            canvas.image = ImageTk.PhotoImage(image)
        else:
            # create a new 400x400 pixel image with a black background (if 0, 0, 0)
            image = Image.new("RGBA", (top_width, top_height), (0, 157, 196))

            # create an ImageDraw object to draw on the image
            draw = ImageDraw.Draw(image)

            # draw 50 circles with random colors and positions
            for _ in range(100):
                # generate a random color
                color = (random.randint(0, 255), random.randint(
                    0, 255), random.randint(0, 255), 255)
                # generate a random position for the circle
                x = random.randint(0, top_width)
                y = random.randint(0, top_height)
                x0, y0 = x, y
                maindir = ((-1)**random.randint(1, 2),
                           (-1)**random.randint(1, 2))

                # draw random pollock
                for _ in range(random.randint(100, 800)):
                    chance = np.random.standard_gamma(10, 1)
                    axis = random.randint(1, 2)
                    if chance > 50:
                        maindir[axis] = maindir[axis] * (-1)

                    # generate a random radius for the circle
                    radius = int(np.random.gamma(10, 0.2, 1)*5) + 1
                    x1 = x0+maindir[0]+(-1)**(radius*random.randint(1, 2))
                    y1 = y0+maindir[1]+(-1)**(radius*random.randint(1, 2))
                    draw.ellipse((x1-radius, y1-radius, x1 +
                                 radius, y1+radius), fill=color)
                    x0, y0 = x1, y1

            # create a Tkinter-compatible photo image from the Pillow image
            canvas.image = ImageTk.PhotoImage(image)

            # root.wait, (top_width, top_height), (0, 157, 196))
            canvaspaint = tktt.CanvasPaint(canvas, image, width=0, height=0)
            canvaspaint.pack()
            #canvas.image = ImageTk.PhotoImage(canvaspaint.image)

        canvas.create_image(int(top_width//2), int(top_height//2),
                            anchor="center", image=canvas.image)
        if credits:
            canvas.create_text(int(top_width)-2, int(top_height)-2, anchor='se',
                               text=credits, font=("Arial", 12), fill='white')

        if waittxt:
            canvas.create_text(int(top_width//2), int(top_height//2), justify='center',
                               text=waittxt, font=("Garamond", 40), fill='white', activefill="black", disabledfill="white")
        return root.wait

    def open_interface(*args, **kwargs):
        opf_main_ui(*args, **kwargs)
        root.deiconify()
        root.attributes('-topmost', True)
        root.attributes('-topmost', False)
        root.wait.withdraw()


    if wait == False:
        opf_main_ui(root, *args, **kwargs)
    else:
        root = tk.Tk()
        root.withdraw()
        root.wait = wait_page(root, wait, waitimg, waittxt)
        #root.wait.set_focus()
        threading.Thread(target=open_interface, args=args, kwargs=kwargs).start()
        #root.after(1000, lambda r=root, a=args, k=kwargs: open_interface(r, *a, **k))
        root.after(10000, lambda: root.wait.overrideredirect(False))
        root.mainloop()
    #exit(0)


class opf_main_ui(QWidget):
    def __init__(self, pfp_version, textBox, lib="OpenFlux", path=None, addons=[],
                 welcometxt='¤ WELCOME, WILKOMEN, BIENVENUE\n',
                 create="enable", remove="enable", modify=True, sort="disabled", move=True):
        super(pfp_main_ui, self).__init__()
        # set the mode attribute
        self.mode = "interactive"
        # menu bar
        self.menubar = QMenuBar(self)
        # File menu
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setTitle("File")
        # File/Convert submenu
        self.menuFileConvert = QMenu(self.menuFile)
        self.menuFileConvert.setTitle("Convert")
        # Edit menu
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setTitle("Edit")
        # Run menu
        self.menuRun = QMenu(self.menubar)
        self.menuRun.setTitle("Run")
        # Plot menu
        self.menuPlot = QMenu(self.menubar)
        self.menuPlot.setTitle("Plot")
        # Utilities menu
        self.menuUtilities = QMenu(self.menubar)
        self.menuUtilities.setTitle("Utilities")
        # Utilities/u* threshold submenu
        self.menuUtilitiesUstar = QMenu(self.menuUtilities)
        self.menuUtilitiesUstar.setTitle("u* threshold")
        # Help menu
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setTitle("Help")
        # File menu items: menu actions for control files
        self.actionFileProfile = QAction(self)
        self.actionFileProfile.setText("Profile")
        self.actionFileOpen = QAction(self)
        self.actionFileOpen.setText("Open")
        self.actionFileOpen.setShortcut('Ctrl+O')
        self.actionFileAddon = QAction(self)
        self.actionFileAddon.setText("Add-on")
        self.actionFileSave = QAction(self)
        self.actionFileSave.setText("Save")
        self.actionFileSave.setShortcut('Ctrl+S')
        self.actionFileSaveAs = QAction(self)
        self.actionFileSaveAs.setText("Save As...")
        self.actionFileSaveAs.setShortcut('Shift+Ctrl+S')
        self.actionFileRestart = QAction(self)
        self.actionFileRestart.setText("Restart")
        # File/Convert submenu
        self.actionFileConvertnc2biomet = QAction(self)
        self.actionFileConvertnc2biomet.setText("nc to Biomet")
        self.actionFileConvertnc2xls = QAction(self)
        self.actionFileConvertnc2xls.setText("nc to Excel")
        self.actionFileConvertnc2reddyproc = QAction(self)
        self.actionFileConvertnc2reddyproc.setText("nc to REddyProc")
        # File menu item: split netCDF
        self.actionFileSplit = QAction(self)
        self.actionFileSplit.setText("Split")
        self.actionFileSplit.setShortcut('Ctrl+P')
        # File menu item: Quit
        self.actionFileQuit = QAction(self)
        self.actionFileQuit.setText("Quit")
        # the Vinod mod ...
        self.actionFileQuit.setShortcut('Ctrl+Q')
        # Edit menu items
        self.actionEditPreferences = QAction(self)
        self.actionEditPreferences.setText("Preferences...")
        self.actionEditStringize = QAction(self)
        self.actionEditStringize.setText("String")
        self.actionEditCast = QAction(self)
        self.actionEditCast.setText("Cast")
        # Run menu items
        self.actionRunCurrent = QAction(self)
        self.actionRunCurrent.setText("Current...")
        self.actionRunCurrent.setShortcut('Ctrl+R')
        self.actionRunClearLogWindow = QAction(self)
        self.actionRunClearLogWindow.setText("Clear log window")
        self.actionStopCurrent = QAction(self)
        self.actionStopCurrent.setText("Stop run")
        # Plot menu items
        #self.actionPlotFcVersusUstar = QAction(self)
        #self.actionPlotFcVersusUstar.setText("Fco2 vs u*")
        # Plot Fco2 vs u* submenu
        self.menuPlotFco2vsUstar = QMenu(self.menuPlot)
        self.menuPlotFco2vsUstar.setTitle("Fco2 vs u*")
        self.actionPlotFingerprints = QAction(self)
        self.actionPlotFingerprints.setText("Fingerprints")
        self.actionPlotQuickCheck = QAction(self)
        self.actionPlotQuickCheck.setText("Summary")
        self.actionPlotTimeSeries = QAction(self)
        self.actionPlotTimeSeries.setText("Time series")
        self.actionPlotWindrose = QAction(self)
        self.actionPlotWindrose.setText("Windrose")
        self.actionPlotClosePlots = QAction(self)
        self.actionPlotClosePlots.setText("Close plots")
        # Plot Fco2 vs u* submenu
        self.actionPlotFco2vsUstar_annual = QAction(self)
        self.actionPlotFco2vsUstar_annual.setText("Annual")
        self.actionPlotFco2vsUstar_seasonal = QAction(self)
        self.actionPlotFco2vsUstar_seasonal.setText("Seasonal")
        self.actionPlotFco2vsUstar_monthly = QAction(self)
        self.actionPlotFco2vsUstar_monthly.setText("Monthly")
        # Utilities menu
        self.actionUtilitiesClimatology = QAction(self)
        self.actionUtilitiesClimatology.setText("Climatology")
        self.actionUtilitiesUstarCPDBarr = QAction(self)
        self.actionUtilitiesUstarCPDBarr.setText("CPD (Barr)")
        self.actionUtilitiesUstarCPDMcHugh = QAction(self)
        self.actionUtilitiesUstarCPDMcHugh.setText("CPD (McHugh)")
        self.actionUtilitiesUstarCPDMcNew = QAction(self)
        self.actionUtilitiesUstarCPDMcNew.setText("CPD (McNew)")
        self.actionUtilitiesUstarMPT = QAction(self)
        self.actionUtilitiesUstarMPT.setText("MPT")
        #self.actionUtilitiesCFCheck = QAction(self)
        #self.actionUtilitiesCFCheck.setText("CF check")
        # Help menu
        self.actionHelpWiki = QAction(self)
        self.actionHelpWiki.setText("Wiki")
        self.actionHelpAbout = QAction(self)
        self.actionHelpAbout.setText("About")
        self.actionHelpMeta = QAction(self)
        self.actionHelpMeta.setText("Save .meta")
        self.actionHelpRoutine = QAction(self)
        self.actionHelpRoutine.setText("Save .routine")
        self.actionHelpLastconfig = QAction(self)
        self.actionHelpLastconfig.setText("Save .lastconfig")
        # add the actions to the menus
        # File/Convert submenu
        self.menuFileConvert.addAction(self.actionFileConvertnc2xls)
        self.menuFileConvert.addAction(self.actionFileConvertnc2biomet)
        self.menuFileConvert.addAction(self.actionFileConvertnc2reddyproc)
        # File menu
        self.menuFile.addAction(self.actionFileOpen)
        self.menuFile.addAction(self.actionFileAddon)
        self.menuFile.addAction(self.actionFileSave)
        self.menuFile.addAction(self.actionFileSaveAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.menuFileConvert.menuAction())
        self.menuFile.addAction(self.actionFileSplit)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionFileQuit)
        # Edit menu
        self.menuEdit.addAction(self.actionEditPreferences)
        self.menuEdit.addAction(self.actionEditStringize)
        self.menuEdit.addAction(self.actionEditCast)
        # Run menu
        self.menuRun.addAction(self.actionRunCurrent)
        self.menuRun.addAction(self.actionRunClearLogWindow)
        # Plot Fco2 vs u* submenu
        self.menuPlotFco2vsUstar.addAction(self.actionPlotFco2vsUstar_annual)
        self.menuPlotFco2vsUstar.addAction(self.actionPlotFco2vsUstar_seasonal)
        self.menuPlotFco2vsUstar.addAction(self.actionPlotFco2vsUstar_monthly)
        # Plot menu
        #self.menuPlot.addAction(self.actionPlotFcVersusUstar)
        self.menuPlot.addAction(self.menuPlotFco2vsUstar.menuAction())
        self.menuPlot.addAction(self.actionPlotFingerprints)
        self.menuPlot.addAction(self.actionPlotQuickCheck)
        self.menuPlot.addAction(self.actionPlotTimeSeries)
        self.menuPlot.addAction(self.actionPlotWindrose)
        self.menuPlot.addSeparator()
        self.menuPlot.addAction(self.actionPlotClosePlots)
        # Utilities/u* threshold submenu
        self.menuUtilitiesUstar.addAction(self.actionUtilitiesUstarCPDBarr)
        self.menuUtilitiesUstar.addAction(self.actionUtilitiesUstarCPDMcHugh)
        self.menuUtilitiesUstar.addAction(self.actionUtilitiesUstarCPDMcNew)
        self.menuUtilitiesUstar.addAction(self.actionUtilitiesUstarMPT)
        # Utilities menu
        self.menuUtilities.addAction(self.actionUtilitiesClimatology)
        self.menuUtilities.addAction(self.menuUtilitiesUstar.menuAction())
        #self.menuUtilities.addAction(self.actionUtilitiesCFCheck)
        # add individual menus to menu bar
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuRun.menuAction())
        self.menubar.addAction(self.menuPlot.menuAction())
        self.menubar.addAction(self.menuUtilities.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        # Help menu
        self.menuHelp.addAction(self.actionHelpWiki)
        self.menuHelp.addAction(self.actionHelpAbout)

        # create a tab bar
        self.tabs = QTabWidget(self)
        self.tabs.tab_index_all = 0
        self.tabs.tab_index_current = 0
        self.tabs.tab_dict = {}
        # make the tabs closeable
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        # add the text editor to the first tab
        self.tabs.addTab(textBox, "Log")
        self.tabs.tab_index_all = self.tabs.tab_index_all + 1
        # hide the tab close icon for the console tab
        self.tabs.tabBar().setTabButton(0, QTabBar.RightSide, None)
        # connect the tab-in-focus signal to the appropriate slot
        self.tabs.currentChanged[int].connect(self.tabSelected)

        # use VBoxLayout to position widgets so they resize with main window
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        # add widgets to the layout
        layout.addWidget(self.menubar)
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.setGeometry(50, 50, 800, 600)
        self.setWindowTitle(pfp_version)

        self.threadpool = QThreadPool()

        # Connect signals to slots
        # File menu actions
        self.actionFileConvertnc2biomet.triggered.connect(
            lambda: pfp_top_level.do_file_convert_nc2biomet(None, mode="standard"))
        self.actionFileConvertnc2xls.triggered.connect(
            pfp_top_level.do_file_convert_nc2xls)
        self.actionFileConvertnc2reddyproc.triggered.connect(
            lambda: pfp_top_level.do_file_convert_nc2reddyproc(None, mode="standard"))
        self.actionFileOpen.triggered.connect(self.file_open)
        self.actionFileOpen.triggered.connect(self.file_open_addon)
        self.actionFileSave.triggered.connect(self.file_save)
        self.actionFileSaveAs.triggered.connect(self.file_save_as)
        self.actionFileSplit.triggered.connect(pfp_top_level.do_file_split)
        self.actionFileQuit.triggered.connect(QApplication.quit)
        # Edit menu actions
        self.actionEditPreferences.triggered.connect(self.edit_preferences)
        # Run menu actions
        self.actionRunCurrent.triggered.connect(self.run_current)
        self.actionRunClearLogWindow.triggered.connect(
            self.run_clear_log_window)
        # Plot menu actions
        self.actionPlotFco2vsUstar_annual.triggered.connect(
            pfp_top_level.do_plot_fcvsustar_annual)
        self.actionPlotFco2vsUstar_seasonal.triggered.connect(
            pfp_top_level.do_plot_fcvsustar_seasonal)
        self.actionPlotFco2vsUstar_monthly.triggered.connect(
            pfp_top_level.do_plot_fcvsustar_monthly)
        self.actionPlotFingerprints.triggered.connect(
            pfp_top_level.do_plot_fingerprints)
        self.actionPlotQuickCheck.triggered.connect(
            pfp_top_level.do_plot_quickcheck)
        self.actionPlotTimeSeries.triggered.connect(
            pfp_top_level.do_plot_timeseries)
        self.actionPlotWindrose.triggered.connect(
            pfp_top_level.do_plot_windrose_standard)
        self.actionPlotClosePlots.triggered.connect(
            pfp_top_level.do_plot_closeplots)
        # Utilities menu actions
        self.actionUtilitiesClimatology.triggered.connect(
            self.utilities_climatology_standard)
        self.actionUtilitiesUstarCPDBarr.triggered.connect(
            self.utilities_ustar_cpd_barr_standard)
        self.actionUtilitiesUstarCPDMcHugh.triggered.connect(
            self.utilities_ustar_cpd_mchugh_standard)
        self.actionUtilitiesUstarCPDMcNew.triggered.connect(
            self.utilities_ustar_cpd_mcnew_standard)
        self.actionUtilitiesUstarMPT.triggered.connect(
            self.utilities_ustar_mpt_standard)
        #self.actionUtilitiesCFCheck.triggered.connect(self.utilities_cfcheck)
        # Help menu actions
        self.actionHelpWiki.triggered.connect(self.help_wiki)
        self.actionHelpAbout.triggered.connect(self.help_about)
        # add the L4 GUI
        self.l4_ui = pfp_gui.pfp_l4_ui(self)
        # add the L5 GUI
        self.solo_gui = pfp_gui.solo_gui(self)

    def file_open(self, file_uri=None):
        """
        Purpose:
         Get a file name, figure out if it is a control file or a netCDF
         file and try to open it.
        """
        # local logger
        logger = logging.getLogger(name="pfp_log")
        # get the control file path
        if not file_uri:
            file_uri = QFileDialog.getOpenFileName(
                caption="Choose a file ...")[0]
            # check to see if file open was cancelled
            if len(str(file_uri)) == 0:
                return
        self.file_uri = str(file_uri)
        # read the contents of the control file
        logger.info(" Opening " + self.file_uri)
        # check to see if it is a control file
        file_open_success = False
        if not file_open_success:
            try:
                self.file = ConfigObj(self.file_uri, indent_type="    ", list_values=False,
                                      write_empty_values=True)
                file_open_success = True
            except Exception:
                # trying to open a netCDF file will throw UnicodeDecodeError
                # opening a ConfigObj file with syntax erros throws ConfigObjError
                exc_type, _, _ = sys.exc_info()
                if exc_type.__name__ == "UnicodeDecodeError":
                    # most likely a netCDF file
                    pass
                elif exc_type.__name__ == "ConfigObjError":
                    # syntax error in control file
                    msg = "Syntax error in control file, see below for line number"
                    logger.error(msg)
                    error_message = traceback.format_exc()
                    logger.error(error_message)
                    return
                else:
                    # unrecognised file type
                    msg = "File must be either a control file or a netCDF file"
                    logger.error(msg)
                    error_message = traceback.format_exc()
                    logger.error(error_message)
                    return
        # check to see if it is a netCDF file
        if not file_open_success:
            try:
                self.file = netCDF4.Dataset(self.file_uri, "r")
                file_open_success = True
            except:
                # unrecognised file type
                msg = "File must be either a control file or a netCDF file"
                logger.error(msg)
                error_message = traceback.format_exc()
                logger.error(error_message)
                return
        # do the business depending on the file type
        if isinstance(self.file, ConfigObj):
            # we are opening a control file
            self.open_control_file()
        elif isinstance(self.file, netCDF4._netCDF4.Dataset):
            # we are opening a netCDF file
            self.open_netcdf_file()
        else:
            # unrecognised file type
            msg = "File must be either a control file or a netCDF file"
            logger.error(msg)
            error_message = traceback.format_exc()
            logger.error(error_message)
        return

    def help_about(self):
        msg = cfg.version_name + " " + cfg.version_number + "\n"
        msg += "Contributors: Peter Isaac, Jamie Cleverly, Cacilia Ewenz, Ian McHugh"
        pfp_gui.myMessageBox(msg)
        return

    def help_wiki(self):
        """ Opens the default browser and goes to the PyFluxPro Wiki."""
        browser = webbrowser.get()
        browser.open_new("https://github.com/OzFlux/PyFluxPro/wiki")
        return

    def open_control_file(self):
        logger = logging.getLogger(name="pfp_log")
        # check to see if the processing level is defined in the control file
        if "level" not in self.file:
            # if not, then sniff the control file to see what it is
            self.file["level"] = self.get_cf_level()
            # and save the control file
            self.file.write()
        # create a QtTreeView to edit the control file
        if self.file["level"] in ["L1"]:
            # update control file to new syntax
            if not pfp_compliance.l1_update_controlfile(self.file):
                return
            # put the GUI for editing the L1 control file in a new tab
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_L1(
                self)
        elif self.file["level"] in ["L2"]:
            if not pfp_compliance.l2_update_controlfile(self.file):
                return
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_L2(
                self)
        elif self.file["level"] in ["L3"]:
            if not pfp_compliance.l3_update_controlfile(self.file):
                return
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_L3(
                self)
        elif self.file["level"] in ["concatenate"]:
            if not pfp_compliance.concatenate_update_controlfile(self.file):
                return
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_concatenate(
                self)
        elif self.file["level"] in ["climatology"]:
            if not pfp_compliance.climatology_update_controlfile(self.file):
                return
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_climatology(
                self)
        elif self.file["level"] in ["cpd_barr"]:
            if not pfp_compliance.cpd_barr_update_controlfile(self.file):
                return
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_cpd_barr(
                self)
        elif self.file["level"] in ["cpd_mchugh"]:
            if not pfp_compliance.cpd_mchugh_update_controlfile(self.file):
                return
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_cpd_mchugh(
                self)
        elif self.file["level"] in ["cpd_mcnew"]:
            if not pfp_compliance.cpd_mcnew_update_controlfile(self.file):
                return
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_cpd_mcnew(
                self)
        elif self.file["level"] in ["mpt"]:
            if not pfp_compliance.mpt_update_controlfile(self.file):
                return
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_mpt(
                self)
        elif self.file["level"] in ["L4"]:
            if not pfp_compliance.l4_update_controlfile(self.file):
                return
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_L4(
                self)
        elif self.file["level"] in ["L5"]:
            if not pfp_compliance.l5_update_controlfile(self.file):
                return
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_L5(
                self)
        elif self.file["level"] in ["L6"]:
            if not pfp_compliance.l6_update_controlfile(self.file):
                return
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_L6(
                self)
        elif self.file["level"] in ["nc2csv_biomet"]:
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_nc2csv_biomet(
                self)
        elif self.file["level"] in ["nc2csv_ecostress"]:
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_nc2csv_ecostress(
                self)
        elif self.file["level"] in ["nc2csv_fluxnet"]:
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_nc2csv_fluxnet(
                self)
        elif self.file["level"] in ["nc2csv_reddyproc"]:
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_nc2csv_reddyproc(
                self)
        elif self.file["level"] in ["batch"]:
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_batch(
                self)
        elif self.file["level"] in ["windrose"]:
            self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.edit_cfg_windrose(
                self)
        else:
            logger.error(" Unrecognised control file type: " +
                         self.file["level"])
            return
        # add a tab for the control file
        tab_title = os.path.basename(str(self.file_uri))
        self.tabs.addTab(
            self.tabs.tab_dict[self.tabs.tab_index_all], tab_title)
        self.tabs.setCurrentIndex(self.tabs.tab_index_all)
        self.tabs.tab_index_all = self.tabs.tab_index_all + 1
        return

    def open_netcdf_file(self):
        file_uri = self.file.filepath()
        # close the netCDF file
        self.file.close()
        # read the netCDF file to a data structure
        self.ds = pfp_io.NetCDFRead(file_uri, checktimestep=False)
        if self.ds.info["returncodes"]["value"] != 0:
            return
        # display the netcdf file in the GUI
        self.tabs.tab_dict[self.tabs.tab_index_all] = pfp_gui.file_explore(
            self)
        # return if something went wrong
        if self.tabs.tab_dict[self.tabs.tab_index_all].ds.info["returncodes"]["value"] != 0:
            return
        # add a tab for the netCDF file contents
        tab_title = os.path.basename(self.ds.info["filepath"])
        self.tabs.addTab(
            self.tabs.tab_dict[self.tabs.tab_index_all], tab_title)
        self.tabs.setCurrentIndex(self.tabs.tab_index_all)
        self.tabs.tab_index_all = self.tabs.tab_index_all + 1
        return

    def get_cf_level(self):
        """ Sniff the control file to find out it's type."""
        logger = logging.getLogger(name="pfp_log")
        self.file["level"] = ""
        # check for L1
        if self.check_cfg_L1():
            logger.info(" L1 control file detected")
            self.file["level"] = "L1"
        # check for L2
        elif self.check_cfg_L2():
            logger.info(" L2 control file detected")
            self.file["level"] = "L2"
        # check for L3
        elif self.check_cfg_L3():
            logger.info(" L3 control file detected")
            self.file["level"] = "L3"
        # check for concatenate
        elif self.check_cfg_concatenate():
            logger.info(" Concatenate control file detected")
            self.file["level"] = "concatenate"
        # check for L4
        elif self.check_cfg_L4():
            logger.info(" L4 control file detected")
            self.file["level"] = "L4"
        # check for L5
        elif self.check_cfg_L5():
            logger.info(" L5 control file detected")
            self.file["level"] = "L5"
        # check for L6
        elif self.check_cfg_L6():
            logger.info(" L6 control file detected")
            self.file["level"] = "L6"
        else:
            logger.info(" Unable to detect level, enter manually ...")
            text, ok = QInputDialog.getText(
                self, 'Processing level', 'Enter the processing level:')
            if ok:
                self.file["level"] = text
        return self.file["level"]

    def check_cfg_L1(self):
        """ Return true if a control file is an L1 file."""
        result = False
        try:
            cfg_sections = list(self.file.keys())
            # remove the common sections
            common_sections = ["level", "controlfile_name", "Files", "Global", "Output",
                               "Plots", "General", "Options", "Soil", "Massman", "GUI"]
            for section in list(self.file.keys()):
                if section in common_sections:
                    cfg_sections.remove(section)
            # now loop over the remaining sections
            for section in cfg_sections:
                subsections = list(self.file[section].keys())
                for subsection in subsections:
                    if "Attr" in list(self.file[section][subsection].keys()):
                        result = True
                        break
        except:
            result = False
        return result

    def check_cfg_L2(self):
        """ Return true if a control file is an L2 file."""
        result = False
        try:
            got_sections = False
            cfg_sections = list(self.file.keys())
            if (("Files" in cfg_sections) and
                    ("Variables" in cfg_sections)):
                got_sections = True
            # loop over [Variables] sections
            got_qc = False
            qc_list = ["RangeCheck", "DiurnalCheck", "ExcludeDates", "DependencyCheck", "UpperCheck",
                       "LowerCheck", "ExcludeHours", "Linear", "CorrectWindDirection"]
            for section in ["Variables"]:
                subsections = list(self.file[section].keys())
                for subsection in subsections:
                    for qc in qc_list:
                        if qc in list(self.file[section][subsection].keys()):
                            got_qc = True
                            break
            # final check
            if got_sections and got_qc and not self.check_cfg_L3() and not self.check_cfg_L4():
                result = True
        except:
            result = False
        return result

    def check_cfg_L3(self):
        """ Return true if a control file is an L3 file."""
        result = False
        try:
            cfg_sections = list(self.file.keys())
            if ((("General" in cfg_sections) or
                ("Soil" in cfg_sections) or
                ("Massman" in cfg_sections)) and
                    ("Options" in cfg_sections)):
                result = True
        except:
            result = False
        return result

    def check_cfg_concatenate(self):
        """ Return true if control file is concatenation."""
        result = False
        try:
            cfg_sections = list(self.file.keys())
            if "Files" in cfg_sections:
                if (("Out" in list(self.file["Files"].keys())) and
                        ("In" in list(self.file["Files"].keys()))):
                    result = True
        except:
            result = False
        return result

    def check_cfg_L4(self):
        """ Return true if control file is L4."""
        result = False
        try:
            cfg_sections = list(self.file.keys())
            for section in cfg_sections:
                if section in ["Variables", "Drivers", "Fluxes"]:
                    subsections = list(self.file[section].keys())
                    for subsection in subsections:
                        if (("GapFillFromAlternate" in list(self.file[section][subsection].keys())) or
                                ("GapFillFromClimatology" in list(self.file[section][subsection].keys()))):
                            result = True
                            break
        except:
            result = False
        return result

    def check_cfg_L5(self):
        """ Return true if control file is L5."""
        result = False
        try:
            cfg_sections = list(self.file.keys())
            for section in cfg_sections:
                if section in ["Variables", "Drivers", "Fluxes"]:
                    subsections = list(self.file[section].keys())
                    for subsection in subsections:
                        if (("GapFillUsingSOLO" in list(self.file[section][subsection].keys())) or
                                ("GapFillUsingMDS" in list(self.file[section][subsection].keys()))):
                            result = True
                            break
        except:
            result = False
        return result

    def check_cfg_L6(self):
        """ Return true if control file is L6."""
        result = False
        try:
            cfg_sections = list(self.file.keys())
            if ("EcosystemRespiration" in cfg_sections or
                "NetEcosystemExchange" in cfg_sections or
                    "GrossPrimaryProductivity" in cfg_sections):
                result = True
        except:
            result = False
        return result

    def direct_run(self):
        """ Placeholder until full implementation done."""
        logger = logging.getLogger(name="pfp_log")
        msg = " Open control file and use 'Run/Current ...'"
        logger.warning(msg)
        return

    def file_save(self):
        """ Save the current file."""
        logger = logging.getLogger(name="pfp_log")
        # get the current tab index
        tab_index_current = self.tabs.tab_index_current
        # trap user attempts to save the Log window :=) thanks, Craig Macfarlane!
        if tab_index_current == 0:
            msg = "Log files are automatically saved" + "\n"
            msg += "in the PyFluxPro" + os.sep + "logfiles folder"
            pfp_gui.MsgBox_Continue(msg)
            return
        content = self.tabs.tab_dict[tab_index_current].get_data_from_model()
        if isinstance(content, ConfigObj):
            # we are saving a control file
            self.save_control_file()
        elif isinstance(content, pfp_io.DataStructure):
            # we are saving a data structure
            self.save_netcdf_file()
        else:
            # unrecognised content type
            msg = "Object must be either a control file or a data structure"
            logger.error(msg)
        return

    def save_control_file(self):
        """ Save the current tab as a control file."""
        logger = logging.getLogger(name="pfp_log")
        # get the current tab index
        tab_index_current = self.tabs.tab_index_current
        # get the updated control file data
        cfg = self.tabs.tab_dict[tab_index_current].get_data_from_model()
        # check to make sure we are not overwriting the template version
        if "template" in cfg.filename:
            msg = " You are trying to write to the template folder.\n"
            msg = msg + "Please save this control file to a different location."
            pfp_gui.myMessageBox(msg)
            # put up a "Save as ..." dialog
            cfg_filename = QFileDialog.getSaveFileName(self, "Save as ...")[0]
            # return without doing anything if cancel used
            if len(str(cfg_filename)) == 0:
                return
            # set the control file name
            cfg.filename = str(cfg_filename)
        # write the control file
        msg = " Saving " + cfg.filename
        logger.info(msg)
        cfg.write()
        # remove the asterisk in the tab text
        tab_text = str(self.tabs.tabText(tab_index_current))
        self.tabs.setTabText(self.tabs.tab_index_current,
                             tab_text.replace("*", ""))
        return

    def save_netcdf_file(self):
        """Save the current tab as a netCDF file."""
        # get the current tab index
        tab_index_current = self.tabs.tab_index_current
        # get the updated control file data
        ds = self.tabs.tab_dict[tab_index_current].get_data_from_model()
        # write the data structure to file
        pfp_io.NetCDFWrite(ds.info["filepath"], ds)
        # remove the asterisk in the tab text
        tab_text = str(self.tabs.tabText(tab_index_current))
        self.tabs.setTabText(self.tabs.tab_index_current,
                             tab_text.replace("*", ""))
        return

    def file_save_as(self):
        """Save a file with a different name."""
        logger = logging.getLogger(name="pfp_log")
        # get the current tab index
        tab_index_current = self.tabs.tab_index_current
        # trap user attempts to save the Log window :=) thanks, Craig Macfarlane!
        if tab_index_current == 0:
            msg = "Log files are automatically saved" + "\n"
            msg += "in the PyFluxPro" + os.sep + "logfiles folder"
            pfp_gui.MsgBox_Continue(msg)
            return
        content = self.tabs.tab_dict[tab_index_current].get_data_from_model()
        if isinstance(content, ConfigObj):
            # we are saving a control file
            file_uri = content.filename
            file_uri = QFileDialog.getSaveFileName(
                self, "Save as ...", file_uri)[0]
            if len(str(file_uri)) == 0:
                return
            content.filename = file_uri
            self.save_as_control_file(content)
        elif isinstance(content, pfp_io.DataStructure):
            # we are opening a netCDF file
            file_uri = content.info["filepath"]
            file_uri = QFileDialog.getSaveFileName(
                self, "Save as ...", file_uri)[0]
            if len(str(file_uri)) == 0:
                return
            content.info["filepath"] = file_uri
            self.save_as_netcdf_file(content)
        else:
            # unrecognised file type
            msg = "File must be either a control file or a netCDF file"
            logger.error(msg)
        return

    def save_as_control_file(self, cfg):
        """ Save the current tab with a different name."""
        tab_index_current = self.tabs.tab_index_current
        logger = logging.getLogger(name="pfp_log")
        # write the control file
        logger.info(" Saving " + cfg.filename)
        cfg.write()
        # update the tab text
        tab_title = os.path.basename(str(cfg.filename))
        self.tabs.setTabText(tab_index_current, tab_title)
        return

    def save_as_netcdf_file(self, ds):
        """ Save the current tab with a different name."""
        # get the current tab index
        tab_index_current = self.tabs.tab_index_current
        # write the data structure to file
        pfp_io.NetCDFWrite(ds.info["filepath"], ds)
        # update the tab text
        tab_title = os.path.basename(str(ds.info["filepath"]))
        self.tabs.setTabText(tab_index_current, tab_title)
        return

    def edit_preferences(self):
        logger.debug("Edit/Preferences goes here")
        pass

    def tabSelected(self, arg=None):
        self.tabs.tab_index_current = arg

    def run_clear_log_window(self):
        """ Clear the Log window"""
        # the Log window is always tab index 0
        tb = self.tabs.widget(0)
        tb.clear()

    def run_current(self):
        self.stop_flag = False
        # save the current tab index
        logger = logging.getLogger(name="pfp_log")
        tab_index_current = self.tabs.tab_index_current
        if tab_index_current == 0:
            msg = " No control file selected ..."
            logger.warning(msg)
            return
        # disable the Run/Current menu option
        self.actionRunCurrent.setDisabled(True)
        # get the updated control file data
        cfg = self.tabs.tab_dict[tab_index_current].get_data_from_model()
        # set the focus back to the log tab
        self.tabs.setCurrentIndex(0)
        # call the appropriate processing routine depending on the level
        self.tabs.tab_index_running = tab_index_current
        if cfg["level"] == "batch":
            # check the L1 control file to see if it is OK to run
            if not pfp_compliance.check_batch_controlfile(cfg):
                return
            # add stop to run menu
            self.menuRun.addAction(self.actionStopCurrent)
            self.actionStopCurrent.triggered.connect(self.stop_current)
            # get a worker thread
            worker = pfp_threading.Worker(pfp_top_level.do_run_batch, self)
            # start the worker
            self.threadpool.start(worker)
            # no threading
            #pfp_top_level.do_run_batch(self)
        elif cfg["level"] == "L1":
            # check the L1 control file to see if it is OK to run
            if pfp_compliance.check_l1_controlfile(cfg):
                pfp_top_level.do_run_l1(cfg)
            self.actionRunCurrent.setDisabled(False)
        elif cfg["level"] == "L2":
            # check the L2 control file to see if it is OK to run
            if pfp_compliance.check_l2_controlfile(cfg):
                pfp_top_level.do_run_l2(cfg)
            self.actionRunCurrent.setDisabled(False)
        elif cfg["level"] == "L3":
            pfp_top_level.do_run_l3(cfg)
            self.actionRunCurrent.setDisabled(False)
        elif cfg["level"] == "concatenate":
            pfp_top_level.do_file_concatenate(cfg)
            self.actionRunCurrent.setDisabled(False)
        elif cfg["level"] == "climatology":
            self.utilities_climatology_custom()
        elif cfg["level"] == "cpd_barr":
            self.utilities_ustar_cpd_barr_custom()
        elif cfg["level"] == "cpd_mchugh":
            self.utilities_ustar_cpd_mchugh_custom()
        elif cfg["level"] == "cpd_mcnew":
            self.utilities_ustar_cpd_mcnew_custom()
        elif cfg["level"] == "mpt":
            self.utilities_ustar_mpt_custom()
        elif cfg["level"] == "L4":
            pfp_top_level.do_run_l4(self)
            self.actionRunCurrent.setDisabled(False)
        elif cfg["level"] == "L5":
            if pfp_compliance.check_l5_controlfile(cfg):
                pfp_top_level.do_run_l5(self)
            self.actionRunCurrent.setDisabled(False)
        elif cfg["level"] == "L6":
            if pfp_compliance.check_l6_controlfile(cfg):
                pfp_top_level.do_run_l6(self)
            self.actionRunCurrent.setDisabled(False)
        elif cfg["level"] == "nc2csv_biomet":
            pfp_top_level.do_file_convert_nc2biomet(self, mode="custom")
            self.actionRunCurrent.setDisabled(False)
        elif cfg["level"] == "nc2csv_ecostress":
            pfp_top_level.do_file_convert_nc2ecostress(self)
            self.actionRunCurrent.setDisabled(False)
        elif cfg["level"] == "nc2csv_fluxnet":
            pfp_top_level.do_file_convert_nc2fluxnet(self)
            self.actionRunCurrent.setDisabled(False)
        elif cfg["level"] == "nc2csv_reddyproc":
            pfp_top_level.do_file_convert_nc2reddyproc(self, mode="custom")
            self.actionRunCurrent.setDisabled(False)
        elif cfg["level"] == "windrose":
            if pfp_compliance.check_windrose_controlfile(cfg):
                pfp_top_level.do_plot_windrose_custom(self)
            self.actionRunCurrent.setDisabled(False)
        else:
            logger.error("Level not implemented yet ...")
        return

    def stop_current(self):
        # put up a message box, continue or quit
        msg = "Do you want to quit processing?"
        result = pfp_gui.MsgBox_ContinueOrQuit(msg, title="Quit processing?")
        if result.clickedButton().text() == "Quit":
            self.stop_flag = True
            msg = "Processing will stop when this level is finished"
            result = pfp_gui.myMessageBox(msg)
        return

    def closeTab(self, currentIndex):
        """ Close the selected tab."""
        # the tab close button ("x") shows on MacOS even though it is disabled
        # here we trap user attempts to close the log window
        if (currentIndex == 0):
            return
        # check to see if the tab contents have been saved
        tab_text = str(self.tabs.tabText(currentIndex))
        if "*" in tab_text:
            msg = "Save control file?"
            reply = QMessageBox.question(self, 'Message', msg,
                                               QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.file_save()
        # get the current tab from its index
        currentQWidget = self.tabs.widget(currentIndex)
        # delete the tab
        currentQWidget.deleteLater()
        self.tabs.removeTab(currentIndex)
        # remove the corresponding entry in tab_dict
        self.tabs.tab_dict.pop(currentIndex)
        # and renumber the keys
        for n in list(self.tabs.tab_dict.keys()):
            if n > currentIndex:
                self.tabs.tab_dict[n-1] = self.tabs.tab_dict.pop(n)
        # decrement the tab index
        self.tabs.tab_index_all = self.tabs.tab_index_all - 1
        return

    def update_tab_text(self):
        """ Add an asterisk to the tab title text to indicate tab contents have changed."""
        # add an asterisk to the tab text to indicate the tab contents have changed
        tab_text = str(self.tabs.tabText(self.tabs.tab_index_current))
        if "*" not in tab_text:
            self.tabs.setTabText(self.tabs.tab_index_current, tab_text+"*")
        return

    def utilities_climatology_custom(self):
        # run climatology from a control file
        worker = pfp_threading.Worker(
            pfp_top_level.do_utilities_climatology_custom, self)
        self.threadpool.start(worker)
        return

    def utilities_climatology_standard(self):
        # run climatology from the Utilities menu
        # disable the Run/Current menu option
        self.actionRunCurrent.setDisabled(True)
        logger = logging.getLogger(name="pfp_log")
        nc_file_uri = pfp_io.get_filename_dialog(
            title="Choose a netCDF file", ext="*.nc")
        if not os.path.exists(nc_file_uri):
            logger.info(" Climatology: no netCDF file chosen")
            return
        worker = pfp_threading.Worker(pfp_top_level.do_utilities_climatology_standard,
                                      self, nc_file_uri)
        self.threadpool.start(worker)
        return

    def utilities_ustar_cpd_barr_custom(self):
        worker = pfp_threading.Worker(
            pfp_top_level.do_utilities_ustar_cpd_barr_custom, self)
        self.threadpool.start(worker)
        return

    def utilities_ustar_cpd_barr_standard(self):
        # disable the Run/Current menu option
        self.actionRunCurrent.setDisabled(True)
        logger = logging.getLogger(name="pfp_log")
        nc_file_uri = pfp_io.get_filename_dialog(
            title="Choose a netCDF file", ext="*.nc")
        if not os.path.exists(nc_file_uri):
            logger.info(" CPD (Barr): no netCDF file chosen")
            return
        worker = pfp_threading.Worker(pfp_top_level.do_utilities_ustar_cpd_barr_standard,
                                      self, nc_file_uri)
        self.threadpool.start(worker)
        return

    def utilities_ustar_cpd_mchugh_custom(self):
        worker = pfp_threading.Worker(
            pfp_top_level.do_utilities_ustar_cpd_mchugh_custom, self)
        self.threadpool.start(worker)
        return

    def utilities_ustar_cpd_mchugh_standard(self):
        # disable the Run/Current menu option
        self.actionRunCurrent.setDisabled(True)
        logger = logging.getLogger(name="pfp_log")
        nc_file_uri = pfp_io.get_filename_dialog(
            title="Choose a netCDF file", ext="*.nc")
        if not os.path.exists(nc_file_uri):
            logger.info(" CPD (McHugh): no netCDF file chosen")
            return
        worker = pfp_threading.Worker(pfp_top_level.do_utilities_ustar_cpd_mchugh_standard,
                                      self, nc_file_uri)
        self.threadpool.start(worker)
        return

    def utilities_ustar_cpd_mcnew_custom(self):
        worker = pfp_threading.Worker(
            pfp_top_level.do_utilities_ustar_cpd_mcnew_custom, self)
        self.threadpool.start(worker)
        return

    def utilities_ustar_cpd_mcnew_standard(self):
        # disable the Run/Current menu option
        self.actionRunCurrent.setDisabled(True)
        logger = logging.getLogger(name="pfp_log")
        nc_file_uri = pfp_io.get_filename_dialog(
            title="Choose a netCDF file", ext="*.nc")
        if not os.path.exists(nc_file_uri):
            logger.info(" CPD (McNew): no netCDF file chosen")
            return
        worker = pfp_threading.Worker(pfp_top_level.do_utilities_ustar_cpd_mcnew_standard,
                                      self, nc_file_uri)
        self.threadpool.start(worker)
        return

    def utilities_ustar_mpt_custom(self):
        worker = pfp_threading.Worker(
            pfp_top_level.do_utilities_ustar_mpt_custom, self)
        self.threadpool.start(worker)
        return

    def utilities_ustar_mpt_standard(self):
        # disable the Run/Current menu option
        self.actionRunCurrent.setDisabled(True)
        logger = logging.getLogger(name="pfp_log")
        nc_file_uri = pfp_io.get_filename_dialog(
            title="Choose a netCDF file", ext="*.nc")
        if not os.path.exists(nc_file_uri):
            logger.info(" CPD (MPT): no netCDF file chosen")
            return
        worker = pfp_threading.Worker(pfp_top_level.do_utilities_ustar_mpt_standard,
                                      self, nc_file_uri)
        self.threadpool.start(worker)
        return


class actvate_menu:
    def __init__(self, root, lib="OpenFlux", path=None, addons=[],
                 welcometxt='¤ WELCOME, WILKOMEN, BIENVENUE\n',
                 create="enable", remove="enable", modify=True, sort="disabled", move=True):
        # Redirect stdout to a variable
        self.hold_std = {'in': StringIO(), 'out': StringIO(),
                         'err': StringIO()}  # sys.stdout
        sys.stdin = self.hold_std['in']
        sys.stdout = self.hold_std['out']
        sys.stderr = self.hold_std['err']
        # open('stdout.txt', 'w', buffering=1)

        # Reset stdout
        #sys.stdout = sys.__stdout__

        disable_variants = ["disabled", False]

        self.modify = False if modify in disable_variants else True
        self.create = "disabled" if create in disable_variants else "normal"
        self.remove = "disabled" if remove in disable_variants else "normal"
        self.sort = False if sort in disable_variants else True
        self.move = False if move in disable_variants else True

        self.root_mother = root
        self.title = 'OpenFlux - GUI'
        self.root_mother.geometry('1200x450+200+200')
        self.root_mother.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.window = tk.PanedWindow(self.root_mother, orient=tk.HORIZONTAL)
        self.window.pack(expand=True, fill=tk.BOTH)

        self.LeftFrame = tk.Frame(self.window)
        self.window.add(self.LeftFrame)

        # keep track of changes
        self.changetrack = tk.IntVar()
        self.changetrack.set(0)
        self.undolist = {"index": -1, "versions": [("type", "args"), ]}
        self.runningtrack = tk.IntVar()
        self.runningtrack.set(0)
        self.changetrack.trace_add('write', lambda *a: root.title(self.title + '*' * (
            self.changetrack.get() > 0) + ' (running)' * self.runningtrack.get()))
        #self.changetrack.trace_add('write', lambda *a: self.setup_to_button() if self.changetrack.get()>0 else None)
        self.runningtrack.trace_add('write', lambda *a: root.title(self.title + '*' * (
            self.changetrack.get() > 0) + ' (running)' * self.runningtrack.get()))

        # SETUP LIB
        self.lib = tk.StringVar()
        self.lib.set(lib)

        # SETUP READ
        self.path = tk.StringVar()
        self.showpath = tk.StringVar()
        self.path.trace_add("write", lambda *a: self.showpath.set(
            f"{self.path.get()[:10]}...{self.path.get()[-60:]}" if len(self.path.get()) > 73 else self.path.get()))
        unsavedmenu = os.path.join(pcd, ".tmp", ".unsavedmenu", self.lib.get() + ".yaml")
        if os.path.exists(unsavedmenu) and (time.time() - os.path.getmtime(unsavedmenu)) < 59:
            path = unsavedmenu
            self.path.set(path)
        elif path is not None and os.path.exists(path):
            self.path.set(path)
        elif os.path.isfile(os.path.join(pcd, 'Lib', lib, 'setup', 'readme.yaml')):
            self.path.set(os.path.join(pcd, 'Lib', lib, 'setup', 'readme.yaml'))
        else:
            self.path.set(askopenfilename(
                defaultextension='.yaml',
                filetypes=DEFAULT_FILE_TYPES))

        self.addon = []

        self.info = ttk.Frame(self.LeftFrame)
        self.info.pack(fill='x', anchor='nw')  # grid(sticky='nswe')

        tk.Label(self.info, textvariable=self.showpath).pack(side=tk.LEFT)

        # EDITABLE

        self.LeftFrame.Bottom = tk.Frame(self.LeftFrame)
        self.LeftFrame.Bottom.pack(fill='both', expand=True)

        self.Editable = tk.Frame(self.LeftFrame.Bottom)
        self.Editable.pack(side=tk.LEFT, fill='both', expand=True)

        # EDITABLE > TREE

        self.Editable.Tree = tk.Frame(self.Editable)
        self.Editable.Tree.pack(fill='both', expand=True)

        self.tree = self.Editable.Tree.tree = ttk.Treeview(
            self.Editable.Tree, height=1, columns=["Value", "Type"])  # show="headings",

        self.tree["columns"] = ("Value", "Type", "Description")
        self.tree.column("#0", width=120, anchor='center')
        self.tree.column("Value", width=300, anchor='center')
        self.tree.column("Type", width=40, anchor='center')
        self.tree.column("Description", width=120, anchor='center')

        self.tree.heading("#0", text="Item")
        self.tree.heading("Value", text="Value")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Description", text="Description")

        if self.sort:
            for col in self.tree["columns"]:
                self.tree.heading(
                    col, text=col, command=lambda _col=col: self.treeview_sort_column(_col, False))

        self.tree["displaycolumns"] = ("Value", "Type")

        self.nrow = 0
        #self.true_values = {}

        # .grid(column=0, row=0, sticky='nsew')
        self.tree.pack(side=tk.LEFT, fill='both', expand=True)

        self.tree.vsb = ttk.Scrollbar(
            self.Editable.Tree, orient="vertical", command=self.tree.yview)
        # .grid(column=1, row=0, sticky='nswe')
        self.tree.vsb.pack(side=tk.RIGHT, fill='y', expand=False)
        self.tree.configure(yscrollcommand=self.tree.vsb.set)

        if self.path.get() and os.path.exists(self.path.get()):
            self.menu = gg.readable_file(self.path.get()).safe_load().to_dict()
            [self.addon_path(p) for p in addons]

            if os.path.exists(self.path.get().rsplit('.', 1)[0] + '.meta'):
                self.metamenu = gg.readable_file(self.path.get().rsplit('.', 1)[0] + '.meta').safe_load(
                ).to_dict()
            else:
                self.metamenu = {}
            # if os.path.exists(os.path.join(pcd, '.lastconfig')):
            try:
                self.menuconfig = gg.readable_file(os.path.join(pcd, '.lastconfig')).safe_load(
                ).to_dict()
            except:
                self.menuconfig = {}
            try:
                self.menuroutine = gg.readable_file(self.path.get().rsplit('.', 1)[0] + '.routine').safe_load(
                ).to_dict()
            except:
                self.menuroutine = {}
        else:
            self.menu = {}
            self.metamenu = {}
            self.menuconfig = {}
            self.menuroutine = {}

        self.visible = {}

        self.visible['Columns'] = {k: tk.BooleanVar(
            value=False) if k in ['Description'] else tk.BooleanVar(
            value=True) for k in self.tree["columns"]}
        self.visible['Columns']["Value"].trace_add('write', self.showhide_tree)
        self.visible['Columns']["Type"].trace_add('write', self.showhide_tree)
        self.visible['Columns']["Description"].trace_add(
            'write', self.showhide_tree)

        #self.visible["FCButtons"] = tk.BooleanVar()
        #self.visible["FCButtons"].trace_add(
        #        'write', lambda *a: self.showhide_wg(self.FMenuMod, self.visible["FCButtons"].get()))

        self.visible['Shell'] = tk.BooleanVar(value=True)
        self.visible['Shell'].trace_add('write', lambda *a: self.showhide_pw(
            self.window, self.RightFrame, self.visible["Shell"].get()))
        self.visible['Warnings'] = tk.BooleanVar(value=True)
        #self.visible['Warnings'].trace_add('write', lambda *a: print('Warnings', self.visible["Warnings"].get()))

        # MENU
        self.MenuClk = tk.Frame(self.LeftFrame.Bottom)
        self.MenuClk.pack(side=tk.RIGHT, fill='y', expand=False)

        #self.MenuClk.Shell = tktt.VerticalScrolledFrame(self.MenuClk)
        #self.MenuClk.Shell.pack(side=tk.RIGHT)

        #self.root = tk.Frame(self.MenuClk.Shell.interior)
        #self.root.pack(fill='both', expand=True)

        self.main = ttk.Frame(self.MenuClk)  # self.root)
        self.main.pack(fill="both", expand=True)
        #self.main.grid(column=0, row=1, sticky='nswe')

        #self.FMenu = tk.Frame(self.self.main)
        #self.FMenu.grid(column=1, row=0, sticky='nsew')

        self.tipwindow = None
        self.tipfuncwindow = None
        self.last_focus = None
        self.FNewVar = None
        self.movefrom = None
        self.AnyActiveThread = False
        self.CurrentThread = threading.Thread(target=print)
        #self.selFunction = {}
        self.butFunction = {}

        self.tree.tag_configure('focus', background='yellow')
        self.tree.tag_configure('duplic', background='red')

        self.help = tk.IntVar(value=0)
        self.help.trace_add('write', lambda *a: self.assistance())
        self.root_mother.bind("<F11>", lambda e: self.root_mother.bind(
            "<F11>", lambda *a: self.help.set(0 if self.help.get() else 1)))
        self.root_mother.bind("<Control-s>", lambda e: self.save_setup())
        self.root_mother.bind("<Control-z>", lambda e: self.undoredo("undo"))
        self.root_mother.bind("<Control-y>", lambda e: self.undoredo("redo"))

        self.tree.bind('<Button-3>', lambda e: self.tree_context_menu(e))
        if self.modify:
            self.tree.bind('<Double-1>', self.set_cell_value)

        """
        self.FMenuMod = tk.Frame(self.main, width=30, height=15, bd=3)

        tk.Label(self.FMenuMod, width=30, height=2, text="\nUser's menu:",
                 anchor=tk.W).pack(fill=tk.BOTH)

        #self.FShellFunc = tktt.VerticalScrolledFrame(self.FMenuMod)
        #self.FShellFunc.pack()
        self.FMenuFunc = tk.Frame(self.FMenuMod)#.FShellFunc.interior)
        self.FMenuFunc.pack()#fill='x')#, expand=True)

        #self.FMenuFunc = tk.Frame(self.FMenu, width=15, height=15)
        #self.FMenuFunc.pack()
        """

        """
        def runselected():
            #if '__run_selected__' in self.menu.keys():
            kwargs = {k: {k_: v_ for k_, v_ in v.items() if k_ in [
                                                       'fc', 'kw']} for k, v in self.selFunction.items() if v['state'].get()}
            fc = gg.LazyCallable(self.menu['__init__']['__run_selected__']['__init__']['path'],
                                 self.menu['__init__']['__run_selected__']['__init__']['function']).__get__().fc
            kwargs.update({k: v for k, v in self.menu['__init__']['__run_selected__'].items(
            ) if k not in SYSTEM_KEYS})
            self.startthread(fc=fc, kw=kwargs)
            # GET FUNCTION

            for k, v in self.selFunction:
                if v['state'].get():
                    self.startthread(v['fc'], v['kw'],
                                     silence=self.verbositynoise)
                    # v['button'].invoke()
                    # wait thread to finish
                    self.CurrentThread.join()
        """

        #self.FMenuFuncButSel = tk.Button(self.FMenuMod,
        #                                 text='Run Selected ({})'.format(int(sum([f['state'].get() for f in self.selFunction.values()]))),
        #                                 width=20, command=runselected)
        #self.FMenuFuncButSel.pack()

        def cls(w=None, txt=""):
            self.txtprompt.stringvar.set("")
            self.errprompt.stringvar.set("")

        # Show/hide Shell
        #tk.Button(self.main, text="|", width=1, height=10, bd=1,
        #          command=lambda *a: self.visible['Shell'].set(0 if self.visible['Shell'].get() else 1)).pack(fill="y", side="right")
        _showhideshellbut = tk.Canvas(
            self.main, height=10, width=3, background="SystemButtonFace", borderwidth=2, relief="raised")
        _showhideshellbut.create_text(
            1, 50, angle="90", text="....", fill="SystemButtonText")
        _showhideshellbut.bind(
            "<ButtonPress-1>", lambda ev: ev.widget.configure(relief="sunken"))
        _showhideshellbut.bind(
            "<ButtonPress-1>", lambda *a: self.visible['Shell'].set(0 if self.visible['Shell'].get() else 1))
        _showhideshellbut.bind("<ButtonRelease-1>",
                               lambda ev: ev.widget.configure(relief="raised"))
        _showhideshellbut.bind(
            "<Configure>", lambda ev: ev.widget.configure(relief="raised"))
        _showhideshellbut.pack(fill="y", side="right")

        # PROMPT
        self.RightFrame = tk.PanedWindow(self.window, orient=tk.VERTICAL)
        #self.RightFrame.pack(fill="both", expand=True)
        self.window.add(self.RightFrame)

        #self.window = ttk.PanedWindow(self.root_mother, orient=tk.HORIZONTAL)
        #self.window.pack(expand=True, fill=tk.BOTH)

        # PROMPT > WINDOWs
        self.NotebookTextPromptTop = ttk.Notebook(
            self.RightFrame, height=100)  # .interior
        self.NotebookTextPromptTop.bind('<B1-Motion>', self.movenotebook)
        #self.NotebookTextPrompt.pack(fill='both', expand=True)
        self.RightFrame.add(self.NotebookTextPromptTop, stretch="always")

        # PROMPT > WINDOW > SHELL
        self.txtprompt = tk.Text(self.NotebookTextPromptTop, height=1,
                                 state='normal', bg='black', fg='white', font=('Consolas', 12))
        self.txtprompt.stringvar = tk.StringVar(value=welcometxt)
        self.txtprompt.insert(tk.INSERT, self.txtprompt.stringvar.get())
        self.txtprompt.config(state="disabled")
        self.txtprompt.ysc = tk.Scrollbar(self.NotebookTextPromptTop, command=self.txtprompt.yview)
        self.txtprompt['yscrollcommand'] = self.txtprompt.ysc.set
        self.txtprompt.ysc.pack(side=tk.RIGHT, fill=tk.Y)
        self.txtprompt.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        """
        self.txtprompt = tktt.VerticalScrolledFrame(self.NotebookTextPromptTop)
        #self.txtprompt.pack(fill='both', expand=True)
        self.txtprompt.canvas.config(background='black')
        self.txtprompt.stringvar = tk.StringVar(value=welcometxt)

        self.txtprompt.label = tk.Label(self.txtprompt.interior, textvariable=self.txtprompt.stringvar,
                                        anchor=tk.N+tk.W, justify='left', bg='black', fg='white', font=('Consolas', 12))
        self.txtprompt.label.bind('<Configure>', lambda e: self.txtprompt.label.config(
            wraplength=self.txtprompt.label.winfo_width()))
        self.txtprompt.label.pack(fill='both', expand=True)
        """
        self.NotebookTextPromptTop.add(self.txtprompt, text='Shell')

        self.sysvars = tktt.VerticalScrolledFrame(self.NotebookTextPromptTop)
        self.NotebookTextPromptTop.add(self.sysvars, text='System')
        sysvarstoshow = {"file path": pcd,
                         "CPUs": multiprocessing.cpu_count()}
        sysvarstoshow.update(globals())
        for i, (k, v) in enumerate(sysvarstoshow.items()):
            tk.Label(self.sysvars.interior, text=k, bg='#D3D3D3',
                     justify='left', anchor='nw').grid(row=i+1, column=0, sticky='nswe')
            tk.Label(self.sysvars.interior, text=v, justify='left',
                     anchor='nw', wraplength=600).grid(row=i+1, column=1, sticky='nswe')

        # PROMPT > WINDOWs
        self.NotebookTextPromptBot = ttk.Notebook(
            self.RightFrame, height=50)  # .interior
        self.NotebookTextPromptBot.bind('<B1-Motion>', self.movenotebook)
        self.RightFrame.add(self.NotebookTextPromptBot, stretch="always")

        # PROMPT > WINDOW > WARNINGS
        self.errprompt = tk.Text(self.NotebookTextPromptBot, height=1,
                                 state='normal', bg='black', fg='white', font=('Consolas', 12))
        self.errprompt.stringvar = tk.StringVar()
        self.errprompt.insert(tk.INSERT, self.errprompt.stringvar.get())
        self.errprompt.config(state="disabled")
        self.errprompt.ysc = tk.Scrollbar(self.NotebookTextPromptBot, command=self.errprompt.yview)
        self.errprompt['yscrollcommand'] = self.errprompt.ysc.set
        self.errprompt.ysc.pack(side=tk.RIGHT, fill=tk.Y)
        self.errprompt.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        """
        self.errprompt = tktt.VerticalScrolledFrame(
            self.NotebookTextPromptBot, bg='black')
        self.errprompt.canvas.config(background='black')
        self.errprompt.stringvar = tk.StringVar()
        self.errprompt.label = tk.Label(self.errprompt.interior, textvariable=self.errprompt.stringvar,
                                        anchor=tk.S+tk.W, justify='left', bg='black', fg='white', font=('Consolas', 12))
        self.errprompt.label.bind('<Configure>', lambda e: self.errprompt.label.config(
            wraplength=self.errprompt.label.winfo_width()))
        self.errprompt.label.pack(fill='both', expand=True)
        """
        self.NotebookTextPromptBot.add(self.errprompt, text='Warnings')
        
        # PROMPT > WINDOW > TERMINAL
        self.terminalprompt = tk.Frame(self.NotebookTextPromptBot, bg='black')
        self.terminalprompt.cmd = tktt.Prompt(self.terminalprompt)
        self.terminalprompt.cmd.pack(fill='both', expand=True, anchor=tk.S)
        self.NotebookTextPromptBot.add(self.terminalprompt, text='Terminal')

        # PROMPT > WINDOW > PYTHON INTERFACE
        self.pythonprompt = tk.Frame(self.NotebookTextPromptBot, bg='black')
        self.pythonprompt.cmd = tktt.CPython(self.pythonprompt, _globals=globals())
        self.pythonprompt.cmd.pack(fill='both', expand=True, anchor=tk.S)
        self.NotebookTextPromptBot.add(self.pythonprompt, text='Python')

        # PROMPT > WINDOW > BLOCKS
        def runselected__():
            if self.allow_run.get():
                ntthreads = int(trygetfromdict(
                    self.menu, ["__init__", "API", "ntthreads"], 1))
                ntprocess = int(trygetfromdict(
                    self.menu, ["__init__", "API", "ntprocess"], 1))

                _fc = gg.LazyCallable(trygetfromdict(self.menu, ['__init__', 'API', 'path'],
                                                     os.path.abspath(os.path.join(pcd, '__gargantua__.py'))),
                                      trygetfromdict(self.menu, ['__init__', 'API', 'function'], "api")).__get__().fc
                apidic = {k: {k_: v_ for k_, v_ in v.items() if k_ in ['__init__'] or k in [
                    '__init__']} if isinstance(v, dict) else v for k, v in self.menu.items()}
                apidic.update(self.butFunction)
                # _fc_ = self.butFunction
                self.safe_run(_fc, {'setup': self.menu, 'block': self.ordblock.returnselected(),
                                    'nproc': ntprocess, 'nthread': ntthreads})
                #_fc(self.menu, block=self.ordblock.returnselected(), nproc=ntprocess, nthread=ntthreads)
            else:
                print("\nRun in order: \n{}".format(
                    '\n'.join([f'{i+1}: {s}' for i, s in enumerate(self.ordblock.returnselected())])))

        self.frmblock = tktt.VerticalScrolledFrame(self.NotebookTextPromptBot)
        self.ordblock = tktt.OrderBlocks(
            self.frmblock.interior, list=[], edit=False)
        self.ordblock.screen.active.trace_add(
            "write", lambda *a: self.runableblocks() if not self.ordblock.screen.active.get() else None)
        self.ordblock.pack()
        self.runblocks = tk.Button(
            self.ordblock, text="Run Blocks", command=lambda: runselected__())
        self.runblocks.pack(side='bottom')
        #self.edtblocks = tk.IntVar()
        #self.edtblocks.trace_add("write", lambda *a: self.ordblock.editable.set(self.edtblocks.get()))
        #self.edtblocks.trace_add("write", lambda *a: self.runableblocks())
        #self.edtblocks.set(0)
        self.NotebookTextPromptBot.add(self.frmblock, text="Routine")

        tk.Button(self.root_mother, text='Break', bg='red', fg='white',
                  # exit(9)
                  width=5, command=lambda: os.system('python restart.py')
                  ).place(relx=1, rely=0, anchor='ne')

        # MENU BAR
        def applyfckeepmenuopen(fc, *a, **kw):
            #doesnt work
            fc(*a, **kw)
            root.tk.call('::tk::TraverseToMenu', root, 'F')

        def donothing(): return print("Not implemented yet.")

        self.menubar = tk.Menu(self.root_mother)
        self.menubar.file = tk.Menu(self.menubar, tearoff=0)

        self.menubar.file.profile = tk.Menu(self.menubar, tearoff=0)
        self.ChoiceUsrDev = tk.IntVar(value=1)
        self.ChoiceUsrDev.trace_add('write', lambda *a: self.dev_options())
        self.menubar.file.profile.add_radiobutton(
            label="User", variable=self.ChoiceUsrDev, value=0)
        self.menubar.file.profile.add_radiobutton(
            label="Developper", variable=self.ChoiceUsrDev, value=1)

        self.menubar.file.add_cascade(
            label="Profile", menu=self.menubar.file.profile)
        self.menubar.file.add_separator()
        self.menubar.file.add_command(label="New", command=lambda: donothing)
        self.menubar.file.add_command(label="Open", command=self.change_path)
        self.menubar.file.add_command(label="Addon", command=self.add_addon)
        self.menubar.file.add_command(
            label="Save", state="disabled", command=donothing)
        self.menubar.file.add_command(
            label="Save as...", command=self.save_setup)
        self.menubar.file.add_command(
            label="Restart", command=lambda*a: self.exit(9))
        self.menubar.file.add_command(label="Close", command=donothing)

        self.menubar.file.add_separator()
        self.menubar.file.add_command(label="Exit", command=root.quit)
        self.menubar.add_cascade(label="File", menu=self.menubar.file)

        self.menubar.edit = tk.Menu(self.menubar, tearoff=0)
        self.menubar.edit.add_command(
            label="Undo", command=lambda *a: self.undoredo("undo"))
        self.menubar.edit.add_command(
            label="Redo", command=lambda *a: self.undoredo("redo"))
        self.menubar.edit.add_separator()
        self.menubar.edit.add_command(label="New", command=self.newrow)
        self.menubar.edit.add_command(label="Branch", command=self.add_branch)
        self.menubar.edit.add_command(label="Cut", command=donothing)
        self.menubar.edit.add_command(label="Copy", command=donothing)
        self.menubar.edit.add_command(label="Paste", command=donothing)
        self.menubar.edit.add_command(label="Delete", command=self.delrow)
        self.menubar.edit.add_command(label="Select All", command=donothing)
        self.menubar.edit.add_separator()
        self.menubar.edit.add_command(label="Str", command=self.stringize)
        self.menubar.edit.add_command(label="Cast", command=self.casttype)
        self.menubar.edit.add_separator()

        self.menubar.edit.adv = tk.Menu(self.menubar, tearoff=0)
        self.menubar.edit.add_cascade(
            label="For developpers", menu=self.menubar.edit.adv)

        self.menubar.add_cascade(label="Edit", menu=self.menubar.edit)

        self.menubar.runf = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Run", menu=self.menubar.runf)

        self.menubar.libs = tk.Menu(self.menubar, tearoff=0)
        [self.menubar.libs.add_command(label=l, command=lambda: self.exit(9))
        for l in os.listdir(os.path.join(pcd, "Lib")) if os.path.isdir(os.path.join(pcd, "Lib", l))]
        self.menubar.add_cascade(label="Lib", menu=self.menubar.libs)

        self.menubar.options = tk.Menu(self.menubar, tearoff=0)
        self.menubar.options._vars = {"background": tk.BooleanVar(value=True),
                                      "meta": tk.BooleanVar(value=True),
                                      "routine": tk.BooleanVar(value=False),
                                      "lastconfig": tk.BooleanVar(value=True)}
        self.allow_run = tk.IntVar(value=0)
        self.menubar.options.add_checkbutton(
            label="Allow run", variable=self.allow_run)
        self.menubar.options.add_checkbutton(
            label="Run on background", variable=self.menubar.options._vars["background"])
        self.menubar.options.qdelay = tk.Menu(self.menubar.options, tearoff=0)
        self.QueueDelay = tk.IntVar(value=1)
        self.menubar.options.qdelay.add_radiobutton(
            label="1 sec", variable=self.QueueDelay, value=1)
        self.menubar.options.qdelay.add_radiobutton(
            label="10 sec", variable=self.QueueDelay, value=10)
        self.menubar.options.qdelay.add_radiobutton(
            label="1 min", variable=self.QueueDelay, value=60)
        self.menubar.options.qdelay.add_radiobutton(
            label="5 min", variable=self.QueueDelay, value=300)
        self.menubar.options.add_cascade(
            label="Queue Delay", menu=self.menubar.options.qdelay)
        self.menubar.options.add_separator()
        self.menubar.options.add_checkbutton(
            label="Save .meta", variable=self.menubar.options._vars["meta"])
        self.menubar.options.add_checkbutton(
            label="Save .routine", variable=self.menubar.options._vars["routine"])
        self.menubar.options.add_checkbutton(
            label="Save .lastconfig", variable=self.menubar.options._vars["lastconfig"])
        self.menubar.options.add_separator()
        self.ThreadProcess = tk.IntVar(value=1)
        self.menubar.options.add_radiobutton(
            label="Thread", variable=self.ThreadProcess, value=1)
        self.menubar.options.add_radiobutton(
            label="Processing", variable=self.ThreadProcess, value=0)
        self.menubar.options.add_radiobutton(
            label="Julia", variable=self.ThreadProcess, value=-1)
        self.menubar.add_cascade(label="Options", menu=self.menubar.options)

        self.menubar.screen = tk.Menu(self.menubar, tearoff=0)
        [self.menubar.screen.add_checkbutton(
            label=c, variable=self.visible["Columns"][c]) for c in self.tree["columns"]]
        self.menubar.screen.add_separator()
        self.menubar.screen.add_checkbutton(
            label="Show/Hide Shell", variable=self.visible['Shell'])
        #self.menubar.screen.add_checkbutton(label="Show/Hide Buttons", variable=self.visible['FCButtons'])
        self.menubar.screen.add_separator()
        self.menubar.screen.add_command(label="Clear", command=cls)
        self.verbositynoise = tk.IntVar()
        self.menubar.screen.add_checkbutton(
            label="Silence warnings", variable=self.verbositynoise, onvalue=0, offvalue=1)
        self.menubar.add_cascade(label="Show", menu=self.menubar.screen)

        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_checkbutton(label="Tips (F11)", variable=self.help)
        self.menubar.edit.add_separator()
        helpmenu.add_checkbutton(
            label="Save .meta", variable=self.menubar.options._vars["meta"])
        helpmenu.add_checkbutton(
            label="Save .routine", variable=self.menubar.options._vars["routine"])
        helpmenu.add_checkbutton(
            label="Save .lastconfig", variable=self.menubar.options._vars["lastconfig"])
        self.menubar.edit.add_separator()
        helpmenu.add_command(label="Help Index", command=donothing)
        helpmenu.add_command(label="About...", command=donothing)
        self.menubar.add_cascade(label="Help", menu=helpmenu)

        self.root_mother.config(menu=self.menubar)

        # WORK IS DONE
        self.root_mother.after(1000, self.update_std_pipe)  # call
        self.ChoiceUsrDev.set(1)
        #self.visible["FCButtons"].set(True)
        self.changetrack.set(
            0 if not os.path.dirname(self.path.get()).endswith(".unsavedmenu") else 1)
        self.refresh_tree()

    # ELEMENTS > VISIBILITY

    def showhide_pw(self, parent, child, show):
        if show:
            parent.add(child)
        else:
            parent.forget(child)

    def showhide_wg(self, child, show):
        if show:
            child.pack()
        else:
            child.forget()

    def showhide_tree(self, *a):
        self.tree["displaycolumns"] = tuple(
            c for c, v in self.visible['Columns'].items() if v.get())

    def update_std_pipe(self, ix=['in', 'out', 'err']):
        # check if running for updating title
        if self.CurrentThread.is_alive():
            self.runningtrack.set(1)
        else:
            self.runningtrack.set(0)

        def __update__(txtwid, newprompt):
            cdt = datetime.datetime.fromtimestamp(
                time.time()).strftime("[%d-%m-%Y %H:%M]")
            newprompt = newprompt.replace("\n", f"\n| ")
            newprompt = newprompt.replace("\r", f"\r\n| ")
            newprompt = newprompt.replace("¤ ", "\n¤ ")
            current = txtwid.get('end-2l', 'end')#[-99999:]
            #current = current.replace('\n\n\n', '\n\n')
            txtwid.config(state="normal")
            if current.endswith('\r\n| \n'):
                #txtwid.stringvar.set(re.sub('\n.*\r\n', '\n', txtwid.stringvar.get(
                #)) + f'{new_prompt}\n')
                txtwid.delete("end-2l", "end")
                # current.rsplit('\n', 2)[1] + f'\n{newprompt}'
                txtwid.insert(tk.INSERT, f"\n|' {newprompt}")
            else:
                # newprompt = current + f'{newprompt}'
                txtwid.insert(tk.INSERT, newprompt)
            txtwid.config(state="disabled")

            #txtwid.canvas.update_idletasks()
            txtwid.yview_moveto('1.0')

        where = {'in': self.txtprompt,
                 'out': self.txtprompt, 'err': self.errprompt}

        for i in ix:
            prompt = self.hold_std[i].getvalue()

            if prompt in ["", "\n"]:
                continue

            __update__(where[i], prompt)

            # Reset stdout
            self.hold_std[i] = StringIO()

            if i == 'in':
                sys.stdin = sys.__stdin__
                sys.stdin = self.hold_std[i]
            elif i == 'out':
                sys.stdout = sys.__stdout__
                sys.stdout = self.hold_std[i]
            elif i == 'err':
                sys.stderr = sys.__stderr__
                sys.stderr = self.hold_std[i]
        
        self.root_mother.after(1000,
                               lambda: self.update_std_pipe())  # call

    def dev_options(self):
        if self.ChoiceUsrDev.get():
            self.menubar.edit.entryconfig("For developpers", state="normal")
            if self.move:
                self.tree.bind("<Control-B1-Motion>", self.bMove)
                self.tree.bind("<Control-c>", self.bCopyfrom)
                self.tree.bind("<Control-v>", self.bCopyto)
                self.tree.bind("<Delete>", self.delrow)
                self.tree.bind("<Insert>", self.newrow)
        else:
            self.menubar.edit.entryconfig("For developpers", state="disabled")
            self.tree.unbind("<Control-B1-Motion>")
            self.tree.unbind("<Control-c>")
            self.tree.unbind("<Control-v>")
            self.tree.unbind("<Delete>")
            self.tree.unbind("Insert")

    def tree_context_menu(self, event):
        self.tree.selection_clear()
        self.tree.selection_set(self.tree.identify_row(event.y))
        for item in self.tree.selection():
            item_text = self.tree.item(item, "text")
        state = 'normal' if self.ChoiceUsrDev.get() else 'disabled'
        self.ctxMenu = tk.Menu(self.root_mother, tearoff=0)
        self.ctxMenu.add_command(
            label='Edit', command=lambda: self.set_cell_value(event))
        self.ctxMenu.add_command(label='New', command=self.newrow, state=state)
        self.ctxMenu.add_command(
            label='Branch', command=self.add_branch, state=state)
        self.ctxMenu.add_command(
            label='Delete', command=self.delrow, state=state)
        self.ctxMenu.add_separator()
        self.ctxMenu.add_command(
            label='To button', command=lambda t=item_text: self.sendtobutton(t), state=state if item_text in self.menu.keys() else 'disabled')
        self.ctxMenu.add_separator()
        self.ctxMenu.add_command(label="Str", command=self.stringize)
        self.ctxMenu.add_command(label="Cast", command=self.casttype)
        self.ctxMenu.post(event.x_root, event.y_root)
        return

    def info_icon():
        import PIL.ImageDraw as ImageDraw
        import PIL
        draw = ImageDraw.Draw(PIL.Image.new('RGBA', (22, 22), color=(0, 0, 0,0)))
        x, y, r = (10, 10, 10)
        leftUpPoint = (x-r, y-r)
        rightDownPoint = (x+r, y+r)
        twoPointList = [leftUpPoint, rightDownPoint]
        draw.ellipse(twoPointList, fill=(255, 0, 0,255))
        draw.text((8, 5), "i", fill=(0, 0, 0,0))
        draw._image
        return PIL.Image(draw._image)

    def runableblocks(self):
        self.ordblock.editable.set(False)
        self.ordblock.screen.active.set(False)
        for b in self.ordblock.screen.but:
            b.config(command=lambda w=b, n=b["text"]: self.buttoninforun(w, n))

    def sendtobutton(self, name):
        fc_name = trygetfromdict(self.menu, [name, "__init__", "name"], name)
        path = trygetfromdict(
            self.menu, [name, "__init__", "path"], self.menu['__init__']['main'])
        func = trygetfromdict(self.menu, [name, "__init__", "function"], name)
        #try:
        #    fc_name = self.menu[name]["__init__"]["name"]
        #except:
        #    fc_name = name

        #fn_kw = {k: v for k, v in self.menu[name].items() if k != "__init__"}
        # put the references on
        fn_kw = gg.referencedictionary(self.menu, meta=self.metamenu)[name]

        self.butFunction[fc_name] = {'fc': [path, func], 'kw': fn_kw}
        self.ordblock.addbuttom(fc_name)
        self.runableblocks()

    def buttoninforun(self, wid, name):
        def moveblock(*a):
            self.ordblock.editable.set(True)
            self.ordblock.sSep(*a)

        fc = gg.LazyCallable(*self.butFunction[name]['fc']).__get__().fc
        kw = self.butFunction[name]['kw']
        localMenu = tk.Menu(self.root_mother, tearoff=0)
        localMenu.add_command(
            label='run', command=lambda f=fc, k=kw: self.safe_run(f, k))
        localMenu.add_command(label='ⓘ', command=lambda f=fc,
                              k=kw: self.infoonbutton(f, k))
        localMenu.add_command(
            label='move', command=lambda w=wid: moveblock(*w.req))
        localMenu.post(wid.winfo_rootx(), wid.winfo_rooty())

    def infoonbutton(self, fc, kw):
        try:
            if self.tipfuncwindow is not None:
                for child in self.tipfuncwindow.winfo_children():
                    child.destroy()
            self.tipfuncwindow.destroy()
            self.tipfuncwindow = None
        except:
            None

        self.tipfuncwindow = tk.Toplevel(self.root_mother)
        self.tipfuncwindow.wm_geometry(
            "+%d+%d" % (self.root_mother.winfo_pointerx(), self.root_mother.winfo_pointery()))

        self.tipfuncframe_ = tktt.VerticalScrolledFrame(self.tipfuncwindow)
        self.tipfuncframe = self.tipfuncframe_.interior
        #self.tipfuncframe = tk.Frame(self.tipfuncwindow)
        self.tipfuncframe_.pack(fill=tk.BOTH)
        #tk.Label(self.tipfuncframe, text='run', bg='red', justify='left', anchor='nw').grid(row=0, column=0, sticky='nswe')
        #tk.Label(self.tipfuncframe, text=inspect.signature(fc), justify='left', anchor='nw').grid(row=0, column=1, sticky='nswe')
        #kwtxt = '\n'.join([k+',' for k in str(kw)[1:-1].split(',')])
        kwtxt = '\n'.join([k+': '+str(v) for k, v in kw.items()])
        tk.Label(self.tipfuncframe, text='**kwargs', bg='#D3D3D3',
                 justify='left', anchor='nw').grid(row=1, column=0, sticky='nswe')
        tk.Label(self.tipfuncframe, text=kwtxt, justify='left',
                 anchor='nw', wraplength=600).grid(row=1, column=1, sticky='nswe')
        tk.Label(self.tipfuncframe, text='source', bg='#D3D3D3',
                 justify='left', anchor='nw').grid(row=2, column=0, sticky='nswe')
        tk.Label(self.tipfuncframe, text=inspect.getsource(
            fc), justify='left', anchor='nw', wraplength=600).grid(row=2, column=1, sticky='nswe')

    """
    def setup_to_button(self):
        for child in self.FMenuFunc.winfo_children():#[1:]:
            child.destroy()
        
        self.selFunction = {k: v for k, v in self.selFunction.items() if k in self.menu.keys()}
        #if '__run_selected__' in self.menu['__init__']:
        #    self.FMenuFuncButSel.configure(state='normal')
        #else:
        #    self.FMenuFuncButSel.configure(state='disabled')
                
        self.refresh_menu()

        for _, (k, v) in enumerate(self.menu.items()):
            if k in SYSTEM_KEYS:
                continue

            create = False
            
            nest_cond = isinstance(v, dict) and '__init__' in v.keys()
            
            but_name = v['__init__']['name'] if nest_cond and 'name' in v['__init__'].keys(
            ) else k
            func_name = v['__init__']['function'] if nest_cond and 'function' in v['__init__'].keys(
            ) else k
            state = v['__init__']['state'] if nest_cond and 'state' in v['__init__'].keys(
            ) else 'normal'

            if isinstance(v, dict) and ('__init__' in self.menu.keys()) and ('main' in self.menu['__init__']):
                # and ('button' in self.menu['__init__']) and self.menu['__init__']['button']!='disabled'
                create = True
                try:
                    func = gg.LazyCallable(
                        self.menu['__init__']['main'], func_name).__get__().fc
                except:
                    state = 'disabled'
                    func = None
                    
            elif nest_cond and ('path' in v['__init__']):
                create = True
                try:
                    func = gg.LazyCallable(
                        v['__init__']['path'], func_name).__get__().fc
                except:
                    state = 'disabled'
                    func = None
            
            if create:
                def seq_replace(string, dictionary):
                    if re.findall('<.+>', str(string)):
                        if isinstance(string, dict):
                            string = {k__: seq_replace(v__, dictionary) for k__, v__ in string.items()}
                        elif isinstance(string, list) or isinstance(string, tuple):
                            string = [seq_replace(v__, dictionary) for v__ in string]
                        else:
                            for sk, sv in dictionary.items():
                                string = string.replace(sk, sv)
                    return string
                
                # get mother shortcuts <.>
                shortcuts = {k_: str(v_) for k_, v_ in self.menu['__init__'].items() if (k_.startswith('<')) and (k_.endswith('>'))} if ('__init__' in self.menu.keys()) else {}
                
                # replace shortcuts <.> in section's shortcuts
                sec_shortcuts = {k_: seq_replace(v_, shortcuts) if re.findall('<.+>', str(v_)) else v_ for k_, v_ in v['__init__'].items() if (k_.startswith('<')) and (k_.endswith('>'))} if nest_cond else {}
                                
                # get section's shortcuts <.>
                shortcuts.update({k_: str(v_) for k_, v_ in sec_shortcuts.items() if (k_.startswith('<')) and (k_.endswith('>'))} if nest_cond else {})
                
                fn_kw = {k_: seq_replace(v_, shortcuts) if re.findall('<.+>', str(v_)) else v_ for k_, v_ in v.items() if k_ not in [
                    '__init__']}
            
                butFrame = tk.Frame(self.FMenuFunc)
                butFrame.pack(fill=tk.BOTH)

                if func_name not in self.selFunction.keys():
                    self.selFunction[func_name] = {}
                    self.selFunction[func_name]['state'] = tk.IntVar()
                #tk.Checkbutton(butFrame, variable=self.selFunction[func_name]['state'], #width=1, height=1, bd=0, border=0, borderwidth=0, padx=0,
                #                command=lambda: self.FMenuFuncButSel.configure(text='Run Selected ({})'.format(int(sum([f['state'].get() for f in self.selFunction.values()]))))
                #                ).grid(row=0, column=0)
                                
                self.selFunction[func_name]['fc'] = func
                self.selFunction[func_name]['kw'] = fn_kw
                tk.Button(butFrame, text=but_name, width=20,
                        state=state, command=lambda fc=func, kw=fn_kw: self.startthread(fc, kw)).grid(row=0, column=1)#side=tk.LEFT)
                
                def tipfuncwindow(fc, kw):
                    try:
                        if self.tipfuncwindow is not None:
                            for child in self.tipfuncwindow.winfo_children():
                                child.destroy()
                            self.tipfuncwindow.destroy()
                            self.tipfuncwindow = None
                    except:
                        None

                    self.tipfuncwindow = tk.Toplevel(self.root_mother)
                    self.tipfuncwindow.wm_geometry(
                        "+%d+%d" % (self.root_mother.winfo_pointerx(), self.root_mother.winfo_pointery()))
                    self.tipfuncframe = tk.Frame(self.tipfuncwindow)
                    self.tipfuncframe.pack(fill=tk.BOTH)
                    #tk.Label(self.tipfuncframe, text='run', bg='red', justify='left', anchor='nw').grid(row=0, column=0, sticky='nswe')
                    #tk.Label(self.tipfuncframe, text=inspect.signature(fc), justify='left', anchor='nw').grid(row=0, column=1, sticky='nswe')
                    tk.Label(self.tipfuncframe, text='**kwargs', bg='#D3D3D3', justify='left', anchor='nw').grid(row=1, column=0, sticky='nswe')
                    tk.Label(self.tipfuncframe, text='\n'.join([k+',' for k in str(kw)[1:-1].split(',')]), justify='left', anchor='nw').grid(row=1, column=1, sticky='nswe')
                    tk.Label(self.tipfuncframe, text='source', bg='#D3D3D3', justify='left', anchor='nw').grid(row=2, column=0, sticky='nswe')
                    tk.Label(self.tipfuncframe, text=inspect.getsource(fc), justify='left', anchor='nw').grid(row=2, column=1, sticky='nswe')
                
                tk.Button(butFrame, text='ⓘ',
                          width=3, height=1, bd=0, state=state, command=lambda fc=func, kw=fn_kw: tipfuncwindow(fc, kw)).grid(row=0, column=2)#.pack(side=tk.RIGHT)
    """

    def startthread(self, fc, kw, ntthreads=None, ntprocess=None):
        self.runningtrack.set(1)
        ntthreads = ntthreads if ntthreads is not None else int(
            trygetfromdict(self.menu, ["__init__", "ntthreads"], 1))
        ntprocess = ntprocess if ntprocess is not None else int(
            trygetfromdict(self.menu, ["__init__", "ntprocess"], 1))

        if not self.CurrentThread.is_alive():
            if self.verbositynoise:
                warnings.resetwarnings()
            else:
                warnings.filterwarnings("ignore")
            if self.ThreadProcess.get() < 0:
                #print(f"¤ Running\nThread: {fc.__name__}\nModule: {fc.__module__}\nParallel: {ntthreads}\nStart: {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M')}")
                print(running_message(fc.__name__,
                      fc.__module__, "Julia", ntthreads))
                for _ in range(max(1, min(multiprocessing.cpu_count()-1, ntthreads))):
                    self.CurrentThread = threading.Thread(target=fc, kwargs=kw)
                    self.CurrentThread.start()
                    time.sleep(self.QueueDelay.get())
            elif self.ThreadProcess.get():
                #print(f"¤ Running\nThread: {fc.__name__}\nModule: {fc.__module__}\nParallel: {ntthreads}\nStart: {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M')}")
                print(running_message(fc.__name__,
                      fc.__module__, "Thread", ntthreads))
                for _ in range(max(1, min(multiprocessing.cpu_count()-1, ntthreads))):
                    self.CurrentThread = threading.Thread(target=fc, kwargs=kw)
                    self.CurrentThread.start()
                    time.sleep(self.QueueDelay.get())
            else:
                #print(f"¤ Running\nProcess: {fc.__name__}\nModule: {fc.__module__}\nParallel: {ntprocess}\nStart: {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M')}")
                print(running_message(fc.__name__, fc.__module__,
                      "Multiprocessing", ntprocess))
                for _ in range(max(1, min(multiprocessing.cpu_count()-1, ntprocess))):
                    self.CurrentThread = multiprocessing.Process(
                        target=fc, kwargs=kw)
                    self.CurrentThread.start()
                    time.sleep(self.QueueDelay.get())
            self.CurrentThread.__name__ = str(fc.__name__)
        else:
            print(
                f"Nothing was done, because '{self.CurrentThread.__name__}' is still active.")

    def refresh_tree(self, ignore_default=False, config_kwargs={}):
        """look at menu and refresh tree"""
        def delete_child(item=''):
            for child in self.tree.get_children(item):
                if self.tree.get_children(child):
                    delete_child(child)
                self.tree.delete(child)

        delete_child()

        # DEFAULT
        if not ignore_default:
            self.import_config(**config_kwargs)

        for _, (k, v) in enumerate(self.menu.items()):
            tp = self.metamenu[k] if k in self.metamenu.keys() else {}
            if isinstance(v, dict):
                self.tree.insert("", "end", self.nrow, text=k, open=False)
                self.nrow += 1
                self.add_node(k, v, tp=tp)
            else:
                #self.true_values.update({self.nrow: v})
                self.tree.insert("", "end", self.nrow, text=k,
                                 values=(str(v),
                                         trygetfromdict(
                                             tp, ['type'], type(v).__name__),
                                         trygetfromdict(tp, ['help'], "")))
                self.nrow += 1

        self.runableblocks()
        self.refresh_functions()
        #self.setup_to_button()

    def refresh_functions(self):
        self.menubar.runf.delete(0, "end")
        refd = gg.referencedictionary(
            self.menu, meta=self.metamenu, kinit=True)
        allfunctions = {k: {k_: v_ for k_, v_ in v.items() if k_ not in ["__init__"]} if isinstance(
            v, dict) else v for k, v in refd.items() if k not in ["__init__"]}

        for k, v in allfunctions.items():
            state = 'normal'
            try:
                _init = refd[k]['__init__']
                fn = trygetfromdict(_init, ['function'], k)
                func = gg.LazyCallable(_init['path'], fn).__get__().fc
            except:
                try:
                    fn = trygetfromdict(refd, [k, '__init__', 'function'], k)
                    #try:
                    #    fn = _menu[k]['__init__']['function']
                    #except:
                    #    fn = k
                    try:
                        func = gg.LazyCallable(refd['__init__']['main'], fn).__get__().fc
                    except Exception as e1:
                        func = gg.LazyCallable(str(os.path.join(pcd, '__gargantua__.py')), fn).__get__().fc
                except Exception as e2:
                    func = None
                    state = 'disabled'
            self.menubar.runf.add_command(
                label=k, command=lambda fc=func, kw=v: self.safe_run(fc, kw), state=state)

    def change_path(self):
        npath = askopenfilename(title='Select setup path',
                                      defaultextension='.yaml',
                                      filetypes=DEFAULT_FILE_TYPES)
        if npath:
            self.menu = gg.readable_file(npath).safe_load().to_dict()
            self.metamenu = gg.readable_file(npath.rsplit('.', 1)[0] + '.meta').safe_load(
            ).to_dict() if os.path.exists(npath.rsplit('.', 1)[0] + '.meta') else {}
            self.menuroutine = gg.readable_file(npath.rsplit('.', 1)[0] + '.routine').safe_load(
            ).to_dict() if os.path.exists(npath.rsplit('.', 1)[0] + '.routine') else {}
            if os.path.exists(os.path.join(pcd, '.lastconfig')):
                self.menuconfig = gg.readable_file(os.path.join(pcd, '.lastconfig')).safe_load(
                ).to_dict()

            self.path.set(npath)
            [a.destroy() for a in self.addon]
            self.addon = []
            self.changetrack.set(0)
            self.refresh_tree()

    def add_addon(self, npath=None):
        if isinstance(npath, str):
            npath = [npath]
        if npath == None:
            npath = askopenfilenames(title='Select setup path',
                                    defaultextension='.yaml',
                                    filetypes=DEFAULT_FILE_TYPES)
        for p in npath:
            if os.path.exists(p) == False:
                return
            self.addon_path(p)
            self.refresh_tree(config_kwargs={"win": False})
        return

    def addon_path(self, npath):
        self.menu = update_nested_dict(
            self.menu, gg.readable_file(npath).safe_load().to_dict())
        if os.path.exists(npath.rsplit('.', 1)[0] + '.meta'):
            self.metamenu = update_nested_dict(self.metamenu, gg.readable_file(
                npath.rsplit('.', 1)[0] + '.meta').safe_load().to_dict())
        #self.path.set(self.path.get() +
        #              f' + {ntpath.basename(npath).rsplit(".", 1)[0]}')
        label = ntpath.basename(npath).rsplit(".", 1)[0]
        label = re.sub("^(readme)?(addon)?_", "", label)
        self.addon += [tk.Label(self.info,
                                text=f'+ {label}', fg='white', bg='green')]
        self.addon[-1].pack(side=tk.LEFT)

    def add_branch(self):
        item = self.tree.selection()[0]  # get selected item
        item_text = self.tree.item(item)
        parent = self.tree.parent(item)
        index = self.tree.index(item)

        if len(item_text['values']) > 0:
            text = [
                item_text['text'], item_text['values'][0], item_text['values'][1]]
            self.tree.delete(item)
            self.tree.insert(parent, index, item, text=text[0], open=True)
            self.tree.insert(item, 0, self.nrow,
                             text=text[0], values=text[1:])
        else:
            text = item_text['text']
            self.tree.insert(item, index, self.nrow, text=self.different_var_name(
                item, "__VAR__"), values=("__VALUE__", "str"))

        self.nrow += 1

    def add_node(self, k, v, tp=None):
        #global nrow, true_values
        i = self.nrow-1
        for _, (k_, v_) in enumerate(v.items()):
            tp_ = tp[k_] if isinstance(tp, dict) and k_ in tp.keys() else ""
            if isinstance(v_, dict):
                self.tree.insert(i, "end", self.nrow, text=k_, open=True)
                self.nrow += 1
                self.add_node(k_, v_, tp_)
            else:
                #self.true_values.update({self.nrow: v_})
                self.tree.insert(i, "end", self.nrow, text=k_,
                                 values=(str(v_),
                                         trygetfromdict(
                                             tp_, ['type'], type(v_).__name__),
                                         trygetfromdict(tp_, ['help'], "")))
                self.nrow += 1

    def treeview_sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
            self.tree.heading(
                col, command=lambda: self.treeview_sort_column(col, not reverse))

    def set_cell_value(self, event):
        def insertpdir():
            nval = askdirectory()
            if nval:
                entryedit.delete(0.0, tk.END)
                entryedit.insert("end", nval)

        def insertpath():
            nval = askopenfilename()
            if nval:
                entryedit.delete(0.0, tk.END)
                entryedit.insert("end", nval)

        def saveedit():
            v = entryedit.get(0.0, "end")[:-1]
            v = v.replace('\n', '')

            def fromparent(k, v, w='text'):
                current = {self.tree.item(k, w): v}
                if self.tree.parent(k):
                    return fromparent(self.tree.parent(k), current)
                else:
                    return current

            if cn == 1:
                unique = [self.tree.item(i, 'text') for i in self.tree.get_children(
                    self.tree.parent(item)) if i != item]
                if v not in unique:
                    rename = fromparent(item, v)
                    self.tree.item(item, text=v)
                else:
                    return
            elif cn == 2:
                self.casttype(item, v)
                #if isinstance(v, str) and (re.match('^[0-9-]*[,.]?[0-9-]*$', v) is not None):
                #    v = int(v) if re.search(
                #        '[,.]', v) is None else float(v.replace(',', '.'))
                #self.tree.set(item, column=column, value=str(v))
                #self.tree.set(item, column="Type", value=type(v).__name__)
                #self.true_values.update({rn: v})

            self.tree.update()

            if cn == 1:
                v = str(v)
                self.menu = rename_nested_dict(self.menu, rename)
                self.metamenu = rename_nested_dict(self.metamenu, rename)
            else:
                v = str(v) if self.tree.item(item, 'value')[1] in [
                    'str', 'function'] else ast.literal_eval(str(v))
                if type(v).__name__ != self.tree.item(item, 'value')[1]:
                    warnings.warn(
                        f"Sending value as {type(v)} when it showed as {self.tree.item(item, 'value')[1]}.")
                self.menu = update_nested_dict(self.menu, fromparent(item, v))
                self.metamenu = update_nested_dict(self.metamenu, fromparent(
                    item, {"type": self.tree.item(item, 'value')[1]}))
            self.refresh_functions()
            dropedit()
            #self.setup_to_button()
            self.changetrack.set(self.changetrack.get()+1)
            self.undoredo("add", ("modify", [cn, item, suggestionlabel, v]))

        def dropedit():
            for child in self.FNewVar.winfo_children():
                child.destroy()
            self.FNewVar.destroy()
            self.FNewVar = None
            #self.FShow.grid_rowconfigure(0, weight=1)
            #self.FShow.grid_rowconfigure(1, weight=0)
            #self.root.unbind("<Control-Return>")
            #self.root.unbind("<Escape>")

        self.root_mother.bind("<Control-Return>", lambda e: saveedit())
        self.root_mother.bind("<Escape>", lambda e: dropedit())

        for item in self.tree.selection():
            #item_text = self.tree.item(item, "values")
            item_text = self.tree.item(item)
            column = self.tree.identify_column(event.x)
            row = self.tree.identify_row(event.y)
        #print(column, row)
        cn = int(str(column).replace('#', '')) + 1
        rn = int(str(row).replace('I', '')) + 1

        if (cn != 1 and self.tree.get_children(item)) or (cn == 3) or (cn == 1 and self.ChoiceUsrDev.get() == 0):
            cn = 1
            #return

        if self.FNewVar is not None:
            dropedit()

        self.FNewVar = tk.Frame(self.Editable, width=20, height=1)
        # .grid(column=0, sticky='nswe')
        self.FNewVar.pack(fill='both', expand=True)
        #self.FShow.grid_rowconfigure(0, weight=2)
        #self.FShow.grid_rowconfigure(1, weight=3)

        suggestionlabel = item_text['text'] if (self.tree.get_children(item)) or (
            cn == 1) else item_text['values'][0] if cn == 2 else item_text['values'][1]

        entrylabel = tk.Label(self.FNewVar, text='replace:',
                              width=15, height=1, anchor=tk.W)
        entrylabel.pack(side=tk.LEFT)

        entryedit = tk.Text(self.FNewVar, width=1, height=1)
        entryedit.insert('end', str(suggestionlabel))
        entryedit.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        entryedit.focus_set()

        nob = tk.Button(self.FNewVar, text='✗', width=2, command=dropedit)
        nob.pack(side=tk.RIGHT)
        okb = tk.Button(self.FNewVar, text='✓', width=2, command=saveedit)
        okb.pack(side=tk.RIGHT)
        inb = tk.Button(self.FNewVar, text='/.*', width=3, command=insertpath)
        inb.pack(side=tk.RIGHT)
        inb = tk.Button(self.FNewVar, text='C:/', width=3, command=insertpdir)
        inb.pack(side=tk.RIGHT)
        inb = tk.Button(self.FNewVar, text='date', width=3, state='disabled')
        inb.pack(side=tk.RIGHT)

    def assistance(self, e=None):
        if self.help.get():
            #print('Enabled')
            self.tree.bind("<Motion>", self.mycallback)
            self.main.bind("<Motion>", self.cancel_tip)
            #self.help.set(1)
        else:
            #print('Disabled')
            self.tree.unbind("<Motion>")
            self.main.unbind("<Motion>")
            self.tipwindow.destroy()
            self.tipwindow = None
            #self.help.set(0)

    def newrow(self, e=None, i=1, keeptrack=True, values=("__VALUE__", "str")):
        if self.tree.selection():
            if '__VAR__' not in self.menu.keys():
                selected_item = self.tree.selection()[0]  # get selected item
                parent = self.tree.parent(selected_item)
                index = self.tree.index(selected_item) + i
                #global nrow
                self.tree.insert(parent,
                                 index,
                                 self.nrow,
                                 text=self.different_var_name(
                                     parent, '__VAR__'),
                                 values=values)
                self.tree.update()
                self.changetrack.set(self.changetrack.get()+1)
                if keeptrack:
                    self.undoredo(
                        "add", ("newrow", [[parent, index, self.tree.item(self.nrow), self.nrow]]))
                self.nrow += 1

    def delrow(self, e=None, keeptrack=True):
        #selected_item = self.tree.selection()[0]  # get selected item
        if self.tree.selection():
            delrows = []
            for s in self.tree.selection():
                delrows += [[
                    self.tree.parent(s), self.tree.index(s), self.tree.item(s), self.tree.focus()]]
                self.tree.delete(s)
            self.changetrack.set(self.changetrack.get()+1)
            if keeptrack:
                self.undoredo("add", ("delrow", delrows))

    def stringize(self):
        item = self.tree.selection()[0]  # get selected item
        v = self.tree.item(item)['values'][0]
        self.tree.set(item, column="Value", value=str(v))
        self.tree.set(item, column="Type", value='str')

    def casttype(self, item=None, v=None):
        if item is None:
            item = self.tree.selection()[0]  # get selected item
        if v is None:
            v = self.tree.item(item)['values'][0]

        # custom type
        #gt.checkcustomtypes(v)
        if re.match(r"f(.+,.+)", v):
            self.tree.set(item, column="Type", value='function')
        else:
            try:
                v = ast.literal_eval(str(v))
            except:
                v = str(v)
            self.tree.set(item, column="Type", value=type(v).__name__)
        self.tree.set(item, column="Value", value=str(v))

    def refresh_menu(self, *args):
        """look at tree and refresh menu"""
        def refresh(item, dic, metadic={}):
            for x in self.tree.get_children(item):
                #if len(self.tree.get_children(x))==0:
                name = self.tree.item(x)["text"].replace('\n', '')
                #print('*', value_dict)
                #print(self.tree.item(x)["values"])
                val = [str(j).replace('\n', '')
                       for j in self.tree.item(x)["values"]]

                if self.tree.get_children(x):
                    #print(name)
                    dic.update({name: {}})
                    metadic.update({name: {}})
                    refresh(x, dic[name], metadic[name])  # , *args, {name: x})

                else:
                    value = str(val[0]) if val[1] in [
                        'str', 'function'] else ast.literal_eval(str(val[0]))
                    if type(value).__name__ != val[1]:
                        warnings.warn(
                            f"Sending value as {type(value)} when it showed as {val[1]}.")
                    #value = value if type(value).__name__ == val[1] else str(val[0])
                    dic.update({name: value})
                    metadic.update({name: {"type": val[1], "help": ""}})

        self.menu = OrderedDict({})
        self.metamenu = OrderedDict({})
        refresh('', self.menu, self.metamenu)
        self.refresh_config()

    def import_config(self, win=True, tree=True, fcbut=True):
        if win:
            try:
                win_geom = self.menuconfig['__init__']['OPEN_DEFAULTS']['WIN_GEOMETRY']
                self.root_mother.geometry(win_geom)
            except:
                None

        if tree:
            for k, v in self.visible.items():
                try:
                    v.set(self.menu['__init__']
                          ['OPEN_DEFAULTS']['VISIBILITY'][k])
                except:
                    None
                if self.menubar.options._vars["lastconfig"].get():
                    try:
                        v.set(self.menuconfig['__init__']
                              ['OPEN_DEFAULTS']['VISIBILITY'][k])
                    except:
                        None
        if fcbut:
            try:
                self.ordblock.screen.butlist = self.menuroutine[
                    '__init__']['OPEN_DEFAULTS']["ORG_BUTTONS"]
                self.butFunction = self.menuroutine['__init__']['OPEN_DEFAULTS']["FUN_BUTTONS"]
                self.ordblock.listtocanvas()
            except:
                self.ordblock.screen.butlist = []
                self.butFunction = {}
                self.ordblock.listtocanvas()
            """
            try:
                self.selFunction = self.menu['__init__']['OPEN_DEFAULTS']['selected_functions']
                self.selFunction = {k: {k_: tk.IntVar(
                    value=v_) if k_ == 'state' else v_ for k_, v_ in v.items()} for k, v in self.selFunction.items()}
                self.FMenuFuncButSel.configure(text='Run Selected ({})'.format(
                    int(sum([f['state'].get() for f in self.selFunction.values()]))))
            except:
                None
            """

    def refresh_config(self):
        self.menuconfig = {"__init__": {"OPEN_DEFAULTS": {
            #"selected_functions":
            #{k: {k_: v_.get() for k_, v_ in v.items() if k_ == 'state'}
                # for k, v in self.selFunction.items()},
                "VISIBILITY": {k: v.get() if not isinstance(v, dict) else {k_: v_.get() for k_, v_ in v.items()} for k, v in self.visible.items()},
                "WIN_GEOMETRY": self.root_mother.geometry(),
        }}}
        self.menuroutine = update_nested_dict(self.menuroutine, {'__init__': {
                                              'OPEN_DEFAULTS': {"ORG_BUTTONS": self.ordblock.screen.butlist}}})
        self.menuroutine = update_nested_dict(self.menuroutine, {'__init__': {
                                              'OPEN_DEFAULTS': {"FUN_BUTTONS": self.butFunction}}})

        #if "__init__" in self.menu.keys() and 'OPEN_DEFAULTS' in self.menu['__init__'].keys():
        #    self.menu['__init__']['OPEN_DEFAULTS']['selected_functions'] = {k: {k_: v_.get(
        #    ) for k_, v_ in v.items() if k_ == 'state'} for k, v in self.selFunction.items()}
        #if "__init__" in self.menu.keys() and 'OPEN_DEFAULTS' in self.menu['__init__'].keys() and 'VISIBILITY' in self.menu['__init__']['OPEN_DEFAULTS']:
        #    self.menu['__init__']['OPEN_DEFAULTS']['VISIBILITY']['BUTTON'] = self.visible['FCButtons'].get()

    def save_setup(self, save_path="", meta=False, routine=False):
        self.refresh_menu()
        if not save_path:
            save_path = asksaveasfilename(confirmoverwrite=True,
                                          defaultextension='.yaml',
                                          filetypes=DEFAULT_FILE_TYPES)

        if save_path:
            #print('save in:', save_path)
            gg.readable_file(save_path, **self.menu).dump()
            if meta or self.menubar.options._vars["meta"].get():
                gg.readable_file(save_path.rsplit('.', 1)[
                                 0] + ".meta", **self.metamenu).dump()
            if routine or self.menubar.options._vars["routine"].get():
                gg.readable_file(save_path.rsplit('.', 1)[
                                 0] + ".routine", **self.menuroutine).dump()
            print(f"¤ Saved setup in {save_path}.")
            self.changetrack.set(0)
        return

    class ToolTip(object):
        def __init__(self, widget):
            self.widget = widget
            self.tipwindow = None
            self.id = None
            self.x = self.y = 0

        def showtip(self, text):
            "Display text in tooltip window"
            self.text = text
            if self.tipwindow or not self.text:
                return
            x, y, cx, cy = self.widget.bbox("insert")
            x = x + self.widget.winfo_rootx() + 57
            y = y + cy + self.widget.winfo_rooty() + 27
            self.tipwindow = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(1)
            tw.wm_geometry("+%d+%d" % (x, y))
            label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                             background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                          font=("tahoma", "8", "normal"))
            label.pack(ipadx=1)

        def hidetip(self):
            tw = self.tipwindow
            self.tipwindow = None
            if tw:
                tw.destroy()

    def CreateToolTip(self, widget, text):
        toolTip = self.ToolTip(widget)

        def enter(event):
            toolTip.showtip(text)

        def leave(event):
            toolTip.hidetip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def cancel_tip(self, event):
        x, y = self.main.winfo_pointerxy()
        #print(self.main.winfo_containing(x, y), str(self.main.winfo_containing(x, y)).split('.!')[-1], ' '*15, end='\r')
        if (self.main.winfo_containing(x, y) not in [self.tree]) and (self.tipwindow is not None):
            #(str(self.main.winfo_containing(x, y)).split('.!')[-1] not in ['label']) and \
            self.tipwindow.destroy()
            self.tipwindow = None

    def mycallback(self, event):
        _iid = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        el = self.tree.identify_element(event.x, event.y)
        cn = int(str(column).replace('#', ''))

        item_text = self.tree.item(_iid)

        #print(item_text)
        if len(item_text['values']) > 0:
            i = _iid
            p = [self.tree.item(i)['text']]
            while self.tree.parent(i):
                i = self.tree.parent(i)
                p += [self.tree.item(i)['text']]
            p.reverse()
            text = [item_text['text'], item_text['values'][0],
                    item_text['values'][1], item_text['values'][2]]
            text = text[-1] if text[-1] else text[cn]
        else:
            text = item_text['text']

        try:
            if (_iid, column) != self.last_focus:
                if self.tipwindow is not None:
                    self.tipwindow.destroy()
                    self.tipwindow = None
                self.tipwindow = tk.Toplevel(self.tree)
                self.tipwindow.wm_overrideredirect(1)
                self.tipwindow.wm_geometry(
                    "+%d+%d" % (self.root.winfo_pointerx(), self.root.winfo_pointery()))

                label = tk.Label(self.tipwindow, text=text, justify=tk.LEFT,
                              background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                              font=("tahoma", "8", "normal"))
                label.pack(ipadx=1)

                #print(_iid)
                if self.last_focus:
                    self.tree.item(self.last_focus[0], tags=[])
                self.tree.item(_iid, tags=['focus'])
                self.last_focus = (_iid, column)
        except:
            None

    def movenotebook(self, e):
        try:
            index = e.widget.index(f"@{e.x},{e.y}")
            e.widget.insert(index, child=e.widget.select())
        except tk.TclError:
            pass

    def bMove(self, e):
        # move items around
        #tv = event.widget
        item = self.tree.identify_row(e.y)
        moveto = self.tree.index(item)
        parent = self.tree.parent(item)
        #if parent:
        #    moveto=0

        for s in self.tree.selection():
            self.tree.move(s, parent, moveto)

    def bCopyfrom(self, e):
        self.movefrom = [{'item': item,
                          'text': self.tree.item(item, 'text'),
                          'values': self.tree.item(item, 'values')} for item in self.tree.selection()]

    def bCopyto(self, e):
        if self.movefrom is not None:
            parent = self.tree.parent(self.tree.selection()[0])
            moveto = self.tree.index(self.tree.selection()[0])+1
            [self.tree.insert(parent, moveto+i, text=self.different_var_name(parent, self.tree.item(item['item'], 'text')), values=item['values'])
             for i, item in enumerate(self.movefrom)]

            #for s in self.movefrom:
            #    self.tree.move(s, '', moveto)
            #self.movefrom = None

    def different_var_name(self, parent, text, counter=""):
        unique = [self.tree.item(i, 'text')
                  for i in self.tree.get_children(parent)]
        if '{}{}'.format(text, counter).replace('\n', '') not in unique:
            return '{}{}'.format(text, counter).replace('\n', '')
        else:
            counter = '_{}'.format(
                int(counter.replace('_', ''))+1) if counter else "_2"
            return self.different_var_name(parent, text, counter)

    def undoredo(self, mode="", mod=("type", "args")):
        if mode == "add":
            # forget what happened after current version
            self.undolist['versions'] = self.undolist['versions'][:(
                len(self.undolist['versions']) + 1 + self.undolist['index'])]
            # add last modification
            self.undolist['versions'] += [mod]
            # set index to last and current version
            self.undolist['index'] = -1
        else:
            if mode == "undo":
                if self.undolist["index"] <= -len(self.undolist['versions']):
                    self.undolist["index"] = -len(self.undolist['versions'])
                    return
                _t, _a = self.undolist['versions'][self.undolist['index']]
                if _t == "modify":
                    _ac, _ai, _av, _ = _a
                self.undolist["index"] = self.undolist["index"]-1

            elif mode == "redo":
                if self.undolist["index"] >= -1:
                    self.undolist["index"] = -1
                    return
                self.undolist["index"] = self.undolist["index"]+1
                _t, _a = self.undolist['versions'][self.undolist['index']]
                if _t == "modify":
                    _ac, _ai, _, _av = _a
                elif _t == "delrow":
                    _t = "newrow"
                elif _t == "newrow":
                    _t = "delrow"

            if _t == "modify":
                if _ac == 1:
                    self.tree.item(_ai, text=_av)
                elif _ac == 2:
                    self.casttype(_ai, str(_av).replace('\n', ''))
            elif _t == "delrow":
                for _p, _ix, _tv, _id in _a:
                    self.tree.insert(
                        parent=_p, iid=_id, index=_ix, text=_tv["text"], values=_tv["values"])
            elif _t == "newrow":
                for _, _, _, _id in _a:
                    self.tree.delete(_id)
        return

    def safe_run(self, fc, kw, loop=False, saveMemory=False):
        if self.allow_run.get() and self.menubar.options._vars["background"].get():
            return self.startthread(fc, kw)
        elif self.allow_run.get() and not self.menubar.options._vars["background"].get():
            #print(f"¤ Running\nFunction: {fc.__name__}\nModule: {fc.__module__}\nStart: {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M')}\nThe main window will freeze during run.")
            print(running_message(fc.__name__, fc.__module__,
                  message="The main window may freeze during run."))
            time.sleep(1.5)
            return fc(**kw)
        else:
            print(
                f"\nRun: {fc.__name__}\nModule: {fc.__module__}\n**kwargs: {kw}")

    def exit(self, e=9):
        if self.changetrack.get():
            self.save_setup(os.path.join(pcd, ".tmp", ".unsavedmenu", self.lib.get() + ".yaml"), meta=1, routine=1)
        exit(e)

    def on_closing(self):
        last_config_save = self.menubar.options._vars["lastconfig"].get()
        if self.changetrack.get():
            _in = askyesnocancel(
                'Quit', 'Unsaved changes.\nSave before quitting?')
            if _in:
                self.save_setup()
            if _in is None:
                return
        else:
            if self.runningtrack.get():
                _in = askyesnocancel(
                    'Quit', 'Still running (and might keep running on the background).\nAre you sure you want to quit?')
                if not _in:
                    return
        # go on to shutdown
        if last_config_save:
            self.refresh_config()
            gg.readable_file(os.path.join(pcd, '.lastconfig'), **self.menuconfig).dump()
        self.root_mother.destroy()
        python = sys.executable
        os.execl(python, python, command="quit()")


def main(*a, path=os.path.join(pcd, 'setup/readme.yaml'),
         waitimg=os.path.join(pcd, 'logo'), 
         waittxt='Gargantua v0.1',
         welcometxt='WELCOME, WILKOMEN, BIENVENUE',
         font="",
         **kw):
    if font:
        welcometxt = art.text2art(welcometxt, font=font)
    #♣full_menu(path=path, waitimg=waitimg, waittxt=waittxt, welcometxt=welcometxt + "\n", **kw)

    # get the application name and version
    opf_version = versions.version_name + " " + versions.version_number
    app = QApplication(["Gargantua"])
    # get a text editor for the log window
    textBox = QTextEdit()
    textBox.setReadOnly(True)
    logger.consoleHandler.sigLog.connect(textBox.append)
    # instance the main GUI
    ui = opf_main_ui(opf_version, textBox)
    ui.show()
    #pfp_compliance.check_executables()
    app.exec_()
    del ui


if __name__ == '__main__':
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, required=True)
    parser.add_argument('-arg2', '--argument2', type=str, required=True)
    args = parser.parse_args()
    print(args)
    """
    print("sys.argv", sys.argv)
    args = [a for a in sys.argv if '=' not in a]
    kwargs = dict([a.split('=') for a in sys.argv if '=' in a])
    main(*args, **kwargs)
