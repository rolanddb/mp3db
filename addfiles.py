root_dir = "/media/hdd1/data/Music/Downloads/Compleet"
import os
import mediafile
from couchdbkit import *


server = Server('http://admin:admin@localhost:5984') 
db = server.get_or_create_db("songs") 

class Song(Document):
	filename = StringProperty()
	artist = StringProperty()
	title = StringProperty()
	year = IntegerProperty()
	length = FloatProperty()
	bitrate = IntegerProperty()
	filesize = IntegerProperty()

# associate Song class to the db
Song.set_db(db)

def mp3_files(root):
  # this is a generator that will return mp3 file paths within given dir
  for f in os.listdir(root):
      fullpath = os.path.join(root,f)
      if os.path.isdir(fullpath) and not os.path.islink(fullpath):
          for x in mp3_files(fullpath):  # recurse into subdir
              yield x
      else:
          if fullpath[len(fullpath)-3:] == 'mp3':
            yield fullpath

for f in mp3_files(root_dir):
  f = f.decode('utf-8') # fix some weird encoding
#  filesiz=str(os.path.getsize(f))
  print f

  #get id info
  m=mediafile.MediaFile(f)

  # create new tracklist object
  song = Song(filename = f,
      artist=m.artist,
      title=m.title,
      year=m.year,
      length=m.length,
      bitrate=m.bitrate,
      filesize=os.path.getsize(f))
      
  song.save()
