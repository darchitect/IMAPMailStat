######################################################
#
# IMAPMailstat.py
#
######################################################
# 
# Sort of a horrible hack - the idea is to create a
# mailstat clone for IMAP folders so I can see number
# of emails delivered to each folder. The main driver
# for this is that since I use IMAP and Sieve, I can't
# get a summary automatically. Thunderbird can manage
# it by doing a brute force count between sessions
#
######################################################
#
# Basic flow
# - parse arguments
# - login into the IMAP mail server
# - for each folder count the messages since the last
#   process run
#
#######################################################

import argparse
import logging
import getpass
import re

from imaplib import IMAP4, IMAP4_SSL

# based on https://stackoverflow.com/questions/703185/using-email-headerparser-with-imaplib-fetch-in-python
from email.parser import HeaderParser

class Folder:

    _name = None
    _has_children = False

    def __init__(self, name, has_children=False):
        self._name = name
        self._has_children = has_children

    # Static method
    def parse_list(self, data):
        # ("Child indicator" "optional name") "/" 
        # Folder name - may have spaces.
        # f = re.compile( '^\(([A-Za-z]+)' )
        # Group 1 = child indicator
        # Group 2 (opt) = server name
        # Group 3 = folder seperator
        # Group 4 = Folder name
        # call groups before to see how many
        f = re.compile( r'^\(\\(?P<children>[A-Za-z]+)(\s\\(?P<server_name>[A-Za-z])+)?\)\s(?P<seperator>\S{3})\s(?P<folder_name>.+)$' )
        matches = f.match( data ).groupdict()
        self._name = matches['folder_name']
        self._has_children = True if matches['children'] == "HasChildren" else False
        
    def __str__(self):
        return "[Folder: {0}, Children: {1}]".format( self._name, self._has_children )            


def parse_arguments():
    '''Setup and parse the options for this script'''
    parser = argparse.ArgumentParser(description='mailstat for IMAP')
    parser.add_argument('-i', '--imap', 
                        required=True, 
                        help='IMAP Server')
    parser.add_argument('-u', '--user', 
                        required=True, 
                        help='IMAP Server username')
    parser.add_argument('-p', '--port',
                        required=True,
                        help="port for IMAP server")
    parser.add_argument('-l', '--logfile', 
                        default="STDERR", 
                        help="Logfile - defaults to STDERR")
    parser.add_argument('--debug',
                        action='store_true',
                        help="enable DEBUG (akin to verbose)")
    args = parser.parse_args()
    return args

def setup_logger( logfile, debug=False ):
    '''Setup the logger - default is the STDERR file handle - we test for the string "STDERR" and 
    rather than try and be clever, use the appropriate basicConfig call'''
    level = logging.DEBUG if debug else logging.INFO
    if logfile == "STDERR":
        logging.basicConfig( level=level, format='%(asctime)s|%(levelname)s|%(message)s' )
    else:
        logging.basicConfig( filename=logfile, level=level, format='%(asctime)s|%(levelname)s|%(message)s' ) 

def log_startup_options( args ):
    '''capture startup args in the log'''
    logging.info( "Arguments [{0}]".format( args ))

def load_account():
    '''
    Load account infomation from a file so the user/password
    isn't supplied every time
    '''
    pass

def test_mail( args ):
    logging.debug( "Connecting to Server" )
    M = IMAP4_SSL( args.imap, args.port )
    logging.debug( "Password" )
    M.login(args.user, getpass.getpass())
    resp, data = M.select('INBOX', readonly=True )
    print "Number of messages in: %s is %s\n" % ('INBOX', data)
    for folder in  M.list()[1]:
        # ("Child indicator" "optional name") "/" 
        # Folder name - may have spaces.
        f = Folder()
        f.parse_list( folder )
        print f

    resp, data = M.search(None, 'ALL')
    for num in data[0].split():
        resp, header_data = M.fetch(num, '(BODY[HEADER])')
        parser = HeaderParser()
        msg = parser.parsestr( header_data[0][1] )
        #print 'Message %s:%s\n' % (num, msg['Subject'])
    M.close()
    M.logout()

def main():
    args = parse_arguments()
    setup_logger( args.logfile, debug=args.debug )
    log_startup_options( args )
    test_mail( args )

'''Main function - execution starts here'''
if __name__ == '__main__':
    main()