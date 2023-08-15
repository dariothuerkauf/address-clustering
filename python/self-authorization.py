from pymongo import MongoClient
import pandas as pd
import re
import networkx as nx

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
cluster_df = pd.DataFrame(columns=['Cluster_ID', 'Address'])

# Assign a cluster ID to each address
for cluster_id, cluster in enumerate(clusters):
    for address in cluster:
        cluster_df = cluster_df.append({'Cluster_ID': cluster_id, 'Address': address}, ignore_index=True)

print(cluster_df)


