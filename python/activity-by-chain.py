import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt


# Get all transfers as a pandas dataframe except the '_id', 'userAddress' and 'isSet' column
df_transfer = pd.read_csv('../data/raw_transfer_events.csv', usecols=lambda x: x not in ['_id', 'userAddress', 'isSet'])

# Get all transactions as a pandas dataframe except the '_id' column
df_transactions_eth = pd.read_csv('../data/raw_ethereum_transactions.csv', usecols=lambda x: x not in ['_id'])
df_transactions_polygon = pd.read_csv('../data/raw_polygon_transactions.csv', usecols=lambda x: x not in ['_id'])
df_tx = pd.concat([df_transactions_eth, df_transactions_polygon])

# Drop duplicates
print(df_transfer.shape[0])
df_transfer = df_transfer.drop_duplicates()
print(f'Total number of transfer events: {df_transfer.shape[0]}')
# Count number of transfers per chain
print(df_transfer.groupby('chainName').size().reset_index(name='count'))
print(df_transfer.groupby(['chainName','tokenType']).size().reset_index(name='count'))

# Drop duplicates
print(df_tx.shape[0])
df_tx = df_tx.drop_duplicates()
print(f'Total number of transactions: {df_tx.shape[0]}')
# Count number of transactions per chain
print(df_tx.groupby('chainName').size().reset_index(name='count'))

# Convert timestamp to datetime
df_transfer['timeStamp'] = pd.to_datetime(df_transfer['timeStamp'], unit='s')
df_tx['timeStamp'] = pd.to_datetime(df_tx['timeStamp'], unit='s')

# Get the number of transfers per day and chainName and create a new dataframe
#df_transfer_grouped = df_transfer.groupby([pd.Grouper(key='timeStamp', freq='D'), 'chainName']).size().reset_index(name='count')
df_transfer_grouped = df_transfer.groupby([pd.Grouper(key='timeStamp', freq='M'), 'chainName']).size().reset_index(name='count')
df_transfer_grouped['type'] = 'transfer'

# Get the number of transactions per month and chainName and create a new dataframe
#df_tx_grouped = df_tx.groupby([pd.Grouper(key='timeStamp', freq='D'), 'chainName']).size().reset_index(name='count')
df_tx_grouped = df_tx.groupby([pd.Grouper(key='timeStamp', freq='M'), 'chainName']).size().reset_index(name='count')
df_tx_grouped['type'] = 'transaction'

# Concatenate the two dataframes
df = pd.concat([df_transfer_grouped, df_tx_grouped])
print(df.head(50))

# Get the count for each group
counts = df.groupby(['chainName', 'type']).size().reset_index(name='count')
print(counts)

# Create a new column that combines chainName and type for hue
df['chain_type'] = df['chainName'] + '-' + df['type']

# Create the line plot with dots and set the color palette
sns.set(style='whitegrid')
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x='timeStamp', y="count", hue='chain_type', palette='colorblind')

# Fill the area below the lines with the same colors
palette = sns.color_palette('colorblind')
for i, line in enumerate(df['chain_type'].unique()):
    color = palette[i]
    subset = df[df['chain_type'] == line]
    plt.fill_between(subset['timeStamp'], subset['count'], color=color, alpha=0.2)

plt.legend(title=None)
plt.ylim(bottom=-10)
plt.xlim(left=df.timeStamp.min(), right=df.timeStamp.max())
plt.xlabel("")
plt.ylabel("")
plt.savefig('../figures/transfers_tx_by_chain.png', dpi=300, bbox_inches='tight')
plt.show()