from pymongo import MongoClient
from IPython.display import YouTubeVideo, Image, display
from datetime import timedelta
import dateutil.parser
import matplotlib.pyplot as plt
import csv
import pandas as pd
import datetime
from datetime import date
import numpy as np

class Database:
    def __init__(self, key, database):
        self.client = MongoClient(key)
        self.dbName = database
        self.db = self.client[database]
        
    def addItem(self, payload, collection):
        if self.dbName == 'iNaturalist':
            if self.db[collection].find_one(payload) == None:
                self.db[collection].insert_one(payload);
        else:
            try:
                self.db[collection].insert_one(payload)
            except:
                # Item already exists in database
                pass
        
    def getAllItems(self, collection):
        res = self.db[collection].find()
        return [x for x in res]
    
    def convertToUTC(self, collection):
        res = self.db[collection].find({"relevant":None})
        count = 0
        anticount = 0
        
        for doc in res:
            date_str = doc['publishedAt']
#             print(type(date_str))
            if type(date_str) == str:
                doc_id = doc['_id']
                datetime_obj = dateutil.parser.parse(date_str)
                #print(doc_id)
                #print(type(datetime_obj))
                #print(type(doc['publishedAt']))
                self.db[collection].update_one({'_id': doc_id}, {'$set':{'publishedAt': datetime_obj}})
                count = count + 1
                #print(type(doc['publishedAt']))
            else:
