import cPickle as pickle
import Tkinter, ttk, re


#load recipe list
f = open('sub/Recipes.pkl','r')
Recipes = pickle.load(f)
f.close()

#load ingredient list
f = open('sub/Ingredients.pkl','r')
Ingredients = pickle.load(f)
f.close()

#useful lists for later
classlist = ['Any','Alchemist','Armorer','Blacksmith','Carpenter','Culinarian','Goldsmith','Leatherworker','Weaver']
levellist = ['Any','1-5','6-10','11-15','16-20','21-25','26-30','31-35','36-40','41-45','46-50','50+']
leveldict = {'Any':range(1,100),'1-5':range(1,6),'6-10':range(6,11),'11-15':range(11,16),'16-20':range(16,21),'21-25':range(21,26),'26-30':range(26,31),'31-35':range(31,36),'36-40':range(36,41),'41-45':range(41,46),'46-50':range(46,51),'51+':range(51,100)}





#these functions used to search for recipes and display results

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






#these functions add/remove items to/from the make list, ingredients list, and totals list

#add selected recipe to makelist
def add(*args):
    for idx in rlistbox.curselection():
        idx = int(idx)
        item = re.sub(' \(.* Level [0-9]*\)$', '', eval(resultlist.get())[idx])
        if item in mllistd:
            mllistd[item] += 1
        else:
            mllistd[item] = 1
        recipe = find(item)
        for ingredient in recipe['Ingredients']:
            name, count = ingredient[0], ingredient[1]
            if name in iltree.get_children():
                iltree.set(name, 'count', int(iltree.set(name, 'count')) + count)
                iltree.set(name, 'mark', '[  ]')
            else:
                iltree.insert('', 'end', name, text=name, values=(count, '[  ]', ))
                if name in Ingredients:
                    iltree.set(name, 'info', Ingredients[name])
            if name in [this['Name'] for this in Recipes]:
                birthadd(name, count)
            else:
                if name in tltree.get_children():
                    tltree.set(name, 'count', int(tltree.set(name, 'count')) + count)
                    tltree.set(name, 'mark', '[  ]')
                else:
                    tltree.insert('', 'end', name, text=name, values=(count, '[  ]', ))
                    if name in Ingredients:
                        tltree.set(name, 'info', Ingredients[name])
    for child in sorted(iltree.get_children()):
        name = iltree.item(child)['text'].lower()
        if 'shard' in name or 'crystal' in name or 'cluster' in name:
            iltree.move(child, '', 0)
        else:
            iltree.move(child, '', 'end')
    for child in sorted(tltree.get_children()):
        name = tltree.item(child)['text'].lower()
        if 'shard' in name or 'crystal' in name or 'cluster' in name:
            tltree.move(child, '', 0)
        else:
            tltree.move(child, '', 'end')
    mllist.set(tuple(sorted(['{}x {}'.format(mllistd[item], item) for item in mllistd if mllistd[item] > 0], key=lambda k: re.sub('[0-9]*x ', '', k))))
    check()
    sentry.focus_set()
    sentry.select_range(0, Tkinter.END)

#add child ingredients
def birthadd(parent, parent_count):
    recipe = find(iltree.item(parent)['text'])
    for ingredient in recipe['Ingredients']:
        name, count = ingredient[0], ingredient[1]
        _id = '{}/{}'.format(parent, ingredient[0])
        if _id in iltree.get_children(parent):
            iltree.set(_id, 'count', int(iltree.set(_id, 'count')) + (count * parent_count))
            iltree.set(_id, 'mark', '[  ]')
        else:
            iltree.insert(parent, 'end', _id, text=name, values=(count * parent_count, '[  ]', ))
            if name in Ingredients:
                iltree.set(_id, 'info', Ingredients[name])
        if name in [this['Name'] for this in Recipes]:
            birthadd(_id, count * parent_count)
        else:
            if name in tltree.get_children():
                tltree.set(name, 'count', int(tltree.set(name, 'count')) + (count * parent_count))
                tltree.set(name, 'mark', '[  ]')
            else:
                tltree.insert('', 'end', name, text=name, values=(count * parent_count, '[  ]', ))
                if name in Ingredients:
                    tltree.set(name, 'info', Ingredients[name])


