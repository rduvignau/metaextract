from collections import defaultdict
import pickle
import urllib.parse, urllib.request
import json
import csv

from os.path import join, exists
from os import mkdir

# serialization & reading/writing utils

def savedump(myobj, filename):
    with open(filename,'wb') as f:
        pickle.dump(myobj, f)

def loaddump(filename):
    with open(filename,'rb') as f:
        return pickle.load(f)

def readcsv(filename):
    with open(filename,"r") as csvfile:
        return [row for row in csv.reader(csvfile, delimiter=',')]

def writecsv(filename, data):
    with open(filename,"w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        for row in data:
            csvwriter.writerow(row)

#### database functions #####

"""
    WARNING, the full dataset might not be loadable in memory (can be too big):
    netflix_full 42000 titles, 330525 video-extracts, 193955489 "windows"
"""

# you can stream the database not to have to put it in memory that way
def stream_db(filename="codaspy_full.txt"):
    with open(filename,"r") as file:
        for line in file.readlines():
            record = line.split('\t')
            yield (record[0], int(record[1]),
                   [int(window) for window in record[2].split(',') if window !='\n'])

# the full database takes 7.5GB in main memory
def load_db_dict(database):
    data = defaultdict(dict)
    for (title, encoding, list_of_windows) in database:
        data[title][encoding] = list_of_windows
    return data

# save database into binary dump
def save_database():
    data = list(stream_db("codaspy_full.txt"))
    savedump(data, "db_full.bin")
    return data

#### titles, genres, series utilities #####

"""
    video_titles.csv: (encoding are in kbits per second, multiply by 125 to get in bytes/s)
    Format: full_title, seconds_recorded, encoding_1, ..., encoding_n
"""

def extract_video_titles(database):
    data = defaultdict(list)
    for title, encoding, fingerprint in database:
        data[title].append(encoding)
    writecsv("video_titles.csv", [(title, *sorted(data[title])) for title in data])

#make some exception to reduce number of titles
def is_series_with_column(name):
    return any(s in name for s in ["30 for 30", "My Little Pony", "NOVA"
                                   "America's Funniest Home Videos",
                                   "Barney", "Bob the Builder",
                                   "Disney Animation Collection", "Monster High",
                                   "Trailer Park Boys"])

def parse_title(title):
    name = title.split("/Season")
    name = title.split("/Series") if len(name) == 1 else name
    name = title.split("/Collection") if len(name) == 1 else name

    if ':' in name[0] and is_series_with_column(name[0]):
        i = name[0].index(':')
        return name[0][:i], 0, name[0][i+1:]

    title = name[0].replace('"', "'")
    season = name[1].split(" : Episode ")[0] if len(name) > 1 else 0
    episode = name[1].split(" : Episode ")[1] if len(name) > 1 else 0

    return title, season, episode

def extract_series_title(title):
    return parse_title(title)[0]

# Retrieve genre from themoviedb API (provide your own API key to it)
def retrieve_genres(title, api_key):
    base = f"https://api.themoviedb.org/3/search/multi?api_key={api_key}"
    options = f'&language=en-US&query={urllib.parse.quote(title)}&page=1'
    with urllib.request.urlopen(base+options) as url:
        data = json.loads(url.read().decode())
        if data['results']:
            best_result = data['results'][0]
            if 'genre_ids' in best_result:
                return best_result['genre_ids']
            return []
        elif ':' in title: # try removing what's after ':'
            return retrieve_genres(title[:title.index(':')], api_key)    
        return [] # give up
    
"""        
    series_or_movies_titles_genres.csv: Keep only 1 entry per series/movie.
    Format: title, number_of_seasons, total_number_of_episodes, genre_1, ..., genre_n
"""

#this is relatively long as it queries ~4500 the web api to get the genre of titles
def extract_series_titles_and_download_genres(database,
                                              outputfile="series_or_movies_titles_genres.csv"):
    api_key = input("Type MovieDB API key:")

    series = defaultdict(int)
    seasons = defaultdict(set)
    episodes = defaultdict(set)
    for title, encoding, fingerprint in database:
        name, season, episode = parse_title(title)
        series[name] += 1
        seasons[name].add(season)
        episodes[name].add(episode)
       
    all_series_films = []
    for serie in series:
        genres = retrieve_genres(serie, api_key)
        all_series_films.append((serie,len(seasons[serie]),len(episodes[serie]),*genres))

    writecsv(outputfile, all_series_films)

def genres_dic():
    # load genres into a dictionary: "title" -> list of genres
    titlegenres = readcsv("series_or_movies_titles_genres.csv")
    genres = {}
    for line in titlegenres:
        genres[line[0]] = line[3:]
    return genres

def seasons_epsiodes_dic():
    # load #seasons #episodes into a dictionary: "title" -> (#seasons,#epsisodes)
    titlesp = readcsv("series_or_movies_titles_genres.csv")
    dic = {}
    for line in titlesp:
        dic[line[0]] = (int(line[1]),int(line[2]))
    return dic

"""        
    series_titles_genres.csv: Keep only series.
    Format: series_title, number_of_seasons, total_number_of_episodes, genre_1, ..., genre_n
"""

def extract_only_series():
    titles = readcsv("series_or_movies_titles_genres.csv")
    #total_number_of_episode is 1, then it's more a movie than a serie!
    series = [title for title in titles if int(title[2]) > 1]
    writecsv("series_titles_genres.csv", series)

#### build csv summaries #####

"""        
    fingerprints_summary.csv: Summary of the fingerprint database.
    Format: trace_ID, title -- encoding, genre_1, ..., genre_n
"""

def build_summary(database):
    traceID = 1
    genres = genres_dic()
    with open("fingerprints_summary.csv", "w") as f:
        for title, encoding, fingerprint in database:
            short_title = parse_title(title)[0]

            # some traces do not have any genres (couldn't find any in the online DB)
            trace_class = genres[short_title] if short_title in genres else []

            # print one line per trace using unique ID
            print(traceID, f'"{title} -- {encoding}"', *trace_class, sep=',', flush=True, file=f)
            
            traceID += 1

"""        
    fingerprints_info.csv: Meta-information for each fingerprint.
    Format: trace_ID, title, number_of_seasons, total_number_of_episodes, is_series?
"""

def gen_fingerprints_info_file():
    data = readcsv("fingerprints_summary.csv")
    sep = seasons_epsiodes_dic()
    with open("fingerprints_info.csv", "w") as f:
        for line in data:
            traceID, titleAndEncoding = int(line[0]), line[1]
            title = titleAndEncoding.split(" -- ")[0]
            short_title = parse_title(title)[0]
            seasons, episodes = sep[short_title]
            is_series = (seasons+episodes)>2
            print(traceID, f'"{title}"', seasons, episodes, is_series, sep=',', flush=True, file=f)
        

"""
    Smaller 10k fingerprint database (just as proof of concept for now; 3% of the original dataset)
    20 datapoints (eg features) = 1 min of video
"""
def clean_and_save_summary():
    summary = readcsv("fingerprints_summary.csv")
    summary2 = []
    for trace in summary:
        title, encoding = trace[1].split(' -- ')
        if "The Good Son: The Life of Ray" in title:
            title = 'The Good Son: The Life of Ray "Boom Boom" Mancini'
        summary2.append((int(trace[0])-1, title, encoding, trace[2:]))
    savedump(summary2, "summary.bin")
    return summary2

def stream_trace_and_fingerprint(data):
    for trace_id, trace_title, trace_encoding, trace_genres in loaddump("summary.bin"):
        fingerprint = data[trace_title][int(trace_encoding)]
        yield trace_id, trace_title, trace_encoding, trace_genres, fingerprint
    
def save_small_database(database, summary):
    data = load_db_dict(database)
    
    # keep only single-genre videos with exact 9 video encodings (13703 titles)
    titles = set(trace_title for trace_id, trace_title, *_ in summary)
    filtered_titles = set(title for title in titles if len(data[title].keys()) == 9)

    # only keep series with 25+ episodes -- 31852 traces (series) --> 11016 traces
    video_titles = readcsv("series_or_movies_titles_genres.csv")
    long_series = set(title[0] for title in video_titles if int(title[2]) > 25)
    filtered_db = [(trace_id,trace_title,int(trace_enc),[trace_genres[0]],
                    data[trace_title][int(trace_enc)])
                   for trace_id, trace_title, trace_enc, trace_genres in summary
                    if (trace_title in filtered_titles)
                     and (parse_title(trace_title)[0] in long_series) and len(trace_genres) == 1]

    savedump(filtered_db, "db.bin")

def save_shorter_database(k=150): # only keep the first k datapoints in each fingerprint
    summary = readcsv("fingerprints_summary.csv")
    data = loaddump("db_full.bin")
    for trace in summary:
        title, encoding = trace[1].split(' -- ')
        if "The Good Son: The Life of Ray" in title:
            db.append(data['The Good Son: The Life of Ray "Boom Boom" Mancini'][int(encoding)][:150])
        else:
            db.append(data[title][int(encoding)][:k])
    savedump(db, f"db{k}.bin")

### default execution
      
if __name__ == "__main__":
    if not exists("db_full.bin"):
        if not exists("codaspy_full.txt"):
            print("Usage: place original 'codaspy_full.txt' in same folder.")
        else:
            print("Generating fingerprint database... (can take some time)")
            data = save_database()
            print("done.")
    else: #preloaded database (~15-20sec to load in memory)
        data = loaddump("db_full.bin")

    if not exists("video_titles.csv"):
        print("Generating video titles...")
        extract_video_titles(data)
        print("done.")

    if not exists("series_or_movies_titles_genres.csv"):
        print("Generating series/film genres...")
        extract_series_titles_and_download_genres(data)
        print("done.")

    if not exists("fingerprints_summary.csv"):
        print("Generating fingerprint summary...")
        build_summary(data)
        summary = clean_and_save_summary()
        print("done.")
    else:
        summary = loaddump("summary.bin")
        
    if not exists("db.bin"):
        print("Generating small database...")
        save_small_database(data, summary)
        print("done.")
    
    print("All necessary files have been generated.")
    
        
