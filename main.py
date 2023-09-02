from weighted_hits import *
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib as plt
from sklearn.preprocessing import minmax_scale

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    return np.exp(x) / np.sum(np.exp(x), axis=0)

w = [7,9,6,13,5,11]
# w = [(float(i)-np.mean(w))/np.std(w) for i in w]
# w = softmax(w)
# w = minmax_scale(w)


edges = [("BankAmerica","CreditFrance",dict(weight=w[0])),
         ("CreditFrance","USAPLC",dict(weight=w[1])),
         ("CreditFrance","GermanBank",dict(weight=w[2])),
         ("USAPLC","GermanBank",dict(weight=w[3])),
         ("USAPLC","DutchInv",dict(weight=w[4])),
         ("GermanBank","DutchInv",dict(weight=w[5]))]

G = nx.DiGraph()
G.add_edges_from(edges)
# weighted_hits(G, weight='weight')
nx.hits(G)[0]

nx.pagerank(G)

edges = [("A","B"),
         ("A","D"),
         ("B","C"),
         ("D","C"),
         ("B","E"),
         ("B","F"),
         ("D","G"),
         ("G","H"),
        #  ("H","A"),
         ("1","2"),
         ("1","3"),
         ("1","4"),
         ("4","A")]

G = nx.DiGraph()
G.add_edges_from(edges)
nx.hits(G)[0]
