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

from imaplib import IMAP4, IMAP4_SSL

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

def test_mail( args ):
    logging.debug( "Connecting to Server" )
    M = IMAP4_SSL( args.imap, args.port )
    logging.debug( "Password" )
    M.login(args.user, getpass.getpass())
    M.select()
    typ, data = M.search(None, 'ALL')
    for num in data[0].split():
        print 'Message %s\n' % (num)
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