import sqlite3
from item import Item, Day
import copy

class SQL:
    def __init__(self):
        self.createTables()

    def getConnection(self):
        conn = sqlite3.connect('db/nutes.db')
        return conn

    def execute(self, statement, arguments=None, fetch=None):
        conn = self.getConnection()
        c = conn.cursor()
        try:
            if arguments is None:
                c.execute(statement)
            else:
                c.execute(statement, arguments)
        except sqlite3.OperationalError, e:
            print e
            return False
        else:
            value = None
            if fetch == "one":
                value = c.fetchone()
            elif fetch == "all":
                value = c.fetchall()
            elif fetch == "last":
                value = c.lastrowid
            conn.commit()
            conn.close()
            return value

    def checkTableCreated(self, name):
        statement = '''SELECT COUNT(name) FROM sqlite_master WHERE type="table" AND name=?'''
        arguments = (name,)
        if self.execute(statement, arguments, "one")[0] > 0:
            return True
        return False

    def formatDaysLabelsResults(self, results):
        items = []
        for res in results:
            newItem = Item(None, res[3], res[5], res[6], res[7], res[8], res[9], res[10])
            newItem.uniqueId = res[1]
            newItem.setServingsFromStr(res[4])
            items.append(newItem)
            #row, name, servingSizes, servingUnits, calories, protein, carb, fat
        return items

    def formatLabelsResults(self, results):
        items = []
        for res in results:
            items.append(Item(res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7]))
            #row, name, servingSizes, servingUnits, calories, protein, carb, fat
        return items

    def getItemsLikeName(self, name, limit, page):
        start = (page-1)*limit
        statement = '''select * FROM labels WHERE name LIKE ? ORDER BY name ASC LIMIT ?,?'''
        arguments = ("%"+name+"%", start, limit)
        results = self.execute(statement, arguments, "all")
        return self.formatLabelsResults(results)

    def getItems(self, limit, page):
        start = (page-1)*limit
        statement = '''select * FROM labels ORDER BY name ASC LIMIT ?,?'''
        arguments = (start, limit)
        results = self.execute(statement, arguments, "all")
        return self.formatLabelsResults(results)

    def createTables(self):
        if not self.checkTableCreated("labels"):
            statement = '''CREATE TABLE labels 
                (
                    id INTEGER  NOT NULL,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    servingSize VARCHAR(255) NOT NULL,
                    servingUnit VARCHAR(255) NOT NULL,
                    calories VARCHAR(255) NOT NULL,
                    protein VARCHAR(255) NOT NULL,
                    carb VARCHAR(255) NOT NULL,
                    fat VARCHAR(255) NOT NULL,
                    PRIMARY KEY (id ASC)
                )'''
            self.execute(statement)
        
        if not self.checkTableCreated("daysLabels"):
            statement = '''CREATE TABLE daysLabels 
                (
                    id INTEGER NOT NULL,
                    uniqueId VARCHAR(255) NOT NULL UNIQUE,
                    daysId INTEGER NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    servings VARCHAR(255) NOT NULL,
                    servingSize VARCHAR(255) NOT NULL,
                    servingUnit VARCHAR(255) NOT NULL,
                    calories VARCHAR(255) NOT NULL,
                    protein VARCHAR(255) NOT NULL,
                    carb VARCHAR(255) NOT NULL,
                    fat VARCHAR(255) NOT NULL,
                    PRIMARY KEY (id ASC)
                )'''
            self.execute(statement)

        if not self.checkTableCreated("days"):
            statement = '''CREATE TABLE days 
                (
                    id INTEGER NOT NULL,
                    day INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    UNIQUE(day, month, year) ON CONFLICT REPLACE,
                    PRIMARY KEY (id ASC)
                )'''
            self.execute(statement)

    def deleteItemByName(self, name):
        statement = '''DELETE FROM labels WHERE name=?'''
        arguments = (name,)
        self.execute(statement, arguments)

    def checkItemExists(self, name, row):
        statement = '''SELECT count(id) FROM labels WHERE name=? AND id!=?'''
        arguments = (name,row)
        val = self.execute(statement, arguments,'one')
        if not val or val[0] <=0:
            return False
        return True 

    def updateItem(self, item):
        statement = '''UPDATE labels SET name=?, servingSize=?, servingUnit=?, calories=?, protein=?, carb=?, fat=?
            WHERE id=?'''
        servingSizes = ";".join([str(x[0]) for x in item.servingSizes])
        servingUnits = ";".join([str(x[1]) for x in item.servingSizes])
        arguments = (item.name, servingSizes, servingUnits, item.calories, item.protein, item.carb, item.fat, item.row)
        self.execute(statement, arguments)

    def addItem(self, item):
        statement = '''INSERT INTO labels
            (name, servingSize, servingUnit, calories, protein, carb, fat)
            VALUES (
                ?, ?, ?, ?, ?, ?, ?
            )'''

        arguments = (item.name, item.createServingSizesStr(), item.createServingUnitsStr(), item.calories, item.protein, item.carb, item.fat)
        self.execute(statement, arguments)

    def loadDay(self, day, month, year):
        #check if day exists
        statement = '''SELECT id FROM days WHERE day=? AND month=? AND year=?'''
        arguments = (day, month, year)
        val = self.execute(statement, arguments, "one")
        if not val:
            return Day(day, month, year, [])

        #get day id
        dayRow = val[0]

        # get daysLabels
        statement = '''SELECT * FROM daysLabels WHERE daysId =?'''
        arguments = (dayRow,)

        results = self.execute(statement, arguments, "all")

        newItems = self.formatDaysLabelsResults(results)

        day = Day(day, month, year, [])
        day.items = newItems
        #return day
        return day

    def saveDay(self, dayObj):
        #check if day exists
        statement = '''SELECT id FROM days WHERE day=? AND month=? AND year=?'''
        arguments = (dayObj.day, dayObj.month, dayObj.year)
        val = self.execute(statement, arguments, "one")

        #get day id
        if not val:
            statement = '''INSERT INTO days
                (day, month, year)
                VALUES (
                    ?, ?, ?
                )'''
            arguments = (dayObj.day, dayObj.month, dayObj.year)
            row = self.execute(statement, arguments, "last")
        else:
            row = val[0]

        #drop all not in uniqueIds in daysLabels
        conn = self.getConnection()
        c = conn.cursor()

        uniqueIds = [o.uniqueId for o in dayObj.items]
        statement = '''DELETE FROM daysLabels WHERE daysId=? AND uniqueId NOT IN (%s)''' % ','.join('?'*len(dayObj.items))
        arguments = [row]
        arguments.extend(uniqueIds)
        arguments = tuple(arguments)
        c.execute(statement, arguments)

        #insert or replace
        for it in dayObj.items:
            statement = '''INSERT OR REPLACE INTO daysLabels (uniqueId, daysId, name, servings, servingSize, servingUnit, calories, protein, carb, fat) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            arguments = (it.uniqueId, row, it.name, it.createServingsStr(), it.createServingSizesStr(), it.createServingUnitsStr(), it.calories, it.protein, it.carb, it.fat)
            c.execute(statement, arguments)
        conn.commit()
