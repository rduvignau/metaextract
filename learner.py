import numpy as np
from sklearn import svm
from read import *

"""
    Simple Proof-Of-Concept of a SVM meta-information extraction pipeline.
"""

def normalize_fingerprint(x0, minlength):
    xmin, xmax = min(x0), max(x0)
    return [-2+4*(x-xmin)/(xmax-xmin) for x in x0] + [0]*max(0,minlength-len(x0))

class TestLearner():
    def _load_database(self, dbfilename, start=0, end=None):
        # format of the database: id (0), title (1), encoding (2), genres (3), fingerprint (4)
        self.db = []
        if end:     # cut each fingerprint to only what is necessary
            for trace in loaddump(dbfilename):
                cut_trace = list(trace[:])
                cut_trace[4] = [int(segment) for segment in cut_trace[4][start:end]]
                self.db.append(cut_trace)

    def __init__(self, dbfilename="db.bin", start=0, end=15, N=None):
        self._load_database(dbfilename, start, end)
        self.db = self.db[:N] if N else self.db
        self.nb = len(self.db)
        self.start = start
        self.end = end
        self.length = end-start

    def _generate_training_set(self, j, k):    # j/k are used as training set
        self.trainingIDs = [n for i in range(0,self.nb,k) for n in range(i,min(i+j,self.nb))]

    def _generate_features(self, fingerprint):
        return fingerprint  # default: simply use the fingerprint itself as features

    def _gen_sample(self, fingerprint):
        return normalize_fingerprint(self._generate_features(fingerprint),self.length)

    def _generate_training_samples(self):
        self.X_train = [self._gen_sample(self.db[i][4][self.start:self.end])
                        for i in self.trainingIDs]

    def _gen_class(self, trace):
        # default: [Identification] here use video's title as name for each class
        return trace[1]
    
    def _generate_training_classes(self):
        self.Y_train = [self._gen_class(self.db[i]) for i in self.trainingIDs]

    def _generate_testing_set(self, j, k):      # use the last (k-j)/k as testing set
        self.testingIDs = [i for i in range(j,self.nb,k)]

    def _generate_testing_samples(self):
        self.X_test = [self._gen_sample(self.db[i][4][self.start:self.end])
                        for i in self.testingIDs]

    def _generate_testing_classes(self):
        self.Y_test = [self._gen_class(self.db[i]) for i in self.testingIDs]

    def learn(self, j=8, k=9):
        self._generate_training_set(j,k)
        self._generate_training_samples()
        self._generate_training_classes()
        self.clf = svm.SVC()
        self.clf.fit(self.X_train, self.Y_train)

    def predict(self, fingerprint):
        return self.clf.predict([self._gen_sample(fingerprint[self.start:self.end])])[0]

    def test(self, j=8, k=9):
        #each video has 9 encodings, use the first 8/9 = 89% as training set
        self.learn(j, k)
        #testing set -- use 1/9 = 11% of the encodings for the testing set
        self._generate_testing_set(j, k)

        self._generate_testing_samples()
        Y_pred = self.clf.predict(self.X_test)
        self._generate_testing_classes()
        nb_correct = sum(truth == predicted for truth, predicted in zip(self.Y_test, Y_pred))
        accuracy = nb_correct/len(self.testingIDs)

        return float(f'{accuracy:.3f}') # truncate accuracy level to 3 decimals

    def test_apr(self):
        self.learn()
        self._generate_testing_set(8,9)
        self._generate_testing_samples()
        Y_pred = self.clf.predict(self.X_test)
        self._generate_testing_classes()
        
        nb_correct = sum(truth == predicted for truth, predicted in zip(self.Y_test, Y_pred))
        true_positive = sum(truth == predicted == True for truth, predicted in zip(self.Y_test, Y_pred))
        true_negative = sum(truth == predicted == False for truth, predicted in zip(self.Y_test, Y_pred))
        false_positive = sum(truth == False and predicted == True for truth, predicted in zip(self.Y_test, Y_pred))
        false_negative = sum(truth == True and predicted == False for truth, predicted in zip(self.Y_test, Y_pred))

        accuracy = nb_correct / len(self.testingIDs)
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive > 0 else 0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative > 0 else 0

        return float(f'{accuracy:.3f}'), float(f'{precision:.3f}'), float(f'{recall:.3f}')

    def test_confusion_matrix(self):
        self.learn()
        self._generate_testing_set(8,9)
        self._generate_testing_samples()
        Y_pred = self.clf.predict(self.X_test)
        self._generate_testing_classes()

        all_outcomes = list(set(g for g in self.Y_test))
        matrix = {}
        for g in all_outcomes:
            matrix[g] = defaultdict(int)

        for truth, predicted in zip(self.Y_test, Y_pred):
            matrix[truth][predicted] += 1

        for g1 in all_outcomes:
            total = sum(matrix[g1][g2] for g2 in all_outcomes)
            for g2 in all_outcomes:
                matrix[g1][g2] = float(f'{matrix[g1][g2]/total:.3f}')
            
        return matrix
        
class TestSeriesLearner(TestLearner):
    def _gen_class(self, trace):
        return extract_series_title(trace[1])

class TestGenresLearner(TestLearner):
    def _gen_class(self, trace): # uses only the first genre in the list
        return trace[3][0]

class TestOneVersusAllGenresLearner(TestLearner):
    def __init__(self, genreID, **kwargs):
        super(TestOneVersusAllGenresLearner, self).__init__(**kwargs)
        self.genre = genreID
        
    def _gen_class(self, trace):
        return self.genre in trace[3]

class TestAllVsAllGenresLearner(TestLearner): 
    def _gen_class(self, trace): 
        return '-'.join(sorted(trace[3]))

    def number_of_genres(self):
        return len(set(self._gen_class(trace) for trace in self.db))



