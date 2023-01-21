#!/usr/bin/env python3

# import time,os,logging,configparser,argparse,traceback,signal,sys,subprocess,io
import time,os,sys,pickle
from time import sleep

#
## - - - - - TEST CODE BELOW HERE - - - -
#
def main():
    ohdSBPHome = os.getcwd()
    blinkOn()
    sleep(60)
    blinkOff()
    sys.exit(0)

def blinkOn():
    ohdSBPHome = os.getcwd()
    pipeOut = open(ohdSBPHome + '/inpipe', 'wb')
    command = str.encode('start')
    pipeOut.write(command)
    bOnReturn = 'start'
    # print(bOnReturn)
    with open('ohdSBPStatus.pkl', 'wb') as sbps:
        pickle.dump(command, sbps, protocol=pickle.HIGHEST_PROTOCOL)
    pipeOut.flush()
    pipeOut.close()
    return bOnReturn

def override():
    ohdSBPHome = os.getcwd()
    pipeOut = open(ohdSBPHome + '/inpipe', 'wb')
    command = str.encode('override')
    pipeOut.write(command)
    bOffReturn = 'override'
    # print(bOffReturn)
    with open('ohdSBPStatus.pkl', 'wb') as sbps:
        pickle.dump(command, sbps, protocol=pickle.HIGHEST_PROTOCOL)
    pipeOut.flush()
    pipeOut.close()
    return bOffReturn

def blinkOff():
    # ohdSBPHome = os.getcwd()
    pipeOut = open('inpipe', 'wb')
    command = str.encode('stop')
    pipeOut.write(command)
    bOffReturn = 'stop'
    # print(bOffReturn)
    pipeOut.close()
    with open('ohdSBPStatus.pkl', 'wb') as sbps:
        pickle.dump(command, sbps, protocol=pickle.HIGHEST_PROTOCOL)
    return bOffReturn

def SBPCheck():
    ohdSBPHome = os.getcwd()
    with open(ohdSBPHome + '/ohdSBPStatus.pkl', 'rb') as sbps:
        SBPStat = bytes.decode(pickle.load(sbps))
        # print(SBPStat)
    return SBPStat