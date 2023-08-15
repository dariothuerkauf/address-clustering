from utils import *

all_transfers_df = pd.read_csv('../data/all_intra_transfers.csv', index_col=[0])
ens_pairs = pd.read_csv('../data/ens_pairs.csv', index_col=[0])

# Specify the addresses to be compared
addresses = ['0xa5dbd5f2f45cec05ace6c08f0b75bec711ea9517','0xf1289a44a9e7f75809de380ffa261f6095387c72']

show_patterns(all_transfers_df, addresses, hour_bins=12, show_kde=True, figsize=(15, 10))
plt.suptitle("erikarand.eth", fontsize=20, weight='bold')
plt.tight_layout()
plt.savefig('../figures/time-of-day-activity.png', bbox_inches='tight', dpi=500)
plt.show()