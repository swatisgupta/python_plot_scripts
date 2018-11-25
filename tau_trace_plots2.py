#!/usr/bin/python

from __future__ import division 
from ctypes import *
import sys
import math
import matplotlib.pyplot as plt
import numpy

class TAU_EV32(Structure):
    _fields_ = [ ('ev', c_int),
                 ('nid', c_ushort ), #unsigned short),
                 ('tid', c_ushort ), #unsigned short),
                 ( 'par', c_ulonglong),
                 ( 'ti', c_ulonglong ) ]

Colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan', 'blue', 'orange']

# for 64 bit platforms
#class TAU_EV64(Structure):
#    _fields_ = [ ('ev', int),
#                 ('nid', unsigned short),
#                 ('tid', unsigned short),
#                 ('padding', unsigned int),
#                 ( 'par', long long int),
#                 ( 'ti', unsigned long long int) ]

#Read Event types
#Know what events to read -- command line arguments??
#Note the time and value of that event
#dump to a file or plot it
image_path = "."
max_cnt = 0
max_len = 0
max_len2 = 0
max_mem = 6000000000
max_miss = 20
function_id = {}
tag = {}
unmap = {}
mylist = {}
L1 = 0
L2 = 1
L3 = 2
LD = 4
ST = 5
TCYC = 6
VHWM = 7
RSS = 8
TOT = 9
FP = 10

unmap[L1] = -1
unmap[L2] = -1
unmap[L3] = -1
unmap[FP] = -1
unmap[TOT] = -1
unmap[LD] = -1
unmap[ST] = -1
unmap[TCYC] = -1
unmap[VHWM] = -1
unmap[RSS] = -1

def get_event(event_id):
    if event_id == unmap[L1]:
        return 1
    elif event_id == unmap[L2]:
        return 1
    elif event_id == unmap[L3]:
        return 1
    elif event_id == unmap[TOT]:
        return 1
    elif event_id == unmap[LD]:
        return 1
    elif event_id == unmap[ST]:
        return 1
    elif event_id == unmap[TCYC]:
        return 1
    elif event_id == unmap[FP]:
        return 1
    elif event_id == unmap[VHWM]:
        return 1
    elif event_id == unmap[RSS]:
        return 1
    else:
        return 0
 
def get_trigger(word):
    #print(word)
    if word == "PAPI_L1_TCM":
        trigger = L1
        print("Found PAPI_L1_TCM")
    elif word == "PAPI_L2_TCM":
        trigger = L2
        print("Found PAPI_L2_TCM")
    elif word == "PAPI_L3_TCM":
        trigger = L3
        print("Found PAPI_L3_TCM")
    elif word == "PAPI_TOT_INS":
        trigger = TOT
        print("Found PAPI_TOT_INS")
    elif word == "PAPI_FP_INS":
        trigger = FP
        print("Found PAPI_FP_INS")
    elif word == "PAPI_LD_INS":
        trigger = LD
        print("Found PAPI_LD_INS")
    elif word == "PAPI_SR_INS":
        trigger = ST
        print("Found PAPI_SR_INS")
    elif word == "PAPI_TOT_CYC":
        trigger = TCYC
        print("Found PAPI_TOT_CYC")
    elif word == "Peak Memory Usage Resident Set Size (VmHWM) (KB)" :
        trigger = VHWM
        print("Found VnHWM")
    elif word == "Memory Footprint (VmRSS) (KB)":
        trigger = RSS
        print("Found Memory Footprint (VmRSS) (KB)")
    else:
       trigger = -1
    return trigger
	  
def read_edf(name):
    with open(name, 'r') as f:
        line = f.readline()        
        line = f.readline()        
        for line in f:
            words = line.split('\"')
            #print(words)
            trigger = get_trigger(words[1])
            if ( trigger != -1 ) :
                words2 = words[0].split(' ')
                #print(words2) 
                #print(trigger)
                #function_id[trigger] = int(words2[0])
                function_id[int(words2[0])] = trigger
               
                unmap[trigger] = int(words2[0])
                #print(function_id[trigger])
                #print(tag[trigger])



