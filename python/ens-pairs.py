import pandas as pd
from web3 import Web3
from pymongo import MongoClient

# Connect to db collections
client = MongoClient('mongodb://localhost:27017/')
db = client['address-clustering']
transfers = db['transfers']

# Connect to Infura
infura_url = 'https://mainnet.infura.io/v3/315913b854b7474b82c69ded14f25b72'
w3 = Web3(Web3.HTTPProvider(infura_url))

# Test
vitalik_address = '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'.lower()
vitalik = w3.ens.name(vitalik_address)
print(vitalik)

# Get addresses that interacted with ENS as a list
query_conditions = {
    "tokenName": "Ethereum Name Service",
    "tokenType": 721
}

ens_df = pd.DataFrame(list(transfers.find(query_conditions)))
ens_users = ens_df['userAddress'].unique().tolist()


data = []
# For each address, find the ENS name it points to
for i,address in enumerate(ens_users):
    ens_name = w3.ens.name(address)
    data.append([address, ens_name])
    if i%100 == 0:
        print(f'Addresses checked: {i}/{len(ens_users)}')


# Create ens_list.csv
df = pd.DataFrame(data, columns=['Address', 'ENS Name'])
df.to_csv('../data/ens_list.csv')
df = pd.read_csv('../data/ens_list.csv')


# Create ens_pairs.csv
# group by ENS Name and find 2 addresses that point to the same name
grouped_df = df.groupby('ENS Name').filter(lambda x: len(x) == 2)
data = []
for ens_name, group in grouped_df.groupby('ENS Name'):
    addresses = group['Address'].tolist()
    data.append([ens_name, addresses[0], addresses[1]])

ens_addresses_df = pd.DataFrame(data, columns=['ens_name', 'addr1', 'addr2']).set_index('ens_name')
ens_addresses_df.to_csv('../data/ens_pairs.csv')