#add selected recipe to makelist
def minus(*args):
    for idx in mllistbox.curselection():
        idx = int(idx)
        item = re.sub('^[0-9]*x ', '', eval(mllist.get())[idx])
        if item in mllistd:
            mllistd[item] -= 1
            if mllistd[item] <= 0:
                del(mllistd[item])
        recipe = find(item)
        for ingredient in recipe['Ingredients']:
            name, count = ingredient[0], ingredient[1]
            if name in iltree.get_children():
                iltree.set(name, 'count', int(iltree.set(name, 'count')) - count)
                if iltree.set(name, 'count') <= 0:
                    iltree.delete(name)
                    if name in [this['Name'] for this in Recipes]:
                        birthminus(name, count, True)
                elif name in [this['Name'] for this in Recipes]:
                    birthminus(name, count)
            if name not in [this['Name'] for this in Recipes] and name in tltree.get_children():
                tltree.set(name, 'count', int(tltree.set(name, 'count')) - count)
                if tltree.set(name, 'count') <= 0:
                    tltree.delete(name)
    mllist.set(tuple(sorted(['{}x {}'.format(mllistd[item], item) for item in mllistd if mllistd[item] > 0], key=lambda k: re.sub('[0-9]*x ', '', k))))

#add child ingredients
def birthminus(parent, parent_count, tot=False):
    intot = tot
    if not tot: recipe = find(iltree.item(parent)['text'])
    else: recipe = find(parent)
    for ingredient in recipe['Ingredients']:
        name, count = ingredient[0], ingredient[1]
        _id = '{}/{}'.format(parent, ingredient[0])
        if not tot and _id in iltree.get_children(parent):
            iltree.set(_id, 'count', int(iltree.set(_id, 'count')) - (count * parent_count))
            if iltree.set(_id, 'count') <= 0:
                intot = True
                iltree.delete(_id)
        if name not in [this['Name'] for this in Recipes] and name in tltree.get_children():
                tltree.set(name, 'count', int(tltree.set(name, 'count')) - (count * parent_count))
                if tltree.set(name, 'count') <= 0:
                    tltree.delete(name)
        if name in [this['Name'] for this in Recipes]:
            if intot: birthminus(name, count * parent_count, intot)
            else: birthminus(_id, count * parent_count, intot)







#the following functions handle marking/unmarking items in the ingredients lists

##mark/unmark selected item(s) in ingredients list
def ilmark(*args):
    for item in iltree.selection():
        mark = iltree.set(item, 'mark')
        name = iltree.item(item)['text']
        if mark == '[  ]':
            iltree.set(item, 'mark', '[x]')
            birthmark(item)
        if mark == '[x]':
            iltree.set(item, 'mark', '[  ]')
            birthmark(item, True)
            parentmark(item, True)
    check()

##check for marked items in ingredient list and automatically assign
##appropriate mark to crorresponding itemin totals list
def check():
    for name in tltree.get_children():
        completion = []
        children = iltree.get_children()
        for child in children:
            if child == name:
                if iltree.set(child, 'mark') == '[x]':
                    completion.append(1)
                else:
                    completion.append(0)
            tlincmark(child, name, completion)
        if 1 in completion and 0 in completion:
            tltree.set(name, 'mark', '[-]')
        elif 0 in completion:
            tltree.set(name, 'mark', '[  ]')
        elif 1 in completion:
            tltree.set(name, 'mark', '[x]')

###used by previous function to iterate (downward) through trees
def tlincmark(parent, name, completion):
    children = iltree.get_children(parent)
    for child in children:
        if child.endswith(name):
            if iltree.set(child, 'mark') == '[x]':
                completion.append(1)
            else:
                completion.append(0)
        tlincmark(child, name, completion)

##this function checks the parent of an item that is marked in the ingredient
##list. if all children are thusly marked, the parent is automatically marked
##if any child ingredient is found unmarked, the parent in unmarked
##(iterates upward)
def parentmark(child, unmark=False):
    parent = iltree.parent(child)
    if parent != '':
        if unmark:
            iltree.set(parent, 'mark', '[  ]')
            parentmark(parent, True)
        else:
            children = iltree.get_children(parent)
            markit = True
            for child in children:
                if iltree.set(child, 'mark') == '[  ]':
                    markit = False
            if markit:
                iltree.set(parent, 'mark', '[x]')
                parentmark(parent)
        
##this function will automatically mark/unmark any children of an item that is marked in
##the ingredient list
##(iterates downward)
def birthmark(parent, unmark=False):
    children = iltree.get_children(parent)
    if len(children) > 0:
        for child in children:
            name = iltree.item(child)['text']
            if not unmark:
                iltree.set(child, 'mark', '[x]')
                birthmark(child)
            else:
                iltree.set(child, 'mark', '[  ]')
                birthmark(child, True)

