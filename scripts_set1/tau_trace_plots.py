e!/usr/bin/python

from __future__ import division 
from ctypes import *
import sys
import math
import matplotlib.pyplot as plt

class TAU_EV32(Structure):
    _fields_ = [ ('ev', c_int),
                 ('nid', c_ushort ), #unsigned short),
                 ('tid', c_ushort ), #unsigned short),
                 ( 'par', c_ulonglong),
                 ( 'ti', c_ulonglong ) ]

Colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']

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
FP = 4
TOT = 3
VHWM = 5
RSS = 6
unmap[L1] = -1
unmap[L2] = -1
unmap[L3] = -1
unmap[FP] = -1
unmap[TOT] = -1
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
    while i < nprocs:
        name = tracedir + "/tautrace." + str(i) + ".0.0.trc"     
        #print name
        dicts = [{}, {}, {}, {}, {}, {}, {}, {}]
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
        mylist[i] = dicts           
        #print(mylist[i])
        i += 1


def getvalues(dict, nths, index):
    i = 0
    curr_len = len(dict[i][index])
    global max_len
    global max_len2

    if index == unmap[VHWM] or index == unmap[RSS]:
        if curr_len > max_len2:
           max_len2 = curr_len
    else:
        if curr_len > max_len:
            max_len = curr_len

    all_vals = {}
    while i < nths:
        vals = []
        dictth = dict[i]
        keys = sorted(dict[i][index])
        for key in keys:
            vals.append(dictth[index][key])
        all_vals[i] = vals
        i += 1
    return all_vals

def main():
    if len(sys.argv) != 4:
       print("Usage: python tau_python.py tracedir nprocs nthreads")
    
    tracedir = sys.argv[1]
    nprocs = int(sys.argv[2]) 
    nthreads = int(sys.argv[3])
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
    vals_tot = getvalues(mylist, nprocs, unmap[TOT])
    vals_fp = getvalues(mylist, nprocs, unmap[FP])
   
    nrows = math.ceil(nprocs/2)

    max_mem = 0
    for i in range(nprocs):
        if max_mem < max(vals_vmhwm[i]):
            max_mem = max(vals_vmhwm[i])

    plt.figure("Virtual Memory high water mark")
    plt.title('Virtual memory High Water Mark', fontsize=12)
    print nprocs 
    for i in range(nprocs):
        labl = "Process " + str(i)
        sp = plt.subplot(nrows, 2, i+1 )
        sp.set_title(labl);
        sp.set_xlim([0, max_len2]);
        sp.set_ylim([0, max_mem]);
        plt.subplots_adjust(wspace=1.0, hspace=1.0) 
        plt.ylabel('Kilo Bytes')
        color=Colors[i]
        sp.plot(vals_vmhwm[i], label=labl, color=color)
        #plt.legend(shadow=True, fancybox=True, fontsize='xx-small', loc=9, ncol=10)

    plt.figure("Resident Set Size")
    plt.title('Resident Set Size', fontsize=12)
    for i in range(nprocs):
        labl = "Process " + str(i)
        sp = plt.subplot(nrows, 2, i+1 )
        sp.set_xlim([0, max_len2]);
        sp.set_ylim([0, max_mem]);
        plt.subplots_adjust(wspace=1.0, hspace=1.0) 
        plt.ylabel('Kilo Bytes')
        color=Colors[i]
        sp.set_title(labl);
        sp.plot(vals_rss[i], label=labl, color=color)
        #plt.legend(shadow=True, fancybox=True, fontsize='xx-small', loc=9, ncol=10)

