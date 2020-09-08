## Wildbook Social Media Bias Research

This repository contains classes to work with Youtube, Twitter, Flickr and iNaturalist APIs inorder to collect data
to help monitor wildlife populations. In using this data, it is important to analyze any potential biases
behind the data collect by gaining insight on the user base. 

In this repository you will find the following:

**playground** folder contains code to query our database, manually filter our data, and display analytics for each platform on the data filtered so far. Each social media platform (YouTube, Flickr, iNaturalist, and Twitter) has their own playground. Additionally, you will find within this folder a **Database** playground, which is used to generate analytics for species across each platform and compare effectively. 

**wildbook-social** folder contains the scripts responsible for loading the api and collecting data. Within this folder you will find a folder for each platform and their respective API endpoint queries, as well as an additional **Database** folder. This **Database** folder contains the script responsible for handling operations dealing with species collections in MongoDB.

Analytics collected so far include:
  *user-encounter location maps
  *posts per week (with and without a moving avg filter)
  *distribution of difference in user-encounter location distances 
  *time delay between successive posts
  
