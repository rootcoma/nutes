#!/usr/bin/env python2
import Tkinter as Tk
import tkMessageBox
import tkFont
import ttk
from storage import SQL
from item import Item, Day, Separator
import TkTreectrl as treectrl
import copy
from datetime import date
from calendar import monthrange

'''
TODO:
 - form validation
'''

class App:
    def __init__(self, master):
        self.sql = SQL()
        self.master = master
        self.master.iconbitmap("@nutes.xbm")
        self.master.title("Nutes")
        self.initView()
        self.day = self.getDay()
        self.updateView()

        self.inventoryWindow = None
        self.searchWindow = None
        self.editWindow = None
        self.resetScrollbars()

    def resetScrollbars(self):
        self.listbox._scrolledWidget.xview_moveto(0)
        self.listbox._scrolledWidget.yview_moveto(0)

    def clearComboSelection(self, event):
        event.widget.selection_clear()
        self.newDay()

    def getDay(self):
        day = self.sql.loadDay(self.dayStringVar.get(), self.getNumericMonth(self.monthStringVar.get()), self.yearStringVar.get())
        #day = Day(self.dayStringVar.get(), self.getNumericMonth(self.monthStringVar.get()), self.yearStringVar.get())
        return day

    def newDay(self):
        self.updateDayCombo()
        self.day = self.getDay()
        self.updateView()

    def getMonthsTuple(self):
        return ("January", "Febuary", "March", "April", "May", 
                    "June", "July", "August", "September", "October",
                    "November", "December")

    def getNumericMonth(self, month):
        months = self.getMonthsTuple()
        for i, m in enumerate(months):
            if month==m:
                return i+1

    def saveDay(self):
        self.sql.saveDay(self.day)

    def swapItem(self, a, b):
        self.day.items[a], self.day.items[b] = self.day.items[b], self.day.items[a]
        self.updateView()
        self.saveDay()
        self.listbox.listbox.select_set(b)

    def upCmd(self):
        if self.selected <= 0:
            return
        self.swapItem(self.selected, self.selected-1)

    def downCmd(self):
        if self.selected < 0:
            return
        if self.selected > len(self.day.items)-2:
            return
        self.swapItem(self.selected, self.selected+1)

    def initView(self):
        self.selected = -1

        self.master.geometry("580x400")

        self.topFrame = Tk.Frame(self.master)
        self.topFrame.pack(side=Tk.TOP, fill='x')

        self.searchBar = Tk.Entry(self.topFrame)
        self.searchBar.pack(side=Tk.LEFT, fill='both', expand='yes')

        self.inventoryButton = Tk.Button(self.topFrame, text="Inventory", command=self.viewInventory)
        self.inventoryButton.pack(side=Tk.RIGHT)

        self.searchButton = Tk.Button(self.topFrame, text="Search", command=self.viewSearch)
        self.searchButton.pack(side=Tk.RIGHT)

        self.middleFrame = Tk.Frame(self.master)
        self.middleFrame.pack(fill='x', pady=2, padx=1)

        today = date.today()

        self.monthStringVar = Tk.StringVar()
        self.monthCombo = ttk.Combobox(self.middleFrame, state='readonly', textvariable=self.monthStringVar, width=10)
        self.monthCombo.bind("<<ComboboxSelected>>", self.clearComboSelection)
        months = ("January", "Febuary", "March", "April", "May", 
                    "June", "July", "August", "September", "October",
                    "November", "December")
        self.monthCombo["values"] = months
        self.monthCombo.current(today.month-1)
        self.monthCombo.pack(side=Tk.LEFT)

        self.dayStringVar = Tk.StringVar()
        self.dayCombo = ttk.Combobox(self.middleFrame, state='readonly', textvariable=self.dayStringVar, width=10)
        today = date.today()
        daysInMonth = monthrange(today.year, today.month)

        days = []
        for i in range(daysInMonth[1]):
            days.append(str(i+1))
        self.dayCombo["values"] = days
        self.dayCombo.current(today.day-1)
        self.dayCombo.pack(side=Tk.LEFT)
        self.dayCombo.bind("<<ComboboxSelected>>", self.clearComboSelection)
        self.yearStringVar = Tk.StringVar()
        self.yearCombo = ttk.Combobox(self.middleFrame, state='readonly', textvariable=self.yearStringVar, width=10)

        thisYear = today.year;
        years = [str(thisYear)]
        for i in range(4):
            years.append(str(thisYear-i-1))
        years = tuple(years)

        self.yearCombo["values"] = years
        self.yearCombo.current(0)
        self.yearCombo.pack(side=Tk.LEFT)

        self.yearCombo.bind("<<ComboboxSelected>>", self.clearComboSelection)
        self.bottomFrame = Tk.Frame(self.master)
        self.bottomFrame.pack(fill="both", expand=1)

        self.listbox = treectrl.ScrolledMultiListbox(self.bottomFrame)
        self.listbox.config(height="20", scrollmode='auto')
        self.listbox.listbox.config(columns=('Name', 'Servings', 'Calories', 'Protein', 'Carbs', 'Fat'))
        self.listbox.listbox.config(selectcmd=self.selectCmd, selectmode='single')

        #self.listbox.listbox.column_configure(0, width=260)
        self.listbox.pack(side='top', fill='both', expand=1)

        self.editButton = Tk.Button(self.bottomFrame, text="Edit", command=self.editCmd)
        self.editButton.pack(side='right')
        self.deleteButton = Tk.Button(self.bottomFrame, text="Delete", command=self.deleteCmd)
        self.deleteButton.pack(side='right')

        Tk.Frame(self.bottomFrame).pack(side='right', padx=12)

        self.downImage = Tk.BitmapImage(file="down.xbm")
        self.downButton = Tk.Button(self.bottomFrame, image=self.downImage, text="Down", command=self.downCmd)
        self.downButton.pack(side='right', fill='y')

        self.upImage = Tk.BitmapImage(file="up.xbm")
        self.upButton = Tk.Button(self.bottomFrame, image=self.upImage, text="Up", command=self.upCmd)
        self.upButton.pack(side='right', fill='y')

        self.exportButton = Tk.Button(self.bottomFrame, text="Export CSV", command=self.exportCmd)
        self.exportButton.pack(side='left')

        self.statsFrame = Tk.Frame(self.master)
        self.statsFrame.pack(side='top', pady=2, fill='x')

        self.footerFont = tkFont.Font(size=10)
        self.footerBoldFont = tkFont.Font(size=10, weight='bold')

        self.footerPad = 4

        self.caloriesFrame = Tk.Frame(self.statsFrame)
        self.caloriesFrame.pack(side='left', padx=self.footerPad)
        self.caloriesTopFrame = Tk.Frame(self.caloriesFrame)
        self.caloriesTopFrame.pack(side='top', fill='x')
        self.caloriesBottomFrame = Tk.Frame(self.caloriesFrame)
        self.caloriesBottomFrame.pack(side='bottom', fill='x')

        self.caloriesStringVar = Tk.StringVar()
        Tk.Label(self.caloriesTopFrame, text="Calories", font=self.footerFont).pack(side='left')
        self.caloriesLabel = Tk.Label(self.caloriesBottomFrame, textvariable=self.caloriesStringVar, font=self.footerBoldFont)
        self.caloriesLabel.pack(side='left')

        self.proteinFrame = Tk.Frame(self.statsFrame)
        self.proteinFrame.pack(side='left', padx=self.footerPad)
        self.proteinTopFrame = Tk.Frame(self.proteinFrame)
        self.proteinTopFrame.pack(side='top', fill='x')
        self.proteinBottomFrame = Tk.Frame(self.proteinFrame)
        self.proteinBottomFrame.pack(side='bottom', fill='x')

        self.proteinStringVar = Tk.StringVar()
        Tk.Label(self.proteinTopFrame, text=" Protein", font=self.footerFont).pack(side='left')
        self.proteinLabel = Tk.Label(self.proteinBottomFrame, textvariable=self.proteinStringVar, font=self.footerBoldFont)
        self.proteinLabel.pack(side='left')

        self.carbFrame = Tk.Frame(self.statsFrame)
        self.carbFrame.pack(side='left', padx=self.footerPad)
        self.carbTopFrame = Tk.Frame(self.carbFrame)
        self.carbTopFrame.pack(side='top', fill='x')
        self.carbBottomFrame = Tk.Frame(self.carbFrame)
        self.carbBottomFrame.pack(side='bottom', fill='x')

        self.carbStringVar = Tk.StringVar()
        Tk.Label(self.carbTopFrame, text=" Carb", font=self.footerFont).pack(side='left')
        self.carbLabel = Tk.Label(self.carbBottomFrame, textvariable=self.carbStringVar, font=self.footerBoldFont)
        self.carbLabel.pack(side='left')

        self.fatFrame = Tk.Frame(self.statsFrame)
        self.fatFrame.pack(side='left', padx=self.footerPad)
        self.fatTopFrame = Tk.Frame(self.fatFrame)
        self.fatTopFrame.pack(side='top', fill='x')
        self.fatBottomFrame = Tk.Frame(self.fatFrame)
        self.fatBottomFrame.pack(side='bottom', fill='x')

        self.fatStringVar = Tk.StringVar()
        Tk.Label(self.fatTopFrame, text=" Fat", font=self.footerFont).pack(side='left')
        self.fatLabel = Tk.Label(self.fatBottomFrame, textvariable=self.fatStringVar, font=self.footerBoldFont)
        self.fatLabel.pack(side='left')

    def exportCmd(self):
        filename = "export/%s-%s-%s.csv" % (self.day.month,self.day.day,self.day.year)
        try:
            f = open(filename, 'w')
            f.write(self.day.toCSV())
            f.close()
        except:
            tkMessageBox.showerror("Export CSV", "Could not save file: \n(%s)" % filename, parent=self.master)
        else:
            tkMessageBox.showinfo("Export CSV", "File successfully exported to: \n(%s)" % filename, parent=self.master)

    def updateDayCombo(self):
        daysInMonth = monthrange(int(self.yearStringVar.get()), self.getNumericMonth(self.monthStringVar.get()))

        days = []
        for i in range(daysInMonth[1]):
            days.append(str(i+1))

        self.dayCombo["values"] = days

    def updateView(self):
        self.listbox.listbox.delete(treectrl.ALL)
        totalCalories = float(0)
        totalProtein = float(0)
        totalCarb = float(0)
        totalFat = float(0)
        for item in self.day.items:
            self.listbox.listbox.insert('end', *map(unicode, item.totalAsTuple()))
            totalCalories += item.totalCalories
            totalProtein += item.totalProtein
            totalCarb += item.totalCarb
            totalFat += item.totalFat
        proteinPercent = 0
        carbPercent = 0
        fatPercent = 0
        divisor = (totalProtein + totalFat + totalCarb)
        if divisor != 0:
            proteinPercent = (totalProtein / divisor) * 100
            carbPercent = (totalCarb / divisor) * 100
            fatPercent = (totalFat / divisor) * 100
        self.caloriesStringVar.set(str("%g" % (round(totalCalories,2))))
        self.proteinStringVar.set(str("%gg(%g%%)" % (round(totalProtein,2), round(proteinPercent,2))))
        self.carbStringVar.set(str("%gg(%g%%)" % (round(totalCarb,2), round(carbPercent,2))))
        self.fatStringVar.set(str("%gg(%g%%)" % (round(totalFat,2), round(fatPercent,2))))

    def deleteCmd(self):
        if self.selected < 0:
            return
        confirm = tkMessageBox.askyesno(message='Are you sure you want to delete?', icon='question', title='Confirm delete', parent=self.master)
        if not confirm:
            return
        del self.day.items[self.selected]
        self.updateView()
        self.saveDay()

    def editCmd(self):
        if self.selected < 0:
            return
        if self.editWindow == None:
            self.editWindow = Tk.Toplevel(self.master)
            self.editWindow.protocol('WM_DELETE_WINDOW', lambda: self.removeWindow(self.editWindow))
            ItemEdit(self.editWindow, self, self.day.items[self.selected])
            return

        if self.editWindow.state() == 'normal':
            self.removeWindow(self.editWindow)
            self.editWindow = Tk.Toplevel(self.master)
            self.editWindow.protocol('WM_DELETE_WINDOW', lambda: self.removeWindow(self.editWindow))
            ItemEdit(self.editWindow, self, self.day.items[self.selected])
            return

    def selectCmd(self, selected):
        if not selected:
            self.selected = -1
        else:
            self.selected = selected[0]

    def deleteItem(self, item):
        for i, it in enumerate(self.day.items):
            if it.uniqueId == item.uniqueId:
                del self.day.items[i]
                self.updateView()
                self.saveDay()

    def viewInventory(self):
        if self.inventoryWindow == None:
            self.inventoryWindow = Tk.Toplevel(self.master)
            self.inventoryWindow.protocol('WM_DELETE_WINDOW', lambda: self.removeWindow(self.inventoryWindow))
            ItemInventory(self.inventoryWindow, self)
            return

        if self.inventoryWindow.state() == 'normal':
            self.inventoryWindow.focus_force()
            self.inventoryWindow.lift()
            return

    def removeWindow(self, window):
        if window == self.inventoryWindow:
            self.inventoryWindow.destroy()
            self.inventoryWindow = None
        elif window == self.searchWindow:
            self.searchWindow.destroy()
            self.searchWindow = None
        elif window == self.editWindow:
            self.editWindow.destroy()
            self.editWindow = None

    def viewSearch(self):
        if self.searchWindow == None:
            self.searchWindow = Tk.Toplevel(self.master)
            self.searchWindow.protocol('WM_DELETE_WINDOW', lambda: self.removeWindow(self.searchWindow))
            ItemSearch(self.searchWindow, self, self.searchBar.get())
            return

        if self.searchWindow.state() == 'normal':
            self.searchWindow.focus_force()
            self.searchWindow.lift()
            return

    def updateItems(self):
        self.updateView()
        self.saveDay()

    def addItem(self, item):
        self.day.items.append(item)
        self.updateView()
        self.saveDay()

