import pandas as pd
import numpy as np
from datetime import datetime


def add_ToD(df):
    df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='s')
    df['ToD'] = df['timeStamp'].dt.hour * 3600 + df['timeStamp'].dt.minute * 60 + df['timeStamp'].dt.second
    return df

def compute_statistics(data):
    """ Compute mean, median, standard deviation for each 'from' address """
    stats = data.groupby('from').agg({'ToD': ['mean', 'median', np.std]})
    stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
    return stats

def compute_histogram(data, bins):
    """ Compute histogram for ToD column with specified number of bins """
    labels = [f"hist_bin_{i}" for i in range(1, bins+1)]
    data['bin'] = pd.cut(data['ToD'], bins=bins, labels=labels)
    hist_data = data.groupby(['from', 'bin']).size().unstack(fill_value=0)
    return hist_data


# Load data
ethereum_trx = pd.read_csv('../data/raw_ethereum_transactions.csv', index_col=[0])
polygon_trx = pd.read_csv('../data/raw_polygon_transactions.csv', index_col=[0])
transaction_df = pd.concat([ethereum_trx, polygon_trx])



#################
### TimeOfDay ###
#################

# Add ToD column
transaction_df = add_ToD(transaction_df)

# Filter out addresses with less then 5 trx sent
#counts = transaction_df.groupby('from').size()
#addresses_to_keep = counts[counts >= 5].index
#transaction_df_filtered = transaction_df[transaction_df['from'].isin(addresses_to_keep)]
transaction_df_filtered = transaction_df[transaction_df.groupby('from')['from'].transform('size') >= 5]


# Compute statistics and histogram
hist_df = compute_histogram(transaction_df_filtered, bins=6)
stats_df = compute_statistics(transaction_df_filtered)
result_df = pd.merge(stats_df, hist_df, left_index=True, right_index=True)

# Save to csv
result_df.to_csv('../data/timeOfDay.csv')


################
### GasPrice ###
################

# Add date column
ethereum_trx['date'] = ethereum_trx['timeStamp'].apply(lambda x: datetime.fromtimestamp(x))
polygon_trx['date'] = polygon_trx['timeStamp'].apply(lambda x: datetime.fromtimestamp(x))

# Compute daily average gasPrice
daily_avg_eth = ethereum_trx.groupby('date')['gasPrice'].mean()
daily_avg_polygon = polygon_trx.groupby('date')['gasPrice'].mean()

# Compute normalized gasPrice
ethereum_trx['daily_avg_gasPrice'] = ethereum_trx['date'].map(daily_avg_eth)
polygon_trx['daily_avg_gasPrice'] = polygon_trx['date'].map(daily_avg_polygon)
ethereum_trx['normalized_gasPrice'] = ethereum_trx['gasPrice'] / ethereum_trx['daily_avg_gasPrice']
polygon_trx['normalized_gasPrice'] = polygon_trx['gasPrice'] / polygon_trx['daily_avg_gasPrice']

# Concatenate dataframes
transaction_df = pd.concat([ethereum_trx, polygon_trx])

# # Filter out addresses with less then 5 trx sent
# counts = transaction_df.groupby('from').size()
# addresses_to_keep = counts[counts >= 5].index
# transaction_df_clean = transaction_df[transaction_df['from'].isin(addresses_to_keep)]

# Compute statistics and histogram
hist_df = compute_histogram(transaction_df_filtered, bins=50)
stats_df = compute_statistics(transaction_df_filtered)
result_df = pd.merge(stats_df, hist_df, left_index=True, right_index=True)

result_df.to_csv('../data/normalizedGas.csv')