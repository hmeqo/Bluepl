import argparse

from .. import gconfig
from .__init__ import main

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()
gconfig.App.debug = args.debug
main()