class ItemEdit:
    def __init__(self, master, parent, item):
        self.master = master
        self.parent = parent
        self.item = item
        self.master.iconbitmap("@nutes.xbm")
        self.master.title("Nutes - Edit Servings")

        self.initView()
        self.updateView()

    def clearComboSelection(self, event):
        event.widget.selection_clear()

    def initView(self):
        self.servingFrame = Tk.Frame(self.master)
        self.servingFrame.pack(fill='both')

        Tk.Label(self.servingFrame, text="Servings").pack(side=Tk.LEFT)

        self.servingStringVar = Tk.StringVar()
        self.servingBar = Tk.Entry(self.servingFrame, textvariable=self.servingStringVar)
        self.servingBar.pack(side=Tk.LEFT)

        self.servingUnitStringVar = Tk.StringVar()
        self.servingUnitCombo = ttk.Combobox(self.servingFrame, state='readonly', textvariable=self.servingUnitStringVar)
        self.servingUnitCombo["values"] = (
                    "Serving(s)"
                )
        self.servingUnitCombo.bind("<<ComboboxSelected>>", self.clearComboSelection)
        self.servingUnitCombo.current(0)
        self.servingUnitCombo.pack(side=Tk.LEFT)

        self.detailsFrame = Tk.Frame(self.master)
        self.detailsFrame.pack(fill='both')

        self.showDetailsIntVar = Tk.IntVar()
        self.showDetailsCheckbox = Tk.Checkbutton(self.detailsFrame, text="Edit basic details", variable=self.showDetailsIntVar, command=self.checkboxCmd)
        self.showDetailsCheckbox.pack(side='top', pady=5)

        self.nameFrame = Tk.Frame(self.detailsFrame)
        self.nameFrame.pack(fill='x')

        self.nameLabel = Tk.Label(self.nameFrame, text="Name", width=10, anchor='w', state="disabled")
        self.nameEntry = Tk.Entry(self.nameFrame)
        self.nameLabel.pack(side='left')
        self.nameEntry.pack(side='left', fill='x', expand=1)

        self.servingFrame = Tk.Frame(self.detailsFrame)
        self.servingFrame.pack(fill='x')
        self.servingLabel = Tk.Label(self.servingFrame, text="Serving Size", width=10, anchor='w', state="disabled")
        self.servingEntry = Tk.Entry(self.servingFrame)
        self.servingLabel.pack(side='left')
        self.servingEntry.pack(side='left')
        self.servingUnitLabel = Tk.Label(self.servingFrame, text="Units", anchor='w', state="disabled")
        self.servingUnitEntry = Tk.Entry(self.servingFrame)
        self.servingUnitLabel.pack(side='left')
        self.servingUnitEntry.pack(side='left', padx=2, fill='x', expand=1)

        self.caloriesFrame = Tk.Frame(self.detailsFrame)
        self.caloriesFrame.pack(fill='x')

        self.caloriesLabel = Tk.Label(self.caloriesFrame, text="Calories", width=10, anchor='w', state="disabled")
        self.caloriesEntry = Tk.Entry(self.caloriesFrame)
        self.caloriesLabel.pack(side='left')
        self.caloriesEntry.pack(side='left', fill='x')

        self.proteinFrame = Tk.Frame(self.detailsFrame)
        self.proteinFrame.pack(fill='x')

        self.proteinLabel = Tk.Label(self.proteinFrame, text="Protein", width=10, anchor='w', state="disabled")
        self.proteinEntry = Tk.Entry(self.proteinFrame)
        self.proteinLabel.pack(side='left')
        self.proteinEntry.pack(side='left', fill='x')
        Tk.Label(self.proteinFrame, text="g").pack(side='left')

        self.carbFrame = Tk.Frame(self.detailsFrame)
        self.carbFrame.pack(fill='x')

        self.carbLabel = Tk.Label(self.carbFrame, text="Carb", width=10, anchor='w', state="disabled")
        self.carbEntry = Tk.Entry(self.carbFrame)
        self.carbLabel.pack(side='left')
        self.carbEntry.pack(side='left', fill='x')
        Tk.Label(self.carbFrame, text="g").pack(side='left')

        self.fatFrame = Tk.Frame(self.detailsFrame)
        self.fatFrame.pack(fill='x')

        self.fatLabel = Tk.Label(self.fatFrame, text="Fat", width=10, anchor='w', state="disabled")
        self.fatEntry = Tk.Entry(self.fatFrame)
        self.fatLabel.pack(side='left')
        self.fatEntry.pack(side='left', fill='x')
        Tk.Label(self.fatFrame, text="g").pack(side='left')

        self.saveButton = Tk.Button(self.master, text="Save", command=self.saveCmd)
        self.saveButton.pack(fill='x', side='bottom')

        servingSizes = ";".join([str(x[0]) for x in self.item.servingSizes])
        servingUnits = ";".join([str(x[1]) for x in self.item.servingSizes])
        self.nameEntry.insert(0, self.item.name)
        self.servingEntry.insert(0, servingSizes)
        self.servingUnitEntry.insert(0, servingUnits)
        self.caloriesEntry.insert(0, self.item.calories)
        self.proteinEntry.insert(0, self.item.protein)
        self.carbEntry.insert(0, self.item.carb)
        self.fatEntry.insert(0, self.item.fat)

        self.nameEntry.configure(state='readonly')
        self.servingEntry.configure(state='readonly')
        self.servingUnitEntry.configure(state='readonly')
        self.caloriesEntry.configure(state='readonly')
        self.proteinEntry.configure(state='readonly')
        self.carbEntry.configure(state='readonly')
        self.fatEntry.configure(state='readonly')

    def checkboxCmd(self):
        if self.showDetailsIntVar.get()==1:
            #show the details
            self.nameEntry.configure(state='normal')
            self.servingEntry.configure(state='normal')
            self.servingUnitEntry.configure(state='normal')
            self.caloriesEntry.configure(state='normal')
            self.proteinEntry.configure(state='normal')
            self.carbEntry.configure(state='normal')
            self.fatEntry.configure(state='normal')

            self.nameLabel.configure(state='normal')
            self.servingLabel.configure(state='normal')
            self.servingUnitLabel.configure(state='normal')
            self.caloriesLabel.configure(state='normal')
            self.proteinLabel.configure(state='normal')
            self.carbLabel.configure(state='normal')
            self.fatLabel.configure(state='normal')
        else:
            #hide details
            self.nameEntry.configure(state='readonly')
            self.servingEntry.configure(state='readonly')
            self.servingUnitEntry.configure(state='readonly')
            self.caloriesEntry.configure(state='readonly')
            self.proteinEntry.configure(state='readonly')
            self.carbEntry.configure(state='readonly')
            self.fatEntry.configure(state='readonly')

            self.nameLabel.configure(state='disabled')
            self.servingLabel.configure(state='disabled')
            self.servingUnitLabel.configure(state='disabled')
            self.caloriesLabel.configure(state='disabled')
            self.proteinLabel.configure(state='disabled')
            self.carbLabel.configure(state='disabled')
            self.fatLabel.configure(state='disabled')

    def saveCmd(self):
        self.item.name = self.nameEntry.get()
        self.item.calories = self.caloriesEntry.get()
        self.item.protein = self.proteinEntry.get()
        self.item.carb = self.carbEntry.get()
        self.item.fat = self.fatEntry.get()
        self.item.servingSizes = self.item.formatServingSizes(self.servingEntry.get(), self.servingUnitEntry.get())
        self.item.setServings(self.servingStringVar.get(), str(self.servingUnitStringVar.get()))
        self.parent.updateItems()
        self.parent.removeWindow(self.master)

    def updateView(self):
        self.updateServingsInput()

    def updateServingsInput(self):
        self.servingUnitCombo.delete(0, Tk.END)
        servingList = []
        i = 0
        current = 0
        for item in self.item.servingSizes:
            servingList.append(item[1])
            if(item[1]==self.item.getCurrentServingUnit()):
                current = i
            i += 1
        if self.item.getCurrentServingUnit() == False:
            current = i
        servingList.append("Serving(s)")
        self.servingUnitCombo["values"] = tuple(servingList)

        self.servingUnitCombo.current(current)

        self.servingStringVar.set(self.item.getDefaultServings()[0])

