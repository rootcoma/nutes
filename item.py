from random import SystemRandom
import copy
from fractions import Fraction

class Day:
    def __init__(self, day, month, year, items=[]):
        self.items = copy.copy(items) #weird but, won't overwrite unless copied
        self.day = day
        self.month = month
        self.year = year

    def toCSV(self):
        csvText = "Month,Day,Year\n%s,%s,%s\n" % (self.month, self.day, self.year)
        csvText += "Total Calories,Total Protein,Total Carbs,Total Fat\n"

        totalCalories = 0
        totalProtein = 0
        totalCarb = 0
        totalFat = 0
        for item in self.items:
            totalCalories += item.totalCalories
            totalProtein += item.totalProtein
            totalCarb += item.totalCarb
            totalFat += item.totalFat
        csvText += "%s,%s,%s,%s\n" % (round(totalCalories,4),round(totalProtein,4),round(totalCarb,4),round(totalFat,4))

        csvText += "Name,Servings,Calories,Protein,Carbs,Fat\n"
        for item in self.items:
            tmp = item.totalAsFloatTuple()
            csvText += "%s,%s,%s,%s,%s,%s\n" % (tmp[0],tmp[1],tmp[2],tmp[3],tmp[4],tmp[5])

        return csvText

class Separator:
    def __init__(self, name, position):
        self.name = name
        self.position = position

