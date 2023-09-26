base=[0.7161350336577502,
  0.6516138661833649,
  0.6139153865492943,
  0.6255052914669644,
  0.7260150494159172]
summer=[0.5748618187585982,
  0.6547671409385124,
  0.6008450669220429,
  0.6592666262704193,
  0.7301893809765676]
winter=[0.5944727174940919,
  0.6546344092273376,
  0.6528257823452761,
  0.7170084334059842,
  0.800700050645216]

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

X = ['Affected\nregions', 'Northwest', 'Southwest', 'Northeast', 'Southeast']
Ygirls = base
Zboys = summer
Nbio = winter
legend_font = {"family": "Times New Roman", "size": 20}
legend_font1 = {"family": "Times New Roman", "size": 16}
X_axis = np.arange(len(X))



plt.bar(X_axis - 0.25, Ygirls, 0.2, label='Without disruption',edgecolor='C0',color='w',hatch='xxx')
plt.bar(X_axis + 0.0, Zboys, 0.2, label='With disruption (case 1)',edgecolor='C1',color='w',hatch='\\\\\\')
plt.bar(X_axis + 0.25, Nbio, 0.2, label='With disruption (case 2)',edgecolor='C2',color='w',hatch='///')

plt.ylim(0.5, 0.9)
plt.xticks(X_axis, X, fontproperties=legend_font1)
plt.yticks(fontproperties=legend_font1)
# plt.xlabel("", fontproperties=legend_font)
plt.ylabel("Ratio of served passengers", fontproperties=legend_font)
# plt.title("Number of Students in each group",fontproperties = legend_font)
plt.legend(prop=legend_font, loc=0)
ax= plt.gca()
ax.yaxis.set_major_locator(MultipleLocator(0.1))
plt.tight_layout()

plt.savefig(
  "/Users/zihanding/Desktop/research/CPS/Thesis/3.15 update figure/3.16update/evaluation_fig/region_based_motivation.pdf")

