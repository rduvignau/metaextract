from learner import *
from svt import *
from test import *
from matplotlib import pyplot as plt
from os.path import join

"""
    All plots / tables used for the Evaluation.
"""

genres_1vsAll_accuracy = [1.0, 0.996, 1.0, 1.0, 1.0, 0.996, 1.0]

genres_names = ["Action & Adventure", "Comedy", "Documentary", "Kids", "Animation", "Drama", "Action"]
genres_names = ["A & A", "Comedy", "Docu.", "Kids", "Anim.", "Drama", "Action"]

genres_1vsAll_accuracies = [[0.985, 0.985, 0.985, 0.985, 0.984, 0.999, 0.999, 1.0, 1.0, 1.0],
[0.633, 0.694, 0.736, 0.766, 0.804, 0.83, 0.87, 0.923, 0.955, 0.988],
[0.99, 0.99, 0.99, 0.99, 0.993, 0.995, 0.998, 0.999, 1.0, 1.0],
[0.98, 0.98, 0.988, 0.995, 0.999, 1.0, 1.0, 1.0, 1.0, 1.0],
[0.825, 0.858, 0.868, 0.912, 0.934, 0.963, 0.971, 0.986, 0.993, 1.0],
[0.784, 0.804, 0.807, 0.818, 0.828, 0.848, 0.882, 0.938, 0.962, 0.985],
[0.998, 0.998, 0.998, 0.998, 0.998, 0.998, 0.998, 0.998, 1.0, 1.0]]

genres_1vsAll_precisions = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.947, 1.0, 1.0, 1.0, 1.0],
[0.616, 0.691, 0.755, 0.775, 0.786, 0.803, 0.846, 0.9, 0.944, 0.982],
[0.0, 0.0, 0.0, 0.0, 0.714, 1.0, 1.0, 1.0, 1.0, 1.0],
[0.0, 0.0, 0.696, 0.846, 0.96, 1.0, 1.0, 1.0, 1.0, 1.0],
[0.0, 0.823, 0.853, 0.858, 0.929, 0.957, 0.984, 0.995, 0.99, 1.0],
[0.574, 0.728, 0.725, 0.744, 0.79, 0.82, 0.888, 0.952, 0.98, 1.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]]

genres_1vsAll_recalls = [[0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.944, 1.0, 1.0, 1.0],
[0.876, 0.799, 0.768, 0.809, 0.882, 0.915, 0.933, 0.967, 0.976, 0.996],
[0.0, 0.0, 0.0, 0.0, 0.417, 0.5, 0.75, 0.917, 1.0, 1.0],
[0.0, 0.0, 0.667, 0.917, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
[0.0, 0.238, 0.299, 0.593, 0.673, 0.827, 0.85, 0.925, 0.972, 1.0],
[0.248, 0.238, 0.262, 0.319, 0.348, 0.436, 0.56, 0.77, 0.855, 0.936],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.333, 1.0, 1.0]]

def identification_accuracy_plot():
    plt.figure(figsize=(6,2.5))
    plt.ylabel('Accuracy')
    plt.xlabel('Capture Time (s)')
    plt.grid(linestyle='--')
    plt.plot(durations,video_accuracy,marker='d',linestyle="-",color="blue",label='Identification of videos')
    plt.plot(durations,series_accuracy,marker="s",linestyle="-.",color="green",label='Identification of series')
    plt.plot(durations,genres_accuracy,marker="o",linestyle=":",color="red",label='Identification of genres')
    plt.legend(framealpha=0.9)
    plt.tight_layout()
    plt.savefig("accuracy1.pdf")

def identification_accuracy_plot_svt():
    plt.figure(figsize=(6,2.5))
    plt.ylabel('Accuracy')
    plt.xlabel('Capture Time (s)')
    plt.ylim((0,1))
    plt.grid(linestyle='--')
    plt.plot(durations_svt,video_accuracy_svt,marker='d',linestyle="-",color="blue",label='Identification of videos')
    plt.plot(durations_svt,series_accuracy_svt,marker="s",linestyle="-.",color="green",label='Identification of series')
    plt.plot(durations_svt,all_vs_all_accuracy_svt,marker="o",linestyle=":",color="red",label='Identification of genres')
    plt.legend(framealpha=0.9)
    plt.tight_layout()
    plt.savefig("accuracy_svt.pdf")

