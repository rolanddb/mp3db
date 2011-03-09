#root_dir = "/media/hdd1/data/Music/Downloads/Compleet"
root_dir = "/media/hdd2/data/download/soulseek"
echonest_catalog = "echonest_catalog.json"
import os
import mediafile
import simplejson as json
from couchdbkit import *
import uuid
from urllib import urlencode

server = Server('http://admin:admin@localhost:5984') 
db = server.get_or_create_db("songs") 

class EchonestSong(Document):
        item_id = StringProperty()
        song_name = StringProperty()
        artist_name = StringProperty()
	url = StringProperty()	
        
class Song(Document):
	id = StringProperty()
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

list = [] # for storing songs
for f in mp3_files(root_dir):
  f = f.decode('utf-8') # fix some weird encoding error
  print
  print
  print f
  f = urlencode(f) # be on the safe side

  try:

    #get id info
    m=mediafile.MediaFile(f)
    uid = str(uuid.uuid1())  

    # create new tracklist object
    song = Song(id = uid,
        filename = f,
        artist=m.artist,
        title=m.title,
        year=m.year,
        length=m.length,
        bitrate=(m.bitrate/1000), # convert to more common metric, eg 320 kbit
        filesize=os.path.getsize(f))

    if ((len(song.artist) > 0) and (len(song.title) > 0)):  # don't fill up the db with empty data, for now. todo: parse from file name or fingerprint.      
      song.save() # save in couch

      # now construct a summary for echonest
      echonestsong = EchonestSong(item_id = song.id, 
                                  song_name = song.title,
                                  artist_name = song.artist,
                                  url = f)

      list.append({"item":dict(echonestsong)})

  except:
    print "Error occured paring file " + f
    print "Continuing..."

# write summaries to file, to export to echonest catalog
jsonitems=json.dumps(list)
file = open(echonest_catalog, 'w')
file.write(jsonitems)
file.close()
#writetofile(jsonitems)
print jsonitems
