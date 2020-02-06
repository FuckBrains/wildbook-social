from .Youtube.youtube import YouTube
from .Twitter.twitter import Twitter
from .Database.database import Database
from .iNaturalist.inaturalist import iNaturalist

assert all((iNaturalist, YouTube, Twitter, Database))

name = "wildbook_social"
