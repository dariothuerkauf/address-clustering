from pymongo import MongoClient
import pandas as pd

# Connect to db collections
client = MongoClient('mongodb://localhost:27017/')
db = client['address-clustering']
transactions = db['transactions']
users = pd.read_csv('../data/subsets.csv')['Address'].to_list()

# Query all approval transactions
approvals = pd.DataFrame(list(transactions.find({"functionName": "approve(address spender, uint256 rawAmount)"})))
print(f'Total approvals: {len(approvals)}')

# Extract spender address from calldata, Add '0x' to the start of each address
approvals['spender'] = approvals['input'].str[34:74]
approvals['spender'] = approvals['spender'].apply(lambda x: '0x' + x)

# Only keep spenders from set
self_approvals = approvals[approvals['spender'].isin(users)]

# Only keep senders from set that approved another address
filtered_self_approvals = self_approvals[self_approvals['from'] != self_approvals['spender']]

# Remove unnecessary rows
filtered_self_approvals = filtered_self_approvals[['hash','from', 'to', 'spender']].reset_index(drop=True)

# Group approvals by 'from' address
grouped_df = filtered_self_approvals.groupby(['from']).size().reset_index(name='Number of Approvals given')
print(grouped_df)
