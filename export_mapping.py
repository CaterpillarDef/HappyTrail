import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

def export_heatmap(data, filename="heatmap.png"):
    fig = sns.heatmap(data, cbar=False,xticklabels=False,yticklabels=False,cmap=sns.cm.rocket).get_figure()
    fig.savefig(filename,bbox_inches='tight')

def export_heatmap_with_path(cost,path,export_filename='heatmaps/generated_path_map.png', path_color='green'):
    plt.figure(figsize=(24,20))
    ax = sns.heatmap(cost, cbar=False,xticklabels=False,yticklabels=False,cmap=sns.cm.rocket)
    path_y,path_x = np.where(path.values == 0)
    ax.scatter(path_x+0.5, path_y+0.5, color=path_color, s=1, alpha=0.8)
    plt.tight_layout()
    fig = ax.get_figure()
    fig.savefig(export_filename,bbox_inches='tight',dpi=300)
    plt.close(fig)
