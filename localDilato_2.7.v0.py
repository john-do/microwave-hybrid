#! usr/bin/env python2.7
"""
0.1 12/2015 Text only version of measurements for hybrid dilatometry
0.2 25/1/2016 Addition of graphing, self check when typing COMport, escape measurement with Ctrl+C, added computer clock time to printout, automatically make output *.txt
0.3 Added Gui and file dialog

----------
v0_py2.7
    Functioning TEXT ONLY data collection for microwave hybrid dilatometry.
    Measures temperature previously configured serial connection
        !!!COM PORT HARDCODED TO COM4
    Measures length from LVDT via NIDAQ USB-6000 via 0-10V
    Saves index, computer time, elapsed time, temperature (deg C), length (mm) to ./
    
"""

import sys
import time
import serial
import matplotlib.pyplot as plt
#import matplotlib.animation as animation
from PyDAQmx import *
from numpy import zeros,mean
from numpy import float64 as f64
#from datetime import datetime
from PyQt4.QtGui import *


def file_init(file_name):
    file = open(file_name,'w')
    """if file[-4:]== '.txt':
        pass
    else:
        file = file + '.txt'"""
    file.write("Hybrid dilatometry\n")
    lo = input("Initial length [mm]:")
    file.write("Initial length: %s mm\n" % lo)
    tnow = time.strftime("%Y-%m-%d %H:%M:%S")
    file.write(tnow)
    file.write("\n#\tClock time\tElapsed time [s]\tT [C]\t l [mm]\n")
    return file
    

def main():

    comPort = raw_input('COMX X = ? :')
    
    if type(comPort) is int:
        comPort = 'COM'+str(comPort)
    else:
        comPort = comPort.upper()
        
    file_name = raw_input('Choose file name:')
    
    #Initiate Files
    
    file = file_init(file_name)
    
    # Connect and configure DAQ
    analog_input = Task()
    data = zeros((100,),dtype=f64)
    read = int32()
    
    analog_input.CreateAIVoltageChan("Dev1/ai0","",DAQmx_Val_Cfg_Default,-5.0,10.0,DAQmx_Val_Volts,None)
    analog_input.CfgSampClkTiming("",1000.0,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,100)
    
    analog_input.ReadAnalogF64(100,10.0,DAQmx_Val_GroupByChannel,data,100,byref(read),None)
    

    # Connect to OTP
    

    ser = serial.Serial(3,9600)
    
    #configure plot
    
    """plt.axis([500,1500,1,0])
    plt.ion()
    plt.show()"""
    
    #Start measurement
    n = 0 
    time_array = []
    temperature_array = []
    length_array = []
    
    
    start_time = time.time() 
    #last_loop_time = 0
    try:
        while True:
            n += 1
            ser.flushInput(),ser.flushOutput()
            tnow = time.strftime("%H:%M:%S")
            #measure l        
            try:
                analog_input.ReadAnalogF64(100,10.0,DAQmx_Val_GroupByChannel,data,100,byref(read),None)
                    
                v = mean(data)
                l = 0.1*v
                
                length_array.append(l)
            except:
                #print l
                l = None
                #print l
                        
            # measure T             
            try:
                #ser.flushInput(),ser.flushOutput()
                t_text = ser.readline().strip()
                          
                T = float(t_text[2:8])
                temperature_array.append(T)
                #print T
            except:
                T = None
                temperature_array.append(T)
                #print T
            
            # Print to file 
            elapsed_time = time.time() - start_time
            time_array.append(elapsed_time)
                        
            file.write("%i\t%s\t%f\t%s\t %f\n" %(n, tnow, elapsed_time, T, l) )
            
            print "%i\t%s\t%f\t%s\t %f\n" %(n, tnow, elapsed_time, T, l)
            
            """#plot new data point
            plt.scatter(T,l)
            plt.draw"""
            
    except KeyboardInterrupt:
        print 'Interupted. Closing Measurement'
        DAQmxStopTask(analog_input)
        DAQmxClearTask(analog_input)
        file.close()

    print 'Measurement Complete'
    
    
   
if __name__ == "__main__":
    main()