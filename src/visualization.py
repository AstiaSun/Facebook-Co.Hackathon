from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from bson.json_util import dumps
import base64
from io import BytesIO

def draw_piechart(jsn, column = 'area_id_old', grouping_threshold = 0.025):
    df = pd.read_json(jsn)
    fd = BytesIO()
    try:
        areas = df[column].apply(lambda x: str(base64.b64decode(x).decode('utf8')))
    except:
        areas = df[column]
    counts = areas.value_counts(normalize=True)
    #print(counts)
    other_count = 0
    for (index, count) in counts.iteritems():
        if (count < grouping_threshold):
            other_count = other_count + count
            counts.drop(labels=[index], inplace=True)
    other = pd.Series([other_count], index=['Інше'])
    counts = counts.append(other)
    f, ax = plt.subplots()
    ax.pie(counts.values, labels=counts.index.values.tolist(), autopct='%1.1f%%',
        shadow=True, startangle=90)
    ax.axis('equal')
    ax.legend(loc='best')
    plt.savefig(fd, format='png')
    return b"data:image/png;base64," + base64.b64encode(fd.getvalue())

def draw_hist(jsn, column = 'area_id_old', grouping_threshold = 0.025):
    df = pd.read_json(jsn)
    fd = BytesIO()
    try:
        areas = df[column].apply(lambda x: str(base64.b64decode(x).decode('utf8')))
    except:
        areas = df[column]

    print(areas[:5])
    counts = areas.value_counts(normalize=True)
    countsnonn = areas.value_counts(normalize=False)
    print(counts[:5])
    print(countsnonn[:5])
    other_count = 0
    for (index, count) in counts.iteritems():
        if (count < grouping_threshold):
            other_count = other_count + countsnonn[index]
            countsnonn.drop(labels=[index], inplace=True)
            counts.drop(labels=[index], inplace=True)
    other = pd.Series([other_count], index=['Інше'])
    countsnonn = countsnonn.append(other)
    f, ax = plt.subplots()
    print(countsnonn[:5])
    #ax.plot(countsnonn.index.values.tolist(), countsnonn, '|')
    ax.bar(x=range(len(countsnonn.values)), height=countsnonn.values, tick_label=countsnonn.index.values.tolist())
    ax.xaxis.set_tick_params(rotation=45)
    #ax.axis('equal')
    #ax.legend(loc='best')
    plt.savefig(fd, format='png')
    return b"data:image/png;base64," + base64.b64encode(fd.getvalue())