def identification_accuracy_plots():
    fig, ax = plt.subplots(1, 2, sharey=True)
    fig.set_size_inches(6,2.5)
    
    for i in range(len(ax)):
        ax[i].set_xlabel('Capture Time (s)')
        ax[i].grid(linestyle='--')

    ax[0].set_ylabel('Accuracy')
    ax[0].plot(durations,video_accuracy,marker='d',linestyle="-",color="blue",label='Video titles')
    ax[0].plot(durations,series_accuracy,marker="s",linestyle="-.",color="green",label='Series titles')
    ax[0].plot(durations,genres_accuracy,marker="o",linestyle=":",color="red",label='Genres (All-Vs-All)')
    ax[0].legend(framealpha=0.9)
    ax[0].set_title("(a) over dataset NetflixSmall.")

    ax[1].plot(durations_svt,video_accuracy_svt,marker='d',linestyle="-",color="blue",label='Video titles')
    ax[1].plot(durations_svt,series_accuracy_svt,marker="s",linestyle="-.",color="green",label='Series titles')
    ax[1].plot(durations_svt,all_vs_all_accuracy_svt,marker="o",linestyle=":",color="red",label='Genres (All-Vs-All)')
    ax[1].legend(framealpha=0.9)
    ax[1].set_title("(b) over dataset SVT.")
    
    
    fig.tight_layout()
    fig.savefig("accuracy_2.pdf")

def identification_apr_plots():
    fig, axes = plt.subplots(3,1, sharex=True)
    fig.set_size_inches(6,6)

    axes[0].set_ylabel('Accuracy 1-Versus-All')
    axes[1].set_ylabel('Precision 1-Versus-All')
    axes[2].set_ylabel('Recall 1-Versus-All')

    axes[2].set_xlabel('Capture Time (s)')

    data = [genres_1vsAll_accuracies, genres_1vsAll_precisions, genres_1vsAll_recalls]
    linestyles = ['-', ':', ':', '-.', (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1))]
    markers = ['d', 's', 'o', 'v', '^', '<', '>']
    colors = ['b','g','r','darkblue','darkgreen','darkred','teal']
    
    for j in range(len(axes)):
        axes[j].grid(linestyle='--')
        for i in range(len(genres_names)):
            axes[j].plot([durations[k] for k in range(len(durations)) if data[j][i][k] > 0],
                         [f for f in data[j][i] if f > 0],
                         marker=markers[i],
                         linestyle=linestyles[i],
                         color=colors[i],
                         label=genres_names[i])

    axes[0].legend(framealpha=0.9, ncol=2)

    fig.tight_layout()
    fig.savefig("apr_1versusAll_2.pdf")

def identification_apr_plots_variant():
    fig, axes = plt.subplots(1,3)
    fig.set_size_inches(12,2.25)

    axes[0].set_title('(a) Accuracy 1-Versus-All.')
    axes[1].set_title('(b) Precision 1-Versus-All.')
    axes[2].set_title('(c) Recall 1-Versus-All.')

    axes[0].set_xlabel('Capture Time (s)')
    axes[1].set_xlabel('Capture Time (s)')
    axes[2].set_xlabel('Capture Time (s)')

    data = [genres_1vsAll_accuracies, genres_1vsAll_precisions, genres_1vsAll_recalls]
    linestyles = ['-', ':', ':', '-.', (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1))]
    markers = ['d', 's', 'o', 'v', '^', '<', '>']
    colors = ['b','g','r','darkblue','darkgreen','darkred','teal']
    
    for j in range(len(axes)):
        axes[j].grid(linestyle='--')
        for i in range(len(genres_names)):
            axes[j].plot([durations[k] for k in range(len(durations)) if data[j][i][k] > 0],
                         [f for f in data[j][i] if f > 0],
                         marker=markers[i],
                         linestyle=linestyles[i],
                         color=colors[i],
                         label=genres_names[i])

    axes[0].legend(framealpha=0.9, fontsize=8, ncol=2)
    axes[1].legend(framealpha=0.9, fontsize=8, ncol=2)
    axes[2].legend(framealpha=0.9, fontsize=8, ncol=2)

    fig.tight_layout()
    fig.savefig("apr_1versusAll_3.pdf")


def print_confusion_matrix(length=60): # for the all-versus-all only with 1min of video
    matrix = compute_confusion_matrix(length)
    all_genres = matrix.keys()
    print(all_genres)

    genres_ids_2_names = {}
    for i in range(len(genres)):
        genres_ids_2_names[genres[i]] = genres_names[i]
        
    print("& ", ' & '.join([genres_ids_2_names[g] for g in genres]), "\\\\")

    for g in genres:
        print(genres_ids_2_names[g], end="")
        for g2 in genres:
            print(" & ", matrix[g][g2], end="")
        print("\\\\")