class ItemSearch:
    def __init__(self, master, parent, searchTerm=None):
        self.master = master
        self.parent = parent
        self.master.iconbitmap("@nutes.xbm")
        self.master.title("Nutes - Search")
        self.searchTerm = searchTerm
        self.master.geometry("500x280")

        self.resultsPerPage = 100000000
        self.page = 1

        self.sql = SQL()
        self.initView()
        self.updateView()
        self.resetScrollbars()

    def resetScrollbars(self):
        self.listbox._scrolledWidget.xview_moveto(0)
        self.listbox._scrolledWidget.yview_moveto(0)

    def onSearchBarChange(self, *args):
        self.updateView()

    def initView(self):
        self.topFrame = Tk.Frame(self.master)
        self.topFrame.pack(side=Tk.TOP, fill='x')

        self.searchStringVar = Tk.StringVar()
        self.searchBar = Tk.Entry(self.topFrame, textvariable=self.searchStringVar)
        self.searchStringVar.set(self.searchTerm)
        self.searchBar.pack(side=Tk.LEFT, fill='both', expand='yes')

        self.searchStringVar.trace("w", self.onSearchBarChange)

        self.searchButton = Tk.Button(self.topFrame, text="Search", command=self.updateView)
        self.searchButton.pack(side=Tk.RIGHT)

        self.selected = -1

        self.middleFrame = Tk.Frame(self.master)
        self.middleFrame.pack(fill='both', expand=1)

        self.listbox = treectrl.ScrolledMultiListbox(self.middleFrame)
        self.listbox.config(height="20", scrollmode='auto')
        self.listbox.listbox.config(columns=('Name', 'Serving Size', 'Calories', 'Protein', 'Carbs', 'Fat'))
        self.listbox.listbox.column_configure(0, width=160)
        self.listbox.listbox.config(selectcmd=self.selectCmd, selectmode='single')
        self.listbox.pack(side='top', fill='both', expand=1)

        self.servingFrame = Tk.Frame(self.master)
        self.servingFrame.pack(fill='both')

        Tk.Label(self.servingFrame, text="Servings").pack(side=Tk.LEFT)

        self.servingStringVar = Tk.StringVar()
        self.servingBar = Tk.Entry(self.servingFrame, textvariable=self.servingStringVar)
        self.servingBar.pack(side=Tk.LEFT)

        self.servingUnitStringVar = Tk.StringVar()
        self.servingUnitCombo = ttk.Combobox(self.servingFrame, state='readonly', textvariable=self.servingUnitStringVar)
        self.servingUnitCombo["values"] = (
                    "Serving(s)"
                )
        self.servingUnitCombo.current(0)
        self.servingUnitCombo.bind("<<ComboboxSelected>>", self.clearComboSelection)
        self.servingUnitCombo.pack(side=Tk.LEFT)

        self.bottomFrame = Tk.Frame(self.master)
        self.bottomFrame.pack(side=Tk.BOTTOM, fill='x', pady='5', padx='5')


        self.addButton = Tk.Button(self.bottomFrame, text="Add", command=self.addToParent)
        self.addButton.pack(fill='x', expand=1)

    def clearComboSelection(self, event):
        event.widget.selection_clear()

    def updateView(self):
        self.items = self.sql.getItemsLikeName(self.searchStringVar.get(), self.resultsPerPage, self.page)

        self.listbox.listbox.delete(treectrl.ALL)

        for item in self.items:
            self.listbox.listbox.insert('end', *map(unicode, item.asStrTuple()))

        self.updateServingsInput()

    def updateServingsInput(self):
        self.servingUnitCombo.delete(0, Tk.END)
        servingList = []
        i = 0
        current = 0
        for item in self.items[self.selected].servingSizes:
            servingList.append(item[1])
            if(item[1]==self.items[self.selected].getCurrentServingUnit()):
                current = i
            i += 1
        if self.items[self.selected].getCurrentServingUnit() == False:
            current = i
        servingList.append("Serving(s)")
        self.servingUnitCombo["values"] = tuple(servingList)
        self.servingUnitCombo.current(current)
        if self.selected == -1:
            self.servingStringVar.set(1)
        elif len(self.items[self.selected].servingSizes) < 1:
            self.servingStringVar.set(1)
        else:
            self.servingStringVar.set(self.items[self.selected].getDefaultServings()[0])

    def selectCmd(self, selected):
        if not selected:
            self.selected = -1
        else:
            self.selected = selected[0]
        self.updateServingsInput()

    def addToParent(self):
        if self.selected < 0:
            return
        itemCopy = copy.copy(self.items[self.selected])
        itemCopy.setServings(self.servingStringVar.get(), self.servingUnitStringVar.get())
        self.parent.addItem(itemCopy)
        self.parent.removeWindow(self.master)

