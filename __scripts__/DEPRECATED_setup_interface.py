# for full_menu and actvate_menu
#from .common import readable_file, LazyCallable
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesnocancel, askquestion
from tkinter import ttk
from tkinter import *
import ast, re
from PIL import ImageTk, Image, ImageDraw
import copy
import ntpath
import inspect
import threading, multiprocessing, queue
import queue
import warnings
from io import StringIO
import glob, pathlib
from collections import OrderedDict
import os, sys, time, datetime
import random
import numpy as np
import pandas as pd
import importlib

from . import tk_commons as tktt
from . import gargantua as gg

cfp = pathlib.Path(__file__).parent.resolve()

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
    if par: rm += f"\nMode: {par}"
    if nt: rm += f"\nParallel: {nt}"
    rm += f"\nStart: {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M')}"
    if message: rm += f"\n{message}"
    return rm + end


def update_nested_dict(d, u):
    d = d if isinstance(d, dict) else {}
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = update_nested_dict(d.get(k, {}), v)
        else:
            if isinstance(d, dict): d[k] = v
            else: d = {k: v}
    return d

def rename_nested_dict(d, u):
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = rename_nested_dict(d.get(k, {}) if isinstance(d, dict) else {}, v)
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
            waitimg = random.choice([os.path.join(waitimg, f) for f in os.listdir(waitimg) if f.endswith(('.jpg', '.jpeg', '.png', '.webp', '.ico'))])
            if os.path.exists(waitimg.rsplit('.', 1)[0] + '.credits'):
                with open(waitimg.rsplit('.', 1)[0] + '.credits') as input_file:
                    credits = input_file.readline()
        if waitimg and os.path.exists(waitimg):
            # Load the image
            image = Image.open(waitimg)
            width, height = image.size
            if width/height > top_width/top_height:
                image = image.resize(
                    (int(width * (top_height / height)), top_height), Image.ANTIALIAS)
            else:
                image = image.resize(
                    (top_width, int(height * (top_width / width))), Image.ANTIALIAS)
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
                maindir = ((-1)**random.randint(1, 2), (-1)**random.randint(1, 2))
                
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
                    draw.ellipse((x1-radius, y1-radius, x1+radius, y1+radius), fill=color)
                    x0, y0 = x1, y1

            # create a Tkinter-compatible photo image from the Pillow image
            canvas.image = ImageTk.PhotoImage(image)
            
            canvaspaint = tktt.CanvasPaint(canvas, image, width=0, height=0)#root.wait, (top_width, top_height), (0, 157, 196))
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

    def open_interface(root, *args, **kwargs):
        actvate_menu(root, *args, **kwargs)
        root.deiconify()
        root.attributes('-topmost', True)
        root.attributes('-topmost', False)
        root.wait.withdraw()
    
    root = tk.Tk()

    if wait==False:
        actvate_menu(root, *args, **kwargs)
    else:        
        root.withdraw()
        root.wait = wait_page(root, wait, waitimg, waittxt)
        #root.wait.set_focus()
        threading.Thread(target=open_interface, args=[root, *args], kwargs=kwargs).start()
        #root.after(1000, lambda r=root, a=args, k=kwargs: open_interface(r, *a, **k))
        root.after(10000, lambda: root.wait.overrideredirect(False))
    
    root.mainloop()
    #exit(0)