##next function marks/unmarks selected item(s) in totals list
##then it marks/unmarks any corresponding item in the ingredient list
def tlmark(*args):
    for item in tltree.selection():
        mark = tltree.set(item, 'mark')
        if mark != '[x]':
            tltree.set(item, 'mark', '[x]')
            children = iltree.get_children()
            for child in children:
                if child == item:
                    iltree.set(child, 'mark', '[x]')
                tlilbirthmark(child, item)
        if mark == '[x]':
            tltree.set(item, 'mark', '[  ]')
            children = iltree.get_children()
            for child in children:
                if child == item:
                    iltree.set(child, 'mark', '[  ]')
                    parentmark(child, True)
                tlilbirthmark(child, item, True)

###used by previous function to iterate (downward) through trees
def tlilbirthmark(parent, name, unmark=False):
    children = iltree.get_children(parent)
    if len(children) > 0:
        for child in iltree.get_children(parent):
            if child.endswith(name):
                if not unmark:
                    iltree.set(child, 'mark', '[x]')
                else:
                    iltree.set(child, 'mark', '[  ]')
                    parentmark(child, True)
            tlilbirthmark(child, name, unmark)










#construct the UI
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
nsearch.trace('w', search)
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
rlistbox.bind('<Return>', add)
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
ilframe.grid_rowconfigure(1, weight=1)

##variable
illistd = {}
##widgets
illabel = ttk.Label(ilframe, text='(double click to mark/unmark an item)')
iltree = ttk.Treeview(ilframe, columns=('count','mark','info'), height=8)
iltree.bind('<Double-1>', ilmark)
iltree.bind('<space>', ilmark)
iltree.bind('<Return>', ilmark)
iltree.column('#0', width=150, minwidth=150, stretch=0)
iltree.column('count', width=50, minwidth=50, stretch=0)
iltree.column('mark', width=30, minwidth=30, stretch=0)
iltree.heading('#0', text='Ingredient', anchor='w')
iltree.heading('count', text='Count', anchor='w')
iltree.heading('mark', text='[x]', anchor='w')
iltree.heading('info', text='Info', anchor='w')
ilscroll = ttk.Scrollbar(ilframe, orient=Tkinter.VERTICAL, command=iltree.yview)
iltree.configure(yscrollcommand=ilscroll.set)
##arrange
illabel.grid(column=0,row=0, sticky='W', padx=5)
iltree.grid(column=0, row=1, sticky='NSEW', padx=(5, 0), pady=(5, 5))
ilscroll.grid(column=1, row=1, sticky='NS', padx=(0, 5), pady=(5, 5))

#makelist frame
mlframe = ttk.LabelFrame(sup, text='Make List')
mpane.add(mlframe, weight=1)
mlframe.grid_columnconfigure(0, weight=1)
mlframe.grid_rowconfigure(0,weight=1)

##variable
mllist = Tkinter.StringVar(value=())
mllistd = {}
##widgets
mllistbox = Tkinter.Listbox(mlframe, listvariable=mllist, selectmode='extended', height=10)
mllistbox.bind('<Double-1>', minus)
mllistbox.bind('<BackSpace>', minus)
mllistbox.bind('<Delete>', minus)
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
tlframe.grid_rowconfigure(1, weight=1)

##widgets
tllabel = ttk.Label(tlframe, text='(double click to mark/unmark an item)')
tltree = ttk.Treeview(tlframe, columns=('count','mark','info'))
tltree.bind('<Double-1>', tlmark)
tltree.bind('<space>', tlmark)
tltree.bind('<Return>', tlmark)
tltree.column('#0', width=120, minwidth=120, stretch=0)
tltree.column('count', width=50, minwidth=50, stretch=0)
tltree.column('mark', width=30, minwidth=30, stretch=0)
tltree.heading('#0', text='Ingredient', anchor='w')
tltree.heading('count', text='Count', anchor='w')
tltree.heading('mark', text='[x]', anchor='w')
tltree.heading('info', text='Info', anchor='w')
tlscroll = ttk.Scrollbar(tlframe, orient=Tkinter.VERTICAL, command=tltree.yview)
tltree.configure(yscrollcommand=tlscroll.set)
##arrange
tllabel.grid(column=0,row=0, sticky='W', padx=5)
tltree.grid(column=0, row=1, sticky='NSEW', padx=(5, 0), pady=(5, 5))
tlscroll.grid(column=1, row=1, sticky='NS', padx=(0, 5), pady=(5, 5))


#throw on a sizegrip
ttk.Sizegrip(sup).grid(column=0, row=1, sticky='SE')



#initialize the program

#initial search populates results list with all recipes
search()

#set initial focus on search entry
sentry.focus_set()
sentry.select_range(0, Tkinter.END)

#LOOP IT!!!
root.mainloop()