class ItemInventory:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent
        self.master.iconbitmap("@nutes.xbm")
        self.master.title("Nutes - Inventory")

        self.master.geometry("500x300")
        self.editWindow = None

        self.resultsPerPage = 100000000
        self.page = 1

        self.searchTerm = ""


        self.sql = SQL()
        self.initView()
        self.updateView()
        self.resetScrollbars()

    def onSearchBarChange(self, *args):
        self.updateView()

    def removeWindow(self, window):
        if window == self.editWindow:
            self.editWindow.destroy()
            self.editWindow = None

    def resetScrollbars(self):
        self.listbox._scrolledWidget.xview_moveto(0)
        self.listbox._scrolledWidget.yview_moveto(0)

    def initView(self):
        self.topFrame = Tk.Frame(self.master)
        self.topFrame.pack(side=Tk.TOP, fill='x')

        self.searchStringVar = Tk.StringVar()
        self.searchBar = Tk.Entry(self.topFrame, textvariable=self.searchStringVar)
        self.searchStringVar.set(self.searchTerm)
        self.searchBar.pack(side=Tk.LEFT, fill='both', expand='yes')

        self.searchButton = Tk.Button(self.topFrame, text="Filter", command=self.updateView)
        self.searchButton.pack(side=Tk.RIGHT)

        self.selected = -1


        self.listbox = treectrl.ScrolledMultiListbox(self.master)
        self.listbox.pack(side='top', fill='both', expand=1)
        self.listbox.config(height="20", scrollmode='auto')
        self.listbox.listbox.config(columns=('Name', 'Serving Size', 'Calories', 'Protein', 'Carbs', 'Fat'))
        self.listbox.listbox.column_configure(0, width=160)
        self.listbox.listbox.config(selectcmd=self.selectCmd, selectmode='single')


        self.pageFrame = Tk.Frame(self.master)
        self.pageFrame.pack(side="top", fill="x")

        self.addButton = Tk.Button(self.master, text="Add", command=self.addToParent)
        self.addButton.pack(side='left')

        self.deleteButton = Tk.Button(self.master, text="Delete",command=self.deleteItem)
        self.deleteButton.pack(side='right')
        self.newButton = Tk.Button(self.master, text="New",command=self.viewForm)
        self.newButton.pack(side='right')
        self.editButton = Tk.Button(self.master, text="Edit", command=self.editCmd)
        self.editButton.pack(side='right')

        self.searchStringVar.trace("w", self.onSearchBarChange)

    def updateView(self):
        self.searchTerm = self.searchStringVar.get()
        if self.searchTerm == "":
            self.items = self.sql.getItems(self.resultsPerPage, self.page)
        else:
            self.items = self.sql.getItemsLikeName(self.searchTerm, self.resultsPerPage, self.page)
        self.listbox.listbox.delete(treectrl.ALL)

        for item in self.items:
            self.listbox.listbox.insert('end', *map(unicode, item.asStrTuple()))

    def editCmd(self):
        if self.selected == -1:
            return
        if self.editWindow == None:
            self.editWindow = Tk.Toplevel(self.master)
            self.editWindow.protocol('WM_DELETE_WINDOW', lambda: self.removeWindow(self.editWindow))
            ItemForm(self.editWindow, self, self.items[self.selected])
            return

        if self.editWindow.state() == 'normal':
            self.removeWindow(self.editWindow)
            self.editWindow = Tk.Toplevel(self.master)
            self.editWindow.protocol('WM_DELETE_WINDOW', lambda: self.removeWindow(self.editWindow))
            ItemForm(self.editWindow, self, self.items[self.selected])
            return

    def selectCmd(self, selected):
        if not selected:
            self.selected = -1
        else:
            self.selected = selected[0]

    def deleteItem(self):
        if self.selected < 0:
            return
        confirm = tkMessageBox.askyesno(message='Are you sure you want to delete?\n\nThis item will be permanently erased from the inventory.', icon='warning', title='Confirm Delete', parent=self.master)
        if not confirm:
            self.master.lift()
            return
        name=self.items[self.selected].name
        self.sql.deleteItemByName(name)
        self.updateView()
        self.parent.newDay()
        self.master.lift()

    def deleteItemByName(self, name):
        self.sql.deleteItemByName(name)
        self.updateView()

    def updateItem(self, row, name, servingSize, servingUnit, calories, protein, carb, fat):
        if(self.sql.checkItemExists(name, row)):
            tkMessageBox.showerror("Save Error", "Error: Cannot update item.\n\nDuplicate item exists with name:\n(%s)" % name, parent=self.editWindow)
            self.master.lift()
            self.editWindow.lift()
            return
        item = Item(row, name, servingSize, servingUnit, calories, protein, carb, fat)
        self.removeWindow(self.editWindow)
        self.master.lift()
        self.sql.updateItem(item)
        self.parent.newDay()
        self.updateView()

    def viewForm(self):
        if self.editWindow == None:
            self.editWindow = Tk.Toplevel(self.master)
            self.editWindow.protocol('WM_DELETE_WINDOW', lambda: self.removeWindow(self.editWindow))
            ItemForm(self.editWindow, self)
            return

        if self.editWindow.state() == 'normal':
            self.removeWindow(self.editWindow)
            self.editWindow = Tk.Toplevel(self.master)
            self.editWindow.protocol('WM_DELETE_WINDOW', lambda: self.removeWindow(self.editWindow))
            ItemForm(self.editWindow, self)
            return

    def createItem(self, name, servingSize, servingUnit, calories, protein, carb, fat):
        if(self.sql.checkItemExists(name, -1)):
            tkMessageBox.showerror("Save Error", "Error: Create update item.\n\nDuplicate item exists with name:\n(%s)" % name, parent=self.editWindow)
            self.master.lift()
            self.editWindow.lift()
            return
        item = Item(None, name, servingSize, servingUnit, calories, protein, carb, fat)
        self.removeWindow(self.editWindow)
        self.master.lift()
        self.sql.addItem(item)
        self.parent.newDay()
        self.updateView()

    def addToParent(self):
        if self.selected <= -1:
            return
        itemCopy = copy.copy(self.items[self.selected])
        self.parent.addItem(itemCopy)
        self.parent.removeWindow(self.master)

