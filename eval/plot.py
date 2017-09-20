'''
Created on Sep 12, 2017

@author: Angus
'''


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def showPlot(result_folder, batch_num, plot_array):
    slot = 1
    plt.figure()
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('No. batch X ' + str(slot))
       
    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_ylabel('PPL', color='b')
    ax1.tick_params('y', colors='b')
    ax1.plot(condense_array(plot_array['train']['ppl'], slot), 'b-', linewidth=1)
    ax1.plot(condense_array(plot_array['val']['ppl'], slot), 'b:', linewidth=1)
    
    plt.legend(['PPL-Train', 'PPL-Val'], loc='upper center', bbox_to_anchor=(0.25, 1.10),
          ncol=1, fancybox=True, shadow=True)
        
    ax2 = ax1.twinx()
    ax2.set_ylabel('ACC ', color='r')
    ax2.tick_params('y', colors='r')
    ax2.plot(condense_array(plot_array['train']['acc'], slot), 'r-', linewidth=1)
    ax2.plot(condense_array(plot_array['val']['acc'], slot), 'r:', linewidth=1)
    
    plt.legend(['ACC-Train', 'ACC-Val'], loc='upper center', bbox_to_anchor=(0.75, 1.10),
          ncol=1, fancybox=True, shadow=True)
    
    plt.savefig(result_folder + '/' + str(batch_num) + '.png') 


def main():
    src_file = "../data/squad/train-v1.1.json"
    analyze(src_file)
            
if __name__ == "__main__":
    main()