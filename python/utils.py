# Import packages
import pandas as pd
from karateclub import Diff2Vec, Role2Vec, DeepWalk
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from tqdm import tqdm

# This function is based on the 'ethereum-privacy' package available at:
# https://github.com/ferencberes/ethereum-privacy/blob/master/ethprivacy/node_embeddings.py
def clean_graph(G, k=None):
    """Convert to undirected graph and remove self loops"""
    G_undir = G.to_undirected()
    G_tmp = nx.Graph()
    G_tmp.add_edges_from(G_undir.edges())
    G_tmp.remove_edges_from(nx.selfloop_edges(G_tmp))
    # remove low degree nodes
    if k is not None:
        G_tmp = nx.k_core(G_tmp, k=2)
    return G_tmp

# This function is based on the 'ethereum-privacy' package available at:
# https://github.com/ferencberes/ethereum-privacy/blob/master/ethprivacy/node_embeddings.py
def recode_graph(G):
    """Rename nodes to work with Diff2Vec"""
    N = G.number_of_nodes()
    node_map = dict(zip(G.nodes(), range(N)))
    edges_addr = list(G.edges())
    edges_idx = [(node_map[src], node_map[trg]) for src, trg in edges_addr]
    G_tmp = nx.Graph()
    G_tmp.add_edges_from(edges_idx)
    return G_tmp, node_map

def fit_model(G, model, ordered_addresses):
    """
    Fit the input model on a graph and get the node embeddings.
    Returns a tuple where the first element is the node embeddings (numpy array) and the second element is a DataFrame containing the node embeddings with addresses as indices.
    """
    model.fit(G)
    embeddings = model.get_embedding()
    emb_df = pd.DataFrame(embeddings)
    emb_df["address"] = ordered_addresses
    emb_df = emb_df.set_index('address')
    return embeddings, emb_df


##################################
### Distance Calculation Class ###
##################################

# This class is based on the 'ethereum-privacy' package available at:
# https://github.com/ferencberes/ethereum-privacy/blob/master/ethprivacy/distance_calculation.py
# It also uses the 'faiss' library developed by Facebook AI Research for efficient similarity search and clustering of dense vectors.
# More information about 'faiss' can be found at: https://github.com/facebookresearch/faiss
class DistCalculation:
    def __init__(self, X, node_map):
        """
        Args:
            X (numpy array): Embeddings used to build the FAISS index
            node_map (dict): A dictionary mapping addresses to indices
        """
        import faiss
        self.X = X / np.linalg.norm(X, axis=1, keepdims=True)
        self.index = faiss.IndexFlatL2(X.shape[1])
        self.index.add(self.X)
        self.node_map = node_map

    def get_dist_idx(self, i, k=None):
        """
        computes the distance and the indices of the nearest neighbors for the vector at index i.
        Args:
            idx (int): Index of the query vector
        Returns:
            tuple: Two numpy arrays. The first one contains the distances to the nearest neighbors and the second one contains the indices of these neighbors.
        """
        if k is None:
            k = self.X.shape[0]
        D, I = self.index.search(self.X[i:i + 1], self.X.shape[0])
        return D[0, 1:], I[0, 1:]

    def get_rank(self, address1, address2):
        """
        returns the average rank of two target vectors with respect to each other in a nearest neighbor search.
        Args:
            address1 (str): Address corresponding to the first vector
            address2 (str): Address corresponding to the second vector
        Returns:
            tuple: The average rank of the two vectors and the corresponding distances. If either address is not found in the node_map, it returns (None, None).
        """
        address1, address2 = address1.lower(), address2.lower()
        if address1 in self.node_map and address2 in self.node_map:
            query_idx1 = self.node_map[address1]
            query_idx2 = self.node_map[address2]

            distances1, indices1 = self.get_dist_idx(query_idx1)
            distances2, indices2 = self.get_dist_idx(query_idx2)

            if len(indices1) > 0 and query_idx2 in indices1 and len(indices2) > 0 and query_idx1 in indices2:
                trg_idx1 = np.where(indices1 == query_idx2)[0]
                trg_idx2 = np.where(indices2 == query_idx1)[0]
                average_rank = (trg_idx1.item() + 1 + trg_idx2.item() + 1) / 2
                average_distance = (distances1[trg_idx1].item() + distances2[trg_idx2].item()) / 2
                return average_rank, average_distance
            else:
                return None, None
        else:
            return None, None