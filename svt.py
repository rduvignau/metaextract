from read import *
from learner import *
from test import *

from urllib.request import urlopen
import json

### utils

def genre_list_to_str(genre_list):
    return '-'.join(map(str,sorted([genres2id[g] for g in genre_list])))

### learner

# can change db to reflect that in the code
class SvtTestSeriesLearner(TestLearner):
    def _gen_class(self, trace):
        return trace[2]

class SvtTestGenresLearner(TestLearner):
    def _gen_class(self, trace): # uses only the first genre in the list
        return trace[3][0]

class SvtTestOneVersusAllGenresLearner(TestOneVersusAllGenresLearner):
    def __init__(self, genreID, **kwargs):
        super(TestOneVersusAllGenresLearner, self).__init__(**kwargs)
        self.genre = genreID
        
    def _gen_class(self, trace):
        return self.genre in trace[3]

class SvtTestAllVsAllGenresLearner(TestAllVsAllGenresLearner): 
    def _gen_class(self, trace): 
        return '-'.join(trace[3])

### Utils to generate the database CSV and binary files ###

"""
    svt_genres.csv: retrieve all genres used in the svt database.
    Format: genre_index, genre_name, genre_svt_code
"""

def generate_genre_files(svt_database="svtplay_db.csv",
                         outputfilename="svt_genres.csv"):
    svt_db = readcsv(svt_database)                          #103531 fingerprints
    svt_ids = list(set([trace[2] for trace in svt_db]))     #20736 IDs
    svt_genres = defaultdict(int)
    i = 0

    for svt_id in svt_ids:
        i += 1
        print(i, svt_id, end=' ')
        url = f"https://api.svt.se/video/{svt_id}"
        try:
            response = urlopen(url)
            print("response received")
            data_json = json.loads(response.read())
            genres = data_json["mmsStatistics"]["svt_taggar"]
            for genre in genres.split(','):
                svt_genres[genre] += 1
        except:
            print("id not found")

    genres = sorted([(svt_genres[g], g) for g in svt_genres], reverse=True)
    writecsv(outputfilename, [[i, genres[i][1], genres[i][0]] for i in range(len(genres))])

"""
    svt_video_genres.csv: associate each entry in the svt database to a genre list.
    Format: video_ID, genre_index_1-genre_index_2-...-genre_index_n
"""

def generate_fingerprint_summary(svt_database="svtplay_db.csv",
                                 svt_genres="svt_genres.csv",
                                 outputfilename="svt_video_genres.csv"):
    svt_db = readcsv(svt_database)
    genres = readcsv(svt_genres)
    
    svt_ids = list(set([trace[2] for trace in svt_db]))
    genres2id = {}
    for j, g, nb in genres:
        genres2id[g] = int(j)

    svt_video_genres = []

    i = 0
    for svt_id in svt_ids:
        i += 1
        print(i, svt_id, end=' ')
        url = f"https://api.svt.se/video/{svt_id}"
        try:
            response = urlopen(url)
            data_json = json.loads(response.read())
            svt_genres = data_json["mmsStatistics"]["svt_taggar"].split(',')
            #print(svt_genres)
            print(f"response received, {len(svt_genres)} genre(s) found")
            genre_tag = '-'.join(map(str,sorted([genres2id[g] for g in svt_genres])))
            svt_video_genres.append([svt_id, genre_tag])
        except:
            print("id not found")

    writecsv(outputfilename, svt_video_genres)

"""
    svt_db.bin: dump of the filtered database with 50 genres
    50 genres = each genre has at least 1000 fingerprints (~1%)
    Kept 82650 fingerprints in total (about 80%)
"""

def generate_fingerprint_database(svt_database="svtplay_db.csv",
                                  svt_video_genres="svt_video_genres.csv",
                                  outputfilename="svt_db.bin", nb_genres=50):
    svt_video_genres = readcsv(svt_video_genres)

    # filter genres to keep only the most represented ones + the videos with exactly 3-4 genres
    videoid2genres = {}
    for video_id, genres in svt_video_genres:
        genre_list = [g for g in genres.split('-') if int(g) < nb_genres]
        if 3 <= len(genre_list) <= 4:
            videoid2genres[video_id] = genre_list

    svt_db = readcsv(svt_database)
    svt_db_filtered = []

    # Keep only fingerprints with exactly 5 traces (99% of them)
    id2nb_fingerprints = defaultdict(int)
    for title, duration, video_id, bps, resolution, *fingerprint in svt_db:
        id2nb_fingerprints[video_id] += 1

    i = 0
    for title, duration, video_id, bps, resolution, *fingerprint in svt_db:
        #encoding = int(bps[-3]))
        series = title.split(':')[0]

        if (id2nb_fingerprints[video_id] == 5 and
            video_id in videoid2genres and series != title):
            svt_db_filtered.append((i,title,series,videoid2genres[video_id],fingerprint))

        i = i+1
            
    savedump(svt_db_filtered, outputfilename)

"""    
    NB: Most popular genre "barn" covers only 7.5% of the traces
"""

if __name__ == "__main__":
    if not exists("svt_genres.csv"):
        print("Generating svt genres...")
        generate_genre_files()
        print("done.")

    if not exists("svt_video_genres.csv"):
        print("Generating svt fingerprint summary...")
        generate_fingerprint_summary()
        print("done.")

    if not exists("svt_db.bin"):
        print("Generating svt binary database...")
        generate_fingerprint_database()
        print("done.")

    print("All necessary files have been generated.")