class actvate_menu:
    def __init__(self, root, path=None, addons=[],
                 welcometxt='¤ WELCOME, WILKOMEN, BIENVENUE\n',
                 create="enable", remove="enable", modify=True, sort="disabled", move=True):
        
        # Redirect stdout to a variable
        self.hold_std = {'in': StringIO(), 'out': StringIO(), 'err': StringIO()}  # sys.stdout
        sys.stdin = self.hold_std['in']
        sys.stdout = self.hold_std['out']  # open('stdout.txt', 'w', buffering=1)
        sys.stderr = self.hold_std['err']
                
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
        self.changetrack.trace_add('write', lambda *a: root.title(self.title + '*' * (self.changetrack.get()>0) + ' (running)' * self.runningtrack.get()))
        #self.changetrack.trace_add('write', lambda *a: self.setup_to_button() if self.changetrack.get()>0 else None)
        self.runningtrack.trace_add('write', lambda *a: root.title(self.title + '*' * (self.changetrack.get()>0) + ' (running)' * self.runningtrack.get()))

        # SETUP READ
        self.path = tk.StringVar()
        self.showpath = tk.StringVar()
        self.path.trace_add("write", lambda *a: self.showpath.set(f"{self.path.get()[:10]}...{self.path.get()[-60:]}" if len(self.path.get()) > 73 else self.path.get()))
        unsavedmenu = os.path.join(os.path.dirname(cfp), ".tmp", ".unsavedmenu", "unsavedmenu.yaml")
        if os.path.exists(unsavedmenu) and (time.time() - os.path.getmtime(unsavedmenu)) < 59:
            path = unsavedmenu
            self.path.set(path)
        elif path is not None and os.path.exists(path):
            self.path.set(path)
        else:
            self.path.set(askopenfilename(
                defaultextension='.yaml',
                filetypes=DEFAULT_FILE_TYPES))
            
        self.addon = []

        self.info = ttk.Frame(self.LeftFrame)
        self.info.pack(fill='x', anchor='nw')#grid(sticky='nswe')

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
        
        self.tree.pack(side=tk.LEFT, fill='both', expand=True)#.grid(column=0, row=0, sticky='nsew')
        
        self.tree.vsb = ttk.Scrollbar(
            self.Editable.Tree, orient="vertical", command=self.tree.yview)
        self.tree.vsb.pack(side=tk.RIGHT, fill='y', expand=False)#.grid(column=1, row=0, sticky='nswe')
        self.tree.configure(yscrollcommand=self.tree.vsb.set)

        if self.path.get() and os.path.exists(self.path.get()):
            self.menu = gg.readable_file(self.path.get()).safe_load().to_dict()
            [self.addon_path(p) for p in addons]

            if os.path.exists(self.path.get().rsplit('.', 1)[0] + '.meta'):
                self.metamenu = gg.readable_file(self.path.get().rsplit('.', 1)[0] + '.meta').safe_load(
                ).to_dict()
            else:
                self.metamenu = {}
            try:#if os.path.exists(os.path.join(os.path.dirname(cfp), '.lastconfig')):
                self.menuconfig = gg.readable_file(os.path.join(os.path.dirname(cfp), '.lastconfig')).safe_load(
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
        self.visible['Columns']["Description"].trace_add('write', self.showhide_tree)

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
        
        self.main = ttk.Frame(self.MenuClk)#self.root)
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
            kwargs = {k: {k_: v_ for k_, v_ in v.items() if k_ in ['fc', 'kw']} for k, v in self.selFunction.items() if v['state'].get()}
            fc = gg.LazyCallable(self.menu['__init__']['__run_selected__']['__init__']['path'], self.menu['__init__']['__run_selected__']['__init__']['function']).__get__().fc
            kwargs.update({k: v for k, v in self.menu['__init__']['__run_selected__'].items() if k not in SYSTEM_KEYS})
            self.startthread(fc=fc, kw=kwargs)
            # GET FUNCTION
            
            for k, v in self.selFunction:
                if v['state'].get():
                    self.startthread(v['fc'], v['kw'], silence=self.verbositynoise)
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
        _showhideshellbut = tk.Canvas(self.main, height=10, width=3, background="SystemButtonFace", borderwidth=2, relief="raised")
        _showhideshellbut.create_text(1, 50, angle="90", text="....", fill="SystemButtonText")
        _showhideshellbut.bind("<ButtonPress-1>", lambda ev: ev.widget.configure(relief="sunken"))
        _showhideshellbut.bind("<ButtonPress-1>", lambda *a: self.visible['Shell'].set(0 if self.visible['Shell'].get() else 1))
        _showhideshellbut.bind("<ButtonRelease-1>", lambda ev: ev.widget.configure(relief="raised"))
        _showhideshellbut.bind("<Configure>", lambda ev: ev.widget.configure(relief="raised"))
        _showhideshellbut.pack(fill="y", side="right")

        # PROMPT
        self.RightFrame = tk.PanedWindow(self.window, orient=tk.VERTICAL)
        #self.RightFrame.pack(fill="both", expand=True)
        self.window.add(self.RightFrame)

        #self.window = ttk.PanedWindow(self.root_mother, orient=tk.HORIZONTAL)
        #self.window.pack(expand=True, fill=tk.BOTH)
        
        # PROMPT > WINDOWs
        self.NotebookTextPromptTop = ttk.Notebook(self.RightFrame, height=100)  # .interior
        self.NotebookTextPromptTop.bind('<B1-Motion>', self.movenotebook)
        #self.NotebookTextPrompt.pack(fill='both', expand=True)
        self.RightFrame.add(self.NotebookTextPromptTop, stretch="always")

        # PROMPT > WINDOW > SHELL
        self.txtprompt = tktt.VerticalScrolledFrame(self.NotebookTextPromptTop)
        #self.txtprompt.pack(fill='both', expand=True)
        self.NotebookTextPromptTop.add(self.txtprompt, text='Shell')
        self.txtprompt.canvas.config(background='black')
        self.txtprompt.stringvar = tk.StringVar(value=welcometxt)

        self.txtprompt.label = tk.Label(self.txtprompt.interior, textvariable=self.txtprompt.stringvar,
                               anchor=tk.N+tk.W, justify='left', bg='black', fg='white', font=('Consolas', 12))
        self.txtprompt.label.bind('<Configure>', lambda e: self.txtprompt.label.config(
            wraplength=self.txtprompt.label.winfo_width()))
        self.txtprompt.label.pack(fill='both', expand=True)

        self.sysvars = tktt.VerticalScrolledFrame(self.NotebookTextPromptTop)
        self.NotebookTextPromptTop.add(self.sysvars, text='System')
        sysvarstoshow = {"file path": cfp,
                         "CPUs": multiprocessing.cpu_count()}
        for i, (k, v) in enumerate(sysvarstoshow.items()):
            tk.Label(self.sysvars.interior, text=k, bg='#D3D3D3',
                    justify='left', anchor='nw').grid(row=i+1, column=0, sticky='nswe')
            tk.Label(self.sysvars.interior, text=v, justify='left',
                    anchor='nw', wraplength=600).grid(row=i+1, column=1, sticky='nswe')
                
        # PROMPT > WINDOWs
        self.NotebookTextPromptBot = ttk.Notebook(self.RightFrame, height=50)#.interior
        self.NotebookTextPromptBot.bind('<B1-Motion>', self.movenotebook)
        self.RightFrame.add(self.NotebookTextPromptBot, stretch="always")

        # PROMPT > WINDOW > WARNINGS
        self.errprompt = tktt.VerticalScrolledFrame(self.NotebookTextPromptBot, bg='black')
        self.errprompt.canvas.config(background='black')
        self.errprompt.stringvar = tk.StringVar()
        self.errprompt.label = tk.Label(self.errprompt.interior, textvariable=self.errprompt.stringvar,
                                  anchor=tk.S+tk.W, justify='left', bg='black', fg='white', font=('Consolas', 12))
        self.errprompt.label.bind('<Configure>', lambda e: self.errprompt.label.config(
            wraplength=self.errprompt.label.winfo_width()))
        self.errprompt.label.pack(fill='both', expand=True)
        self.NotebookTextPromptBot.add(self.errprompt, text='Warnings')
        
        # PROMPT > WINDOW > TERMINAL
        self.terminalprompt = tk.Frame(self.NotebookTextPromptBot, bg='black')
        self.terminalprompt.cmd = tktt.Prompt(self.terminalprompt)
        self.terminalprompt.cmd.pack(fill='both', expand=True, anchor=tk.S)
        self.NotebookTextPromptBot.add(self.terminalprompt, text='Terminal')
        
        # PROMPT > WINDOW > BLOCKS
        def runselected__():
            if self.allow_run.get():
                ntthreads = int(trygetfromdict(self.menu, ["__init__", "API", "ntthreads"], 1))
                ntprocess = int(trygetfromdict(self.menu, ["__init__", "API", "ntprocess"], 1))

                _fc = gg.LazyCallable(trygetfromdict(self.menu, ['__init__', 'API', 'path'], 
                                                     os.path.abspath(os.path.join(cfp, '..', 'main.py'))),
                                      trygetfromdict(self.menu, ['__init__','API', 'function'], "api")).__get__().fc
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
        self.ordblock = tktt.OrderBlocks(self.frmblock.interior, list=[], edit=False)
        self.ordblock.screen.active.trace_add("write", lambda *a: self.runableblocks() if not self.ordblock.screen.active.get() else None)
        self.ordblock.pack()
        self.runblocks = tk.Button(self.ordblock, text="Run Blocks", command=lambda: runselected__())
        self.runblocks.pack(side='bottom')
        #self.edtblocks = tk.IntVar()
        #self.edtblocks.trace_add("write", lambda *a: self.ordblock.editable.set(self.edtblocks.get()))
        #self.edtblocks.trace_add("write", lambda *a: self.runableblocks())
        #self.edtblocks.set(0)
        self.NotebookTextPromptBot.add(self.frmblock, text="Routine")
         
        tk.Button(self.root_mother, text='Break', bg='red', fg='white',
                  width=5, command=lambda: os.system('python restart.py') #exit(9)
                  ).place(relx=1, rely=0, anchor='ne')
        
        # MENU BAR
        def applyfckeepmenuopen(fc, *a, **kw):
            #doesnt work
            fc(*a, **kw)
            root.tk.call('::tk::TraverseToMenu', root, 'F')

        donothing = lambda: print("Not implemented yet.")

        self.menubar = Menu(self.root_mother)
        self.menubar.file = Menu(self.menubar, tearoff=0)  

        self.menubar.file.profile = Menu(self.menubar, tearoff=0)
        self.ChoiceUsrDev = tk.IntVar(value=1)
        self.ChoiceUsrDev.trace_add('write', lambda *a: self.dev_options())        
        self.menubar.file.profile.add_radiobutton(label="User", variable=self.ChoiceUsrDev, value=0)
        self.menubar.file.profile.add_radiobutton(label="Developper", variable=self.ChoiceUsrDev, value=1)

        self.menubar.file.add_cascade(label="Profile", menu=self.menubar.file.profile)
        self.menubar.file.add_separator()
        self.menubar.file.add_command(label="New", command=lambda: donothing)
        self.menubar.file.add_command(label="Open", command=self.change_path)
        self.menubar.file.add_command(label="Addon", command=self.add_addon)
        self.menubar.file.add_command(label="Save", state="disabled", command=donothing)
        self.menubar.file.add_command(label="Save as...", command=self.save_setup)        
        self.menubar.file.add_command(label="Restart", command=lambda*a: self.exit(9))
        self.menubar.file.add_command(label="Close", command=donothing)

        self.menubar.file.add_separator()
        self.menubar.file.add_command(label="Exit", command=root.quit)
        self.menubar.add_cascade(label="File", menu=self.menubar.file)

        self.menubar.edit = Menu(self.menubar, tearoff=0)
        self.menubar.edit.add_command(label="Undo", command=lambda *a: self.undoredo("undo"))
        self.menubar.edit.add_command(label="Redo", command=lambda *a: self.undoredo("redo"))
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

        self.menubar.edit.adv = Menu(self.menubar, tearoff=0)
        self.menubar.edit.add_cascade(label="For developpers", menu=self.menubar.edit.adv)

        self.menubar.add_cascade(label="Edit", menu=self.menubar.edit)
        
        self.menubar.runf = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Run", menu=self.menubar.runf)

        self.menubar.libs = Menu(self.menubar, tearoff=0)
        [self.menubar.libs.add_command(label=l, command=lambda: self.exit(9))
        for l in os.listdir(os.path.join(os.path.dirname(cfp), "Lib")) if os.path.isdir(l)]
        self.menubar.add_cascade(label="Lib", menu=self.menubar.libs)

        self.menubar.options = Menu(self.menubar, tearoff=0)
        self.menubar.options._vars = {"background": tk.BooleanVar(value=True),
                                      "meta": tk.BooleanVar(value=True), 
                                      "routine": tk.BooleanVar(value=False), 
                                      "lastconfig": tk.BooleanVar(value=True)}
        self.allow_run = tk.IntVar(value=0)
        self.menubar.options.add_checkbutton(label="Allow run", variable=self.allow_run)
        self.menubar.options.add_checkbutton(
            label="Run on background", variable=self.menubar.options._vars["background"])
        self.menubar.options.qdelay = Menu(self.menubar.options, tearoff=0)
        self.QueueDelay = tk.IntVar(value=1)
        self.menubar.options.qdelay.add_radiobutton(label="1 sec", variable=self.QueueDelay, value=1)
        self.menubar.options.qdelay.add_radiobutton(label="10 sec", variable=self.QueueDelay, value=10)
        self.menubar.options.qdelay.add_radiobutton(label="1 min", variable=self.QueueDelay, value=60)
        self.menubar.options.qdelay.add_radiobutton(label="5 min", variable=self.QueueDelay, value=300)
        self.menubar.options.add_cascade(label="Queue Delay", menu=self.menubar.options.qdelay)
        self.menubar.options.add_separator()
        self.menubar.options.add_checkbutton(
            label="Save .meta", variable=self.menubar.options._vars["meta"])
        self.menubar.options.add_checkbutton(
            label="Save .routine", variable=self.menubar.options._vars["routine"])
        self.menubar.options.add_checkbutton(
            label="Save .lastconfig", variable=self.menubar.options._vars["lastconfig"])
        self.menubar.options.add_separator()
        self.ThreadProcess = tk.IntVar(value=1)
        self.menubar.options.add_radiobutton(label="Thread", variable=self.ThreadProcess, value=1)
        self.menubar.options.add_radiobutton(label="Processing", variable=self.ThreadProcess, value=0)
        self.menubar.options.add_radiobutton(label="Julia", variable=self.ThreadProcess, value=-1)
        self.menubar.add_cascade(label="Options", menu=self.menubar.options)
        
        self.menubar.screen = Menu(self.menubar, tearoff=0)
        [self.menubar.screen.add_checkbutton(
            label=c, variable=self.visible["Columns"][c]) for c in self.tree["columns"]]
        self.menubar.screen.add_separator()
        self.menubar.screen.add_checkbutton(label="Show/Hide Shell", variable=self.visible['Shell'])
        #self.menubar.screen.add_checkbutton(label="Show/Hide Buttons", variable=self.visible['FCButtons'])
        self.menubar.screen.add_separator()
        self.menubar.screen.add_command(label="Clear", command=cls)
        self.verbositynoise = tk.IntVar()
        self.menubar.screen.add_checkbutton(label="Silence warnings", variable=self.verbositynoise, onvalue=0, offvalue=1)        
        self.menubar.add_cascade(label="Show", menu=self.menubar.screen)

        helpmenu = Menu(self.menubar, tearoff=0)
        helpmenu.add_checkbutton(label="Tips (F11)", variable=self.help)
        self.menubar.edit.add_separator()
        helpmenu.add_checkbutton(label="Save .meta", variable=self.menubar.options._vars["meta"])
        helpmenu.add_checkbutton(label="Save .routine", variable=self.menubar.options._vars["routine"])
        helpmenu.add_checkbutton(label="Save .lastconfig", variable=self.menubar.options._vars["lastconfig"])
        self.menubar.edit.add_separator()
        helpmenu.add_command(label="Help Index", command=donothing)
        helpmenu.add_command(label="About...", command=donothing)
        self.menubar.add_cascade(label="Help", menu=helpmenu)

        self.root_mother.config(menu=self.menubar)
        
        # WORK IS DONE
        self.root_mother.after(1000, self.update_std_pipe)  # call
        self.ChoiceUsrDev.set(1)
        #self.visible["FCButtons"].set(True)
        self.changetrack.set(0 if not self.path.get().endswith("unsavedmenu.yaml") else 1)
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

        def update(txtwid, newprompt):
            cdt = datetime.datetime.fromtimestamp(time.time()).strftime("[%d-%m-%Y %H:%M]")
            newprompt = newprompt.replace("\n", f"\n| ")
            newprompt = newprompt.replace("¤ ", "\n¤ ")
            current = txtwid.stringvar.get()[-99999:]
            current = current.replace('\n\n\n', '\n\n')
            if current.endswith('\r\n'):
                #txtwid.stringvar.set(re.sub('\n.*\r\n', '\n', txtwid.stringvar.get(
                #)) + f'{new_prompt}\n')
                txtwid.stringvar.set(current.rsplit('\n', 2)[0] + f'\n{newprompt}')
            else:
                txtwid.stringvar.set(current + f'{newprompt}')
            txtwid.canvas.update_idletasks()
            txtwid.canvas.yview_moveto('1.0')

        where = {'in': self.txtprompt, 'out': self.txtprompt, 'err': self.errprompt}

        for i in ix:
                prompt = self.hold_std[i].getvalue()

                if prompt in ["", "\n"]:
                    continue
                
                update(where[i], prompt)

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
        self.ctxMenu.add_command(label='Branch', command=self.add_branch, state=state)
        self.ctxMenu.add_command(label='Delete', command=self.delrow, state=state)
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
        draw = ImageDraw.Draw(PIL.Image.new('RGBA', (22, 22), color=(0,0,0,0)))
        x, y, r = (10,10,10)
        leftUpPoint = (x-r, y-r)
        rightDownPoint = (x+r, y+r)
        twoPointList = [leftUpPoint, rightDownPoint]
        draw.ellipse(twoPointList, fill=(255,0,0,255))
        draw.text((8, 5), "i", fill=(0,0,0,0))
        draw._image
        return PIL.Image(draw._image)
    
    def runableblocks(self):
        self.ordblock.editable.set(False)
        self.ordblock.screen.active.set(False)
        for b in self.ordblock.screen.but:
            b.config(command=lambda w=b, n=b["text"]: self.buttoninforun(w, n))

    def sendtobutton(self, name):
        fc_name = trygetfromdict(self.menu, [name, "__init__", "name"], name)
        path = trygetfromdict(self.menu, [name, "__init__", "path"], self.menu['__init__']['path'])
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
        localMenu.add_command(label='run', command=lambda f=fc, k=kw: self.safe_run(f, k))
        localMenu.add_command(label='ⓘ', command=lambda f=fc, k=kw: self.infoonbutton(f, k))
        localMenu.add_command(label='move', command=lambda w=wid: moveblock(*w.req))
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
        tk.Label(self.tipfuncframe, text=kwtxt, justify='left', anchor='nw', wraplength=600).grid(row=1, column=1, sticky='nswe')
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

            if isinstance(v, dict) and ('__init__' in self.menu.keys()) and ('path' in self.menu['__init__']):
                # and ('button' in self.menu['__init__']) and self.menu['__init__']['button']!='disabled'
                create = True
                try:
                    func = gg.LazyCallable(
                        self.menu['__init__']['path'], func_name).__get__().fc
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
        ntthreads = ntthreads if ntthreads is not None else int(trygetfromdict(self.menu, ["__init__", "ntthreads"], 1))
        ntprocess = ntprocess if ntprocess is not None else int(trygetfromdict(self.menu, ["__init__", "ntprocess"], 1))
        
        if not self.CurrentThread.is_alive():
            if self.verbositynoise:
                warnings.resetwarnings()
            else:
                warnings.filterwarnings("ignore")
            if self.ThreadProcess.get() < 0:
                #print(f"¤ Running\nThread: {fc.__name__}\nModule: {fc.__module__}\nParallel: {ntthreads}\nStart: {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M')}")
                print(running_message(fc.__name__, fc.__module__, "Julia", ntthreads))
                for _ in range(max(1, min(multiprocessing.cpu_count()-1, ntthreads))):
                    self.CurrentThread = threading.Thread(target=fc, kwargs=kw)
                    self.CurrentThread.start()
                    time.sleep(self.QueueDelay.get())
            elif self.ThreadProcess.get():
                #print(f"¤ Running\nThread: {fc.__name__}\nModule: {fc.__module__}\nParallel: {ntthreads}\nStart: {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M')}")
                print(running_message(fc.__name__, fc.__module__, "Thread", ntthreads))
                for _ in range(max(1, min(multiprocessing.cpu_count()-1, ntthreads))):
                    self.CurrentThread = threading.Thread(target=fc, kwargs=kw)
                    self.CurrentThread.start()
                    time.sleep(self.QueueDelay.get())
            else:
                #print(f"¤ Running\nProcess: {fc.__name__}\nModule: {fc.__module__}\nParallel: {ntprocess}\nStart: {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M')}")
                print(running_message(fc.__name__, fc.__module__, "Multiprocessing", ntprocess))
                for _ in range(max(1, min(multiprocessing.cpu_count()-1, ntprocess))):
                    self.CurrentThread = multiprocessing.Process(target=fc, kwargs=kw)
                    self.CurrentThread.start()
                    time.sleep(self.QueueDelay.get())
            self.CurrentThread.__name__ = str(fc.__name__)
        else:
            print(f"Nothing was done, because '{self.CurrentThread.__name__}' is still active.")
    

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
                                         trygetfromdict(tp, ['type'], type(v).__name__), 
                                         trygetfromdict(tp, ['help'], "")))
                self.nrow += 1
        
        self.runableblocks()
        self.refresh_functions()
        #self.setup_to_button()

    def refresh_functions(self):
        self.menubar.runf.delete(0, "end")
        refd = gg.referencedictionary(self.menu, meta=self.metamenu, kinit=True)
        allfunctions = {k: {k_: v_ for k_, v_ in v.items() if k_ not in ["__init__"]} if isinstance(
            v, dict) else v for k, v in refd.items() if k not in ["__init__"]}
        
        for k, v in allfunctions.items():
            state = 'normal'
            try:
                _init = refd[k]['__init__']
                fn = trygetfromdict(_init, ['function'], k)
                print(k, _init['path'], fn)
                func = gg.LazyCallable(_init['path'], fn).__get__().fc
            except:
                try:
                    fn = trygetfromdict(refd, [k, '__init__', 'function'], k)
                    #try:
                    #    fn = _menu[k]['__init__']['function']
                    #except:
                    #    fn = k
                    print(refd['__init__']['path'], fn)
                    print(gg.LazyCallable(refd['__init__']['path'], fn).__get__())
                    func = gg.LazyCallable(refd['__init__']['path'], fn).__get__().fc
                    print('success')
                except Exception as e:
                    print(str(e))
                    func = None
                    state='disabled'
            self.menubar.runf.add_command(label=k, command=lambda fc=func, kw=v: self.safe_run(fc, kw), state=state)


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
            if os.path.exists(os.path.join(os.path.dirname(cfp), '.lastconfig')):
                self.menuconfig = gg.readable_file(os.path.join(os.path.dirname(cfp), '.lastconfig')).safe_load(
                ).to_dict()

            self.path.set(npath)
            [a.destroy() for a in self.addon]
            self.addon = []
            self.changetrack.set(0)
            self.refresh_tree() 

    def add_addon(self, npath=None):
        if npath == None:
            npath = askopenfilename(title='Select setup path',
                                        defaultextension='.yaml',
                                        filetypes=DEFAULT_FILE_TYPES)
        if os.path.exists(npath) == False:
            return
        self.addon_path(npath)
        self.refresh_tree(config_kwargs={"win": False})       
        return 

    def addon_path(self, npath):
        self.menu = update_nested_dict(self.menu, gg.readable_file(npath).safe_load().to_dict())
        if os.path.exists(npath.rsplit('.', 1)[0] + '.meta'):
            self.metamenu = update_nested_dict(self.metamenu, gg.readable_file(npath.rsplit('.', 1)[0] + '.meta').safe_load().to_dict())
        #self.path.set(self.path.get() +
        #              f' + {ntpath.basename(npath).rsplit(".", 1)[0]}')
        label = ntpath.basename(npath).rsplit(".", 1)[0]
        label = re.sub("^(readme)?(addon)?_", "", label)
        self.addon += [tk.Label(self.info, text=f'+ {label}', fg='white', bg='green')]
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
                                         trygetfromdict(tp_, ['type'], type(v_).__name__),
                                         trygetfromdict(tp_, ['help'], "")))
                self.nrow += 1

    def treeview_sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
            self.tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))

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
                unique = [self.tree.item(i, 'text') for i in self.tree.get_children(self.tree.parent(item)) if i != item] 
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
            
            if cn==1:
                v = str(v)
                self.menu = rename_nested_dict(self.menu, rename)
                self.metamenu = rename_nested_dict(self.metamenu, rename)
            else:
                v = str(v) if self.tree.item(item, 'value')[1] in ['str', 'function'] else ast.literal_eval(str(v))
                if type(v).__name__ != self.tree.item(item, 'value')[1]:
                    warnings.warn(f"Sending value as {type(v)} when it showed as {self.tree.item(item, 'value')[1]}.")
                self.menu = update_nested_dict(self.menu, fromparent(item, v))
                self.metamenu = update_nested_dict(self.metamenu, fromparent(item, {"type": self.tree.item(item, 'value')[1]}))
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
        self.FNewVar.pack(fill='both', expand=True)#.grid(column=0, sticky='nswe')
        #self.FShow.grid_rowconfigure(0, weight=2)
        #self.FShow.grid_rowconfigure(1, weight=3)

        suggestionlabel = item_text['text'] if (self.tree.get_children(item)) or (cn==1) else item_text['values'][0] if cn == 2 else item_text['values'][1]
        
        entrylabel = tk.Label(self.FNewVar, text='replace:', width=15, height=1, anchor=tk.W)
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
                                text=self.different_var_name(parent, '__VAR__'),
                                values=values)
                self.tree.update()
                self.changetrack.set(self.changetrack.get()+1)
                if keeptrack:
                    self.undoredo("add", ("newrow", [[parent, index, self.tree.item(self.nrow), self.nrow]]))
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
            if keeptrack: self.undoredo("add", ("delrow", delrows))


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
        #gg.checkcustomtypes(v)
        if re.match("f\(.+,.+\)", v):
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
                    value = str(val[0]) if val[1] in ['str', 'function'] else ast.literal_eval(str(val[0]))
                    if type(value).__name__ != val[1]:
                        warnings.warn(f"Sending value as {type(value)} when it showed as {val[1]}.")
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
                    v.set(self.menu['__init__']['OPEN_DEFAULTS']['VISIBILITY'][k])
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
                self.ordblock.screen.butlist = self.menuroutine['__init__']['OPEN_DEFAULTS']["ORG_BUTTONS"]
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
        self.menuroutine = update_nested_dict(self.menuroutine, {'__init__': {'OPEN_DEFAULTS': {"ORG_BUTTONS": self.ordblock.screen.butlist}}})
        self.menuroutine = update_nested_dict(self.menuroutine, {'__init__': {'OPEN_DEFAULTS': {"FUN_BUTTONS": self.butFunction}}})

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
                gg.readable_file(save_path.rsplit('.', 1)[0] + ".meta", **self.metamenu).dump()
            if routine or self.menubar.options._vars["routine"].get():
                gg.readable_file(save_path.rsplit('.', 1)[0] + ".routine", **self.menuroutine).dump()
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
            self.tipwindow = tw = Toplevel(self.widget)
            tw.wm_overrideredirect(1)
            tw.wm_geometry("+%d+%d" % (x, y))
            label = Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=SOLID, borderwidth=1,
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
            text = [item_text['text'], item_text['values'][0], item_text['values'][1], item_text['values'][2]]
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

                label = Label(self.tipwindow, text=text, justify=LEFT,
                            background="#ffffe0", relief=SOLID, borderwidth=1,
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
            self.undolist['versions'] = self.undolist['versions'][:(len(self.undolist['versions']) + 1 + self.undolist['index'])]
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
                if _t == "modify": _ac, _ai, _av, _ = _a
                self.undolist["index"] = self.undolist["index"]-1
            
            elif mode == "redo":
                if self.undolist["index"] >= -1:
                    self.undolist["index"] = -1
                    return
                self.undolist["index"] = self.undolist["index"]+1
                _t, _a = self.undolist['versions'][self.undolist['index']]
                if _t == "modify": _ac, _ai, _, _av = _a
                elif _t == "delrow": _t = "newrow"
                elif _t == "newrow": _t = "delrow"
            
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
            print(f"\nRun: {fc.__name__}\nModule: {fc.__module__}\n**kwargs: {kw}")

    def exit(self, e=9):
        if self.changetrack.get():
            self.save_setup(os.path.join(os.path.dirname(
                cfp), ".tmp", ".unsavedmenu", "unsavedmenu.yaml"), meta=1, routine=1)
        exit(e)

    def on_closing(self):
        last_config_save = self.menubar.options._vars["lastconfig"].get()
        if self.changetrack.get():
            _in = askyesnocancel('Quit', 'Unsaved changes.\nSave before quitting?')
            if _in:
                self.save_setup()
            if _in is None:
                return
        else:
            if self.runningtrack.get():
                _in = askyesnocancel('Quit', 'Still running (and might keep running on the background).\nAre you sure you want to quit?')
                if not _in:
                    return
        # go on to shutdown
        if last_config_save:
            self.refresh_config()
            gg.readable_file(os.path.join(os.path.dirname(cfp), '.lastconfig'), **self.menuconfig).dump()
        self.root_mother.destroy()
        python = sys.executable
        os.execl(python, python, command="quit()")


if __name__ == '__main__':
    print(sys.argv)
    args = [a for a in sys.argv[1:] if '=' not in a ]
    kwargs = dict([a.split('=') for a in sys.argv[1:] if '=' in a])
    full_menu(*sys.argv[1:])
