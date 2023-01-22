#import ConfigParser
import imaplib
import email
import time
import os

#config = ConfigParser.ConfigParser()
#config.readfp(open('/home/greg/pipy/ohd/working.conf'))


def checkEmail():
        
    mail = imaplib.IMAP4_SSL('imap.gmail.com');
    mail.login('unit16of16@gmail.com','YfoNtxSTNREP');
    mail.list();  # Gives list of folders or labels in gmail.
        
    try:
        # Connect to inbox
        mail.select("INBOX"); 
        # Search for an unread email from user's email address
        result, data = mail.search(None,'(UNSEEN)', 'FROM', emAdd);
        ids = data[0]   # data is a list
        id_list = ids.split() # ids is a space separated string

        latest_email_id = id_list[-1] # get the latest
        result, data = mail.fetch(latest_email_id, "(RFC822)");
        print("Latest mail ID: " + str(latest_email_id))
 #       print str(WkgSubject)
        raw_email = data[0][1];
        raw_email_string = raw_email.decode('utf-8')
        recv_msg = email.message_from_string(raw_email_string)
        rcvdMsgSub = (recv_msg['Subject'])
        print("Subject: " + rcvdMsgSub)
#        if rcvdMsgSub == str(WkgSubject):
#            print("Received instruction: " + str(WkgSubject) + ".")
#            mail.store(latest_email_id, '+FLAGS', '\\Deleted')
#            mail.expunge()
#            CMexit = 1
#            Email = config.get('Notify', 'NotifyEmail' + str(howManyX))
#            os.system("echo Your message: " + rcvdMsgSub + ", was received. | mail -s " + "\'Text Command\' " + Email)
#            print str(CMexit)
#            return(CMexit)
            
    except IndexError:
        print("No message received.")
        CMexit = 0
        return(CMexit)

def main(argv):
    print("The arg is: " + str(checkEmail(*argv[1:])))

if __name__=="__main__":
    try:
        checkEmail()
    except:
        pass
                