def read_trace(tracedir, nprocs, nthreads):
    i = 0
    #print nthreads
    for i in range(nprocs):
        dicts = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
        j = 0
        while j < nthreads:
            name = tracedir + "/tautrace." + str(i) + ".0." + str(j) +".trc"                
            print name

            with open(name, 'rb') as f:
                event = TAU_EV32()
                while True:
                #for chunk in iter(partial(f.read, 192), ''):
                    nrd = f.readinto(event)
                    if nrd == 0:
                        break
                    #print ("Event is" , event.ev, " nprocs is ", event.nid, " thread is ", event.tid, " parameter id is", event.par, " timestamp is", event.ti  )        
                    #print(event.nid)        
                    #print(event.tid)        

                    if get_event(event.ev) == 1:
                        dicts[event.ev][event.ti] = event.par
                    #print(dicts)
            j += 1
        mylist[i] = dicts           
        #print i
    print "Done with read traces"

def getAllKeys(dict, nths, index):
    i = 0
    global max_len
    global max_len2

    all_keys = {}
    while i < nths:
        key_vals = []
        dictth = dict[i]
        keys = sorted(dict[i][index])
        for key in keys:
            if dictth[index][key] == 0 and (index == unmap[VHWM] or index == unmap[RSS]):
                continue;
            else:    
                vals.append(key)
        all_keys[i] = key_vals
    return all_keys


def getvalues(dict, nths, index):
    i = 0
    global max_len
    global max_len2
    all_vals = {}
    while i < nths:
        vals = []
        dictth = dict[i]
        keys = sorted(dict[i][index])
        for key in keys:
            if dictth[index][key] == 0 and (index == unmap[VHWM] or index == unmap[RSS]):
                continue;
            else:    
                vals.append(dictth[index][key])
        all_vals[i] = vals
    
        curr_len = len(vals)
        if index == unmap[VHWM] or index == unmap[RSS]:
            if curr_len > max_len2:
                max_len2 = curr_len
        else:
            if curr_len > max_len:
                max_len = curr_len
        i += 1

    return all_vals

def plot_memory(nprocs, plt, nrows, vals, title):
    plt.figure(title)
    plt.title(title, fontsize=12)
    global max_mem
    global max_len2
    print nprocs 
    #plt.subplots(int(nrows), 2, sharex=True, sharey=True)

    for i in range(nprocs):
        labl = "Process " + str(i)
        if i > 0:
            sp = plt.subplot(nrows, 2, i+1, sharex = spp, sharey = spp)
        else: 
            sp = plt.subplot(nrows, 2, i+1, sharex = True, sharey = True)
            spp = sp

        sp.set_title(labl);
        sp.set_xlim([0, max_len2]);
        sp.set_ylim([0, max_mem]);
        plt.subplots_adjust(wspace=0.2, hspace=0.26) 
        plt.ylabel('KiloBytes')
        plt.xlabel('Time in seconds')
        ax = plt.axes( yscale='log')
        color=Colors[i]
        sp.plot(vals[i], label=labl, color=color)
        #plt.legend(shadow=True, fancybox=True, fontsize='xx-small', loc=9, ncol=10)
    save_plot(plt, title)

def plot_memory_ravg(nprocs, plt, nrows, vals, running_avg, running_avg2, window, title):
    #plt.figure(title)
    #plt.title(title, fontsize=12)
    global max_mem
    global max_len2
    print nprocs 
    #plt.subplots_adjust(wspace=0.4, hspace=1.5) 
    fig, sp = plt.subplots(int(nrows), 2, sharex=True, sharey=True)
    plt.subplots_adjust(wspace=0.2, hspace=0.26) 
    fig.suptitle(title)
    row_cnt = 0
    j = 0
    for i in range(nprocs):
        labl = "Process " + str(i)
        labl2='Running avg of ' + str(window)+ 'vals' 
        #sp = plt.subplot(nrows, 2, i+1 )
        if j == 2:
           j = 0
           row_cnt = row_cnt + 1
        
        #sp = plt.subplot(nrows, 2, i+1, sharex = spp, sharey = spp)
        #sp[row_cnt, j].set_title(labl);
        sp[row_cnt, j].set_xlim([0, max_len2]);
        sp[row_cnt, j].set_ylim([0, max_mem]);
        color=Colors[i]
        sp[row_cnt, j].plot(vals[i], label=labl, color=color)
        if j == 0:
            sp[row_cnt, j].set_ylabel('KiloBytes')

        if row_cnt == nrows - 1:
            sp[row_cnt, j].set_xlabel('Time in seconds')

        color=Colors[i + 1]
        sp[row_cnt, j].plot(running_avg[i], linestyle=':', label='Running avg', color=color)
        color=Colors[i + 2]
        run_avg = numpy.zeros([window])
        run_avg1 = numpy.append(run_avg, running_avg2[i])
        sp[row_cnt, j].plot(run_avg1, linestyle='-.', label=labl2, color=color)
        #plt.legend(fontsize='xx-small', loc="lower right", ncol=3, mode="expand", bbox_to_anchor=(0,1.02,1,0.2))
        sp[row_cnt, j].legend(fontsize='xx-small', loc="lower right", ncol=3, bbox_to_anchor=(0.15,0.95,0.95,0.1))
        #sp[row_cnt, j].legend(fontsize='xx-small', loc="lower left", ncol=1, bbox_to_anchor=(1.04,0))
        j = j + 1
    save_plot(plt, title)

