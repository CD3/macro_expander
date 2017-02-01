#! /usr/bin/python

from macro_expander import *
import argparse

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Processes macros in text.')
  parser.add_argument('input_file', help="File to be processed.")
  parser.add_argument('output_file', help="Name of file to write.")
  parser.add_argument('--debug', '-d', action='store_true', help="Output debug information.")

  args = parser.parse_args()

  with open(args.input_file,'r') as f:
    text = f.read()

  proc = MacroProcessor()
  text = proc.process(text)


  with open(args.output_file,'w') as f:
    f.write( text )
