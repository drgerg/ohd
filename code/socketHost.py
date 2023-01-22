#!/usr/bin/env python3
# socketHost.py for dr.gerg's ohd (OverHead Door) monitor.
# updated Jan 2023 as part of the v2.1.1 overhaul
#

import socket
import os
import sys
import traceback
# import ast
import logging
import signal
import configparser
import pickle
import ohdSoftBP
import ohdpinchk
# from time import sleep



def main():
    host = ''
    port = 64444
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind((host, port))
    except socket.error as e:
        logger.info(str(e))

    while True:
        try:
            s.listen(1)
            logger.info('Waiting for a connection.')
            conn, addr = s.accept()
            # print('connected to: '+addr[0]+':'+str(addr[1]))
            # conn.send(str.encode('Welcome. Use "quit" to close connection.\n'))
        except Exception:
                traceback.print_exc(file=sys.stdout)
                incoming = 'An error was caught and displayed.'
                data = str.encode('It is time to part ways.')
                conn.sendall(data)
                pass

        while True:
            try:
                sockXferIn = conn.recv(2048)
                InCmd = pickle.loads(sockXferIn)
            except EOFError:
                logger.info("Encountered an empty .pkl file.  Moving on without it.")
                InCmd = 'break'
            logger.info('InCmd variable was populated from sockXferIn: ' + str(InCmd))
            logger.info(str(InCmd))
##  BREAK
            if InCmd == 'break':
                pass
##  CHECK STATUS OF SOFT BYPASS
            if InCmd =='sbpstatus':
                sbpstat = ohdSoftBP.SBPCheck()
                packet = pickle.dumps(sbpstat)
                conn.sendall(packet)
                logger.info('Sent: ' + sbpstat)
                logger.info('Sent Soft Bypass Status.')
##  SET SOFT BYPASS ON
            if InCmd =='sbpon':
                sbpOnRtn = ohdSoftBP.blinkOn()
                packet = pickle.dumps(sbpOnRtn)
                conn.sendall(packet)
                logger.info('Sent Soft Bypass On return.')
##  SET SOFT BYPASS OFF
            if InCmd =='sbpoff':
                sbpOffRtn = ohdSoftBP.blinkOff()
                packet = pickle.dumps(sbpOffRtn)
                conn.sendall(packet)
                logger.info('Sent Soft Bypass Off return.')
##  OVERRIDE HARDWARE BYPASS. SET TO OFF.
            if InCmd =='sbpoverride':
                sbpOffRtn = ohdSoftBP.override()
                packet = pickle.dumps(sbpOffRtn)
                conn.sendall(packet)
                logger.info('Sent Soft Bypass Override return.')
##  GET VALUES FROM OHDPINCHK.PY
            if InCmd == 'pincheck':
                pnchk = []
                DoorStat = ohdpinchk.pinChk()
                bpStat = ohdpinchk.bpChk('Off')
                cpuT = ohdpinchk.cpuTemp()
                pnchk = [DoorStat, bpStat, cpuT]
                packet = pickle.dumps(pnchk)
                conn.sendall(packet)
                logger.info('Sent ohdpinchk output.')

##  CARRY ON AFTER EVERYTHING WRAPS UP
            try:
                conn.shutdown(1)
                conn.close()
                logger.info('Connection from ' + str(addr[0]) + ' closed.')
                break
            # except Exception:
            #     traceback.print_exc(file=sys.stdout)
            #     incoming = 'An error was caught and displayed.'
            except OSError:
                break
    #
    # sockXferIn should not be seen down here, so I'm commenting this out for now.
    #
            # if not sockXferIn:
            #     try:
            #         conn.shutdown(1)
            #         conn.close()
            #         logger.info('Connection closed.')
            #         break
            #     # except Exception:
            #         # traceback.print_exc(file=sys.stdout)
            #         # incoming = 'An error was caught and displayed.'
            #     except OSError:
            #         break
    #
        conn.close()
    else:
        logger.info('All Finished.')
        pass

def SignalHandler(signal, frame):
    if signal == 2:
        sigStr = 'CTRL-C'
        logger.info('* * * ' + sigStr + ' caught. * * * ')
    logger.info("SignalHandler invoked")
    logger.info("Shutting down gracefully")
    logger.debug("Wrote to log in SignalHandler")
    logger.info("That's all folks.  Goodbye")
    logger.info(" - - - - socketHost.py DATA LOGGING STOPPED INTENTIONALLY - - - - ")
    sys.exit(0)



if __name__ == "__main__":
        try:
            import argparse
            ## Init area.  configparser and logger
            #
            sockHome = os.path.abspath(os.path.dirname(__file__))
            # config = configparser.RawConfigParser()
            # config.read(sockHome + '/sock.conf')
            logger = logging.getLogger(__name__)

            ## Command line arguments parsing
            #
            parsersm = argparse.ArgumentParser()
            parsersm.add_argument("-d", "--debug", help="Turn on debugging output to stderr", action="store_true")
            argssm = parsersm.parse_args()
            if argssm.debug:
                logging.basicConfig(filename=sockHome + '/ohd.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
                logging.info("Debugging output enabled")
            else:
                logging.basicConfig(filename=sockHome + '/ohd.log', format='%(asctime)s - %(message)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
            #
            ## End Command line arguments parsing
            logger.info(" - - - - - - - - - - - STARTING socketHost.py NORMALLY - - - - - - - - - - - - - - ")
            signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
            signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
            logger.debug("Top of try")
            main()

        except  ValueError as errVal:
            logger.info(errVal)
            pass
        logger.info("That's all folks.  Goodbye")

