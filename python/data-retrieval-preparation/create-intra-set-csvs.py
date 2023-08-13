from pymongo import MongoClient
import pandas as pd

# Connect to db collections
client = MongoClient('mongodb://localhost:27017/')
db = client['address-clustering']
transfers = db['transfers']
transactions = db['transactions']

# Get list of active addresses on both networks
users = pd.read_csv('../../data/subsets.csv')
user_addresses = list(set(users.loc[users['Polygon'] == 1, 'Address']).union(users.loc[users['Ethereum'] == 1, 'Address']))

## Intra-set token transfers
query_conditions = {
    "from": {"$in": user_addresses},
    "to": {"$in": user_addresses}
}

transfer_df = pd.DataFrame(list(transfers.find(query_conditions)))

# Drop duplicates
transfer_df = transfer_df.drop(['_id', 'isSet', 'userAddress'], axis=1).drop_duplicates().reset_index(drop=True)
transfer_df.to_csv('../../data/intra_token_transfers.csv')


## Intra-set native asset transfers
query_conditions = {
    "input": "0x",
    "from": {"$in": user_addresses},
    "to": {"$in": user_addresses}
}

transaction_df = pd.DataFrame(list(transactions.find(query_conditions)))

# Drop duplicates
transaction_df = transaction_df.drop(['_id'], axis=1).drop_duplicates().reset_index(drop=True)
transaction_df.to_csv('../../data/intra_native_transfers.csv')