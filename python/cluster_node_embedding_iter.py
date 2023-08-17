import numpy as np

from utils import *

all_transfers_df = pd.read_csv('../data/all_intra_transfers.csv', index_col=[0], low_memory=False)

# Create network graph
G = nx.from_pandas_edgelist(all_transfers_df, 'from', 'to', create_using=nx.MultiDiGraph())
G = clean_graph(G)

# Get the largest connected component
largest_cc = max(nx.connected_components(G), key=len)
G_cc = G.subgraph(largest_cc)

# Recode the graph's nodes, node_map maps from address to index
G_cc, node_map = recode_graph(G_cc)

# Create reverse map (from indices to addresses)
idx_map = dict(zip(node_map.values(),node_map.keys()))
ordered_addresses = [idx_map[idx] for idx in range(len(node_map))]

print(f'Nodes: {len(G_cc.nodes())}\nEdges: {len(G_cc.edges())}')

# Get Role2Vec embeddings
emb_r2v_df = pd.read_csv('../data/embeddings/role2vec.csv', index_col='address')
embeddings_r2v = emb_r2v_df.values
faiss_index_r2v = DistCalculation(embeddings_r2v, node_map)


class UnionFind:
    def __init__(self, n):
        self.parent = [i for i in range(n)]
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rootX = self.find(x)
        rootY = self.find(y)
        if rootX != rootY:
            if self.rank[rootX] > self.rank[rootY]:
                self.parent[rootY] = rootX
            else:
                self.parent[rootX] = rootY
                if self.rank[rootX] == self.rank[rootY]:
                    self.rank[rootY] += 1


# Set up the plot
plt.figure(figsize=(10, 6))

# Iterate over different thresholds
thresholds = [0.6, 0.7, 0.8]
colors = sns.color_palette("deep", 3)

for i, threshold in enumerate(thresholds):
    uf = UnionFind(embeddings_r2v.shape[0])
    for j in tqdm(range(embeddings_r2v.shape[0]), desc=f"Creating clusters with threshold {threshold}"):
        D, I = faiss_index_r2v.get_dist_idx(j)
        neighbours = set(I[0][D[0] < threshold])
        for neighbor in neighbours:
            uf.union(j, neighbor)

    clusters_dict = {}
    for k in range(embeddings_r2v.shape[0]):
        root = uf.find(k)
        if root not in clusters_dict:
            clusters_dict[root] = set()
        clusters_dict[root].add(k)
    clusters = list(clusters_dict.values())

    cluster_sizes = [len(cluster) for cluster in clusters]  # Get cluster sizes

    # Plot histogram using Seaborn
    sns.histplot(cluster_sizes, bins=max(cluster_sizes) - min(cluster_sizes), color=colors[i], alpha=0.5,
                 label=f'{threshold}', edgecolor='black', linewidth=0.5)

    # Largest cluster
    #largest_cluster = clusters[cluster_sizes.index(max(cluster_sizes))]
    #print(f'Largest cluster nodes: {largest_cluster}')

# Customize plot
#plt.title('Histogram of Cluster Sizes', fontsize=20)
plt.xlabel('Cluster Size', fontsize=16)
plt.ylabel('Number of Clusters', fontsize=16)
plt.xticks([5,10,15,20])
plt.xlim([1,20])
plt.ylim([0, 15000])
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('../figures/cluster_histogram.png')
plt.show()