class Item:
    def __init__(self, row, name, servingSizes="", servingUnits="", calories="0", protein="0", carb="0", fat="0"):
        self.uniqueId = self.createToken(15)
        self.row = row
        self.name = str(name)
        self.servingSizes = self.formatServingSizes(servingSizes, servingUnits)
        self.calories = calories
        self.protein = protein
        self.carb = carb
        self.fat = fat
        if len(self.servingSizes) > 0 and len(self.servingSizes[0]) > 1:
            self.servings = (self.servingSizes[0][0], self.servingSizes[0][1])
        else:
            self.servings = (1,)
        self.totalCalories = float(calories)
        self.totalProtein = float(protein)
        self.totalCarb = float(carb)
        self.totalFat = float(fat)

    def __copy__(self):
        cpy = Item(self.row, self.name, "", "", self.calories, self.protein, self.carb, self.fat)
        cpy.servingSizes = copy.copy(self.servingSizes)
        cpy.servings = copy.copy(self.servings)
        return cpy

    def createToken(self, n):
        random = SystemRandom()
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-=0123456789~'
        return ''.join(random.choice(alphabet) for _ in range(n))

    def getCurrentServingUnit(self):
        if len(self.servings) < 2:
            return False
        else:
            return self.servings[1]

    def getServingsStr(self):
        if len(self.servings) < 1:
            return False
        elif len(self.servings) < 2:
            return str(self.servings[0]) + "Serving(s)"
        else:
            return str(self.servings[0]) + str(self.servings[1])

    def removeEmptyItems(self, l):
        l = filter(None, l)
        return l

    def setServingsFromStr(self, s):
        self.servings = self.formatServings(s)
        self.updateTotals()

    def setServings(self, servingSize, servingUnit):
        servingTuple = self.getServingTuple(servingUnit)
        if not servingTuple:
            self.servings = (servingSize,)
            self.updateTotals()
            return

        self.servings = (servingSize, servingTuple[1])
        self.updateTotals()

    def createServingsStr(self):
        return ";".join(str(s) for s in self.servings)

    def createServingSizesStr(self):
        return ";".join([str(x[0]) for x in self.servingSizes])

    def createServingUnitsStr(self):
        return ";".join([str(x[1]) for x in self.servingSizes])

    def formatServings(self, servings):
        servingsList = servings.split(";")
        servingsList = self.removeEmptyItems(servingsList)
        if len(servingsList) < 1:
            print "Error: Servings not set"
        elif len(servingsList) < 2:
            return (servingsList[0],)

        return (servingsList[0], servingsList[1])

    def formatServingSizes(self, servingSizes, servingUnits):
        servingSizeList = servingSizes.split(";")
        servingUnitsList = servingUnits.split(";")
        servingSizeList = self.removeEmptyItems(servingSizeList)
        servingUnitsList = self.removeEmptyItems(servingUnitsList)

        if len(servingUnitsList) != len(servingSizeList):
            print "Error: Formating serving sized failed"
            return

        newList = []
        for i in range(len(servingUnitsList)):
            newList.append((str(servingSizeList[i]), str(servingUnitsList[i])))
        return newList

    def getDefaultServings(self):
        if len(self.servings)<1:
            print "Error: No serving sizes"
        if len(self.servings) == 1:
            return (self.servings[0], "Serving(s)")
        return (self.servings[0], self.servings[1])

    def getServingTuple(self, servingUnit):
        for item in self.servingSizes:
            if item[1]==servingUnit:
                return (str(item[0]), str(item[1]))
        return False

    def getServingsFraction(self):
        servings = float(Fraction(self.servings[0]))
        if len(self.servings) > 1:
            servingTuple = self.getServingTuple(self.servings[1])
            servings /= float(Fraction(servingTuple[0]))
        return servings

    def parseNumberValue(self, number):
        value = str(number)
        #if ' ' in value and '/' in value:
        #    (wholeNumber, fraction) = value.strip().split(' ', 1)
        #    return float(Fraction(wholeNumber)) + float(Fraction(fraction))
        #return float(Fraction(number))
        value = value.strip()
        value = sum(map(Fraction, value.split()))
        return float(value)

    def updateTotals(self):
        if len(self.servings) < 1:
            print "Error: cannot update totals without servings"
            return False
        servings = self.parseNumberValue(self.servings[0])
        if len(self.servings) > 1:
            servingTuple = self.getServingTuple(self.servings[1])
            servings /= self.parseNumberValue(servingTuple[0])

        self.totalCalories = float(self.parseNumberValue(self.calories) * servings)
        self.totalProtein = float(self.parseNumberValue(self.protein) * servings)
        self.totalCarb = float(self.parseNumberValue(self.carb) * servings)
        self.totalFat = float(self.parseNumberValue(self.fat) * servings)

    def asStrTuple(self):
        servingTuple = self.getDefaultServings()
        tmp = (
                str(self.name),
                str(servingTuple[0])+" "+str(servingTuple[1]), 
                str("%g" % (round(float(self.calories),2))), 
                str("%g" % (round(float(self.protein),2))) + " g", 
                str("%g" % (round(float(self.carb),2))) + " g", 
                str("%g" % (round(float(self.fat),2))) + " g"

            )
        return tmp

    def totalAsTuple(self):
        if len(self.servings) > 1:
            servingTuple = self.servings
        elif len(self.servings)==1:
            servingTuple = self.getDefaultServings()
            servings = self.parseNumberValue(servingTuple[0])
            servingTuple = ("%g" % (servings), "Serving(s)")
        else:
            print "Error: cannot generate tuple without servings"
            return False
        tmp = (
                str(self.name), 
                str(servingTuple[0])+" "+str(servingTuple[1]), 
                str("%g" % (round(self.totalCalories,2))), 
                str("%g" % (round(self.totalProtein,2))) + " g", 
                str("%g" % (round(self.totalCarb,2))) + " g", 
                str("%g" % (round(self.totalFat,2))) + " g"
            )
        return tmp

    def totalAsFloatTuple(self):
        if len(self.servings) > 1:
            servingTuple = self.servings
        elif len(self.servings)==1:
            servingTuple = self.getDefaultServings()
            servings = self.parseNumberValue(servingTuple[0])
            servingTuple = ("%g" % (servings), "Serving(s)")
        else:
            print "Error: cannot generate tuple without servings"
            return False
        tmp = (
                str(self.name), 
                str(servingTuple[0])+" "+str(servingTuple[1]),
                str("%g" % (round(self.totalCalories,4))),
                str("%g" % (round(self.totalProtein,4))),
                str("%g" % (round(self.totalCarb,4))),
                str("%g" % (round(self.totalFat,4)))
            )
        return tmp
