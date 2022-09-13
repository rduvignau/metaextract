from learner import *
from os.path import join, exists
from os import mkdir
from math import ceil
from random import shuffle, sample

"""
    Meta-information extraction on a database divided into chunks.
    Learn only a database where each video has an unknown number of traces
    By default, roughly 80% of the traces are used as training set and the rest as testing set
"""

class ChunkLearner(TestLearner):
    def _gen_video_indexes(self):
        self.videos = {}
        for i in range(len(self.db)):
            trace_id, video_title, _, _, _ = self.db[i]
            if video_title in self.videos:
                self.videos[video_title] = (self.videos[video_title][0], i)
            else:
                self.videos[video_title] = (i, i)
        

    def _train_test_split_function(self, percentage=80):
        self.trainingIDs, self.testingIDs = [], []
        
        for start_id, end_id in self.videos.values():
            video_IDs = list(range(start_id, end_id))
            split_point = int(ceil(len(video_IDs)*percentage/100))

            self.trainingIDs.extend(video_IDs[:split_point])  # at least percentage% of the traces
            self.testingIDs.extend(video_IDs[split_point:])   # can be empty

    def learn(self):
        self._gen_video_indexes()
        self._train_test_split_function()
        self._generate_training_samples()
        self._generate_training_classes()
        self.clf = svm.SVC(probability=True)                # to be able to access predict_proba
        self.clf.fit(self.X_train, self.Y_train)

    def test(self):
        self.learn()
        self._generate_testing_samples()
        Y_pred = self.clf.predict(self.X_test)
        self._generate_testing_classes()
        nb_correct = sum(truth == predicted for truth, predicted in zip(self.Y_test, Y_pred))
        accuracy = nb_correct/len(self.testingIDs)
        return float(f'{accuracy:.3f}')


class ChunkSeriesLearner(ChunkLearner):
    def _gen_class(self, trace):
        return extract_series_title(trace[1])

class ChunkAllVsAllGenresLearner(ChunkLearner): 
    def _gen_class(self, trace): 
        return '-'.join(sorted(trace[3]))

    
class TestChunkAllVsAllGenresLearner(ChunkLearner): 
    def _gen_class(self, trace): 
        return '-'.join(sorted(trace[3]))

    def number_of_genres(self):
        return len(set(self._gen_class(trace) for trace in self.db))
        
"""
    Build a full database learner by training indepedent models on smaller chunks
    When predicting the output for a trace, return the class from the chunks with the highest score
"""
class TestFullDBLearner():
    def precompute_trained_models(learner_class=ChunkLearner, nb_chunks=30, start_chunk=0,
                                  start=0, end=30, suffix="videos",
                                  db_filepath="dbchunks", model_filepath="chunkmodels"):
        folder = f"{model_filepath}-{nb_chunks}-{end*4}-{suffix}"
        if not exists(folder):
            mkdir(folder)
        for i in range(start_chunk, nb_chunks):
            cklearner = learner_class(join(f"{db_filepath}-{nb_chunks}", f"db{i}.bin"),
                                      start, end)
            cklearner.learn()
            savedump(cklearner, join(folder, f"ck{i}.bin"))

    # default: use precomputed models
    def __init__(self, nb_chunks=30, start=0, end=30, suffix="videos", model_filepath="chunkmodels"):
        self.nb_chunks = nb_chunks
        self.start, self.end = start, end
        self.model_folder = f"{model_filepath}-{nb_chunks}-{end*4}-{suffix}"

    def predict(self, fingerprint):
        normalized_fpt = normalize_fingerprint(fingerprint,self.start-self.end)[self.start:self.end]
        predictions = []
        for i in range(self.nb_chunks):
            cklearner = loaddump(join(self.model_folder, f"ck{i}.bin"))
            predicted = cklearner.clf.predict([normalized_fpt])[0]
            probability = max(cklearner.clf.predict_proba([normalized_fpt])[0])
            predictions.append((probability,predicted))
        return max(predictions)[1]

    def test(self, nb_samples = 100):
        # generate all tested samples
        all_testing_data = []
        for i in range(self.nb_chunks):
            cklearner = loaddump(join(self.model_folder, f"ck{i}.bin"))
            cklearner._generate_testing_samples()
            cklearner._generate_testing_classes()
            all_testing_data.extend([(x,y) for x,y in zip(cklearner.X_test, cklearner.Y_test)])

        print(f"{len(all_testing_data)} test datapoints loaded")
        
        # randomize the testing set (for fairness)
        shuffle(all_testing_data)
        
        # test with only <nb_samples> samples
        test_samples = sample(all_testing_data, nb_samples)
        predictions = [[] for _ in range(len(test_samples))]

        print(f"{len(test_samples)} test samples selected")

        # compute prediction for each trained model
        for i in range(self.nb_chunks):
            cklearner = loaddump(join(self.model_folder, f"ck{i}.bin"))
            for j in range(len(test_samples)):
                x_test = test_samples[j][0]
                predicted = cklearner.clf.predict([x_test])[0]
                probability = max(cklearner.clf.predict_proba([x_test])[0])
                predictions[j].append((probability,predicted))
            print(f"predictions for chunk {i} done")
                
        # compute best prediction and accuracy
        nb_correct = 0
        for j in range(len(test_samples)):
            predicted = max(predictions[j])[1]
            if predicted == test_samples[j][1]:
                nb_correct += 1

        print(f"max of predictions computed for all {len(test_samples)} test samples")

        return round(nb_correct/nb_samples, 2)

"""
    split a large database into smaller chunks
"""

def split_database(nb_chunks=30, db_filepath="dbchunks"):
    data = loaddump("db_full.bin")
    folder = f"{db_filepath}-{nb_chunks}"
    if not exists(folder):
        mkdir(folder)
    
    # each trace is of the form: [trace_id, video_title, genres_list, fingerprint]
    size_of_chunk = len(data)//nb_chunks
    chunk_start = 0
    for chunk_id in range(nb_chunks-1):
        chunk_end = (chunk_id+1)*size_of_chunk-1
        trace = data[chunk_end]
        last_title = trace[2]
        while trace[2] == last_title:
            chunk_end += 1
            trace = data[chunk_end]
        savedump(data[chunk_start:chunk_end], join(folder, f"db{chunk_id}.bin"))
        chunk_start = chunk_end

    savedump(data[chunk_start:], join(folder, f"db{nb_chunks-1}.bin"))
    
### default execution
    
if __name__ == "__main__":
    if not exists("db_full.bin"):
        print("Run read.py first.")
    elif not exists(join("dbchunks-30","db0.bin")):
        split_database()            # Generate 30 chunks by default
        
    dblearner = TestFullDBLearner() # Use 30 chunks by default
    dblearner.test(100)             # Accuracy of 73%
