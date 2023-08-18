import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


def format_x_axis(ax, hour_bins):
    """Formats the x-axis of the time histogram."""
    ax.set_xlim([0, 86400])
    x_ticks = np.linspace(0, 86400, hour_bins + 1)
    ax.set_xticks(x_ticks)
    x_labels = [f'{int(tick / 3600)}' for tick in x_ticks]
    ax.set_xticklabels(x_labels)


def show_patterns(events_df, addresses, ens_name, hour_bins=24, figsize=(15, 15), show_kde=True):
    """Show side channels distribution of the given addresses"""
    addresses = [addr.lower() for addr in addresses]
    events_df['timeStamp'] = pd.to_datetime(events_df['timeStamp'], unit='s')
    events_df['hour'] = events_df['timeStamp'].dt.hour * 3600 + events_df['timeStamp'].dt.minute * 60 + events_df[
        'timeStamp'].dt.second
    sns.set_theme(context='paper')

    # Create a 2x1 grid of subplots
    fig, (ax_hist, ax_kde) = plt.subplots(2, 1, figsize=figsize, gridspec_kw={'height_ratios': [2, 1]})

    # Plot histogram on ax_hist
    bin_edges = np.linspace(events_df['hour'].min(), events_df['hour'].max(), hour_bins + 1)
    for address in addresses:
        user_txs = events_df[events_df["from"] == address]
        sns.histplot(user_txs["hour"], bins=bin_edges, kde=False, ax=ax_hist, alpha=0.5)
        format_x_axis(ax_hist, hour_bins) # assuming you have this function to format the x-axis

    ax_hist.set_xlabel('Hour', fontsize=14)
    ax_hist.set_ylabel('Frequency', fontsize=14)

    # Plot KDE on ax_kde
    if show_kde:
        for address in addresses:
            user_txs = events_df[events_df["from"] == address]
            sns.kdeplot(user_txs['hour'], ax=ax_kde)
            format_x_axis(ax_kde, hour_bins) # assuming you have this function to format the x-axis

    ax_kde.set_xlabel('Hour', fontsize=14)
    ax_kde.set_ylabel('Density', fontsize=14)

    plt.suptitle(ens_name, fontsize=20, weight='bold')
    plt.tight_layout()

    return fig, (ax_hist, ax_kde)


all_transfers_df = pd.read_csv('../data/all_intra_transfers.csv', index_col=[0])
ens_pairs = pd.read_csv('../data/ens_pairs.csv', index_col=[0])

# Specify the addresses to be compared
addresses = ['0xa5dbd5f2f45cec05ace6c08f0b75bec711ea9517','0xf1289a44a9e7f75809de380ffa261f6095387c72']

show_patterns(all_transfers_df, addresses, 'erikarand.eth', hour_bins=12, show_kde=True, figsize=(15, 10))
plt.savefig('../figures/time-of-day-activity.png', bbox_inches='tight', dpi=500)
plt.show()