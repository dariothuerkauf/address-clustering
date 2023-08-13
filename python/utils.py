# Import packages
import pandas as pd
from karateclub import Diff2Vec, Role2Vec, DeepWalk
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from tqdm import tqdm


# Functions
def compute_weights(df):  ### evtl direkt mit undirected graph arbeiten
    # Sort from and to addresses lexicographically
    df['from'], df['to'] = np.where(df['from'] > df['to'], [df['to'], df['from']], [df['from'], df['to']])
    # Group by 'from' and 'to', and count the number of interactions
    grouped_df = df.groupby(['from', 'to']).size().reset_index(name='weight')
    # grouped_df = grouped_df.rename(columns={"from": "address1", "to": "address2"})
    return grouped_df


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


def address_txs(address_str):
    """Get all intra-set transfers/transactions related to an address"""
    transfer_df = pd.read_csv('../data/token_transfers.csv', index_col=[0])
    transaction_df = pd.read_csv('../data/native_transfers.csv', index_col=[0])
    all_df = pd.concat([transaction_df, transfer_df], ignore_index=True)
    address = str(address_str).lower()
    txs = all_df[(all_df["from"] == address) | (all_df["to"] == address)]
    return txs.sort_values("timeStamp")


def show_patterns(events_df, addresses, hour_bins=24, figsize=(15, 3), show_kde=False):
    """Show side channels distribution of the given addresses"""
    addresses = [addr.lower() for addr in addresses]
    events_df['timeStamp'] = pd.to_datetime(events_df['timeStamp'], unit='s')
    events_df['hour'] = events_df['timeStamp'].dt.hour * 3600 + events_df['timeStamp'].dt.minute * 60 + events_df[
        'timeStamp'].dt.second
    sns.set_theme(context='paper')
    if show_kde:
        fig, ax = plt.subplots(1, figsize=(7.5, 3))
        for address in addresses:
            user_txs = events_df[events_df["from"] == address]
            print(address, len(user_txs))
        try:
            for address in addresses:
                user_txs = events_df[events_df["from"] == address]
                sns.kdeplot(user_txs['hour'], ax=ax)
            format_x_axis(ax, hour_bins)
        except Exception as e:
            print(e)

    fig, ax = plt.subplots(1, figsize=(7.5, 3))
    bin_edges = np.linspace(events_df['hour'].min(), events_df['hour'].max(), hour_bins + 1)  # set common bin edges
    for address in addresses:
        user_txs = events_df[events_df["from"] == address]
        sns.histplot(user_txs["hour"], bins=bin_edges, kde=False, ax=ax, alpha=0.5)  # use common bin edges
        format_x_axis(ax, hour_bins)


### Helper function
def format_x_axis(ax, hour_bins):
    """Formats the x-axis of the time histogram."""
    ax.set_xlim([0, 86400])
    x_ticks = np.linspace(0, 86400, hour_bins + 1)
    ax.set_xticks(x_ticks)
    x_labels = [f'{int(tick / 3600)}' for tick in x_ticks]
    ax.set_xticklabels(x_labels)



############################
### Distance Calculation ###
############################

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

    def get_dist_idx(self, idx, k=None):
        """
        computes the distance and the indices of the nearest neighbors for the vector at index idx.
        Args:
            idx (int): Index of the query vector
        Returns:
            tuple: Two numpy arrays. The first one contains the distances to the nearest neighbors and the second one contains the indices of these neighbors.
        """
        if k is None:
            k = self.X.shape[0]
        D, I = self.index.search(self.X[idx:idx + 1], self.X.shape[0])
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
                #print(trg_idx1)
                trg_idx2 = np.where(indices2 == query_idx1)[0]
                #print(trg_idx2)
                average_rank = (trg_idx1.item() + 1 + trg_idx2.item() + 1) / 2
                average_distance = (distances1[trg_idx1].item() + distances2[trg_idx2].item()) / 2
                return average_rank, average_distance
            else:
                return None, None
        else:
            return None, None

    def foo(self, address1, address2):
        """
        returns the rank of a target vector with respect to a query vector in a nearest neighbor search.
        Args:
            address1 (str): Address corresponding to the query vector
            address2 (str): Address corresponding to the target vector
        Returns:
            tuple: The rank of the target vector and the corresponding distance. If either address is not found in the node_map, it returns (None, None).
        """
        address1, address2 = address1.lower(), address2.lower()
        if address1 in self.node_map and address2 in self.node_map:
            query_idx = self.node_map[address1]
            target_idx = self.node_map[address2]

            distances, indices = self.get_dist_idx(query_idx)

            if len(indices) > 0 and target_idx in indices:
                trg_idx = np.where(indices == target_idx)[0]
                return trg_idx.item() + 1, distances[trg_idx].item()
            else:
                return None, None
        else:
            return None, None


