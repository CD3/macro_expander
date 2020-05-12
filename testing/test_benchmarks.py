import os,sys,timeit
import macro_expander

def test_small_single_macro_strings(tmp_path):
  os.chdir(tmp_path)
  print()

  def process(self,args,opts):
    return "PROCESSED"

  def numargs(self,args,opts):
    return str(len(args))

  def countopts(self,args,opts):
    return str(len(self.parse_options_str(opts)))

  proc = macro_expander.MacroProcessor()
  proc.addMacro( 'process', process)
  proc.addMacro( 'numargs', numargs)
  proc.addMacro( 'numopts', countopts)


  def run():
    return proc.process(r'\process{}')

  # assert  run() == r'''PROCESSED'''

  N = 1000
  time = timeit.timeit(run,number=N)
  print("single macro only:", time, "ms")


  def run():
    return proc.process(r'preamble text: \process{} : postamble text')
  # assert  run() == r'''preamble text: PROCESSED : postamble text'''

  N = 1000
  time = timeit.timeit(run,number=N)
  print("single macro with pre/post amble:", time, "ms")




def test_large_multi_macro_strings(tmp_path):
  os.chdir(tmp_path)
  print()

  def process(self,args,opts):
    return "PROCESSED"

  def numargs(self,args,opts):
    return str(len(args))

  def countopts(self,args,opts):
    return str(len(self.parse_options_str(opts)))

  proc = macro_expander.MacroProcessor(use_cache=True)
  proc.addMacro( 'process', process)
  proc.addMacro( 'numargs', numargs)
  proc.addMacro( 'numopts', countopts)

  text = 1000*r'pre-text \process{} middle text \numargs{one}{two} middle text 2 \numopts[a="1",b="2",c="3"]{} post text\n'


  def run():
    return proc.process(text)

  # assert  run() == r'''PROCESSED'''

  N = 2
  time = timeit.timeit(run,number=N)
  print("1000 line text with 3 macros each:", time/2, "s")