class ItemForm:
    def __init__(self, master, parent, item=None):
        self.master = master
        self.parent = parent
        self.master.geometry("460x170")
        self.master.iconbitmap("@nutes.xbm")
        self.master.title("Nutes - Item Form")

        self.item = item

        Tk.Label(master, text="Create a new nutrition label").grid(row=0, columnspan=4)

        Tk.Label(master, text="Name").grid(row=1)
        Tk.Label(master, text="Serving size").grid(row=2)
        Tk.Label(master, text="Units").grid(row=2, column=2)

        self.eName = Tk.Entry(master, width=45)
        '''
        if item!=None:
            self.eName.insert(0, self.item.name)
            self.eName.configure(state='readonly')
        '''
        self.eServingSize = Tk.Entry(master)
        self.eServingSizeUnits = Tk.Entry(master)

        self.eName.grid(row=1, column=1, columnspan=3)
        self.eServingSize.grid(row=2, column=1)
        self.eServingSizeUnits.grid(row=2, column=3)

        Tk.Label(master, text="Calories").grid(row=3)
        self.eCalories= Tk.Entry(master)
        self.eCalories.grid(row=3, column=1)

        Tk.Label(master, text="Protein").grid(row=4)
        self.eProtein= Tk.Entry(master)
        self.eProtein.grid(row=4, column=1)
        Tk.Label(master, text="g").grid(row=4, column=2)

        Tk.Label(master, text="Carb").grid(row=5)
        self.eCarb= Tk.Entry(master)
        self.eCarb.grid(row=5, column=1)
        Tk.Label(master, text="g").grid(row=5, column=2)

        Tk.Label(master, text="Fat").grid(row=6)
        self.eFat= Tk.Entry(master)
        self.eFat.grid(row=6, column=1)
        Tk.Label(master, text="g").grid(row=6, column=2)

        self.button = Tk.Button(master, text="Save", command=self.addToParent)
        self.button.grid(row=8, columnspan=4)

        if self.item != None:

            servingSizes = ";".join([str(x[0]) for x in item.servingSizes])
            servingUnits = ";".join([str(x[1]) for x in item.servingSizes])
            self.eServingSize.insert(0, servingSizes)
            self.eServingSizeUnits.insert(0, servingUnits)
            self.eName.insert(0, self.item.name)
            self.eCalories.insert(0, self.item.calories)
            self.eProtein.insert(0, self.item.protein)
            self.eCarb.insert(0, self.item.carb)
            self.eFat.insert(0, self.item.fat)

    def makeLabel(self, frame, text, left=False):
        label = Tk.Label(frame, text=text)
        if left:
            label.pack(side=Tk.LEFT)
        else:
            label.pack()

    def addToParent(self):
        if self.item != None:
            self.parent.updateItem(self.item.row, self.eName.get(), self.eServingSize.get(), self.eServingSizeUnits.get(), self.eCalories.get(), self.eProtein.get(), self.eCarb.get(), self.eFat.get())
        else:
            self.parent.createItem(self.eName.get(), self.eServingSize.get(), self.eServingSizeUnits.get(), self.eCalories.get(), self.eProtein.get(), self.eCarb.get(), self.eFat.get())

root = Tk.Tk()

root.title("Nutes")
root.iconbitmap("@nutes.xbm")

s = ttk.Style()

app = App(root)

root.mainloop()
try:
    root.destroy()
except Tk.TclError:
    pass
