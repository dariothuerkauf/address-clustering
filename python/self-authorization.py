'''
This script is designed to filter and analyze Ethereum transaction data to identify 'self-authorization' events,
where an Ethereum address approves another address to spend its tokens. The script first filters the transactions
to only keep those where the 'input' field starts with the function signature of an approval function.

The script then extracts the spender address from the transaction 'input' data and filters the transactions
to only keep those where the spender is within the address set.
Further filtering is applied to only keep transactions where the sender is different from the spender.

The filtered transactions are then used to build a directed graph, where an edge from address A to address B
indicates that address A has approved address B. Connected components of the graph are then identified as clusters,
and each address is assigned a cluster ID.

Finally, the largest cluster is removed, and the remaining clusters are saved to a CSV file.

Overall, this script is used to identify self-authorization events in Ethereum transaction data and cluster addresses
based on these events.
'''


from utils import *
from pymongo import MongoClient
import re

# Connect to db collection
client = MongoClient('mongodb://localhost:27017/')
db = client['address-clustering']
transactions = db['transactions']
users = pd.read_csv('../data/subsets.csv')['Address'].to_list()

# List of function signatures of approval functions
signatures = [
    "0x095ea7b3",  # approve(address,uint256) for both ERC-20 and ERC-721
    "0xa22cb465",  # setApprovalForAll(address,bool) for both ERC-721 and ERC-1155
    "0x2eb2c2d6"   # safeBatchTransferFrom(address,address,uint256[],uint256[],bytes) for ERC-1155
]

# MongoDB query to get transactions where the 'input' starts with any of the function signatures
approvals = pd.DataFrame(list(transactions.find({"input": {"$in": [re.compile(f"^{sig}") for sig in signatures]}})))
print(f'Total approvals: {len(approvals)}')

# Extract spender address from calldata, Add '0x' to the start of each address
approvals['spender'] = approvals['input'].str[34:74]
approvals['spender'] = approvals['spender'].apply(lambda x: '0x' + x)

# Only keep spenders from set
self_approvals = approvals[approvals['spender'].isin(users)]
print(f'Approvals of set address: {len(self_approvals)}')

# Only keep senders from set that approved another address
filtered_self_approvals = self_approvals[self_approvals['from'] != self_approvals['spender']]
print(f'Approvals of set address (other address): {len(filtered_self_approvals)}')

# Remove unnecessary rows
filtered_self_approvals = filtered_self_approvals[['hash','from', 'to', 'spender']].reset_index(drop=True)

# Group approvals by 'from' address
grouped_df = filtered_self_approvals.groupby(['from']).size().reset_index(name='Number of Approvals given')
print(grouped_df)
print(filtered_self_approvals)

# Build clusters
G = nx.DiGraph()
# Add edges from 'from' address to 'spender'
for idx, row in filtered_self_approvals.iterrows():
    G.add_edge(row['from'], row['spender'])
clusters = list(nx.connected_components(G.to_undirected()))
cluster_df = pd.DataFrame(columns=['ClusterID', 'Address'])

# Assign a cluster ID to each address
for cluster_id, cluster in enumerate(clusters):
    for address in cluster:
        cluster_df = cluster_df.append({'ClusterID': cluster_id, 'Address': address}, ignore_index=True)

print(cluster_df)

# Remove largest cluster
cluster_df_clean = cluster_df[cluster_df['ClusterID']!=6]
cluster_df_clean.to_csv('../data/clusters/clusters_selfAuthorization.csv', index=False)

