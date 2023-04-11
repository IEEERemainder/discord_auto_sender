import tkinter as tk
from  tkinter import ttk
from tkinter import scrolledtext
from discord_api.discord_api import *
from tkinter import filedialog as fd
import threading
import sys
import re
import time

class DASTask:
    def __init__(self):
        pass

class DiscordAutoSender(tk.Tk):
    def __init__(self, tocen='', dataPath=''):
        super().__init__()
        self.title("Discord Auto Sender GUI")
        self.underlying=[]
        self.columns = ('taskId', 'name', 'running', 'targets', 'timings', 'message', 'files', 'sent', 'errors')
        self.columnsWrappers = (tk.IntVar, tk.StringVar, tk.IntVar, tk.StringVar, tk.StringVar, tk.StringVar, tk.StringVar, tk.IntVar, tk.IntVar)
        self.tree = ttk.Treeview(self, show="headings", columns=self.columns)
        for i in range(len(self.columns)):
            self.tree.heading("#" + str(i + 1), text=self.columns[i])
        ysb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)
        #self.createExampleRow()
        self.tree.bind("<Double-Button-1>", self.on_dbl_clic)
        self.tree.grid(row=0, column=0)
        ysb.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        p1 = tk.PanedWindow()
        p1.grid(row=1, column=0, sticky=tk.N + tk.S)
        p1.add(tk.Label(self, text='Tocen'))
        self.tocenVar = tk.StringVar(self, tocen)
        p1.add(tk.Entry(self, textvariable=self.tocenVar, show='*'))
        p1.add(tk.Button(self, text='new task', command=self.createExampleRow))
        p1.add(tk.Button(self, text='delete task', state='disabled', command=self.deleteSelected))
        p1.add(tk.Button(self, text='load tasks', command=self.loadTascs))
        p1.add(tk.Button(self, text='save tasks', command=self.saveTascs))
        self.lastTocenUsed=''
        self.RESOLUTION_S = 1
        self.api=None
        self.running=True
        self.lastRuns={}
        self.channelsGroupsLines=None
        if dataPath:
            self.loadTascsInner(dataPath)
        self.heartbeat()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.editing=False

    def on_closing(self):
        self.running = False
        self.destroy()
        #self.worcerThread.join()

    def deleteSelected(self):
        raise Exception("Temporarily brocen")
        indexes=[self.tvIndexToInt(x) for x in self.tree.selection()] # attach tvId to underlying id to fix
        indexes = sorted(indexes, reverse=True)
        for i in indexes:
            del self.underlying[i]
            self.tree.delete(self.intToTvIndex(i))

    def loadTascs(self):
        filename = fd.askopenfilename(
            title='Open a json file',
            filetypes= (('JSON files', '*.json'),)
        )
        self.loadTascsInner(filename)

    def loadTascsInner(self, filename):
        j = json.load(open(filename, encoding='utf-8'))
        self.tree.delete(*self.tree.get_children())
        for e in j:
            self.newRow([(str if n != 'files' else json.dumps)(e[n]) for n in self.columns])

    def saveTascs(self):
        filename = fd.asksaveasfilename(
            title='Select json target',
            filetypes= (('JSON files', '*.json'),)
        )
        self.saveTascsInner(filename)

    def getTreeValues(self, tree):
        return [list(tree.item(self.intToTvIndex(index)).values())[2] for index in range(len(tree.get_children()))]

    def saveTascsInner(self, filename):
        col = self.getTreeValues(self.tree)
        res = [{self.columns[i] : json.loads(item[i]) if i in [3, 6] else item[i] for i in range(len(self.columns))} for item in col]
        json.dump(res, open(filename, mode='w', encoding='utf-8'), ensure_ascii=False)

    def createExampleRow(self):
        self.newRow([len(self.underlying)+1, 'exampleTasc', 0, '[]', '10s', 'Hello, world!', "[]", 0, 0]) # [{\"filename\": \"hello.png\", \"path\": \"c:\\\\users\\\\paul\\\\images\\\\hello.png\",\"desc\": \"beautiful flowers with hello text\"}]

    def selectTargetChannels(self):
        top = tk.Toplevel()
        self.sTTop = top
        self.targetsUnderlying=[]
        channelsVar = tk.StringVar()
        groupsVar = tk.StringVar()
        j = json.loads(self.underlying[self.tvIndexToInt(self.lastS)][3].get())
        resultVar=tk.StringVar()
        resultVar.set(j)
        self.stChannelsVar = channelsVar
        self.stResultVar=resultVar
        

        p = tk.PanedWindow(top)
        p.pack(fill=tk.BOTH, expand=1)
        lb = tk.Listbox(p, listvariable=channelsVar, selectmode='extended')
        lb2 = tk.Listbox(p, listvariable=groupsVar, selectmode='single')
        lb3 = tk.Listbox(p, listvariable=resultVar, selectmode='extended')
        lb2.bind("<Double-Button-1>", self.newChannelsGroupSelected)
        self.stGroupsListBox = lb2
        self.stChannelsListBox = lb
        self.stResultListBox = lb3
        self.initChannelsGroupsLines()
        groupsVar.set(self.channelsGroupsLines)
        p.add(lb2)
        p.add(lb)
        p1 = tk.PanedWindow(p, orient=tk.VERTICAL)
        
        p.add(p1)
        p.add(lb3)
            
        #lb2.pack(side='left')
        #lb.pack(side='left')
        
        #p1.pack(side='left')
        #lb3.pack(side='left')
        for i in [tk.Button(top, text='>', command=self.addOne),
                            tk.Button(top, text='>>', command=self.addAll),
                            tk.Button(top, text='<', command=self.removeOne),
                            tk.Button(top, text='<<', command=self.removeAll),
                            tk.Button(top, text='OK', command=self.stSaveNExit)]:
            p1.add(i)
        top.mainloop()

    def stSaveNExit(self):
        self.targetsVar.set(json.dumps(self.targetsUnderlying))
        self.targetsInfo = [self.stResultListBox.get(i) for i in range(self.stResultListBox.size())]
        print(self.targetsInfo)
        self.sTTop.destroy()
    
    def user_readable(self,u):
        return u["username"] + "#" + u["discriminator"]

    def channel_readable(self, c, channels, guild):
        prefix = c["parent_id"] and next((x["name"]+"/" for x in channels if x["id"] == c["parent_id"]), '') or ''
        suffix = guild and " (" + guild['name'] + ")" or '' 
        return(prefix + c["name"] + suffix)
    
    def initChannelsGroupsLines(self):
        if not self.channelsGroupsLines:
            self.initApi()
            self.channelsGroupsLines = ["DM", "DM (people)", "DM (groups)", *[g['name'] for g in self.api.get("GUILDS")]]
    def newChannelsGroupSelected(self, *a):
        self.targetsUnderlying = []
        indx = self.stGroupsListBox.curselection()[0]
        if indx == 0:
            lines = [*self.getPeopleDMsLines(), *self.getGroupsDMsLines()]
        elif indx == 1:
            lines = self.getPeopleDMsLines()
        elif indx == 2:
            lines = self.getGroupsDMsLines()
        else:
            lines = self.getGuildChannelsLines(indx - 3)
        self.stChannelsVar.set(lines)

    def getPeopleDMsLines(self):
        t = self.api.get("DM_TWOSOME")
        self.stLastUnderlying = t
        return [self.user_readable(d["recipients"][0]) for d in t]

    def getGroupsDMsLines(self):
        t = self.api.get("DM_GROUPS")
        self.stLastUnderlying = t
        return [(g["name"] or "") + " " + ";".join([self.user_readable(x) for x in g["recipients"]]) for g in t]

    def getGuildChannelsLines(self, guildIndex):
        guilds = self.api.get("GUILDS")
        g = guilds[guildIndex]
        channels = self.api.get("GUILD_CHANNELS", id=g['id'])
        textChannels = [x for x in channels if x['type'] in [0,2]]
        self.stLastUnderlying = textChannels
        return [self.channel_readable(c, channels, g) for c in textChannels]

    def updateUnderlying(self, i, delete=False):
        if delete:
            del self.targetsUnderlying[i]
        else:
            self.targetsUnderlying.append(int(self.stLastUnderlying[i]['id']))
        print(self.targetsUnderlying)
        
    def addOne(self):
        for i in self.stChannelsListBox.curselection():
            self.stResultListBox.insert('end', self.stChannelsListBox.get(i))
            self.updateUnderlying(i)
            
    def addAll(self):
        for i in range(self.stChannelsListBox.size()):
            self.stResultListBox.insert('end', self.stChannelsListBox.get(i))
            self.updateUnderlying(i)
                                        
    def removeOne(self):
        for i in self.stResultListBox.curselection()[::-1]:
            self.stResultListBox.delete(i, i)
            self.updateUnderlying(i, True)
                                        
    def removeAll(self):
        self.stResultListBox.delete(0, "end")
        self.targetsUnderlying=[]
        
    def createPW(self, master,items, **cwgs):
        p = tk.PanedWindow(master, **cwgs)
        for i in items:
            if type(i) == type(lambda:0):
                i = i(master)
            p.add(i)
        return p
    
    def createFrame(self, master, side, panes):
        f = tk.Frame(master)
        for p in panes:
            p.pack(side=side)
        return f
    
    def selectFiles(self):
        top = tk.Toplevel()
        self.sfTop = top
        pathVar = tk.StringVar(top)
        filenameVar=tk.StringVar(top)
        descVar=tk.StringVar(top)
        
        self.sfVars=[pathVar,filenameVar,descVar]

        self.createFrame(top, 'top', [
            self.createPW(top, [lambda m: tk.Label(m, text='path'), lambda m: tk.Entry(m, textvariable=pathVar), lambda m: tk.Button(m, text='browse', command=self.browseFile)]),
            self.createPW(top, [lambda m: tk.Label(m, text='filename'), lambda m: tk.Entry(m, textvariable=filenameVar)]),
            self.createPW(top, [lambda m: tk.Label(m, text='description'), lambda m: tk.Entry(m, textvariable=descVar)]),
            self.createPW(top, [lambda m: tk.Button(m, text='add', command=self.addFile), lambda m: tk.Button(m, text='delete', command=self.delFile)])
        ]).pack(side='top')
      
        self.sfColumns=('path', 'filename', 'desc')
        tree = ttk.Treeview(top, show="headings", columns=self.sfColumns)
        self.sfTree=tree
        j = json.loads(self.underlying[self.tvIndexToInt(self.lastS)][-3].get())
        for d in j:
            self.sfTree.insert("", tk.END, values=[d[p] for p in self.sfColumns])
        tree.pack(side='top')
        for i in range(len(self.sfColumns)):
            tree.heading("#" + str(i + 1), text=self.sfColumns[i])
        tk.Button(top, text='save', command=self.sfSaveNExit).pack(side='top')

        top.mainloop()

    def sfSaveNExit(self):
        self.filesVar.set(json.dumps([{self.sfColumns[i] : e[i] for i in range(len(self.sfColumns))} for e in self.getTreeValues(self.sfTree)], ensure_ascii=False))
        self.sfTop.destroy()
        
    def normalizeFilename(self, v):
        return re.sub('[^A-Za-z_\.\-]', '_', v)
    def browseFile(self):
        v=fd.askopenfilename(
            title='Open a file',
        )
        self.sfVars[0].set(v)
        if self.sfVars[1].get() == '':
           #self.sfVars[1].set(self.normalizeFilename(v[v.rfind(os.sep)+1:])) # always /
            self.sfVars[1].set(self.normalizeFilename(v[v.rfind('/')+1:]))
    def addFile(self):
        self.sfTree.insert("", tk.END, values=[x.get() for x in self.sfVars])
        for x in self.sfVars:
            x.set("")
    def delFile(self):
        self.sfTree.delete(self.sfTree.selection()[0])
        
    def tvIndexToInt(self, v):
        return int(v[1:])-1
    
    def intToTvIndex(self, i):
        return 'I' + str(i+1).zfill(3)
    
    def on_dbl_clic(self,event):
        self.editing=True
        s = self.tree.selection()[0]
        self.lastS=s
        item = self.tree.item(s)
        values = item["values"]
    
        top = tk.Toplevel()
        self.top=top
        top.title("Tasc edit")
        text=None
        for i in range(len(self.columns)):
            tk.Label(top, text=self.columns[i]).grid(row=i,column=0)
            columnName = self.columns[i]
            var = self.underlying[self.tvIndexToInt(s)][i]
            if columnName in ['name', 'timings', 'taskId']:
                tk.Entry(top, textvariable=var).grid(row=i,column=1)
            elif columnName == 'running':
                ttk.Checkbutton(top, variable=var).grid(row=i,column=1)
            elif columnName == 'targets':
                tk.Entry(top, textvariable=var).grid(row=i,column=1)
                self.targetsVar=var
                tk.Button(top, text='browse', command=self.selectTargetChannels).grid(row=i,column=2)
            elif columnName == 'message':
                text = scrolledtext.ScrolledText(top, height=5, width=60, background = 'black', foreground = "white")
                self.text=text
                text.insert(tk.INSERT, var.get())
                text.grid(row=i, column=1)
            elif columnName == 'files':
                tk.Entry(top, textvariable=var).grid(row=i,column=1)
                self.filesVar=var
                tk.Button(top, text='browse', command=self.selectFiles).grid(row=i,column=2)
            elif columnName in ['sent', 'errors']:
                tk.Entry(top, textvariable=var, state='readonly').grid(row=i,column=1) 
        tk.Button(top, text='save', command=self.saveChangesNExit).grid(row=len(self.columns),column=1)
        top.mainloop()
    
    def saveChangesNExit(self):
        self.underlying[self.tvIndexToInt(self.lastS)][5] = tk.StringVar(self, self.text.get("1.0", tk.END))
        self.updateRow(self.tvIndexToInt(self.lastS))
        self.top.destroy()
        self.editing=False
        
    def updateRow(self, i):
        self.tree.item(self.intToTvIndex(i), values=[x.get() if type(x) != type('') else x for x in self.underlying[i]])

    def initApi(self):
        if not self.api or self.lastTocenUsed != self.tocenVar.get():
            self.api = DiscordApi(self.tocenVar.get(), RLRProcessor=BasicRLRProcessor())
            self.lastTocenUsed = self.tocenVar.get()

    def log(self, json, index):
        print(f"ERROR IN {self.tree.item(self.intToTvIndex(index))['values']}: {json}") # hit slowmode? add a minute to timings until I ll fix it

    def timeStrToNs(self, v):
        # 1s1m1h1d
        v = [x for x in re.split('([a-z]+)', v) if x]
        resultNs = 0
        nsToS = 1_000_000_000
        multipliers = { # add send one time in certain time?
            "s" : nsToS,
            "m": nsToS * 60,
            "h" : nsToS * 60 * 60,
            "d" : nsToS * 60 * 60 * 24
        }
        for i in range(0, len(v), 2):
            resultNs += int(v[i]) * multipliers[v[i+1]]
        return resultNs
            
    
    def heartbeat(self):
        #print("hb")
        index=-1
        for i in self.underlying:
            index += 1
            now = time.time_ns()
            if i[2].get() == 0 or self.editing:
                if i[0].get() in self.lastRuns:
                    del self.lastRuns[i[0].get()]
                continue
            print("tasc",i[0].get(), "active")
            if i[0].get() in self.lastRuns :
                dt = (now - self.lastRuns[i[0].get()])
                print(dt)
                if dt < self.timeStrToNs(i[4].get()): continue
                
            self.lastRuns[i[0].get()] = now
            self.initApi()
            for channelId in json.loads(i[3].get()):
                res = self.api.send_message(channelId, i[5].get(), json.loads(i[6].get()), supressErrors=True)
                if 'message' in res:
                    i[-1].set(i[-1].get() + 1)
                    self.log(res, index)
                else:
                    i[-2].set(i[-2].get() + 1)
                self.updateRow(index)
        self.worcerThread = threading.Timer(self.RESOLUTION_S, self.heartbeat, []) # rename to timer?
        self.worcerThread.start()
                    
    def newRow(self, values):
        self.underlying.append([wr(self, v) for wr, v in zip(self.columnsWrappers, values)])
        self.tree.insert("", tk.END, values=values)

app = DiscordAutoSender(sys.argv[1] if len(sys.argv) >= 2 else '', sys.argv[2] if len(sys.argv) >= 3 else '')
app.mainloop()
