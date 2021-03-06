import sys
from PyQt5.QtWidgets import QApplication,QLabel, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout,QListWidget,QTableWidget,QTableWidgetItem,QAbstractScrollArea
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSlot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import random
import json
import dataVisualisation

class App(QDialog):

    def __init__(self):
        super().__init__()
        self.title = 'FIS results GUI'
        self.left = 50
        self.top = 50
        self.width = 1800
        self.height = 1000
        self.initUI()


        with open("config.json","r") as config:
            self.config = json.load(config)
        with open("results.json","r") as results:
            self.results = json.load(results)


        self.fillCategories()
        self.fillEvents()
        # Display graphs
        self.showGraphs()


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)        
        
        windowLayout = QGridLayout()


        self.categorySelectorGroupBox = QGroupBox("Category")
        self.eventSelectorGroupBox = QGroupBox("Event")

        self.statsGroupBox = QGroupBox("Stats")
        self.plotLine1GroupBox1 = QGroupBox("Podium per country")
        self.plotLine1GroupBox2 = QGroupBox("Controls")
        self.plotLine1GroupBox3 = QGroupBox("Breakdown per month")

        self.plotLine2GroupBox1 = QGroupBox("Race result")
        self.plotLine2GroupBox2 = QGroupBox("Statistic of the season")
        # self.plotLine2GroupBox3 = QGroupBox("Line2 Block 3")

        # self.bottomGroupBox = QGroupBox("Last Race")


        windowLayout.addWidget(self.plotLine1GroupBox1,0,2,2,3)
        windowLayout.addWidget(self.plotLine1GroupBox2,0,5,2,3)
        windowLayout.addWidget(self.plotLine1GroupBox3,0,8,2,3)

        windowLayout.addWidget(self.plotLine2GroupBox1,2,2,2,4)
        windowLayout.addWidget(self.plotLine2GroupBox2,2,6,2,5)
        # windowLayout.addWidget(self.plotLine2GroupBox3,2,8,2,3)

        windowLayout.addWidget(self.categorySelectorGroupBox,0,0,2,2)
        windowLayout.addWidget(self.eventSelectorGroupBox,2,0,2,2)

        # windowLayout.addWidget(self.bottomGroupBox,5,0,2,11)

        self.setLayout(windowLayout)
        self.show()

    def fillCategories(self):
        availablesCategories = list(self.config["resultsStruct"].keys())
        availablesCategories.insert(0,"All")
        # Set default category "All"
        self.category = "All"
        self.categoryList = QListWidget()

        for category in availablesCategories:
            self.categoryList.addItem(str(category))

        self.categoryList.itemClicked.connect(self.categorySelectedCallback)
        self.categorySelector = QVBoxLayout()
        self.categorySelector.addWidget(self.categoryList)
        self.categorySelectorGroupBox.setLayout(self.categorySelector)


    def categorySelectedCallback(self):
        newCategory = self.categoryList.currentItem().text()
        # print(f"Update selected category from {self.category} to {newCategory}")
        self.category = newCategory
        self.resetGraphsCategory()


    def fillEvents(self):
        self.availablesEvents = dataVisualisation.getEventsList(self.results)

        self.event = self.availablesEvents[0]
        self.eventList = QListWidget()

        for event in self.availablesEvents:
            # print(event)
            date = "{:02d}".format(event["date"]["day"])+"/"+str(event["date"]["month"])+"/"+str(event["date"]["year"])
            self.eventList.addItem(date+' | '+str(event["place"])+" - "+event["type"])

        self.eventList.itemClicked.connect(self.eventSelectedCallback)
        self.eventSelector = QVBoxLayout()
        self.eventSelector.addWidget(self.eventList)
        self.eventSelectorGroupBox.setLayout(self.eventSelector)


    def eventSelectedCallback(self):
        newEventIndex = self.eventList.currentRow()
        # print(f"Update selected event from {self.event} to {self.availablesEvents[newEventIndex]}")
        self.event = self.availablesEvents[newEventIndex]
        self.resetGraphsEvents()



    def showGraphs(self):
        self.createCountryPodium()
        self.createEventResults()
        self.createDetailAthlete()
        self.createCountryResultsBreakdown()
        self.createControls()

    def resetGraphsCategory(self):
        # Reset podium per country
        while (self.podiumTable.rowCount() > 0):
            self.podiumTable.removeRow(0)
        self.fillCountryPodium()
        # self.resetGraphBreakdown()


    def resetGraphsEvents(self):
        while (self.eventTable.rowCount() > 0):
            self.eventTable.removeRow(0)
        self.fillEventResults()


    def resetGraphBreakdown(self):
        # discards the old graph
        self.ax.clear()
        # refresh canvas
        self.canvas.draw()


        # Reset all the labels in the controlBox
        # controlLayout.clearL

        for i in reversed(range(self.labelLayout.count())): 
            # layoutToDel = self.labelLayout.itemAt(i)
            widgetToRemove = self.labelLayout.itemAt(i).widget()
            # remove it from the layout list
            self.labelLayout.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)

    def createControls(self):
        self.resetGraphButton = QPushButton(text="Reset graph")

        self.resetGraphButton.clicked.connect(self.resetGraphBreakdown)

        self.controlLayout = QVBoxLayout()
        
        self.controlLayout.addWidget(self.resetGraphButton)
        self.controlLayout.addStretch()
        self.labelLayout = QVBoxLayout()

        self.plotLine1GroupBox2.setLayout(self.controlLayout)
        self.controlLayout.addLayout(self.labelLayout)


    def createCountryPodium(self):
        self.podiumTable = QTableWidget()
        self.podiumTable.setHorizontalHeaderLabels(["Country"," 1st Places ", " 2nd Places ", " 3rd Places "])
        self.fillCountryPodium()

        self.podiumTable.resizeColumnToContents(1)
        self.podiumTable.resizeColumnToContents(2)
        self.podiumTable.resizeColumnToContents(3)

        self.countryPodium = QVBoxLayout()
        self.countryPodium.addWidget(self.podiumTable)

        self.plotLine1GroupBox1.setLayout(self.countryPodium)

        self.podiumTable.cellClicked.connect(self.countryMedalBreakdownCallback)


    def fillCountryPodium(self):
        data = dataVisualisation.countryPodiumTable(self.results,self.category)
        self.podiumTable.setRowCount(len(data))
        self.podiumTable.setColumnCount(4)

        for i,country in enumerate(data):
            self.podiumTable.setItem(i,0, QTableWidgetItem(country.name))
            self.podiumTable.setItem(i,1, QTableWidgetItem(str(country.first)))
            self.podiumTable.setItem(i,2, QTableWidgetItem(str(country.second)))
            self.podiumTable.setItem(i,3, QTableWidgetItem(str(country.third)))

    

    def countryMedalBreakdownCallback(self,row,column):
        if column==0:
            self.country = self.podiumTable.item(row,0).text()
            print(f"Show detailed info about the country : {self.country}")

            self.fillCountryResultsBreakdown()
    
    def createCountryResultsBreakdown(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        
        # create an axis
        self.ax = self.figure.add_subplot(111)

        # discards the old graph
        self.ax.clear()
        
        self.ax.set_xlabel("Months")
        self.ax.set_ylabel("Nb of podiums")

        layout = QVBoxLayout()

        layout.addWidget(self.canvas)

        self.plotLine1GroupBox3.setLayout(layout)

    def fillCountryResultsBreakdown(self):
        data = dataVisualisation.getCountryBreakdown(self.country,self.category)

        
        # plot data
        p = self.ax.plot(data[0],data[1], '*-')

        # refresh canvas
        self.canvas.draw()

        # Get color from last line added on the graph
        hexColor = p[0].get_color()

        # Show info in the control box
        desc = self.country + " : " + self.category
        labelColor = QLabel(desc)
        labelColor.setStyleSheet(f"background-color: {hexColor}; border: 1px solid black;") 

        self.labelLayout.addWidget(labelColor)



    def createEventResults(self):
        self.eventTable = QTableWidget()
        self.fillEventResults()

        self.eventPodium = QVBoxLayout()
        self.eventPodium.addWidget(self.eventTable)

        self.plotLine2GroupBox1.setLayout(self.eventPodium)

        self.eventTable.cellClicked.connect(self.resultSelectionChanged)

    def resultSelectionChanged(self,row,column):
        if column==0:
            self.detailedAthleteName = self.eventTable.item(row,0).text()
            print(f"Show detailed info about the athlete : {self.detailedAthleteName}")

            # Remove all current stats
            for i in reversed(range(self.detailLayout.count())): 
                self.detailLayout.itemAt(i).widget().deleteLater()

            self.fillDetailAthlete()



    def fillEventResults(self):

        if self.event['type'] == "Slalom" or self.event['type'] == "Giant Slalom":
            self.eventTable.setHorizontalHeaderLabels([" Athlete ", " Country ", " Run 1 ", " Run 2 ", " Diff (ms) ", " Total "])
            self.eventTable.setColumnCount(6)
            data = dataVisualisation.eventResultTable(self.event)
            self.eventTable.setRowCount(len(data))
          
            for i,athlete in enumerate(data):
                self.eventTable.setItem(i,0, QTableWidgetItem(str(athlete["name"])[0:22]))
                self.eventTable.setItem(i,1, QTableWidgetItem(str(athlete["country"])))
                self.eventTable.setItem(i,2, QTableWidgetItem(str(athlete["run1"])))
                self.eventTable.setItem(i,3, QTableWidgetItem(str(athlete["run2"])))
                self.eventTable.setItem(i,4,QTableWidgetItem(str(athlete["diff"])))

                if athlete["diff"]>0:
                    self.eventTable.item(i, 4).setBackground(QColor(237, 2, 2))
                elif athlete["diff"]<0:
                    self.eventTable.item(i, 4).setBackground(QColor(98, 252, 3))


                self.eventTable.setItem(i,5, QTableWidgetItem(str(athlete["total"])))

                self.eventTable.resizeColumnsToContents()


        elif self.event['type'] == "Super G" or self.event['type'] == "Downhill":
            self.eventTable.setHorizontalHeaderLabels([" Athlete ", " Country ", " Time "])
            self.eventTable.setColumnCount(3)
            
            data = dataVisualisation.eventResultTable(self.event)
            self.eventTable.setRowCount(len(data))
          
            for i,athlete in enumerate(data):
                self.eventTable.setItem(i,0, QTableWidgetItem(str(athlete["name"])[0:22]))
                self.eventTable.setItem(i,1, QTableWidgetItem(str(athlete["country"])))
                self.eventTable.setItem(i,2, QTableWidgetItem(str(athlete["time"])))

                self.eventTable.resizeColumnsToContents()

        elif self.event['type'] == "Parallel":
            self.eventTable.setHorizontalHeaderLabels([" Athlete ", " Country "])
            self.eventTable.setColumnCount(2)

            data = dataVisualisation.eventResultTable(self.event)
            self.eventTable.setRowCount(len(data))
          
            for i,athlete in enumerate(data):
                self.eventTable.setItem(i,0, QTableWidgetItem(str(athlete["name"])[0:22]))
                self.eventTable.setItem(i,1, QTableWidgetItem(str(athlete["country"])))
                
                self.eventTable.resizeColumnsToContents()



    def createDetailAthlete(self):

        self.instructionAthlete = QLabel("Select an athlete first")
        self.detailLayout = QVBoxLayout()
        self.detailLayout.addWidget(self.instructionAthlete)

        self.plotLine2GroupBox2.setLayout(self.detailLayout)


    def fillDetailAthlete(self):
        data = dataVisualisation.getDetails(self.detailedAthleteName,self.results)
        
        # self.detailLayout.removeWidget(self.instructionAthlete)
        
        
        nameCountry = QLabel(f"Name : {data['name']}  |  Country : {data['country']}")
        numberOfRace = QLabel(f"Number of races : {data['numberOfRace']}")
        numberOfPodium = QLabel(f"Number of podiums : {data['numberOfPodium']}")
        bestRank = QLabel(f"Best rank : {data['bestRank']}")
        bestRace = QLabel(f"Best race : {data['bestRace']}")
        bestCategory = QLabel(f"Best category : {data['bestCategory']}")

        self.detailLayout.addWidget(nameCountry)
        self.detailLayout.addWidget(numberOfRace)
        self.detailLayout.addWidget(numberOfPodium)
        self.detailLayout.addWidget(bestRank)
        self.detailLayout.addWidget(bestRace)
        self.detailLayout.addWidget(bestCategory)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())