from .Youtube.youtube import YouTube
from .Twitter.twitter import Twitter
from .EmbedTweet.embedtweet import EmbedTweet
from .iNaturalist.inaturalist import iNaturalist
from .Flickr.flickr import Flickr
from .Database.database import Database
#from .Database_Beta.database_beta import Database_Beta

assert all((Flickr, iNaturalist, YouTube, Twitter, Database))
#assert all((Flickr, iNaturalist, YouTube, Twitter, Database_Beta))

name = "wildbook_social"