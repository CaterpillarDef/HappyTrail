import seaborn as sns

def export_heatmap(data, filename="heatmap.png"):
    fig = sns.heatmap(data, cbar=False,xticklabels=False,yticklabels=False,cmap=sns.cm.rocket).get_figure()
    fig.savefig(filename,bbox_inches='tight')
