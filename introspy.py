#!/usr/bin/env python

""" Command-line parser for an introspy generated db. """

__version__   = '0.3.0'
__author__    = "Tom Daniels & Alban Diquet"
__license__   = "See ../LICENSE"
__copyright__ = "Copyright 2013, iSEC Partners, Inc."

from sys import argv
import os
from argparse import ArgumentParser
from DBAnalyzer import DBAnalyzer
from HTMLReportGenerator import HTMLReportGenerator
from IOS_Utils.ScpClient import ScpClient


def main(argv):

    # Parse command line
    parser = ArgumentParser(description="Introspy-Analyzer: Report "
        "generation tool for databases created using Introspy-iOS and "
        "Introspy-Android.", version=__version__)

    platform_group = parser.add_argument_group('platform options')
    platform_group.add_argument("-p", "--platform",
        help="Specify the type of database; should be set to \"ios\" or "
        "\"android\".")

    html_group = parser.add_argument_group('HTML reporting options')
    html_group.add_argument("-o", "--outdir",
        help="Generate an HTML report and write it to the\
        specified directory (ignores all other command line\
        options).")

    cli_group = parser.add_argument_group('command-line reporting options')
    cli_group.add_argument("-l", "--list",
        action="store_true",
        help="List all traced calls (no signature analysis\
        performed)")

# TODO: need to rework how API groups work on android before this can work
#    cli_group.add_argument("-g", "--group",
#        choices=APIGroups.API_GROUPS_LIST,
#        help="Filter by signature group")
#    cli_group.add_argument("-s", "--sub-group",
#        choices=APIGroups.API_SUBGROUPS_LIST,
#        help="Filter by signature sub-group")

    stats_group = parser.add_argument_group('iOS-only options')
    stats_group.add_argument("-i", "--info",
        choices=['urls', 'files'],#, 'keys'],
	help="Enumerate URLs or files accessed within the traced calls")#' and keychain items, etc.")
    stats_group.add_argument("-d", "--delete",
        action="store_true",
        help="Remove all introspy databases on a given remote device using SSH. "
        "The db argument should be the device's IP address or hostname.")
    stats_group.add_argument("-f", "--fetch",
        action="store_true",
        help="Fetch an introspy DB from a remote iOS device using SSH. "
        "The db argument should be the device's IP address or hostname.")

    parser.add_argument("db",
        help="The Introspy-generated database to analyze, or the device's IP "
        "address or hostname when using --fetch.")
    args = parser.parse_args()



    androidDb = False
    if 'android' in args.platform:
        androidDb = True
        if args.delete:
            print 'Error: --platform was set to android but --delete can '
            'only be used with ios databases.'
            return
        if args.fetch:
            print 'Error: --platform was set to android but --fetch can '
            'only be used with ios databases.'
            return
        if args.fetch:
            print 'Error: --platform was set to android but --info can '
            'only be used with ios databases.'
            return
    elif 'ios' in args.platform:
        pass
    else:
        print 'Error: --platform was not set to "ios" or "android".'
        return

    if args.delete:
        # Just delete DBs on the device and quit
        scp = ScpClient(ip=args.db)
        scp.delete_remote_dbs()
        return

    if args.fetch:
        # Get the introspy DB from the device
        scp = ScpClient(ip=args.db)
        db_path = scp.select_and_fetch_db()
    else:
        # Get the introspy DB from a local file
        db_path = args.db


    # Process the DB
    # Make sure it's there
    if not os.path.exists(db_path): # Nice race condition
        print 'Error: Could not find the DB file.'
        return

    analyzedDB = DBAnalyzer(db_path, androidDb)


    # Generate output
    if args.outdir: # Generate an HTML report
        reportGen = HTMLReportGenerator(analyzedDB)
        reportGen.write_report_to_directory(args.outdir)

    else: # Print DB info to the console

        if args.info: # Enumerate URLs/files
            if args.info == "urls":
                for url in analyzedDB.get_all_URLs():
                    print url
            elif args.info == "files":
                for path in analyzedDB.get_all_files():
                    print path
            #elif args.info == "keys":
            # TODO

        elif args.list: # Print all traced calls
            # TODO: Call print() here instead of inside the method
            analyzedDB.get_traced_calls_as_text(args.group, args.sub_group)

        else: # Print all findings
            analyzedDB.get_findings_as_text(args.group, args.sub_group)


if __name__ == "__main__":
    main(argv[1:])
