import cPickle as pickle
import Tkinter, ttk, re

#load recipe list
f = open('sub/Recipes.list','r')
Recipes = pickle.load(f)
f.close()

#load ingredient list
f = open('sub/Ingredients.dict','r')
Ingredients = pickle.load(f)
f.close()

#useful lists for later
classlist = ['Any','Alchemist','Armorer','Blacksmith','Carpenter','Culinarian','Goldsmith','Leatherworker','Weaver']
levellist = ['Any','1-5','6-10','11-15','16-20','21-25','26-30','31-35','36-40','41-45','46-50','50+']
leveldict = {'Any':range(1,100),'1-5':range(1,6),'6-10':range(6,11),'11-15':range(11,16),'16-20':range(16,21),'21-25':range(21,26),'26-30':range(26,31),'31-35':range(31,36),'36-40':range(36,41),'41-45':range(41,46),'46-50':range(46,51),'51+':range(51,100)}












#search recipe list by name
def find(name):
    for recipe in Recipes:
        if name == recipe['Name']:
            return recipe

#display results based on class, level, and name restraints
def search(*args):
    cs = csearch.get()
    ls = lsearch.get()
    ns = nsearch.get()
    trl = [recipe for recipe in Recipes if (cs == 'Any' or recipe['Class'] == cs) and (recipe['Level'] in leveldict[ls]) and (ns.lower() in recipe['Name'].lower())]
    resultlist.set(tuple(['{} ({} Level {})'.format(recipe['Name'], recipe['Class'], recipe['Level']) for recipe in trl]))

#add selected recipe to makelist
def add(*args):
    for idx in rlistbox.curselection():
        idx = int(idx)
        item = re.sub(' \(.* Level [0-9]*\)$', '', eval(resultlist.get())[idx])
        if item in mllistd:
            mllistd[item] += 1
        else:
            mllistd[item] = 1
    mllist.set(tuple(['{}x {}'.format(mllistd[item], item) for item in mllistd if mllistd[item] > 0]))

#remove selected recipe to makelist
def minus(*args):
    for idx in mllistbox.curselection():
        idx = int(idx)
        item = re.sub('^[0-9]*x ', '', eval(mllist.get())[idx])
        if item in mllistd:
            mllistd[item] -= 1
            if mllistd[item] == 0:
                del mllistd[item]
    mllist.set(tuple(['{}x {}'.format(mllistd[item], item) for item in mllistd if mllistd[item] > 0]))

#update ingredient list
def update(*args):
    totals = {}
    for child in iltree.get_children():
        iltree.delete(child)
    for child in tltree.get_children():
        tltree.delete(child)
    for item in mllistd:
        recipe = find(item)
        for ingredient in recipe['Ingredients']:
            if ingredient[0] not in [iltree.item(child)['text'] for child in iltree.get_children()]:
                iltree.insert('', 'end', ingredient[0], text=ingredient[0])
                if ingredient[0] in Ingredients:
                    iltree.set(ingredient[0], 'info', Ingredients[ingredient[0]])
                iltree.set(ingredient[0], 'count', ingredient[1] * mllistd[str(item)])
            else:
                iltree.set(ingredient[0], 'count', iltree.set(ingredient[0], 'count') + ingredient[1] * mllistd[str(item)])
            if ingredient[0] in [recipe['Name'] for recipe in Recipes]:
                birth(ingredient[0])
    counttotals('', totals)
    for base in totals:
        bid = tltree.insert('', 'end', text=base, values=(totals[base],))
        if base in Ingredients:
            tltree.set(bid, 'info', Ingredients[base])
    for child in iltree.get_children():
        name = iltree.item(child)['text'].lower()
        if 'shard' in name or 'crystal' in name or 'cluster' in name:
            iltree.move(child, '', 0)
    for child in tltree.get_children():
        name = tltree.item(child)['text'].lower()
        if 'shard' in name or 'crystal' in name or 'cluster' in name:
            tltree.move(child, '', 0)

