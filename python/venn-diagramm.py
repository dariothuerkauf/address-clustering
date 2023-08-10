import pandas as pd
from matplotlib_venn import venn2
import matplotlib.pyplot as plt

df = pd.read_csv('../data/subsets.csv', index_col=[0])

# Addresses active only on Ethereum
eth_only = df[(df['Ethereum'] == 1) & (df['Polygon'] == 0)]
eth_only_count = len(eth_only)

# Addresses active only on Polygon
polygon_only = df[(df['Ethereum'] == 0) & (df['Polygon'] == 1)]
polygon_only_count = len(polygon_only)

# Addresses active on both Ethereum and Polygon
both_active = df[(df['Ethereum'] == 1) & (df['Polygon'] == 1)]
both_active_count = len(both_active)


venn = venn2(subsets=(polygon_only_count, eth_only_count, both_active_count), set_labels=(None, None), set_colors=('#A5D7D2','#D20537'))


ax = plt.gca()
ax.text(-0.3, 0.3, 'Polygon PoS', fontsize=12, ha='center', va='center')
ax.text(0.75, 0.3, 'Ethereum Mainnet', fontsize=12, ha='center', va='center')

venn.get_label_by_id('10').set_position((-0.4, 0))
venn.get_label_by_id('01').set_position((0.65, 0))
venn.get_label_by_id('11').set_position((0.2, 0))

plt.savefig('../figures/venn_diagram.png', dpi=500, bbox_inches='tight')
plt.show()