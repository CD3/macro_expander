#! /usr/bin/python

import os,sys,pprint

if os.path.exists("macros.py"):
  os.remove("macros.py")
with open("macros.py",'w') as f:
  text = r'''
def example(self,args,opts):
  return "Processed by user-defined macro."
  '''
  f.write(text)

import macro_expander

def test_parser():

  def macro(self,args,opts):
    return "PROCESSED"

  def numargs(self,args,opts):
    return str(len(args))

  def countopts(self,args,opts):
    return str(len(self.parse_options_str(opts)))

  proc = macro_expander.MacroProcessor()
  proc.addMacro( 'macro', macro )
  proc.addMacro( 'numargs', numargs)
  proc.addMacro( 'numopts', countopts)
  assert proc.process(r' \macro[a="A"]{argument1}{argument2} ') == r''' PROCESSED '''
  assert proc.process(r' \macro{argument1}{argument2} ') == r''' PROCESSED '''
  assert proc.process(r' \macro{argument1} ') == r''' PROCESSED '''
  assert proc.process(r' \macro ') == r''' PROCESSED '''

  assert proc.process(r' \numargs{a1} ') == r''' 1 '''
  assert proc.process(r' \numargs{a1}{a2} ') == r''' 2 '''
  assert proc.process(r' \numargs{a1}{a2}{a3} ') == r''' 3 '''

  assert proc.process(r' \numopts[a="A"]{a1} ') == r''' 1 '''
  assert proc.process(r' \numopts[a="A",b="B"]{a1} ') == r''' 2 '''
  assert proc.process(r' \numopts[a="A",b="B",c="C"]{a1} ') == r''' 3 '''
  assert proc.process(r' \numopts[a="A", b="B"]{a1} ') == r''' 2 '''
  assert proc.process(r' \numopts[a="A" , b="B"]{a1} ') == r''' 2 '''
  assert proc.process(r' \numopts[a ="A", b= "B"]{a1} ') == r''' 2 '''

def test_macros():
  proc = macro_expander.MacroProcessor()

  assert proc.process("\shell{echo Hello World}").strip() == "Hello World"
  proc.addMacro("shell", lambda s,a,o : "PROCESSED")
  assert proc.process("\shell{echo Hello World}").strip() == "PROCESSED"
  assert proc.process("\example{trash}").strip() == "Processed by user-defined macro."
  tmp = sys.modules['user_macros']
  del sys.modules['user_macros']
  assert proc.process("\example{trash}").strip() == "Processed by example handler."
  sys.modules['user_macros'] = tmp

def test_latex():
  proc = macro_expander.MacroProcessor()

  assert proc.process(r"\frac{1}{2}") == r"\frac{1}{2}"
  assert proc.process(r"\frac{{1}}{{2}}") == r"\frac{{1}}{{2}}"

def test_shell():
  proc = macro_expander.MacroProcessor()

  assert proc.process("\shell{echo Hello World}") == "Hello World\n"
  assert proc.process("\shell{echo;echo Hello World}") == "\nHello World\n"
  assert proc.process("\shell[lstrip]{echo;echo Hello World}") == "Hello World\n"
  assert proc.process("\shell[rstrip]{echo;echo Hello World}") == "\nHello World"
  assert proc.process("\shell[strip]{echo;echo Hello World}") == "Hello World"