def plot_memory_boxplots(nprocs, plt, nrows, vals, title):
    global max_mem
    global max_len2
    print nprocs 
    global max_cnt
    row_cnt = j = 0
    fig, sp = plt.subplots(int(nrows), 2, sharex = True, sharey = True )
    plt.subplots_adjust(wspace=0.2, hspace=0.4) 
    fig.suptitle(title + " part 1")
    for i in range(nprocs):
        labl = "Process " + str(i)
        #sp = plt.subplot(nrows, 2, i+1 )
        if j == 2:
           j = 0
           row_cnt = row_cnt + 1
        sp[row_cnt, j].set_title(labl);
        sp[row_cnt, j].set_xlim([0, max_len2]);
        sp[row_cnt, j].set_ylim([0, max_mem]);
        if j == 0:
            sp[row_cnt, j].set_ylabel('KiloBytes')
        sp[row_cnt, j].boxplot(vals[i])
        j += 1
    save_plot(plt, title)

def plot_histogram(nprocs, plt, nrows, vals, vals_map, title):
    #plt.figure(title)
    #plt.title(title, fontsize=12)
    global max_mem
    global max_len2
    global max_cnt
    fig, sp = plt.subplots(int(nrows), 2, sharex = True)
    plt.subplots_adjust(wspace=0.2, hspace=0.4) 
    fig.suptitle(title + " part 1")
    print nprocs 
    for i in range(int(nrows)):
        labl = "Process " + str(i) +  ": Vals"
        org = range(len(vals[i]))
        sp[i, 0].set_title(labl);
        sp[i, 0].set_xlim([0, len(vals_map[i])])
        sp[i, 0].set_ylim([0, max_mem]);
        color=Colors[i]
        sp[i, 0].bar(org, vals_map[i], width=0.1)
        labl = "Process " + str(i) + ": Frequency"
        sp[i, 1].set_title(labl);
        sp[i, 1].set_xlim([0, len(vals_map[i])])
        sp[i, 1].set_ylim([0, max_cnt + 1])
        sp[i, 1].bar(org, vals[i],  width=0.5) 
        sp[i, 1].set_ylabel('#occurences')
    save_plot(plt, title + " part 1")
    
    fig, sp = plt.subplots(int(nrows), 2, sharex=True)
    plt.subplots_adjust(wspace=0.2, hspace=0.4) 
    fig.suptitle(title + " part 2")
    for i in range(int(nrows), nprocs):
        labl = "Process " + str(i) +  ": Vals"
        org = range(len(vals[i]))
        sp[i - nrows, 0].set_title(labl);
        sp[i - nrows, 0].set_xlim([0, len(vals_map[i])])
        sp[i - nrows, 0].set_ylim([0, max_mem]);
        color=Colors[i]
        sp[i - nrows, 0].bar(org, vals_map[i], width=0.1)
        labl = "Process " + str(i) + ": Frequency"
        sp[i - nrows, 1].set_title(labl);
        sp[i - nrows, 1].set_xlim([0, len(vals_map[i])])
        sp[i - nrows, 1].set_ylim([0, max_cnt + 1])
        sp[i - nrows, 1].bar(org, vals[i], width=0.5) 
        sp[i - nrows, 1].set_ylabel('#occurences')
    save_plot(plt, title + " part 2")


