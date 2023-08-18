from utils import *

all_transfers_df = pd.read_csv('../data/all_intra_transfers.csv', index_col=[0], low_memory=False)

# Create network graph
G = nx.from_pandas_edgelist(all_transfers_df, 'from', 'to', create_using=nx.MultiDiGraph())
G = clean_graph(G)
largest_cc = max(nx.connected_components(G), key=len)
G_cc = G.subgraph(largest_cc)
G_cc, node_map = recode_graph(G_cc) # Recode the graph's nodes, node_map maps from address to index
idx_map = dict(zip(node_map.values(),node_map.keys())) # Create reverse map (from indices to addresses)
ordered_addresses = [idx_map[idx] for idx in range(len(node_map))]

print(f'Nodes: {len(G_cc.nodes())}\nEdges: {len(G_cc.edges())}')

#Diff2Vec
emb_d2v_df = pd.read_csv('../data/embeddings/diff2vec.csv', index_col='address')
embeddings_d2v = emb_d2v_df.values
faiss_index_d2v = DistCalculation(embeddings_d2v, node_map)
#Role2Vec
emb_r2v_df = pd.read_csv('../data/embeddings/role2vec.csv', index_col='address')
embeddings_r2v = emb_r2v_df.values
faiss_index_r2v = DistCalculation(embeddings_r2v, node_map)
#Deepwalk
emb_dw_df = pd.read_csv('../data/embeddings/deepWalk.csv', index_col='address')
embeddings_dw = emb_dw_df.values
faiss_index_deepWalk = DistCalculation(embeddings_dw, node_map)

# Parameters
threshold = 0.5 # Threshold for clustering
nn = 10 # Number of nearest neighbours to consider

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

uf = UnionFind(embeddings_r2v.shape[0])

for i in tqdm(range(embeddings_r2v.shape[0]), desc="Creating initial clusters"):
    D, I = faiss_index_r2v.get_dist_idx(i)
    neighbours = set(I[0][D[0] < threshold])
    for neighbour in neighbours:
        uf.union(i, neighbour)

# Extract clusters from union-find
clusters_dict = {}
for i in range(embeddings_r2v.shape[0]):
    root = uf.find(i)
    if root not in clusters_dict:
        clusters_dict[root] = set()
    clusters_dict[root].add(i)

clusters = list(clusters_dict.values())

# Convert clusters to DataFrame
cluster_df = pd.DataFrame({'ClusterID': range(len(clusters)), 'Nodes': clusters})

# Visualize clusters
cluster_sizes = [len(cluster) for cluster in clusters] # Get cluster sizes
sorted_cluster_sizes = sorted(cluster_sizes, reverse=True)

print(cluster_df)

# Show clusters with sizes greater than 50
indices_large_clusters = [i for i, size in enumerate(cluster_sizes) if size > 50]
for index in indices_large_clusters:
    print(f'Cluster {index}: {clusters[index]}')

# Print the size of the largest cluster
print(sorted_cluster_sizes[0])