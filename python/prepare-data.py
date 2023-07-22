import pandas as pd

# Get Ethereum and Polygon subsets
users = pd.read_csv('../data/subsets.csv')
polygon_addresses = users.loc[users['Polygon'] == 1, 'Address'].tolist()
ethereum_addresses = users.loc[users['Ethereum'] == 1, 'Address'].tolist()

## ERC-721

# Ethereum
# Create isSetFrom and isSetTo column
ethereum_721 = pd.read_csv('../data/ethereum_erc721.csv')
ethereum_721['isSetFrom'] = ethereum_721['from'].isin(ethereum_addresses)
ethereum_721['isSetTo'] = ethereum_721['to'].isin(ethereum_addresses)
ethereum_721 = ethereum_721.drop_duplicates()

# Polygon
# Create isSetFrom and isSetTo column
polygon_721 = pd.read_csv('../data/polygon_erc721.csv')
polygon_721['isSetFrom'] = polygon_721['from'].isin(polygon_addresses)
polygon_721['isSetTo'] = polygon_721['to'].isin(polygon_addresses)
polygon_721 = polygon_721.drop_duplicates()

erc721 = pd.concat([ethereum_721, polygon_721], ignore_index=True)

if len(erc721) == len(polygon_721) + len(ethereum_721):
    print('ERC-721: Length check passed')

## ERC-20

# Ethereum
# Create isSetFrom and isSetTo column
ethereum_20 = pd.read_csv('../data/ethereum_erc20.csv')
ethereum_20['isSetFrom'] = ethereum_20['from'].isin(ethereum_addresses)
ethereum_20['isSetTo'] = ethereum_20['to'].isin(ethereum_addresses)
ethereum_20 = ethereum_20.drop_duplicates()

# Polygon
# Create isSetFrom and isSetTo column
polygon_20 = pd.read_csv('../data/polygon_erc20.csv')
polygon_20['isSetFrom'] = polygon_20['from'].isin(polygon_addresses)
polygon_20['isSetTo'] = polygon_20['to'].isin(polygon_addresses)
polygon_20 = polygon_20.drop_duplicates()

erc20 = pd.concat([ethereum_20, polygon_20], ignore_index=True)

# Convert values
erc20['value'] = erc20['value'].apply(int)
erc20['value'] = erc20['value'] / (10 ** erc20['tokenDecimal'])
erc20 = erc20.drop('tokenDecimal', axis=1)

if len(erc20) == len(ethereum_20) + len(polygon_20):
    print('ERC-20: Length check passed')


## ERC-1155

# Ethereum
# Create isSetFrom and isSetTo column
ethereum_1155 = pd.read_csv('../data/ethereum_erc721.csv')
ethereum_1155['isSetFrom'] = ethereum_1155['from'].isin(ethereum_addresses)
ethereum_1155['isSetTo'] = ethereum_1155['to'].isin(ethereum_addresses)
ethereum_1155 = ethereum_1155.drop_duplicates()

# Polygon
# Create isSetFrom and isSetTo column
polygon_1155 = pd.read_csv('../data/polygon_erc1155.csv')
polygon_1155['isSetFrom'] = polygon_1155['from'].isin(polygon_addresses)
polygon_1155['isSetTo'] = polygon_1155['to'].isin(polygon_addresses)
polygon_1155 = polygon_1155.drop_duplicates()

erc1155 = pd.concat([ethereum_1155, polygon_1155], ignore_index=True)
erc1155 = erc1155.rename(columns={'tokenValue': 'value'})

if len(erc1155) == len(ethereum_1155) + len(polygon_1155):
    print('ERC-1155: Length check passed')


## Concatenate the three DataFrames and check length
events = pd.concat([erc20, erc721, erc1155], ignore_index=True)
print(f'Length of all events: {len(events)}')

if len(events) == len(erc20) + len(erc721) + len(erc1155):
    print('Events: Length check passed')


## Add isSet column

# Filter rows where both 'isSetFrom' and 'isSetTo' are True
both_true_df = events[(events['isSetFrom'] == True) & (events['isSetTo'] == True)]

# Create two copies of both_true_df
df1 = both_true_df.copy()
df2 = both_true_df.copy()

# In df1, set 'isSet' to 'from', and in df2, set 'isSet' to 'to'
df1['isSet'] = 'from'
df2['isSet'] = 'to'

# Rows where only one of 'isSetFrom' and 'isSetTo' is True
only_from_true_df = events[(events['isSetFrom'] == True) & (events['isSetTo'] == False)].copy()
only_from_true_df['isSet'] = 'from'

only_to_true_df = events[(events['isSetFrom'] == False) & (events['isSetTo'] == True)].copy()
only_to_true_df['isSet'] = 'to'

# Concatenate all the DataFrames together
events_inSet = pd.concat([df1, df2, only_from_true_df, only_to_true_df])
events_inSet = events_inSet.drop(['isSetFrom', 'isSetTo'], axis=1)

# Sort by the original index for continuity of data
events_inSet = events_inSet.sort_index()

# Create userAddress column
events_inSet['userAddress'] = events_inSet.apply(lambda row: row['from'] if row['isSet'] == 'from' else row['to'],
                                                 axis=1)

# Save as csv
events_inSet.to_csv('../data/transfer_events.csv')