#                 print("datetime object")
                anticount = anticount + 1
                continue
        print(count)
        print(anticount)
        
    def doStatistics(self, collection, amount):
        i = 1
        while(amount > 0):
            #only retrieve videos to filter that meet the time frame of June 1st, 2019 and forward
            dateStr = '2019-06-01T00:00:00.00Z'
            timeFrameStart = dateutil.parser.parse(dateStr)
            item = self.db[collection].find_one({"$and":[{"relevant": None},{"publishedAt":{"$gte": timeFrameStart}}]})
            if not item:
                break
            
            if self.dbName=='youtube':
                print("{}: {}".format(i, item['title']['original']))
                display(YouTubeVideo(item['_id']))
            elif self.dbName == 'twitter':
                display(Image(item['img_url'], height=100, width=200))
            elif self.dbName == 'iNaturalist':
                display(Image(item['url'], height=100, width=200))
    
            print("Relevant (y/n):", end =" ")
            rel = True if input() == "y" else False
            
            #categorize post as wild or captive
            if rel == True:
                print("Wild (y/n):", end =" ")
                if input() == 'y':
                    wild = True
                else:
                    wild = False
                    if self.dbName == 'youtube':
                        loc = 0
                #prompt user with option to enter location only if encounter is wild (YT videos only)
                if wild == True:
                    if self.dbName == 'youtube':
                        if item['recordingDetails']['location'] == None: 
                            print("Is there a location? (y/n):", end =" ")
                            if input() == "y": 
                                print("Enter location (city,country):", end = " ")
                                loc = input()
                            else:
                                loc = 0   
            #handle irrelevant posts
            if rel == False:
                wild = 0 #bc cannot determine a video to be wild if it is not relevant 
                if self.dbName == 'youtube':
                    loc = 0 #location does not matter if post is not relevant
                
            #update with new values
            if self.dbName == 'youtube':
                self._updateItem(collection, item['_id'], {"relevant": rel, "wild": wild,"newLocation": loc })
                print("Response saved! Location : {}.\n".format(loc))
            else:
                self._updateItem(collection, item['_id'], {"relevant": rel, "wild": wild})
                
            print("Response saved! {} and {}.\n".format("Relevant" if rel else "Not relevant", "Wild" if wild else "Not wild"))
            #update amount of items in collection that need to be filtered
            amount -= 1
            i += 1
        print('No more items to proceed.')
    
            
    def _updateItem(self, collection, id, payload):
        try:
            self.db[collection].update_one({"_id": id}, {"$set": payload})
            return True
        except(e):
            print("Error updating item", e)
            return False
        
    def showStatistics(self, collection):
        total = self.db[collection].count_documents({ "$and": [{"relevant":{"$in":[True,False]}}]})
        if total == 0:
            print("No videos were processed yet.")
            return
        #relevant count
        relevant_count = self.db[collection].count_documents({ "$and": [{"relevant":True}]})
        # percent relevant caluclated out of total
        relevant = self.db[collection].count_documents({ "$and": [{"relevant":True}]}) / total * 100 
        # percent wild calculated out of ONLY relevant items, this way the remaining percent can be
        # assumed to be % of zoo sightings
        wild = self.db[collection].count_documents({ "$and": [{"relevant":{"$in":[True]}}, {"wild":True}] }) / relevant_count * 100
        # percent wild calculated out of total
        wild_tot = self.db[collection].count_documents({ "$and": [{"relevant":{"$in":[True]}}, {"wild":True}] }) / total * 100
        print("Out of {} items, {}% are relevant.From those that are relevant, {}% are wild. Out of the total, {}% are wild".format(total, round(relevant,1), round(wild,1), round(wild_tot, 1)))

        self.showHistogram(collection)

    def showHistogram(self, collection):
        keys = {'youtube': 'publishedAt', 'twitter': 'created_at', 'iNaturalist': 'time_observed_utc'}
        #gather results for youtube or twitter
        if self.dbName == 'youtube' or self.dbName == 'twitter':
            res = self.db[collection].find({'wild':True})
        else:
            #gather results for iNaturalist
            res = self.db[collection].find({"$and": [{'captive': False},{'time_observed_utc':{"$ne":None}}]})
        #create a list of all the times (in original UTC format) in respective fields for each platform    
        self.timePosts = [x[keys[self.dbName]] for x in res]
        if len(self.timePosts) < 1:
            print("No videos were processed yet.")
            return
        self.dates = [dateutil.parser.parse(x).date() for x in self.timePosts] #Convert the times from datetime format to YYYY-MM-DD format
        self.dates.sort() #sort the converted dates in a list with most recent at beginning and least recent towards end
        
        # Find the difference in days between posting dates of successive posts
        lastDate = [self.dates[0]]  #stores all the dates we have already looked at
        timeDiffs = []
        for date in self.dates:
            res = abs(date - lastDate[-1])#find the time difference between successive posts sorted
            timeDiffs.append(res.days)
            lastDate.append(date)

        # Plotting the histogram
        plt.figure(figsize=(15,5))
        plt.hist(timeDiffs, bins = 10, histtype = 'bar', rwidth = 0.8)
        plt.xlabel('Days between succesive posts')
        plt.ylabel('Number of posts')
        plt.title('Histogram for Time Between Succesive Wild Posts')
        plt.show()
        
    #gather all posts within a certain time frame
    #collection should be species name + wild
    #fromDate is the date (string) we want to start gathering data at
    #return a list of dates within time frame
    def gatherDates(self, collection, YYYY = 2019, MM = 6, DD = 1):
        self.listOfDates = []
        for date in self.dates:
            if date >= datetime.date(year = YYYY, month = MM, day = DD): #fromDate:
                self.listOfDates.append(date)
                
        #print("list of dates from fromDate until now")
        #print(self.listOfDates)
        return self.listOfDates
      
    #take list of dates as input and structure a dictionary as such: {week_0: 2, week_1: 15, week_2: 37 ...}
    #plots number of posts (y axis) vs week # (x axis)
    def postsPerWeek(self, YYYY = 2019, MM = 6, DD = 1):
        start = datetime.date(year = YYYY, month = MM, day = DD)
        end = datetime.date.today()
        weekStartDates = []
        
        #make a list of dates for the start of each week beginning from "start" to "end"
        while start < end : 
            weekStartDates.append(start)
            start += datetime.timedelta(days = 7)   
     
        #make a dictionary to order weekStartDates
        #format self.dictWeekNumbers = { 1 : 06.01.19, 2: 06.08.19, 3:06.15.19 ... }
        #where the values are datetime objects 
        self.dictWeekNumbers = {}
        weekNumber = 1
        for week in weekStartDates:
            self.dictWeekNumbers[weekNumber] = week
            weekNumber += 1
        print('\n')
        print("week number dictionary: \n", self.dictWeekNumbers)
        print('\n')
            
        #make a dictionary self.postsPerWeek
        #keys are datetime objects of the date to start a new week
        #values are number of posts that were posted anytime from that date to date + 6 days
        #format self.postsPerWeek = { 06.01.19 : 4, 06.08.19 : 5, 06.15.19 : 1 ... }
        count = 0
        self.postsPerWeekDict = {}
        for weekStartDate in weekStartDates:
            nextDate = weekStartDate + datetime.timedelta(days = 7)
            for date in self.listOfDates:
                if (date >= weekStartDate) and (date < nextDate):
                    count += 1
            self.postsPerWeekDict[weekStartDate] = count
            count = 0
        
        return self.postsPerWeekDict
    
    #use numpy to compute and plot the smoothed out posts per week stats in order to visualize any trends
    #plot average number of posts (y-axis) vs week # (x axis)
    #returns a list of simple moving average data points
    def movingAveragePosts(self,window):
        #create a list of just the counts of posts for each week 
        postsPerWeekList = [item for item in self.postsPerWeekDict.values()]
        print(postsPerWeekList)  

        #print('calculating simple moving average...\n')
        #calculating moving average with data points in postsPerWeekList
        weights = np.repeat(1.0, window)/window
        self.smas = np.convolve(postsPerWeekList, weights, 'valid') #calculate simple moving averages (smas)
        return self.smas
    
    #get videoID's for each document that belongs to a wild encounter
    #return a list of videoID's
    def getUserCountriesIDs(self, collection):
        docs = self.db[collection].find({"wild": True})     
        listOfVideoIDs = [doc['videoID'] for doc in docs if dateutil.parser.parse(doc['publishedAt']).date() in self.listOfDates] 
        return listOfVideoIDs
      
    #customized to youtube only so far
    def heatmap(self,collection, csvName):
        self.csvName = csvName +'.csv'
        #docs_w_loc = self.db[collection].find({'$and': [{'wild': True}, {'newLocation':{'$ne':0}}]})
        docs_w_loc = self.db[collection].find({'newLocation':{'$ne':0}})
        loc_list = []
        for doc in docs_w_loc:
            try:
                dic = {
                    'videoID' : doc['videoID'],
                    'newLocation':doc['newLocation']
                }
                loc_list.append(dic)
                #print(doc)
            except KeyError:
                if KeyError == 'newLocation':
                    pass     
        
        fields = ['videoID', 'newLocation'] 
        with open(self.csvName, 'w') as locations_csv:
            csvName = csv.DictWriter(locations_csv, fieldnames = fields)
            csvName.writeheader()
            for item in loc_list:
                csvName.writerow(item)
        print('done! Check in your jupyter files for a .csv file with the name you entered')
    
    #method to form collections consisting of only wild docs for wildbook api call
    #only tailored towards YouTube currently
    def relevantDocuments(self, existingCollection):
        newDocs = self.db[existingCollection].find({"wild": True})
        newCollection = existingCollection + " wild"
        #insert "wild" encounter items from existingCollection into newCollection
        #if not already in newCollection
        for item in newDocs:
            if self.db[newCollection].find_one(item) == None:
                self.db[newCollection].insert_one(item);
                
    def clearCollection(self, collection, msg=''):
        if (msg == 'yes'):
            self.db[collection].delete_many({})
            print("Collection was cleared.")
        else:
            print("Pass 'yes' into clearCollection() method to really clear it.")
            
    def close(self):
        self.client.close()
        