#populate tree with child ingredients
def birth(parent):
    recipe = find(iltree.item(parent)['text'])
    for ingredient in recipe['Ingredients']:
        _id = '{}/{}'.format(parent, ingredient[0])
        if _id not in iltree.get_children(parent):
            iltree.insert(parent, 'end', _id, text=ingredient[0])
            if ingredient[0] in Ingredients:
                iltree.set(_id, 'info', Ingredients[ingredient[0]])
        iltree.set(_id, 'count', ingredient[1] * iltree.set(parent, 'count'))
        if ingredient[0] in [recipe['Name'] for recipe in Recipes]:
            birth(_id)

#get the total counts for base mats
def counttotals(parent, totals):
    for child in iltree.get_children(parent):
        if len(iltree.get_children(child)) == 0:
            if iltree.item(child)['text'] not in totals:
                totals[iltree.item(child)['text']] = iltree.set(child, 'count')
            else:
                totals[iltree.item(child)['text']] += iltree.set(child,'count')
        else:
            counttotals(child, totals)









        
#make a window
root = Tkinter.Tk()
root.title('FFXIV Crafting Tool')
root.geometry('{}x{}'.format(int(root.winfo_screenwidth()*.75), int(root.winfo_screenheight()*.75)))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0,weight=1)

#top level frame
sup = ttk.Frame(root, padding=(5,5,5,5))
sup.grid(column=0, row=0, sticky='NSEW')
sup.grid_columnconfigure(0, weight=1)
sup.grid_rowconfigure(0, weight=1)

#top level panedwindow
tpane = ttk.Panedwindow(sup, orient=Tkinter.HORIZONTAL)
tpane.grid(column=0, row=0, sticky='NSEW')

#input frame with instructions for user
inst = ttk.LabelFrame(sup, text='What would you like to create?')
tpane.add(inst, weight=1)
inst.grid_columnconfigure(0, weight=1)
inst.grid_columnconfigure(1, weight=1)
inst.grid_rowconfigure(4, weight=1)

#input frame widgets follow

##widget variables
csearch = Tkinter.StringVar(value='Any')
lsearch = Tkinter.StringVar(value='Any')
nsearch = Tkinter.StringVar()
nsearch.trace('w',search)
##various widgets
clabel = ttk.Label(inst, text='Class')
llabel = ttk.Label(inst, text='Level Range')
ccombo = ttk.Combobox(inst, textvariable=csearch)
lcombo = ttk.Combobox(inst, textvariable=lsearch)
##set up class and level comboboxes
ccombo['values'] = tuple(classlist)
lcombo['values'] = tuple(levellist)
ccombo.bind('<<ComboboxSelected>>',search)
lcombo.bind('<<ComboboxSelected>>',search)
##more widgets
slabel = ttk.Label(inst, text='Search')
sentry = ttk.Entry(inst, textvariable=nsearch)
##arrange in parent frame
clabel.grid(column=0, row=0, sticky='W')
llabel.grid(column=1, row=0, sticky='W')
ccombo.grid(column=0, row=1, sticky='EW', padx=5, pady=5)
lcombo.grid(column=1, row=1, sticky='EW', padx=5, pady=5)
slabel.grid(column=0, row=2, columnspan=2, sticky='W')
sentry.grid(column=0, row=3, columnspan=2, sticky='EW', padx=5, pady=5)

##next frame contains search results (still within input frame)
resultframe = ttk.Frame(inst)
resultframe.grid(column=0, row=4, columnspan=2, sticky='NSEW')
resultframe.grid_rowconfigure(0, weight=1)
resultframe.grid_columnconfigure(0, weight=1)

##results frame widgets

###variable
resultlist = Tkinter.StringVar()
###widgets
rlistbox = Tkinter.Listbox(resultframe, listvariable=resultlist, selectmode='extended', height=10)
rlistbox.bind('<Double-1>', add)
rscroll = ttk.Scrollbar(resultframe, orient=Tkinter.VERTICAL, command=rlistbox.yview)
rlistbox.configure(yscrollcommand=rscroll.set)
raddbutton = ttk.Button(resultframe, text='+', width=3, command=add)
ralabel = ttk.Label(resultframe, text='->')
rminusbutton = ttk.Button(resultframe, text='-', width=3, command=minus)
###arrange
rlistbox.grid(column=0, row=0, rowspan=3, sticky='NSEW', padx=(5, 0), pady=(0, 5))
rscroll.grid(column=1, row=0, rowspan=3, sticky='NS', padx=(0, 5), pady=(0, 5))
raddbutton.grid(column=3, row=0, padx=5, sticky='SEW')
ralabel.grid(column=3, row=1)
rminusbutton.grid(column=3, row=2, padx=5, pady=(0, 25), sticky='NEW')

