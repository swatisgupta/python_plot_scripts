#!/usr/bin/python

from __future__ import division 
from ctypes import *
import sys
import matplotlib.pyplot as plt

class TAU_EV32(Structure):
    _fields_ = [ ('ev', c_int),
                 ('nid', c_ushort ), #unsigned short),
                 ('tid', c_ushort ), #unsigned short),
                 ( 'par', c_ulonglong),
                 ( 'ti', c_ulonglong ) ]

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
function_id = {}
tag = {}
unmap = {}
dicts = [{}, {}, {}, {}, {}, {}, {}, {}]
L1 = 0
L2 = 1
L3 = 2
FP = 4
TOT = 3
VHWM = 5
RSS = 6

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



def read_trace(name):
    time = c_ulonglong(0)
    i = 0
    with open(name, 'rb') as f:
        event = TAU_EV32()
        while True:
            i = i + 1
        #for chunk in iter(partial(f.read, 192), ''):
            nrd = f.readinto(event)
            #ev = f.read(32)
            if nrd == 0:
                break
            #print(ev)        
            #print ("Event is" , event.ev, " node is ", event.nid, " thread is ", event.tid, " parameter id is", event.par, " timestamp is", event.ti  )        
            #print(event.nid)        
            #print(event.tid)        
            if i > 1: 
                if get_event(event.ev) == 1:
                    #print("time is ", time)
                    dicts[event.ev][event.ti] = event.par
            else:
                if get_event(event.ev) == 1:
                    dicts[event.ev][0] = event.par
                time = c_ulonglong(event.ti)  
                #print("Initial time is ", event.ti)

def main():
    if len(sys.argv) != 4:
       print("Usage: python tau_python.py tracedir node nthreads")
    
    tracedir = sys.argv[1]
    node = sys.argv[2] 
    nthreads = sys.argv[3]
    edffile = tracedir + "/events." + node + ".edf"
    tracefile = tracedir + "/tautrace.0." + node + ".0" + ".trc"
    #print(len(sys.argv))
    #print(edffile)
    read_edf(edffile)

    read_trace(tracefile)

    vmhwm = sorted(dicts[unmap[VHWM]])
    rss = sorted(dicts[unmap[RSS]])	
    rss = sorted(dicts[unmap[RSS]])	
    l1 = sorted(dicts[unmap[L1]])	
    l2 = sorted(dicts[unmap[L2]])	
    l3 = sorted(dicts[unmap[L3]])	
    tot = sorted(dicts[unmap[TOT]])	
    fp = sorted(dicts[unmap[FP]])	

    vals_vmhwm = []
    vals_rss = []
    vals_l1 = []
    vals_l2 = []
    vals_l3 = []
    vals_tot = []
    vals_fp = []

    for keys in vmhwm:
        vals_vmhwm.append(dicts[unmap[VHWM]][keys])

    for keys in rss:
        vals_rss.append(dicts[unmap[RSS]][keys])

    for keys in l1:
        vals_l1.append(dicts[unmap[L1]][keys])

    for keys in l2:
        vals_l2.append(dicts[unmap[L2]][keys])

    for keys in l3:
        vals_l3.append(dicts[unmap[L3]][keys])

    for keys in tot:
        vals_tot.append(dicts[unmap[TOT]][keys])

    for keys in fp:
        vals_fp.append(dicts[unmap[FP]][keys])

    plt.figure("Memory high water mark")
    plt.subplot(211)
    plt.ylabel('Kilo Bytes')
    plt.title('Virtual memory High Water Mark')
    plt.plot(vals_vmhwm)
    plt.subplot(212)
    plt.title('Resident Set Size')
    plt.ylabel('Kilo Bytes')
    plt.plot(vals_rss)
    plt.show()

    plt.figure("Cache Misses")
    plt.subplot(311)
    plt.title('L1 Cache Misses')
    val_l1 = [j-i for i, j in zip(vals_l1[:-1], vals_l1[1:])]
    plt.plot(val_l1)
    plt.subplot(312)
    plt.title('L2 Cache Misses')
    val_l2 = [j-i for i, j in zip(vals_l2[:-1], vals_l2[1:])]
    plt.plot(val_l2)
    plt.subplot(313)
    val_l3 = [j-i for i, j in zip(vals_l3[:-1], vals_l3[1:])]
    plt.title('L3 Cache Misses')
    plt.plot(val_l3)
    plt.show()
   
    plt.figure("Total operations")
    plt.subplot(211)
    plt.title('Total operations')
    val_tot = [j-i for i, j in zip(vals_tot[:-1], vals_tot[1:])]
    plt.plot(val_tot)
    plt.subplot(212)
    plt.title('FP operations')
    val_fp = [j-i for i, j in zip(vals_fp[:-1], vals_fp[1:])]
    plt.plot(val_fp)
    plt.show()

    plt.figure("Percentage of cache misses wrt Total operations")
    l1_p = [x/y*100 for x,y in zip(val_l1 , val_tot)]
    l2_p = [x/y*100 for x,y in zip(val_l2 , val_tot)]
    l3_p = [x/y*100 for x,y in zip(val_l3 , val_tot)]
    plt.subplot(311)
    plt.ylabel('% of Cache misses')
    plt.title('L1 Cache Misses')
    plt.plot(l1_p)
    plt.subplot(312)
    plt.ylabel('% of Cache misses')
    plt.title('L2 Cache Misses')
    plt.plot(l2_p)
    plt.subplot(313)
    plt.ylabel('% of Cache misses')
    plt.title('L3 Cache Misses')
    plt.plot(l3_p)
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
