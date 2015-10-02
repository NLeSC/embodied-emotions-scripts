"""Helper functions for scripts."""


import sys


def continue_script(boolean, msg):
    """Exit the program if the input boolean is false and print msg to stderr.
    """
    if not boolean:
        sys.stderr.write(msg)
        sys.exit(1) 
