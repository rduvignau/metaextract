from learner import *
from chunk_learner import *
from svt import *
from os.path import join

"""
    Testing utils for the meta-information learner.
"""

svt_dbfile = join("svt","svt_db.bin")

durations = [12,16,20,24,28,32,40,60,80,120] # in seconds
durations_svt = [12,16,20,24,28,32,40,60,80,120,150,180,300] # in seconds

### Video Title Accuracies ###

def compute_accuracies_videos():    #using test database: 11016 different videos
    return [TestLearner(end=length//4).test() for length in durations]

#print(compute_accuracies_videos())
video_accuracy = [0.007, 0.066, 0.207, 0.375, 0.529, 0.621, 0.779, 0.882, 0.953, 0.998]

def compute_accuracies_videos_svt():
    return [TestLearner(dbfilename=svt_dbfile, end=length//4).test(4,5) for length in durations_svt]

#print(compute_accuracies_videos_svt())
video_accuracy_svt = [0.015, 0.028, 0.056, 0.116, 0.179, 0.25, 0.381, 0.642, 0.755, 0.845, 0.879, 0.897, 0.918]

### Series Accuracies ###

def compute_accuracies_series():    #using test database: 29 different series    
    return [TestSeriesLearner(end=length//4).test() for length in durations]

#print(compute_accuracies_series())
series_accuracy = [0.305, 0.368, 0.457, 0.536, 0.598, 0.647, 0.773, 0.912, 0.971, 0.991]

def compute_accuracies_series_svt():
    return [SvtTestSeriesLearner(dbfilename=svt_dbfile, end=length//4).test(4,5)
            for length in durations_svt]

#print(compute_accuracies_series_svt())
series_accuracy_svt = [0.106, 0.153, 0.192, 0.228, 0.273, 0.31, 0.411, 0.618, 0.747, 0.846, 0.877, 0.895, 0.919]

### Genres Accuracies ###

def compute_accuracies_genres():    #using test database: 7 single unique genres represented 
    return [TestGenresLearner(end=length//4).test() for length in durations]

def compute_accuracies_1vsAll_genres(g):    #using test database: 7 single unique genres represented 
    return [TestOneVersusAllGenresLearner(genreID=g,end=length//4).test() for length in durations]

def compute_precisions_1vsAll_genres(g):    #using test database: 7 single unique genres represented 
    return [TestOneVersusAllGenresLearner(genreID=g,end=length//4).test_apr()[1] for length in durations]

def compute_recalls_1vsAll_genres(g):    #using test database: 7 single unique genres represented 
    return [TestOneVersusAllGenresLearner(genreID=g,end=length//4).test_apr()[2] for length in durations]

#print(compute_accuracies_genres())
genres_accuracy = [0.604, 0.627, 0.699, 0.732, 0.773, 0.819, 0.859, 0.934, 0.96, 0.99]

def compute_accuracies_1vsAll_genres(g='0'):
    return [SvtTestOneVersusAllGenresLearner(dbfilename=svt_dbfile, genreID=g,
                                             end=length//4).test(4,5) for length in durations_svt]

# 'barn' genre 1 versus All accuracy levels (very fast!)
# "Return False" = 1-0.03684829478635829 = 96.3%
barn_accuracy_svt = [0.963, 0.979, 0.983, 0.983, 0.983, 0.985, 0.985, 0.987, 0.988, 0.991, 0.992, 0.993, 0.995]

def compute_accuracies_AllvsAll_genres_svt():
    return [SvtTestAllVsAllGenresLearner(dbfilename=svt_dbfile, end=length//4).test(4,5)
            for length in durations_svt]

#print(compute_accuracies_AllvsAll_genres_svt())
all_vs_all_accuracy_svt = [0.163, 0.186, 0.225, 0.259, 0.289, 0.325, 0.398, 0.535, 0.653, 0.775, 0.819, 0.857, 0.902]

genres = ['10759', '35', '99', '10762', '16', '18', '28']
def compute_accuracies_1vsAll_all_genres():    #using test database: compute 1-vs-all classification
    return [TestOneVersusAllGenresLearner(g, end=60).test() for g in genres]

def compute_confusion_matrix(length=60):    #using test database: 7 single unique genres represented 
    return TestGenresLearner(end=length//4).test_confusion_matrix()

### Encoding Accuracies (for testing purpose only) ###

encoding_accuracy = [0.092, 0.092, 0.092, 0.092, 0.092, 0.093, 0.094, 0.094, 0.094, 0.095]

"""
    Compute all tests of the paper.
"""

if __name__ == "__main__":
    print("Video accuracies (Netflix dataset):")
    compute_accuracies_videos()
    print("Video accuracies (SVT dataset):")
    compute_accuracies_videos_svt()
    
    print("Series accuracies (Netflix dataset):")
    compute_accuracies_series()
    print("Series accuracies (SVT dataset):")
    compute_accuracies_series_svt()

    print("Genres accuracies (Netflix dataset):")
    compute_accuracies_genres()
    print("Genres accuracies (SVT dataset):")
    compute_accuracies_AllvsAll_genres_svt()

    print("Compute confusion matrix (Netflix dataset; 1min of capture):")
    compute_confusion_matrix()
    
