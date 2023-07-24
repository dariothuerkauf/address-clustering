import pandas as pd
from pymongo import MongoClient
import numpy as np

# Connect to db collections
client = MongoClient('mongodb://localhost:27017/')
db = client['address-clustering']
transfers = db['transfers']
transactions = db['transactions']

# Tornado Pools dictionary
tornado = [
    ('0xA160cdAB225685dA1d56aa342Ad8841c3b53f291', '100 Eth'),
    ('0x910Cbd523D972eb0a6f4cAe4618aD62622b39DbF', '10 Eth'),
    ('0x47CE0C6eD5B0Ce3d3A51fdb1C52DC66a7c3c2936', '1 Eth'),
    ('0x12D66f87A04A9E220743712cE6d9bB1B5616B8Fc', '0.1 Eth'),
    ('0x23773E65ed146A459791799d01336DB287f25334', '100k Dai'),
    ('0x07687e702b410Fa43f4cB4Af7FA097918ffD2730', '10k Dai'),
    ('0xFD8610d20aA15b7B2E3Be39B396a1bC3516c7144', '1k Dai'),
    ('0xd4b88df4d29f5cedd6857912842cff3b20c8cfa3', '100 Dai'),
    ('0xbB93e510BbCD0B7beb5A853875f9eC60275CF498', '10 wBTC'),
    ('0x610B717796ad172B316836AC95a2ffad065CeaB4', '1 wBTC'),
    ('0x178169B423a011fff22B9e3F3abeA13414dDD0F1', '0.1 wBTC'),
    ('0xD691F27f38B395864Ea86CfC7253969B409c362d', '10k USDC'),
    ('0xd96f2B1c14Db8458374d9Aca76E26c3D18364307', '100 USDC'),
    ('0x4736dCf1b7A3d580672CcE6E7c65cd5cc9cFBa9D', '1k USDC'),
    ('0x9AD122c22B14202B4490eDAf288FDb3C7cb3ff5E', '100k USDT'),
    ('0xF67721A2D8F736E75a49FdD7FAd2e31D8676542a', '10k USDT'),
    ('0x0836222F2B2B24A3F36f98668Ed8F0B38D1a872f', '1k USDT'),
    ('0x169AD27A470D064DEDE56a2D3ff727986b15D52B', '100 USDT'),
    ('0xD21be7248e0197Ee08E0c20D4a96DEBdaC3D20Af', '5M cDai'),
    ('0x2717c5e28cf931547b621a5dddb772ab6a35b701', '500k cDai'),
    ('0xBA214C1c1928a32Bffe790263E38B4Af9bFCD659', '50k cDai'),
    ('0x22aaA7720ddd5388A3c0A3333430953C68f1849b', '5k cDai'),
    ('0x1356c899D8C9467C7f71C195612F8A395aBf2f0a', '50k cUSDC'),
    ('0xaEaaC358560e11f52454D997AAFF2c5731B6f8a6', '5k cUSDC')
]

tornado_pools = pd.DataFrame(tornado, columns=['contract_address', 'pool'])
tornado_pools['contract_address'] = tornado_pools['contract_address'].str.lower()
tornado_pools.set_index('contract_address', inplace=True)
tornado_pool_addresses = tornado_pools.index.tolist()
#tornado_pools.to_csv('../data/tornado-pools.csv')

# Transactions
tornado_transactions = pd.DataFrame(list(transactions.find({"$or": [{"from": {"$in": tornado_pool_addresses}}, {"to": {"$in": tornado_pool_addresses}}]})))
tornado_transactions['tokenName'] = 'Ether'
tornado_transactions['tokenType'] = 'native'
tornado_transactions['isSet'] = 'from'
tornado_transactions['userAddress'] = tornado_transactions['from']
tornado_transactions['contractAddress'] = tornado_transactions['to']

# Token Transfers
tornado_transfers = pd.DataFrame(list(transfers.find({"$or": [{"from": {"$in": tornado_pool_addresses}}, {"to": {"$in": tornado_pool_addresses}}]})))
tornado_transfers['contractAddress'] = np.where(tornado_transfers['isSet'] == 'to', tornado_transfers['from'], tornado_transfers['to'])

# Concatenate
df = pd.concat([tornado_transactions,tornado_transfers])
df.drop(labels=['_id','tokenID'], axis=1, inplace=True)

# Create a dictionary from the DataFrame
tornado_dict = tornado_pools['pool'].to_dict()
df['pool'] = df['contractAddress'].map(tornado_dict)

# Save the DataFrame to a CSV file
df.reset_index(drop=True, inplace=True)
df.to_csv('../data/tornado.csv')
print(df)