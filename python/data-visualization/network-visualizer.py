from pymongo import MongoClient
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

class NetworkVisualizer:

    def __init__(self, addresses):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['address-clustering']
        self.transfers = self.db['transfers']
        self.transactions = self.db['transactions']
        self.addresses = [address.lower() for address in addresses]

    def get_data(self):
        query = { "$or": [ { "from": { "$in": self.addresses } }, { "to": { "$in": self.addresses } } ] }
        transactions_df = pd.DataFrame(list(self.transactions.find(query)))
        transfers_df = pd.DataFrame(list(self.transfers.find(query)))
        all_df = pd.concat([transfers_df, transactions_df], ignore_index=True)
        all_grouped = all_df.groupby(['from', 'to']).size().reset_index(name='weight')
        return all_grouped


    def draw_network(self, data, filename=None):
        if filename is None:
            filename = f"../figures/network_visualization_{self.addresses[0][:5]}.png"

        # Graph
        G = nx.from_pandas_edgelist(data, 'from', 'to', edge_attr='weight', create_using=nx.MultiDiGraph())
        pos = nx.spring_layout(G, scale=1, k=2)

        fig, ax = plt.subplots(figsize=(20, 20))

        # Nodes
        color_map = ['orange' if node in self.addresses else 'black' for node in G]
        node_size = [v * 10 for v in dict(G.degree(weight='weight')).values()]
        node_alpha = [1 if node in self.addresses else 0.3 for node in G]
        nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=node_size, alpha=node_alpha, ax=ax)

        # Edges
        edge_colors = ['red' if u in self.addresses else 'lightgreen' for u, v in G.edges()]
        edge_widths = [0.07 * data.get('weight', 1) for u, v, data in G.edges(data=True)]
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, alpha=1, ax=ax, arrowstyle="-")

        # Labels
        degree_weight = dict(G.degree(weight='weight'))
        sorted_nodes = sorted(degree_weight.items(), key=lambda x: x[1], reverse=True)
        top_nodes = [n for n, d in sorted_nodes[:1]]
        labels = {node: node[:7] for node in top_nodes}
        nx.draw_networkx_labels(G, pos, labels=labels, font_color='black', font_size=20, font_weight='bold', ax=ax)

        plt.axis('off')
        plt.tight_layout()
        plt.savefig(filename, dpi=500, transparent=False)
        plt.show()


if __name__ == "__main__":
    addresses = ['0xE2e2F2240a84A61B7dFF50a86ee10d5FaF7faCa8']
    network_visualizer = NetworkVisualizer(addresses)
    data = network_visualizer.get_data()
    network_visualizer.draw_network(data)
