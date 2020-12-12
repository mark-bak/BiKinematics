#Standard imports 
import matplotlib.pyplot as plt



def plot_results(x,y):
    fig, ax = plt.subplots()
    ax.plot(x,y)
    return fig,ax

if __name__=='__main__':
    x= [0,1,2,3,4]
    y= [0,1,2,3,4]

    fig,ax = plot_results(x,y)
    plt.show()