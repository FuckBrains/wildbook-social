import requests
import json
import time

class Flickr:


    def __init__(self, db = None):
        self.db = db


    def clean_data(self, reponse_data):
        json_data = []
        for photo in reponse_data['photos']['photo']:
                
            data = {}
            data["id"] = photo["id"]
            data["title"] = photo["title"]
            data["owner"] = photo["owner"]
            data["ownername"] = photo["ownername"]
            data["dateupload"] = photo["dateupload"]
            data["datetaken"] = photo["datetaken"]
            data["lastupdate"] = photo["lastupdate"]
            data["views"] = photo["views"]
            data["accuracy"] = photo["accuracy"]
            data["latitude"] = photo["latitude"]
            data["longitude"] = photo["longitude"]
            data["media"] = photo["media"]

            data["encounter"] = {
                            "locationIDs": [], #[Wildbook]
                            "dates": [], #[Wildbook]
                        }
            data["animalsID"] =  [] #[Wildbook]
            data["curationStatus"] =  None #[Wildbook]
            data["curationDecision"] = None #Wildbook]

            data["gatheredAt"] =  time.ctime()
            data["relevant"] = None
            data["wild"] = None
            data["type"] = "flickr"

            
            try:
                data["url_l"] = photo["url_l"]
            except:
                data["url_l"] = ""
            data["tags"] = photo["tags"]
            data["description"] = photo['description']['_content']
            json_data.append(data)
        return json_data

    def search(self, q, date_since="2019-12-01", saveTo=False):
        
        ## bbox for africa-(zebra for plains zebra)
        ##https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key=6ab5883201c84be19c9ceb0a4f5ba959&text=zebra&min_taken_date=2019-06-01&bbox=-18.615646%2C-34.936608%2C50.993729%2C35.266926&format=json&nojsoncallback=1
        
#         ## bbox for kenya + ethiopia= (zebra for grevys zebra)
#         https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key=6ab5883201c84be19c9ceb0a4f5ba959&text=zebra&min_taken_date=2019-06-01&bbox=31.685944%2C-4.096123%2C48.297272%2C14.720100&format=json&nojsoncallback=1

       ## bbox for iberian lynx - spain 
#     https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key=6ab5883201c84be19c9ceb0a4f5ba959&text=iberian+lynx&min_taken_date=2019-06-01&bbox=-10.213165%2C36.183195%2C3.036346%2C43.732282&format=json&nojsoncallback=1
            
        base_url = "https://www.flickr.com/services/rest/?\
            method=flickr.photos.search&api_key=6ab5883201c84be19c9ceb0a4f5ba959&text={text}&min_taken_date={min_date}&extras=description%2Cdate_upload%2C+date_taken%2C+owner_name%2C+last_update%2C+geo%2C+tags%2C+views%2C+media%2C+url_l&page={page}&format=json&nojsoncallback=1"  
        if (saveTo and not self.db):
            saveTo = False
            print("Please provide 'db' argument with an instance to database to save tweet(s).")

        keyword = q.replace(' ','+')
        json_data = []
        url = base_url.format(text=keyword,min_date=date_since,page='1') #tags=keyword
        r = requests.get(url)
        print(r)
        response_data = r.json()
        data = self.clean_data(response_data)
        if (saveTo):
            print('saving...')
            for item in data:
                self.db.addItem(item, saveTo)
        json_data.append(data)
        pages = response_data['photos']['pages']
        print(pages,'Found with',keyword)
        for page in range(2, pages+1):
            print('page no.',page)
            url = base_url.format(text=keyword,min_date=date_since,page=str(page)) #tags=keyword
            r = requests.get(url)
            try:
                print('in try')
                response_data = r.json()
            except JSONDecodeError:
                print("r: ", r)
            data = self.clean_data(response_data)
            if (saveTo):
                print('saving...')
                for item in data:
                    self.db.addItem(item, saveTo)
            json_data.append(data)
        return json_data
    
    #method to get user locations with flickr.people.getInfo()
    def getUserLocations(self, ownerIdDicts):
        owner_locations_dicts = []
        for item in ownerIdDicts:
            #get people.getInfo response from flickr api
            base_url = "https://www.flickr.com/services/rest/?method=flickr.people.getInfo&\
                        api_key=b3fb43d7040c83c55121688a2de47b1f&user_id={}&format=json&nojsoncallback=1"
            
            user_id = item['user_id'].replace('@', '%40')
            url = base_url.format(user_id)
            r = requests.get(url)
            response = r.json()
            try:
                user_location = response['person']['location']['_content'] #for photo in response['photo']
            except KeyError:
                user_location = None
            #add user loc to dictionary
            item['user_location'] = user_location
        return ownerIdDicts
    
            


