#!/usr/bin/env python3

import configparser, socket
#import ohdreadmail
import ohdsendmail


config = configparser.ConfigParser()

config.read_file(open('/home/greg/pipy/ohd/ohd.conf'))

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.1.22', 6802))
    sock.send(b'6|on+20|25|PIR_Tripped|PIR|PIR \n7|on+20|25|PIR_Tripped|PIR|PIR \n8|on+40|25|PIR_Tripped|PIR|PIR \n9|on+40|25|PIR_Tripped|PIR|PIR')
    ohdsendmail.msgS("PIR", "The Front Porch motion detector was tripped.")
    received = str(sock.recv(1024), "utf-8")
    print(received)
