from operator import attrgetter
import datetime
import json

class Country(object):
    """
    Represent the number of podium from a country
    """
    def __init__(self,name):
        self.name = name
        self.first = 0
        self.second = 0
        self.third = 0

    def increaseCounter(self,result=-1):
        if result==0:
            self.first+=1
        elif result==1:
            self.second+=1
        elif result==2:
            self.third+=1


    def __repr__(self):
        return f" {self.name} - {self.first} | {self.second} | {self.third}"

def countryPodiumTable(data,raceType):
    podium = []
    for competition in data:
        for event in competition["events"]:
            if event["cancelled"]==False and event["review"]==True:
                if event["type"]==raceType or raceType=="All":
                    # Get the data from 1st to 3rd place
                    results = []
                    results.append(event["results"]['1']["nation"])
                    results.append(event["results"]['2']["nation"])
                    results.append(event["results"]['3']["nation"])

                    # If not in the podium list, create a new country to add in the list
                    # Else increase the counters
                    # print(results)
                    for i,result in enumerate(results):
                        for country in podium:
                            if country.name == result:
                                country.increaseCounter(i)     
                                break               
                        else:
                            newCountry = Country(result)
                            newCountry.increaseCounter(i)
                            podium.append(newCountry)

    # Sort the podium 
    podium = sorted(podium, key = attrgetter('first','second','third'),reverse=True)

    # for country in podium:
    #     print(country)
    return podium



def getEventsList(results):
    eventList = []
    for competition in results:
        for event in competition["events"]:
            # If event is not cancelled and already past
            if not event["cancelled"] and event["review"]:
                event["place"]=competition["place"]
                event["country"]=competition["country"]

                eventList.append(event)
    return eventList


def eventResultTable(event):
    results = []
    if event['type'] == "Slalom" or event['type'] == "Giant Slalom":
        for rank,athlete in enumerate(event["results"].keys()):
            athleteResult = {}
            athleteResult["rank"] = rank+1
            athleteResult["name"] = event["results"][athlete]["athlete"]
            athleteResult["country"] = event["results"][athlete]["nation"]
            athleteResult["run1"] = event["results"][athlete]["run1"]
            athleteResult["run2"] = event["results"][athlete]["run2"]
            athleteResult["total"] = event["results"][athlete]["totTime"]


            try:
                run1 = datetime.datetime.strptime(event["results"][athlete]["run1"],"%M:%S.%f")
            except:
                run1 = datetime.datetime.strptime(event["results"][athlete]["run1"],"%S.%f")
            try:
                run2 = datetime.datetime.strptime(event["results"][athlete]["run2"],"%M:%S.%f")
            except:
                run2 = datetime.datetime.strptime(event["results"][athlete]["run2"],"%S.%f")

            athleteResult["diff"] = millis_interval(run1,run2)
            results.append(athleteResult)

    elif event['type'] == "Super G" or event['type'] == "Downhill":
        for rank,athlete in enumerate(event["results"].keys()):
            athleteResult = {}
            athleteResult["rank"] = rank+1
            athleteResult["name"] = event["results"][athlete]["athlete"]
            athleteResult["country"] = event["results"][athlete]["nation"]
            athleteResult["time"] = event["results"][athlete]["time"]

            results.append(athleteResult)
    
    elif event['type'] == "Parallel":
        for rank,athlete in enumerate(event["results"].keys()):
            athleteResult = {}
            athleteResult["rank"] = rank+1
            athleteResult["name"] = event["results"][athlete]["athlete"]
            athleteResult["country"] = event["results"][athlete]["nation"]
            
            results.append(athleteResult)

    return results


def getDetails(name,results):
    
    # Name
    # Country
    # Number of races
    # Highest ranking
    bestRank = 1000
    bestRace = None
    numberOfRace = 0
    numberOfPodium=0
    bestCategory=None
    country = None
    for competition in results:
        for event in competition["events"]:
            try:
                results = event["results"]
                for rank,athlete in enumerate(event["results"].keys()):
                    if event["results"][athlete]["athlete"] == name:
                        country=event["results"][athlete]["nation"]
                        numberOfRace+=1
                        if rank+1 < bestRank:
                            bestRank=rank+1
                            bestRace=event["place"]
                            bestCategory=event["type"]
                        if rank<3:
                            numberOfPodium+=1
            except:
                pass
   

    stats = {}
    stats['country']=country
    stats['numberOfRace']=numberOfRace
    stats['bestRank']=bestRank
    stats['bestRace']=bestRace
    stats['bestCategory']=bestCategory
    stats['numberOfPodium']=numberOfPodium
    stats['name']=name
    
    return stats


def getCountryBreakdown(country,category):
    months = {
    "Jul":0,
    "Aug":0,
    "Sep":0,
    "Oct":0,
    "Nov":0,
    "Dec":0,
    "Jan":0,
    "Feb":0,
    "Mar":0,
    "Apr":0,
    "May":0,
    "Jun":0,
    }

    with open("results.json","r") as res:
        results = json.load(res)
    
    # Translate monthID to monthStr
    with open("config.json","r") as config:
        monthTranslate = json.load(config)["idToMonth"]
    
    for competition in results:
        for event in competition["events"]:
            if event["type"]==category or category=="All":
                try:
                    results = event["results"]
                    for i in range(1,4):
                        if results[str(i)]["nation"]==country:
                            monthName = monthTranslate[str(event["date"]["month"])]
                            months[str(monthName)]+=1
                except:
                    pass

    monthLabel = list(months.keys())
    monthData = list(months.values())


    return [monthLabel,monthData]


def millis_interval(start, end):
    """start and end are datetime instances"""
    diff = end - start
    millis = diff.days * 24 * 60 * 60 * 1000
    millis += diff.seconds * 1000
    millis += diff.microseconds / 1000
    return millis




if __name__ == "__main__":
    import json

    # with open("results.json","r") as results:
    #     res = json.load(results)

        # countryPodiumTable(res,"All")
        
    print(getCountryBreakdown("SVK",'All'))