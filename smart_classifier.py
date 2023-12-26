import pickle
from sklearn.tree import DecisionTreeClassifier
import pandas as pd

clf: DecisionTreeClassifier


def __init__():
    global clf
    clf = pickle.load(open("/home/kilian/Uni/Projektseminar/classifier/liszt_1514.dtc", 'rb'))


def predict(pkt):
    pkt_bytes = pkt.get_raw_packet()
    raw_data_frame = {}
    for column_index in range(1514):
        if len(pkt_bytes) > column_index:
            raw_data_frame[f'B_{column_index}'] = [pkt_bytes[column_index]]
        else:
            raw_data_frame[f'B_{column_index}'] = [0]
    return clf.predict(pd.DataFrame(raw_data_frame))[0]
