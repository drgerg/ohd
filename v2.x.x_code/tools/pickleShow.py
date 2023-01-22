#!/usr/bin/env python3
#
# pickleShow.py - Keep tabs on all the .pkl files in this directory and
# let me know if the timestamp changes.
# (c) 2020 - Gregory A. Sanders
#
# import time,os,logging,argparse,traceback,signal,sys,subprocess,io
import time, os, logging, configparser, argparse, traceback, signal, sys, pickle
from time import sleep

#
## - - - - - TEST CODE BELOW HERE - - - -
#
def PklWatch():
    print("\nWatching for changes to pickle files in this directory.\n")
    pklshwHome = os.getcwd()
    oswalkList = list(os.walk(pklshwHome))
    stampDict = {}
    for item in oswalkList[0][2]:
        if ".pkl" in item:
            stamp = os.stat(item).st_mtime
            stampDict.update({item: stamp})
            print(str(stampDict))
    while stampDict != {}:
        for item in oswalkList[0][2]:
            if ".pkl" in item:
                lastStamp = stampDict[item]
                stamp = os.stat(item).st_mtime
                if stamp != lastStamp:
                    print(item)
                    try:
                        with open(pklshwHome + "/" + item, "rb") as pinPik:
                            pklGuts = pickle.load(pinPik)
                            gutsType = type(pklGuts)
                            # print(str(gutsType))
                            if "collections.OrderedDict" in str(gutsType):
                                for entry in pklGuts:
                                    print(str(entry) + " " + str(pklGuts[entry]))
                            else:
                                print(str(pklGuts))
                    except EOFError:
                        print(item + " was an empty .pkl file.  Moving on without it.")
                        pass
                    stampDict.update({item: stamp})
                    sleep(1)

    # return


#
def PklShow():
    pklshwHome = os.getcwd()
    oswalkList = list(os.walk(pklshwHome))
    totList = len(oswalkList[0][2])
    pklTotList = 0
    for item in oswalkList[0][2]:
        if ".pkl" in item:
            pklTotList += 1
    print("\n" + str(totList) + " files in " + str(pklshwHome) + ".")
    print(str(pklTotList) + " are .pkl files.")
    logger.info(
        str(pklTotList)
        + " of "
        + str(totList)
        + " files in "
        + str(pklshwHome)
        + " are .pkl files."
    )
    for item in oswalkList[0][2]:
        if ".pkl" in item:
            print("\n" + item)
            thisFile = input("Show the guts of this one? (y/N/q) ")
            if thisFile == "q" or thisFile == "Q":
                print("\nOK. No problem. I get it.\n")
                break
            if thisFile == "":
                thisFile = "N"
            if thisFile == "y" or thisFile == "Y":
                try:
                    logger.info("Spilled the guts of: " + str(item))
                    with open(pklshwHome + "/" + item, "rb") as pinPik:
                        pklGuts = pickle.load(pinPik)
                        gutsType = type(pklGuts)
                        print("\nFile: " + item)
                        print("Type: " + str(gutsType) + "\n")
                        if "collections.OrderedDict" in str(gutsType):
                            for entry in pklGuts:
                                print(str(entry) + " " + str(pklGuts[entry]))
                        else:
                            print(str(pklGuts))
                except EOFError:
                    print(item + " was an empty .pkl file.  Moving on without it.")
                    pass
    logger.info(" - - - End of session - - - ")


## - - - - - - END TEST CODE - - - - - - -
#


def SignalHandler(signal, frame):
    if signal == 2:
        sigStr = "CTRL-C"
        logger.info("* * * " + sigStr + " caught. * * * ")
    print("SignalHandler invoked")
    logger.info("Shutting down gracefully")
    logger.debug("Wrote to log in SignalHandler")
    logger.info("That's all folks.  Goodbye")
    logger.info(" - - - - pickleShow.py DATA LOGGING STOPPED INTENTIONALLY - - - - ")
    sys.exit(0)


if __name__ == "__main__":

    parserPklS = argparse.ArgumentParser()
    parserPklS.add_argument(
        "-d",
        "--debug",
        help="Turn on debugging output to log file.",
        action="store_true",
    )
    parserPklS.add_argument(
        "-s",
        "--show",
        help="Select and show the contents of a .pkl file.",
        action="store_true",
    )
    parserPklS.add_argument(
        "-f", "--func", help="Call the specified function.", action="store"
    )
    pklshwHome = (
        os.getcwd()
    )  ## os.getcwd() give you the Current Working Directory.  If you run this from some other directory
    # print(pklshwHome)                                     ## then the test.log file (for example) gets written there, not in the directory where this
    logger = logging.getLogger(__name__)  ## python file lives.
    #
    # config = configparser.RawConfigParser()
    # config.read(pklshwHome + '/allApp.conf')
    #
    argsPklS = parserPklS.parse_args()

    # if argsPklS.func:
    #     Tfunc = argsPklS.func
    #     print(Tfunc)

    if argsPklS.debug:
        logging.basicConfig(
            filename=pklshwHome + "/pklshw.log",
            format="[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s",
            datefmt="%D %H:%M:%S",
            level=logging.DEBUG,
        )
        logging.info("Debugging output enabled")
    else:
        logging.basicConfig(
            filename=pklshwHome + "/pklshw.log",
            format="%(asctime)s - %(message)s",
            datefmt="%a, %d %b %Y %H:%M:%S",
            level=logging.INFO,
        )
    #
    logger.info(" - - - - pickleShow.py DATA LOGGING STARTED - - - - ")
    # print('Logger info')
    #
    signal.signal(
        signal.SIGINT, SignalHandler
    )  ## This one catches CTRL-C from the local keyboard
    signal.signal(
        signal.SIGTERM, SignalHandler
    )  ## This one catches the Terminate signal from the system
    try:

        if argsPklS.show:
            PklShow()
        else:
            PklWatch()
        pass
    #                print("Bottom of try")
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - pickleShow.py DATA LOGGING STOPPED BY EXCEPTION - - - - ")
