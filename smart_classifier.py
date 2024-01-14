import pickle
import numpy as np

MAX_FEATURE_COLUMNS = 600


def __init__(clf_file_path: str):
    global clf
    clf = pickle.load(open(clf_file_path, 'rb'))


def predict(pkt):
    features = np.zeros(shape=MAX_FEATURE_COLUMNS, dtype=np.int8)
    pkt_bytes = pkt.get_raw_packet()
    if len(pkt_bytes) > MAX_FEATURE_COLUMNS:
        pkt_bytes = pkt_bytes[:MAX_FEATURE_COLUMNS]
    features[0:len(pkt_bytes)] = np.frombuffer(pkt_bytes, np.int8)
    features = np.delete(features, [6, 7, 8, 9, 10, 11, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37])
    return clf.predict(features.reshape(1, -1))[0]