#    plt.figure("Cummulative Virtual Memory high water mark")
#    sp = plt.subplot(211)
#    sp.set_xlim([0, max_len]);
#    sp.set_ylim([0, max_mem*nrocs]); 
#    plt.ylabel('Kilo Bytes')
#    sp.set_title('Cummulative virtual memory High Water Mark', fontsize=12)
#    c = vals_vmhwm[0]
#    for i in range(1,nprocs):
#        labl = "thread " + str(i)
#        c1 = [x+y for x,y in zip(vals_vmhwm[i], c)]
#        c = c1
#    sp.plot(c)
#
#    sp = plt.subplot(212)
#    sp.set_title('Cummulative Resident Set Size', fontsize=12)
#    sp.set_xlim([0, max_len]);
#    sp.set_ylim([0, max_mem*nrocs]);
#
#    plt.ylabel('Kilo Bytes')
#    c = vals_rss[0]
#    for i in range(1,nprocs):
#        c1 = [x+y for x,y in zip(vals_rss[i], c)]
#        c = c1
#    sp.plot(c)        
#
    plt.figure("L1 Cache Misses")
    plt.title('L1 Cache Misses', fontsize=12)
    val_l1 = []
    for i in range(nprocs):
        labl = "Process " + str(i)
        sp = plt.subplot(nrows, 2, i+1 )
        sp.set_xlim([0, max_len]);
        #sp.set_ylim([0, max_miss]);

        sp.set_title(labl);
        plt.subplots_adjust(hspace=0.7, wspace=0.5) 
        color=Colors[i]
        val_l1.append([j-k for k, j in zip(vals_l1[i][:-1], vals_l1[i][1:])])
        plt.plot(val_l1[i], label=labl, color=color)
#        
#
#    plt.figure("L2 Cache Misses")
#    plt.title('L2 Cache Misses', fontsize=12)
    val_l2 = [] 
    for i in range(nprocs):
#        labl = "Process " + str(i)
#        sp = plt.subplot(nrows, 2, i+1 )
#        sp.set_title(labl);
#        sp.set_xlim([0, max_len]);
#        sp.set_ylim([0, max_miss]);
#        plt.subplots_adjust(wspace=0.7, hspace=0.7) 
#        color=Colors[i]
        val_l2.append([j-k for k, j in zip(vals_l2[i][:-1], vals_l2[i][1:])])
#        plt.plot(val_l2[i], label=labl, color=color)
#        
#
#    plt.figure("L3 Cache Misses")
#    plt.title('L3 Cache Misses', fontsize=12)
    val_l3 = []
    for i in range(nprocs):
#        labl = "Process " + str(i)
#        sp = plt.subplot(nrows, 2, i+1 )
#        sp.set_title(labl);
#        sp.set_xlim([0, max_len]);
#        sp.set_ylim([0, max_miss]);
#        plt.subplots_adjust(wspace=0.7, hspace=0.7) 
#        color=Colors[i]
        val_l3.append([j-k for k, j in zip(vals_l3[i][:-1], vals_l3[i][1:])])
#        plt.plot(val_l3[i], label=labl, color=color)
#        

   
#    plt.figure("Total operations")
#    plt.title('Total operations', fontsize=12)
    val_tot = []
    for i in range(nprocs):
#        labl = "Process " + str(i)
#        sp = plt.subplot(nrows, 2, i+1 )
#        sp.set_title(labl);
#        sp.set_xlim([0, max_len]);
#        sp.set_ylim([0, max_miss]);
#        plt.subplots_adjust(wspace=0.7, hspace=0.7) 
#        color=Colors[i]
        val_tot.append([j-k for k, j in zip(vals_tot[i][:-1], vals_tot[i][1:])])
