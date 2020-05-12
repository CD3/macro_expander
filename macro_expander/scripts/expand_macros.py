from macro_expander import *
import argparse, pathlib

def main():
  parser = argparse.ArgumentParser(description='Processes macros in text.')
  parser.add_argument('input_file', help="File to be processed.")
  parser.add_argument('output_file', help="Name of file to write.")
  parser.add_argument('--use-cache', '-c', action='store_true', default=False, help="Use cache to speed up macro expansion.")
  parser.add_argument('--cache-file', '-f', action='store', default='expand-macros.cache',help="Name of file to read/write cache to..")

  args = parser.parse_args()

  with open(args.input_file,'r') as f:
    text = f.read()

  proc = MacroProcessor(use_cache=args.use_cache)
  if args.use_cache and pathlib.Path(args.cache_file).is_file():
    proc.readCache( args.cache_file )
  text = proc.process(text)
  if args.use_cache:
    proc.writeCache( args.cache_file )


  with open(args.output_file,'w') as f:
    f.write( text )
