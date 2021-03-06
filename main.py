from competition import Competition
from event import Event
from mail import sendHTMLEmail
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json



chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


driver = webdriver.Chrome('/usr/bin/chromedriver',options=chrome_options)


url = "https://www.fis-ski.com/DB/alpine-skiing/calendar-results.html?eventselection=&place=&sectorcode=AL&seasoncode=2021&categorycode=WC&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-2021&saveselection=-1&seasonselection="

driver.get(url)
print("Main page loaded")

elems = driver.find_elements_by_class_name("table-row")


# elems = elems[10:13]

competitionList = []

for e in elems:
    competition = Competition(e)
    competitionList.append(competition)

liveEvent=[]
# For each competition, go to the corresponding page
for competition in competitionList:
    competition.addEvents()

    if competition.live:
        liveEvent.append(competition)

# liveEvent=competitionList

# Send email about live competitions
# sendHTMLEmail()


# Convert nested objects into a dictionnary for storage system
dictCompetitionList = []
for competition in competitionList :
    dictCompetitionList.append(competition.customDict())


with open("results.json","w") as f:
    # print("\nCompetition list:")
    # print(dictCompetitionList)
    f.write(json.dumps(dictCompetitionList))



# print("Number of competitions:",len(elems))


# jsonStr = json.dumps(competitionList[0].__dict__)
# print(jsonStr)