def plot_papi_boxplots(nprocs, plt, nrows, vals, vals_tot, title):
    global max_miss
    global max_len
    print nprocs 
    fig, sp = plt.subplots(int(nrows), 2, sharex=True, sharey=True)
    plt.subplots_adjust(wspace=0.2, hspace=0.4) 
    fig.suptitle(title)
    row_cnt = j = 0
    for i in range(nprocs):
        labl = "Process " + str(i)
        #sp = plt.subplot(nrows, 2, i+1 )
        if j == 2:
            j = 0
            row_cnt = row_cnt + 1
        sp[row_cnt, j].set_title(labl);
        sp[row_cnt, j].set_xlim([0, max_len]);
        sp[row_cnt, j].set_ylim([0, max_miss]);
        color=Colors[i]
        l_p = [x/y*100 for x,y in zip(vals[i] , vals_tot[i])]
        sp[row_cnt, j].boxplot(l_p)
        j = j + 1
    save_plot(plt, title)

def plot_papi(nprocs, plt, nrows, val_l, title):
    global max_miss
    global max_len
    fig, sp = plt.subplots(int(nrows), 2, sharex=True, sharey=True)
    plt.subplots_adjust(wspace=0.2, hspace=0.4) 
    fig.suptitle(title)
    row_cnt = j = 0
    for i in range(nprocs):
        labl = "Process " + str(i)
        #sp = plt.subplot(nrows, 2, i+1 )
        if j == 2:
            j = 0
            row_cnt = row_cnt + 1
        sp[row_cnt, j].set_xlim([0, max_len]);
        #sp.set_ylim([0, max_miss]);
        sp[row_cnt, j].set_title(labl);
        color=Colors[i]
        sp[row_cnt, j].plot(val_l[i], label=labl, color=color)
        j += 1
    save_plot(plt, title)

def plot_papi_percentage(nprocs, plt, nrows, val_l, val_tot, title):
    global max_miss
    global max_len
    fig, sp = plt.subplots(int(nrows), 2, sharex=True, sharey=True)
    plt.subplots_adjust(wspace=0.2, hspace=0.4) 
    fig.suptitle(title)
    row_cnt = j = 0
    for i in range(nprocs):
        labl = "Process " + str(i)
        #sp = plt.subplot(nrows, 2, i+1 )
        if j == 2:
            j = 0
            row_cnt = row_cnt + 1
        sp[row_cnt, j].set_title(labl);
        sp[row_cnt, j].set_xlim([0, max_len]);
        sp[row_cnt, j].set_ylim([0, max_miss]);
        plt.subplots_adjust(wspace=0.7, hspace=0.7) 
        color=Colors[i]
        sp[row_cnt, j].set_ylabel('% misses')
        l_p = [x/y*100 for x,y in zip(val_l[i] , val_tot[i])]
        sp[row_cnt, j].plot(l_p, label=labl, color=color)
        j += 1
    save_plot(plt, title)

def plot_papi_bandwidth(nprocs, plt, nrows, val_l, val_tcyc, title):
    global max_miss
    global max_len
    fig, sp = plt.subplots(int(nrows), 2, sharex=True, sharey=True)
    plt.subplots_adjust(wspace=0.2, hspace=0.4)
    fig.suptitle(title)
    row_cnt = j = 0
    for i in range(nprocs):
        labl = "Process " + str(i)
        #sp = plt.subplot(nrows, 2, i+1 )
        if j == 2:
            j = 0
            row_cnt = row_cnt + 1
        sp[row_cnt, j].set_title(labl);
        sp[row_cnt, j].set_xlim([0, max_len]);
        #sp[row_cnt, j].set_ylim([0, ]);
        plt.subplots_adjust(wspace=0.7, hspace=0.7)
        color=Colors[i]
        sp[row_cnt, j].set_ylabel('(GB/s)')
        l_p = [(((x * 64)/y) * 2.8) for x,y in zip(val_l[i] , val_tcyc[i])]
        sp[row_cnt, j].plot(l_p, label=labl, color=color)
        j += 1
    save_plot(plt, title)


def plot_cummulative_mem(nprocs, plt, nrows, vals_vmhwm, vals_rss):
    plt.figure("Cummulative Virtual Memory high water mark")
    sp = plt.subplot(211)
    global max_mem
    global max_len2
    sp.set_xlim([0, max_len2]);
    sp.set_ylim([0, max_mem * nprocs]); 
    plt.ylabel('Kilo Bytes')
    sp.set_title('Cummulative virtual memory High Water Mark', fontsize=12)
    c = vals_vmhwm[0]
    for i in range(1,nprocs):
        labl = "thread " + str(i)
        c1 = [x+y for x,y in zip(vals_vmhwm[i], c)]
        c = c1
    sp.plot(c)

    sp = plt.subplot(212)
    sp.set_title('Cummulative Resident Set Size', fontsize=12)
    sp.set_xlim([0, max_len]);
    sp.set_ylim([0, max_mem*nrocs]);

    plt.ylabel('Kilo Bytes')
    c = vals_rss[0]
    for i in range(1,nprocs):
        c1 = [x+y for x,y in zip(vals_rss[i], c)]
        c = c1
    sp.plot(c)        
    save_plot(plt, title)    

