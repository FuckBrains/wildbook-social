from googleapiclient.discovery import build
import time
import csv

class YouTube:
    def __init__(self, KEY, db=None):
        self._YOUTUBE_API_SERVICE_NAME = 'youtube'
        self._YOUTUBE_API_VERSION = 'v3'
        self._KEY = KEY
        self.youtube = build(self._YOUTUBE_API_SERVICE_NAME, self._YOUTUBE_API_VERSION, 
                             developerKey=self._KEY)
        self.db = db
        self.nextPageToken = None
        self.page = 1
    
    # Uses youtube.search() API method
    def search(self, q, limit=1, saveTo=False):
        ''' 
        q - search query, (ex. "Whale Shark")
        limit - number of results (ex. 10 or 100)
        fields - Retrieve only selected fields (ex. True, False)
        saveTo - Saves all retrieved videos to provided collection
        '''
        if (saveTo and not self.db):
            saveTo = False
            print("Please provide 'db' argument with an instance to database to save video(s).")
            
        # Going through pages in result
        self.results = []
        while(limit > 0):
            print("Working with page", self.page)
            
            # Quering the result
            searchResult = self.youtube.search().list(
                q=q,
                part='snippet',
                #order = 'date',
                fields='nextPageToken,items(id,snippet(publishedAt,title))',
                type='video',
                maxResults=50 if limit>50 else limit,
                pageToken=self.nextPageToken if self.nextPageToken else '',
                publishedAfter = "2019-06-01T00:00:00Z" #only gather results from June 01 2019 and forwards
            ).execute()
            items = searchResult['items']
            
            self.nextPageToken = searchResult['nextPageToken']
            self.page += 1
            limit -= 50

            # Going through each result
            modifiedResult = []
            for item in items:

                # Quering more details for this result
                details = self.videos(item['id']['videoId'], fields=True)
                for prop in details[0]:
                    try:
                        item[prop].update(details[0][prop])
                    except KeyError:
                        item[prop] = details[0][prop]

                # WILDBOOK FORMAT
                # try:
                newItem = {
                    "_id": item['id']['videoId'],
                    "channelId" : item['snippet'].get('channelId', 0), #added to count posts per user
                    "videoID": item['id']['videoId'],
                    "title": {
                        "original": item['snippet'].get('title', None),
                        "eng": None, #[Microsoft translate]
                    },
                    "tags": {
                        "original": item['snippet'].get('tags', []),
                        "eng": [], #[Microsoft translate]
                    },
                    "description": {
                        "original": item['snippet'].get('description', None),
                        "eng": None, #[Microsoft translate]
                    },
                    "OCR": {
                        "original": [], #[Azure]
                        "eng": [], #[Azure, Microsoft translate]
                    },
                    "url": 'https://youtu.be/' + item['id']['videoId'],
                    "animalsID": [], #[Wildbook]
                    "curationStatus": None, #[Wildbook]
                    "curationDecision": None, #[Wildbook]
                    "publishedAt": item['snippet'].get('publishedAt', None),
                    "uploadedAt": None, #[YouTube]
                    "duration": None, #[YouTube]
                    "regionRestriction": None, #[YouTube]
                    "viewCount": item['statistics'].get('viewCount', None),
                    "likeCount": item['statistics'].get('likeCount', None),
                    "dislikeCount": item['statistics'].get('dislikeCount', None),
                    "recordingDetails": {
                        "location": None, #[YouTube]
                        "date": None, #[YouTube]
                    },
                    "encounter": {
                        "locationIDs": [], #[Wildbook]
                        "dates": [], #[Wildbook]
                    },
                    "fileDetails": None, #[YouTube]
                    "gatheredAt": time.ctime(),
                    "relevant": None,
                    "wild": None
                }

                # Saving item in database
                if (saveTo):
                    self.db.addItem(newItem, saveTo)
                modifiedResult.append(newItem)
            
            # Appending result to all previous search results
            self.results += modifiedResult
        
        print("Done!")
        return self.results
    
        
    # Retrueve info about specific video(s)
    def videos(self, id, fields=False):
        searchResult = self.youtube.videos().list(
            part='snippet,statistics',
            fields='items(snippet(channelId,description,tags),statistics)' if fields else '*',
            id=id
        ).execute()

        return searchResult['items']
    
    
    #iterate through channel result to get country that channel user resides in
    def channelToCountry(self, listOfVideoIDs, collectionName, csvName):
        channelIDs = []
        listOfDicts = []
        #get all channelIDs from videoIDs
        for ID in listOfVideoIDs:
            video_result = self.videos(ID)
            for field in video_result:
                channelIDs.append(field['snippet']['channelId'])     
        
        #get countries from channelIDs
        countryDict = {}
        for channelId in channelIDs:
            result = self.youtube.channels().list(part = 'snippet', id = channelId ).execute()
            for field in result['items']:
                country = field['snippet'].get('country', None)
            if country != None:
                countryDict = {
                    'channelID' : channelId,
                    'country': country
                }
                listOfDicts.append(countryDict)
            else: pass
        print(listOfDicts)
        
        
        #append the country to a csv file
        fields = ['channelID', 'country'] 
        #csvName = 'user locations for ' + collectionName + ' wild'
        with open(csvName, 'w') as user_locations_csv:
            csvName = csv.DictWriter(user_locations_csv, fieldnames = fields)
            csvName.writeheader()
            for item in listOfDicts:
                csvName.writerow(item)
        print('done! Check in your jupyter files for a .csv file with the name you entered')

        #return csvName
        #return channelIDs

    
