from matplotlib_venn import venn2
import matplotlib.pyplot as plt

# Data
polygon_only = 83774
ethereum_only = 7867
both = 49950

venn = venn2(subsets=(polygon_only, ethereum_only, both), set_labels=(None, None), set_colors=('#A5D7D2','#D20537'))


ax = plt.gca()
ax.text(-0.3, 0.3, 'Polygon PoS', fontsize=12, ha='center', va='center')
ax.text(0.75, 0.3, 'Ethereum Mainnet', fontsize=12, ha='center', va='center')

venn.get_label_by_id('10').set_position((-0.4, 0))
venn.get_label_by_id('01').set_position((0.65, 0))
venn.get_label_by_id('11').set_position((0.2, 0))

plt.savefig('../figures/venn_diagram.png', dpi=500, bbox_inches='tight')
plt.show()