def running_mean(x):
    cumsum = numpy.cumsum(numpy.insert(x, 0, 0)) 
    sz = cumsum.size
    N = list(range(1,sz))
    #print(cumsum)
    #print(N)
    avg = [x/y for x,y in zip(cumsum, N)]
    return avg

def running_mean2(x, N):
    cumsum = numpy.cumsum(numpy.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / float(N)


def save_plot(plt, title):
    global image_path
    plt.savefig(image_path + "/" + title + ".png")

def consecutive_count(x, map):
    m = len(x)
    consc_cnt = []
    val = x[0]
    cnt = 1
    k = 0
    global max_cnt

    for i in range(1, m):
        if val == x[i]:
            cnt = cnt + 1
        else:
            consc_cnt.append(cnt); 
            if max_cnt < cnt:
                max_cnt = cnt
            cnt = 1
            map.append(val)
            k = k + 1
            val = x[i]
    return consc_cnt
  
         
def main():
    if len(sys.argv) != 5:
       print("Usage: python tau_python.py tracedir nprocs nthreads")
    
    tracedir = sys.argv[1]
    nprocs = int(sys.argv[2]) 
    nthreads = int(sys.argv[3])
    global image_path
    image_path = sys.argv[4]
    edffile = tracedir + "/events.0.edf"
    #tracefile = tracedir + "/tautrace.0." + nprocs + ".0" + ".trc"
    #print(len(sys.argv))
    #print(edffile)
    read_edf(edffile)

    read_trace(tracedir, nprocs, nthreads)

    #return
    vals_vmhwm = getvalues(mylist, nprocs, unmap[VHWM])
    vals_rss = getvalues(mylist, nprocs, unmap[RSS])
    vals_l1 = getvalues(mylist, nprocs, unmap[L1])
    vals_l2 = getvalues(mylist, nprocs, unmap[L2])
    vals_l3 = getvalues(mylist, nprocs, unmap[L3])
    #vals_tot = getvalues(mylist, nprocs, unmap[TOT])
    vals_ld = getvalues(mylist, nprocs, unmap[LD])
    vals_st = getvalues(mylist, nprocs, unmap[ST])
    vals_tcyc = getvalues(mylist, nprocs, unmap[TCYC])
    keys_rss = getAllKeys(mylist, nprocs, unmap[RSS])
    #vals_fp = getvalues(mylist, nprocs, unmap[FP])
   
    nrows = math.ceil(nprocs/2)
    val_l1=[]
    val_l2=[]
    val_l3=[]
    #val_tot=[]
    val_tot2=[]
    val_ld=[]
    val_st=[]
    val_tcyc=[]
    val_vmhwm=[]
    val_rss=[]
    val_vmhwm2=[]
    val_rss2=[]
    val_vmhwm_ccnt=[]
    val_rss_ccnt=[]
    val_map_vmhwm = []
    val_map_rss = []
    global max_mem
    max_mem = 0
    avg_window = 5

    for i in range(nprocs):
        print i 
        if max_mem < max(vals_vmhwm[i]):
            max_mem = max(vals_vmhwm[i])

        val_l1.append([j-k for k, j in zip(vals_l1[i][:-1], vals_l1[i][1:])])
        val_l2.append([j-k for k, j in zip(vals_l2[i][:-1], vals_l2[i][1:])])
        val_l3.append([j-k for k, j in zip(vals_l3[i][:-1], vals_l3[i][1:])])
        #val_tot.append([j-k for k, j in zip(vals_tot[i][:-1], vals_tot[i][1:])])
        val_ld.append([j-k for k, j in zip(vals_ld[i][:-1], vals_ld[i][1:])])
        val_tcyc.append([j-k for k, j in zip(vals_tcyc[i][:-1], vals_tcyc[i][1:])])
        val_st.append([j-k for k, j in zip(vals_st[i][:-1], vals_st[i][1:])])
        val_tot2.append([j+k for k, j in zip(vals_st[i], vals_ld[i])])
        val_vmhwm.append(running_mean(vals_vmhwm[i])) 
        val_rss.append(running_mean(vals_rss[i])) 
        val_vmhwm2.append(running_mean2(vals_vmhwm[i], avg_window)) 
        val_rss2.append(running_mean2(vals_rss[i], avg_window)) 
        map = []
        val_vmhwm_ccnt.append(consecutive_count(vals_vmhwm[i], map)) 
        val_map_vmhwm.append(map)
        map = []
        val_rss_ccnt.append(consecutive_count(vals_rss[i], map)) 
        val_map_rss.append(map)

    #plot_memory(nprocs, plt, nrows, vals_vmhwm, "Virtual Memory High Water Mark")
    plot_memory(nprocs, plt, nrows, keys_rss, "Resident Set Size Timestamps")

    plot_memory_ravg(nprocs, plt, nrows, vals_vmhwm, val_vmhwm, val_vmhwm2, avg_window, "Virtual Memory High Water Mark")
    plot_memory_ravg(nprocs, plt, nrows, vals_rss, val_rss, val_rss2, avg_window, "Resident Set Size")
    plot_memory_boxplots(nprocs, plt, nrows, vals_vmhwm, "Boxplots: Virtual Memory High Water Mark")
    plot_memory_boxplots(nprocs, plt, nrows, vals_rss, "Boxplots: Resident Set Size")
    plot_histogram(nprocs, plt, nrows, val_vmhwm_ccnt, val_map_vmhwm, "Consecutive Counts: Virtual Memory High Water Mark")
    plot_histogram(nprocs, plt, nrows, val_rss_ccnt, val_map_rss, "Consecutive Counts: Resident Set Size")
    #plot_histogram(nprocs, plt, nrows, val_map_vmhwm, "Consecutive Vals: Virtual Memory High Water Mark")
    #plot_histogram(nprocs, plt, nrows, val_map_rss, "Consecutive Vals: Resident Set Size")

#    plot_papi_percentage(nprocs, plt, nrows, val_l1, val_tot, "Percentage of L1 Cache misses wrt total operations")
#    plot_papi_percentage(nprocs, plt, nrows, val_l2, val_tot, "Percentage of L2 Cache misses wrt total operations")
#    plot_papi_percentage(nprocs, plt, nrows, val_l3, val_tot, "Percentage of L3 Cache misses wrt total operations")
#    plot_papi_boxplots(nprocs, plt, nrows, val_l1, val_tot, "Boxplots: Percentage of L1 Cache misses wrt total operations")
#    plot_papi_boxplots(nprocs, plt, nrows, val_l2, val_tot, "Boxplots: Percentage of L2 Cache misses wrt total operations")
#    plot_papi_boxplots(nprocs, plt, nrows, val_l3, val_tot, "Boxplots: Percentage of L3 Cache misses wrt total operations")

    plot_papi_percentage(nprocs, plt, nrows, val_l1, val_tot2, "Percentage of L1 Cache misses wrt total LD & SR operations")
    plot_papi_percentage(nprocs, plt, nrows, val_l2, val_tot2, "Percentage of L2 Cache misses wrt total LD & SR operations")
    plot_papi_percentage(nprocs, plt, nrows, val_l3, val_tot2, "Percentage of L3 Cache misses wrt total LD & SR operations")
    plot_papi_boxplots(nprocs, plt, nrows, val_l1, val_tot2, "Boxplots: Percentage of L1 Cache misses wrt total LD & SR operations")
    plot_papi_boxplots(nprocs, plt, nrows, val_l2, val_tot2, "Boxplots: Percentage of L2 Cache misses wrt total LD & SR operations")
    plot_papi_boxplots(nprocs, plt, nrows, val_l3, val_tot2, "Boxplots: Percentage of L3 Cache misses wrt total LD & SR operations")

    plot_papi_bandwidth(nprocs, plt, nrows, val_l1, val_tcyc, "Bandwidth L1")
    plot_papi_bandwidth(nprocs, plt, nrows, val_l2, val_tcyc, "Bandwidth L2")
    plot_papi_bandwidth(nprocs, plt, nrows, val_l3, val_tcyc, "Bandwidth L3") 
    #plt.show()


if __name__ == "__main__":
    main()	 
