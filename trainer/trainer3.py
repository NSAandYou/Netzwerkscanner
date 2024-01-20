#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  2 19:35:22 2024

@author: kilian
"""

from scapy.all import rdpcap
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
import numpy as np
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler
import pickle
import time
import csv
import io
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier

premade_mac_cpe_map = {}

with io.open("../mac_cpe_map.csv",'r', encoding='utf-8') as data:
   for line in csv.reader(data, delimiter=','):
       premade_mac_cpe_map[line[0]] = line[3]

MAX_FEATURE_COLUMNS = 600
SAMPLING = "over"
SAMPLING_STRATEGY = "minority"
SAMPLING = "under"
SAMPLING_STRATEGY = "majority"
SAMPLE_MAX_COUNT = 20



def sample_max_count(np_array, print_details=False) -> int:
    values, counts = np.unique(np_array, return_counts=True)
    counts_sum = sum(counts)
    max_relative: int = 0
    
    if print_details:
        print("Klassenhäufigkeit Absolut:")
        for index, value in enumerate(values):
            print(f"\t{value}: {counts[index]}")
        
    if print_details:
        print("Klassenhäufigkeit Relativ:")
    for index, value in enumerate(values):
        relative = (counts[index]/counts_sum)*100
        if relative > max_relative:
            max_relative = relative
        if print_details:
            print(f"\t{value}: {relative:.2f}%")
        
    return max_relative

def better_accuracy(test, pred, print_details=False) -> float:
    arrays = {}
    for key in np.unique(test):
        arrays[key] = []
    for index in range(test.shape[0]):
        arrays[test[index][0]].append(test[index][0] == pred[index])
        
    sum_right = 0
    sum_total = 0
    for key, value in arrays.items():
        right = 0
        total = len(value)
        for index in range(total):
            index += 1
            if index < 20:
                ##print(value[0:index], right, total)
                if value[0:index].count(True) / len(value[0:index]) > 0.5:
                    right += 1
                    ##print("Right")
            else:
                if value[index-20:index].count(True) / len(value[index-20:index]) > 0.5:
                    right += 1
        
        sum_right += right
        sum_total += total
        if print_details:
            print(f"Simple Accuracy class {key}: {value.count(True)/total}")
            print(f"Better Accuracy class {key}: {right/total}")
            print()
    ##print(sum_right, sum_total)
    return(sum_right/sum_total)
                
    
    
## question for pcap name
file_name = input("Dateiname ohne .pcap oder Pfad: ")

##constants
columns_range = range(MAX_FEATURE_COLUMNS)


## Load Data and create raw byte array
start = int(time.time())
print("Lade PCAP-File")
pcaps = [pcap for pcap in rdpcap(f"../pcaps/{file_name}.pcap") if 'Ether' in pcap]


print(f"{int(((time.time()-start)))}: Dateneingabe Label")
mac_list = set([pkt['Ether'].src for pkt in pcaps])
mac_cpe_map = {}
for mac in mac_list:
    if ":".join(mac.split(":")[3:6]).lower() in premade_mac_cpe_map:
        mac_cpe_map[mac] = premade_mac_cpe_map[":".join(mac.split(":")[3:6]).lower()]
        print(f"CPE für {mac}: {mac_cpe_map[mac]}")
    else:
        ##mac_cpe_map[mac] = input(f"CPE für {mac}: ")
        mac_cpe_map[mac] = ""
        print(f"CPE für {mac}: DELETE")
   
print(f"{int(((time.time()-start)))}: Unbekannte Daten aussortieren")
pcaps = [pcap for pcap in pcaps if mac_cpe_map[pcap['Ether'].src] != ""]
print(f"Gelabelte Pakete: {len(pcaps)}")


print(f"{int(((time.time()-start)))}: Feature und Label Array erstellen")
features = np.zeros(shape=((len(pcaps), MAX_FEATURE_COLUMNS)), dtype=np.int8)
labels = np.zeros(shape=((len(pcaps), 1)), dtype='S17').astype(object)


print(f"{int(((time.time()-start)))}: Daten Labeln & Features -> einheitliche Länge")
for index, pcap in enumerate(pcaps):
    pcap_bytes = bytes(pcap)
    if len(pcap_bytes) > MAX_FEATURE_COLUMNS:
        pcap_bytes = pcap_bytes[:MAX_FEATURE_COLUMNS]
    features[index, 0:len(pcap_bytes)] = np.frombuffer(pcap_bytes, np.int8)
    labels[index, 0] = pcap['Ether'].src

for key in mac_cpe_map:
    labels[labels==key] = mac_cpe_map[key]
    
    
print(f"{int(((time.time()-start)))}: Unfaire Bereiche Löschen")
features = np.delete(features, [6,7,8,9,10,11,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37],axis=1)
    

print(f"{int(((time.time()-start)))}: Traings und Testdaten erstellen")
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.05, random_state=1)

print(f"{int(((time.time()-start)))}: Over-/Undersampling")
if(SAMPLING=="under"):
    sampler = RandomUnderSampler(sampling_strategy=SAMPLING_STRATEGY, random_state=1)
else:
    sampler = RandomOverSampler(sampling_strategy=SAMPLING_STRATEGY, random_state=1)
while(sample_max_count(y_train)>SAMPLE_MAX_COUNT):
    X_train, y_train = sampler.fit_resample(X_train, y_train)
sample_max_count(y_train,True)
print(f"Gelabelte Traings Pakete gesammt: {X_train.shape[0]}")


print(f"{int(((time.time()-start)))}: Entscheidungsbaum trainieren")
clf_dtc = DecisionTreeClassifier(criterion='entropy', class_weight='balanced', random_state=1)
clf_dtc = clf_dtc.fit(X_train,y_train)
pickle.dump(clf_dtc, open(f"../classifier/{file_name}_{MAX_FEATURE_COLUMNS}_{SAMPLING}_{SAMPLING_STRATEGY}.dtc", 'wb'))
##clf = pickle.load(open(f"../classifier/{file_name}_{MAX_FEATURE_COLUMNS}.dtc", 'rb'))


print(f"{int(((time.time()-start)))}: Accuracy abschätzen")
y_pred = clf_dtc.predict(X_test)
print("Simple Accuracy total:",metrics.accuracy_score(y_test, y_pred))
print("Better Accuracy total:",better_accuracy(y_test, y_pred, True))

print(f"{int(((time.time()-start)))}: Feature importance abschätzen")
DTFI = [[index, value*100] for index, value in enumerate(clf_dtc.feature_importances_) if value > 0.0001]
done = False
length = len(DTFI)
while not done:
    done = True
    for i in range(length-1):
        if DTFI[i][1] < DTFI[i+1][1]:
            temp = DTFI[i]
            DTFI[i] = DTFI[i+1]
            DTFI[i+1] = temp
            done = False
            
for a in DTFI:
    if a[0] > 5:
        a[0] += 6
    if a[0] > 21:
        a[0] += 16
        
for array in DTFI:
    print(f"Byte {array[0]}: {array[1]:.2f}%")
 
    
print(f"{int(((time.time()-start)))}: Random Forest trainieren")
clf_rfc = RandomForestClassifier(criterion='entropy', class_weight='balanced',  random_state=1)
clf_rfc = clf_rfc.fit(X_train,y_train)
pickle.dump(clf_rfc, open(f"../classifier/{file_name}_{MAX_FEATURE_COLUMNS}_{SAMPLING}_{SAMPLING_STRATEGY}.rfc", 'wb'))

print(f"{int(((time.time()-start)))}: Accuracy abschätzen")
y_pred = clf_rfc.predict(X_test)
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
print("Better Accuracy total:",better_accuracy(y_test, y_pred, True))
    
print(f"{int(((time.time()-start)))}: Neuronales Netz trainieren")
clf_mlp = MLPClassifier(hidden_layer_sizes=(578, 300, 578, 300), max_iter=1000, random_state=1)
clf_mlp = clf_mlp.fit(X_train,y_train)
pickle.dump(clf_mlp, open(f"../classifier/{file_name}_{MAX_FEATURE_COLUMNS}_{SAMPLING}_{SAMPLING_STRATEGY}.mlp", 'wb'))

print(f"{int(((time.time()-start)))}: Accuracy abschätzen")
y_pred = clf_mlp.predict(X_test)
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
print("Better Accuracy total:",better_accuracy(y_test, y_pred, True))


print(f"{int(((time.time()-start)))}: Fertig")