#        plt.plot(val_tot[i], label=labl, color=color)
        #plt.legend(shadow=True, fancybox=True, fontsize='xx-small', loc=9, ncol=10)
        

    #plt.subplot(212)
    #plt.title('FP operations', fontsize=12)
    #val_fp = []

    #for i in range(nthreads):
    #    labl = "process " + str(i)
    #    val_fp.append([j-k for k, j in zip(vals_fp[i][:-1], vals_fp[i][1:])])
    #    plt.plot(val_fp[i], label=labl)
    #plt.legend(shadow=True, fancybox=True, fontsize='xx-small', loc='lower right')
    #plt.legend(shadow=True, fancybox=True, fontsize='xx-small', loc=9, ncol=10)
        
    #plt.show()

    plt.figure("Percentage of L1 cache misses wrt Total operations")
    plt.title('L1 Cache Misses', fontsize=12)
    for i in range(nprocs):
        labl = "Process " + str(i)
        sp = plt.subplot(nrows, 2, i+1 )
        sp.set_title(labl);
        sp.set_xlim([0, max_len]);
        sp.set_ylim([0, max_miss]);
        plt.subplots_adjust(wspace=0.7, hspace=0.7) 
        #plt.subplots_adjust(wspace=1.0, hspace=1.0) 
        color=Colors[i]
        plt.ylabel('% of Cache misses')
        l1_p = [x/y*100 for x,y in zip(val_l1[i] , val_tot[i])]
        plt.plot(l1_p, label=labl, color=color)
    #plt.legend(shadow=True, fancybox=True, fontsize='xx-small', loc='lower right')
    plt.legend(shadow=True, fancybox=True, fontsize='xx-small', loc=9, ncol=10)
        

    plt.figure("Percentage of L2 cache misses wrt Total operations")
    plt.title('L2 Cache Misses', fontsize=12)
    for i in range(nprocs):
        labl = "Process " + str(i)
        sp = plt.subplot(nrows, 2, i+1 )
        sp.set_title(labl);
        sp.set_xlim([0, max_len]);
        sp.set_ylim([0, max_miss]);
        plt.subplots_adjust(wspace=0.7, hspace=0.7) 
        #plt.subplots_adjust(wspace=1.0, hspace=1.0) 
        color=Colors[i]
        plt.ylabel('% of Cache misses')
        l2_p = [x/y*100 for x,y in zip(val_l2[i] , val_tot[i])]
        plt.plot(l2_p, label=labl, color=color)
    #plt.legend(shadow=True, fancybox=True, fontsize='xx-small', loc='lower right')
    plt.legend(shadow=True, fancybox=True, fontsize='xx-small', loc=9, ncol=10)
        

    plt.figure("Percentage of L3 cache misses wrt Total operations")
    plt.ylabel('% of Cache misses')
    plt.title('L3 Cache Misses', fontsize=12)
    for i in range(nprocs):
        labl = "Process " + str(i)
        sp = plt.subplot(nrows, 2, i+1 )
        sp.set_title(labl);
        sp.set_xlim([0, max_len]);
        sp.set_ylim([0, max_miss]);
        plt.subplots_adjust(wspace=0.7, hspace=0.7) 
        #plt.subplots_adjust(wspace=1.0, hspace=1.0) 
        color=Colors[i]
        plt.ylabel('% of Cache misses')
        l3_p = [x/y*100 for x,y in zip(val_l3[i] , val_tot[i])]
        plt.plot(l3_p, label=labl, color=color)
    #plt.legend(shadow=True, fancybox=True, fontsize='xx-small', loc=9, bbox_to_anchor=(1, 0.5), ncol=4)
    #plt.legend(shadow=True, fancybox=True, fontsize='xx-small', loc=9, ncol=10)
        
    plt.show()

    #plt.figure("% of cache misses wrt Floating point operations")
    #l1_p2 = [x/y for x,y in zip(vals_l1 , vals_fp)]
    #l2_p2 = [x/y for x,y in zip(vals_l2 , vals_fp)]
    #l3_p2 = [x/y for x,y in zip(vals_l3 , vals_fp)]
    #plt.subplot(311)
    #plt.title('L1 Cache Misses')
    #plt.plot(l1_p2)
    #plt.subplot(312)
    #plt.title('L2 Cache Misses')
    #plt.plot(l2_p2)
    #plt.subplot(313)
    #plt.title('L3 Cache Misses')
    #plt.plot(l3_p2)
    #plt.show()

    #print(dicts[2])

if __name__ == "__main__":
    main()	 