#mlist and tlist frams' paned window
mpane = ttk.Panedwindow(tpane, orient=Tkinter.VERTICAL)
tpane.add(mpane, weight=1)

#ingredient list frame
ilframe = ttk.LabelFrame(sup, text='Ingredient List')
mpane.add(ilframe, weight=2)
ilframe.grid_columnconfigure(0, weight=1)
ilframe.grid_rowconfigure(0,weight=1)

##variable
illistd = {}
##widgets
iltree = ttk.Treeview(ilframe, columns=('count','info'), height=8)
iltree.column('#0', width=150, minwidth=150, stretch=0)
iltree.column('count', width=50, minwidth=50, stretch=0)
iltree.heading('#0', text='Ingredient', anchor='w')
iltree.heading('count', text='Count', anchor='w')
iltree.heading('info', text='Info', anchor='w')
ilscroll = ttk.Scrollbar(ilframe, orient=Tkinter.VERTICAL, command=iltree.yview)
iltree.configure(yscrollcommand=ilscroll.set)
##arrange
iltree.grid(column=0, row=0, sticky='NSEW', padx=(5, 0), pady=(5, 5))
ilscroll.grid(column=1, row=0, sticky='NS', padx=(0, 5), pady=(5, 5))

#makelist frame
mlframe = ttk.LabelFrame(sup, text='Make List')
mpane.add(mlframe, weight=1)
mlframe.grid_columnconfigure(0, weight=1)
mlframe.grid_rowconfigure(0,weight=1)

##variable
mllist = Tkinter.StringVar(value=())
mllist.trace('w', update)
mllistd = {}
##widgets
mllistbox = Tkinter.Listbox(mlframe, listvariable=mllist, selectmode='extended', height=10)
mllistbox.bind('<Double-1>', minus)
mlscroll = ttk.Scrollbar(mlframe, orient=Tkinter.VERTICAL, command=mllistbox.yview)
mllistbox.configure(yscrollcommand=mlscroll.set)
##arrange
mllistbox.grid(column=0, row=0, sticky='NSEW', padx=(5, 0), pady=(0, 5))
mlscroll.grid(column=1, row=0, sticky='NS', padx=(0, 5), pady=(0, 5))

#next is a list of the total base mats required (not craftable, this is for if you plan to craft from scratch)
##frame
tlframe = ttk.LabelFrame(sup, text='Base Material Totals')
tpane.add(tlframe, weight=2)
tlframe.grid_columnconfigure(0, weight=1)
tlframe.grid_rowconfigure(0,weight=1)

##widgets
tltree = ttk.Treeview(tlframe, columns=('count','info'))
tltree.column('#0', width=120, minwidth=120, stretch=0)
tltree.column('count', width=50, minwidth=50, stretch=0)
tltree.heading('#0', text='Ingredient', anchor='w')
tltree.heading('count', text='Count', anchor='w')
tltree.heading('info', text='Info', anchor='w')
tlscroll = ttk.Scrollbar(tlframe, orient=Tkinter.VERTICAL, command=tltree.yview)
tltree.configure(yscrollcommand=tlscroll.set)
##arrange
tltree.grid(column=0, row=0, sticky='NSEW', padx=(5, 0), pady=(5, 5))
tlscroll.grid(column=1, row=0, sticky='NS', padx=(0, 5), pady=(5, 5))


#throw on a sizegrip
ttk.Sizegrip(sup).grid(column=0, row=1, sticky='SE')

#initial search populates results list with all recipes
search()

#LOOP IT!!!
root.mainloop()
