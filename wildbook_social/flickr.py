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
        base_url = "https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key=6ab5883201c84be19c9ceb0a4f5ba959&tags={text}&text={text}&min_taken_date={min_date}&extras=description%2Cdate_upload%2C+date_taken%2C+owner_name%2C+last_update%2C+geo%2C+tags%2C+views%2C+media%2C+url_l&page={page}&format=json&nojsoncallback=1"
        if (saveTo and not self.db):
            saveTo = False
            print("Please provide 'db' argument with an instance to database to save tweet(s).")

        keyword = q.replace(' ','+')
        json_data = []
        url = base_url.format(text=keyword,tags=keyword,min_date=date_since,page='1')
        r = requests.get(url)
        reponse_data = r.json()
        data = self.clean_data(reponse_data)
        if (saveTo):
            for item in data:
                self.db.addItem(item, saveTo)
        json_data.append(data)
        pages = reponse_data['photos']['pages']
        print(pages,'Found with',keyword)
        for page in range(2, pages+1):
            print('page no.',page)
            url = base_url.format(text=keyword,tags=keyword,min_date='2019-12-01',page=str(page))
            r = requests.get(url)
            reponse_data = r.json()
            data = self.clean_data(reponse_data)
            if (saveTo):
                for item in data:
                    self.db.addItem(item, saveTo)
            json_data.append(data)
        return json_data
            


        
