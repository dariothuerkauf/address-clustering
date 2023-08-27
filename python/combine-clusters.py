'''
This script is used for processing and analyzing the three clusters resulting from Node Embedding,
Self-Authorization and LAND Transfers.
It combines these clusters into a single dataframe, updating the cluster IDs to ensure uniqueness across the combined set.
Next, it identifies and resolves overlapping clusters by updating the cluster IDs in the concatenated
dataframe based on overlapping addresses. Duplicate rows are then removed, and the dataframe is sorted
by 'ClusterID' and the index is reset.

The script then calculates the number of addresses in each cluster and identifies the number of clusters
containing more than one address. Following this, it categorizes the clusters into different size bins
and plots the distribution of cluster sizes as a bar plot.
'''

from utils import *

# Create the three dataframes
df1 = pd.read_csv('../data/clusters/clusters_role2vec_05.csv')
df2 = pd.read_csv('../data/clusters/clusters_selfAuthorization.csv')
df3 = pd.read_csv('../data/clusters/clusters_LAND.csv', usecols=['ClusterID', 'Address'])

# Update ClusterID in df2 and df3
df2['ClusterID'] += df1['ClusterID'].max() + 1
df3['ClusterID'] += df2['ClusterID'].max() + 1

# Concatenate the three dataframes
concat_df = pd.concat([df1, df2, df3], ignore_index=True)

# Identify overlapping clusters
merged_df = concat_df.merge(concat_df, on='Address')
overlap_clusters = merged_df[merged_df['ClusterID_x'] != merged_df['ClusterID_y']]

# Update cluster IDs in concat_df based on overlapping clusters
for _, row in overlap_clusters.iterrows():
    concat_df.loc[concat_df['ClusterID'] == row['ClusterID_y'], 'ClusterID'] = row['ClusterID_x']

# Remove duplicate rows
concat_df.drop_duplicates(inplace=True)

concat_df.sort_values(by=['ClusterID'], inplace=True)
concat_df.reset_index(drop=True, inplace=True)


# Group by ClusterID and count the number of addresses in each cluster
cluster_sizes = concat_df.groupby('ClusterID').size()
clusters_with_multiple_addresses = cluster_sizes[cluster_sizes > 1]
num_clusters_with_multiple_addresses = len(clusters_with_multiple_addresses)
print(f"Number of clusters with more than one address: {num_clusters_with_multiple_addresses}")

# Plot the distribution of cluster sizes
# Define the bins and labels
bins = [0, 1, 2, 3, 4, 5, 10, 20, 50, float('inf')]
labels = ['1', '2', '3', '4', '5', '6-10', '11-20', '21-50', '50+']

# Use pd.cut to categorize the cluster sizes into the defined bins
bin_counts = pd.cut(cluster_sizes, bins=bins, labels=labels, right=True).value_counts()

# Sort the bin counts by the order of the bins
bin_counts = bin_counts.reindex(labels)

# Create a horizontal barplot with a bar for each bin
plt.figure(figsize=(10, 5))
color_palette = sns.color_palette("deep")
ax = sns.barplot(x=bin_counts.values, y=bin_counts.index, color=color_palette[0], alpha=0.7)
plt.xlabel('')
plt.ylabel('Cluster Size', fontsize=14)
plt.title('Number of Clusters', fontsize=14)

# Remove the top, right, and bottom axis lines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)

ax.set_xticklabels([])
ax.set_xticks([])

# Annotate each bar with its value
for p in ax.patches:
    ax.text(p.get_width(), p.get_y() + p.get_height() / 2,
            int(p.get_width()), ha='left', va='center', fontsize=10)

plt.tight_layout()
plt.savefig('../figures/cluster-size-distribution.png', dpi=300)
plt.show()