# import requests
# import json
# import time
# # import database from Database

# class Flickr:


#     def __init__(self, db = None):
#         self.db = db


#     def clean_data(self, reponse_data):
#         json_data = []
#         for photo in reponse_data['photos']['photo']:
                
#             for item in json_data:
                
#                 #check that the item is not already in our collection
# #                 if self.db[collection].count_documents({'id': photo['id']}) >= 1:
# #                     print(self.db[collection].count_documents({'id': photo['id']}))
# #                     print(photo['id'], ' is already in database')
# #                     continue
# #                 else:
#                 data = {}
#                 data["id"] = photo["id"]
#                 data["title"] = photo["title"]
#                 data["owner"] = photo["owner"]
#                 data["ownername"] = photo["ownername"]
#                 data["dateupload"] = photo["dateupload"]
#                 data["datetaken"] = photo["datetaken"]
#                 data["lastupdate"] = photo["lastupdate"]
#                 data["views"] = photo["views"]
#                 data["accuracy"] = photo["accuracy"]
#                 data["latitude"] = photo["latitude"]
#                 data["longitude"] = photo["longitude"]
#                 data["media"] = photo["media"]

#                 data["encounter"] = {
#                                     "locationIDs": [], #[Wildbook]
#                                     "dates": [], #[Wildbook]
#                                 }
#                 data["animalsID"] =  [] #[Wildbook]
#                 data["curationStatus"] =  None #[Wildbook]
#                 data["curationDecision"] = None #Wildbook]

#                 data["gatheredAt"] =  time.ctime()
#                 data["relevant"] = None
#                 data["wild"] = None
#                 data["type"] = "flickr"

#                 try:
#                     data["url_l"] = photo["url_l"]
#                 except:
#                     data["url_l"] = ""
#                 data["tags"] = photo["tags"]
#                 data["description"] = photo['description']['_content']
#                 json_data.append(data)
#         return json_data

#     def search(self, q, date_since="2019-06-01", saveTo=False):
#         base_url = "https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key=b3fb43d7040c83c55121688a2de47b1f&tags={text}&text={text}&min_taken_date={min_date}&extras=description%2Cdate_upload%2C+date_taken%2C+owner_name%2C+last_update%2C+geo%2C+tags%2C+views%2C+media%2C+url_l&page={page}&format=json&nojsoncallback=1"
#         if (saveTo and not self.db):
#             saveTo = False
#             print("Please provide 'db' argument with an instance to database to save posts(s).")

#         keyword = q.replace(' ','+')
#         json_data = []
#         url = base_url.format(text=keyword,tags=keyword,min_date=date_since,page='1')
#         r = requests.get(url) #called for data on 1st page only, so far
#         reponse_data = r.json()
#         data = self.clean_data(reponse_data)
#         if (saveTo != False):
#             print('saveTo not false')
#             for item in data:
#                 print(item)
#                 self.db.addItem(item, saveTo)
#         json_data.append(data)
#         #debugging json_data
#         print(json_data)
#         pages = reponse_data['photos']['pages']
#         print(pages,'Found with',keyword)
#         #call requests.get() method on data for remaining pages
#         for page in range(2, pages+1):
#             print('page no.',page)
#             url = base_url.format(text=keyword,tags=keyword,min_date=date_since,page=str(page))
#             r = requests.get(url)
#             reponse_data = r.json()
#             data = self.clean_data(reponse_data)
#             if (saveTo != False):
#                 for item in data:
#                     self.db.addItem(item, saveTo)
# #                     if self.db[saveTo].find_one(item) == None:
# #                         self.db[saveTo].insert_one(item)
#             json_data.append(data)
#             #debugging json_data
#             print(json_data)
#         return json_data
    
#     #method to get user locations with flickr.people.getInfo()
#     def getUserLocations(self, ownerIdDicts):
#         owner_locations_dicts = []
#         for item in ownerIdDicts:
#             #get people.getInfo response from flickr api
#             base_url = "https://www.flickr.com/services/rest/?method=flickr.people.getInfo&\
#                         api_key=b3fb43d7040c83c55121688a2de47b1f&user_id={}&format=json&nojsoncallback=1"
            
#             user_id = item['user_id'].replace('@', '%40')
#             url = base_url.format(user_id)
#             r = requests.get(url)
#             response = r.json()
#             try:
#                 user_location = response['person']['location']['_content'] #for photo in response['photo']
#             except KeyError:
#                 user_location = None
#             #add user loc to dictionary
#             item['user_location'] = user_location
#         return ownerIdDicts
        
            


        
