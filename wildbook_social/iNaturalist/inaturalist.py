import gmplot
import csv
from pymongo import MongoClient
import requests
import re
# import database as db

class iNaturalist:  
    '''
    initializer method with "query" parameter. During instantiation, pass in string for animal to "query"
    also sets up parameters for requests query 
    db = database to use. In this case, pass in db = 'iNaturalist'
    '''
    def __init__(self, db = None):
        self.URL = "https://www.inaturalist.org/observations.json" #connect to endpoint
        #params
        self.has = 'photos' #only retrieve observations with photos
        self.page = 1       #begin at page 1
        self.perPage = 200  #max allowed per page value
        self.db = db
       
    '''requests method makes actual query to iNaturalist API and retrieves images 
       query = string for species you wish to retrieve results for
       saveTo = collection in database you want to save image documents under
    '''
    def requests(self, query, saveTo = False):
        self.q = query
        self.formatted_dicts = []  #holds results/observations scraped from API in structured python dictionaries
        #begin scraping
        while(self.page <= 22):
            self.result =  requests.get(url = self.URL,params = {'q': self.q,
                                                                  'page': self.page,
                                                                  'per_page':self.perPage,
                                                                  'has[]': self.has}).json()
            for item in self.result:
                if item ==[]:
                    break
                    #FIXME, should we do a pass or continue instead of breaking right away?
                else:
                    newItem = {
                                'id': item['id'],
                                'url':item['uri'],
                                'photo_count': item['observation_photos_count'],
                                'taxon': item['iconic_taxon_name'],
                                'location': item['place_guess'],
                                'latitude': item['latitude'],
                                'longitude': item['longitude'],
                                'observed_on': item['observed_on'],
                                'time_observed_utc': item['time_observed_at_utc'],
                                'time_zone': item['time_zone'],
                                'created_on': item['created_at'],
                                'captive': item['captive']    
                            }
                    #add newItem dict to collection
                    #FIXME: connect to database.py like youtube playground
                    if (saveTo):
                        #if self.db[saveTo].find_one(newItem) == None:
                        self.db.addItem(newItem, saveTo)
                    #add newly structured dictionary to formated_dicts list
                    self.formatted_dicts.append(newItem)
            self.page += 1 #increment page number
        return self.formatted_dicts