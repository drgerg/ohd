#!/usr/bin/env python3

""" ohdreadmail.py - (OverHead Door) Check ohd email address for commands.
    2019 - Gregory Allen Sanders"""

import os
import sys
import configparser
import logging
import time
import signal
import imaplib
import email
#
## ConfigParser init area.  Get some info out of working.conf.
#
ohdHome = os.getcwd()
config = configparser.RawConfigParser()
config.read(ohdHome + '/ohd.conf')
logger = logging.getLogger(__name__)
logger.debug("Connecting to Retrieve Message")
 
   
def main():
#    global emAdd
    config = configparser.ConfigParser()
    config.read_file(open(ohdHome + '/ohd.conf'))
    login = config.get('CommandEmail', 'MyEmailAdd')
    pswd = config.get('CommandEmail', 'MyPasswd')
    x = int(config.get('CommandEmail', 'CmdEmNum'))
    
    #
    ## End ConfigParser init
    logger.debug("Started the main() function")
    AuthAdds = []
    for x in range(1, x+1):
        AuthAdds.append(config.get('CommandEmail', 'InBoundEmail' + str(x)))
    logger.debug("x is: " + str(x))                         # x is the number of email addresses configured in ohd.conf
    mail = imaplib.IMAP4_SSL('imap.gmail.com');
    mail.login(login,pswd);
    mail.list();                                            # Gives list of folders or labels in gmail.
                                                            # Connect to inbox
    mail.select("INBOX");
                                                            # Retrieve a list of all message IDs
    result2, all_uids = mail.uid('search', None, 'ALL');
                                                            # Retrieve a list of ID for messages that contain 'Quiet'
    result3, rcvdMsgAny = mail.search(None, 'X-GM-RAW', "Quiet");
    logger.debug("Result3: " + str(result3))

    logger.debug("all_uids: " + str(all_uids))              # Show me all the IDs
    ids = rcvdMsgAny[0]                                     # rcvdMsgAny is a list
    id_list = ids.split()                                   # 'ids' becomes a space separated string
    logger.debug("id_list: " + str(id_list))                # prove it worked
    fromAdds = []
    if str(id_list) != '[]':                                # as long as the list isn't empty, do these things
        for q_email_id in id_list:                          # from search for 'Quiet'
            result, mdata = mail.fetch(q_email_id, "(RFC822)");
            raw_email = mdata[0][1];                        # get the raw email data.  It is byte literal type
            raw_email_string = raw_email.decode('utf-8')    # turn the data into a string type
            recv_msg = email.message_from_string(raw_email_string)
            fromAdds.append(email.utils.parseaddr(recv_msg['From'])[1])
            logger.debug(fromAdds)

        msgAuth = None
        for add in AuthAdds:
            if add in fromAdds:
                rmFrom = add
                msgAuth = "Yes"
                rcvdQuiet = "Quiet"
                break
        if msgAuth == None:
            msgAuth = "No"
            rmFrom = "UnAuthorized"
        logger.info("Received Auth=" + msgAuth + " -Quiet- message from " + rmFrom)
        cleanup(all_uids, mail)
        return rcvdQuiet, rmFrom, msgAuth
    else:
        cleanup(all_uids, mail)
        rcvdQuiet = str(id_list)
        msgAuth = "None"
        rmFrom = "Nobody"
        logger.info("No Quiet msg.  Returning: " + rcvdQuiet + " and " + rmFrom + " and " + msgAuth)
        return rcvdQuiet, rmFrom, msgAuth


def cleanup(all_uids, mail):
    logger.info("Logging out")
    all_uids = all_uids[0].split()
    logger.debug("Message IDs: " + str(all_uids))
    for num in all_uids:
        num = num.decode('utf-8')
        logging.info("Deleted message UID: " + num)
        mail.uid('STORE', num, '+X-GM-LABELS', '\\Trash')
    logger.debug("This is the end of cleanup(). Closing the email account")
    mail.expunge()
    mail.logout()



    
def SignalHandler(signal, frame):
        logger.info("Cleaning up . . . \n = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
        logger.info("Shutting down gracefully")
        logger.debug("This is SignalHandler in ohdreadmail.py")
        logger.info("Displayed .info and .debug in SignalHandler")
        logger.info("Shutdown initiated")
        logger.debug("Wrote to log in SignalHandler")
        sys.exit(0)



if __name__ == "__main__":
        try:
            import argparse
            signal.signal(signal.SIGINT, SignalHandler)
            ## Command line arguments parsing
            #
            parserrm = argparse.ArgumentParser()
            parserrm.add_argument("-d", "--debug", help="Turn on debugging output to stderr", action="store_true")
            argsrm = parserrm.parse_args()
            if argsrm.debug:
                logging.basicConfig(filename=ohdHome + '/ohd.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
                logging.info("ohdreadmail.py started with debugging output enabled")
            else:
                logging.basicConfig(filename=ohdHome + '/ohd.log', format='%(asctime)s - %(message)s in %(name)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
            #
            ## End Command line arguments parsing
            logger.debug("Top of try")
#            emAdd = config.get('CommandEmail', 'InBoundEmail1')
#            print(emAdd)
            main()
#            cleanup(all_uids, mail)
            logger.info("Bottom of try")

        except:
            pass
            logger.info("That's all folks.  Goodbye")

