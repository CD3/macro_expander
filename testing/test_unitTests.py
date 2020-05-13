#! /usr/bin/env python

import os,sys,pprint,pathlib

if os.path.exists("macros.py"):
  os.remove("macros.py")
with open("macros.py",'w') as f:
  text = r'''
def example(self,args,opts):
  return "Processed by user-defined macro."
def exampletwo(self,args,opts):
  return "Processed by user-defined macro 2."
def otherexample(args,opts):
  return "Processed by other user-defined macro."
  '''
  f.write(text)

import macro_expander

def test_parser(tmp_path):
  os.chdir(tmp_path)

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
  assert proc.process(r' \macro{} ') == r''' PROCESSED '''

  assert proc.process(r' \numargs{a1} ') == r''' 1 '''
  assert proc.process(r' \numargs{a1}{a2} ') == r''' 2 '''
  assert proc.process(r' \numargs{a1}{a2}{a3} ') == r''' 3 '''

  assert proc.process(r' \numopts[a="A"]{a1} ') == r''' 1 '''
  assert proc.process(r' \numopts[a="A",b="B"]{a1} ') == r''' 2 '''
  assert proc.process(r' \numopts[a="A",b="B",c="C"]{a1} ') == r''' 3 '''
  assert proc.process(r' \numopts[a="A", b="B"]{a1} ') == r''' 2 '''
  assert proc.process(r' \numopts[a="A" , b="B"]{a1} ') == r''' 2 '''
  assert proc.process(r' \numopts[a ="A", b= "B"]{a1} ') == r''' 2 '''

  assert proc.process('\tpre:\\macro{}:post') == '''\tpre:PROCESSED:post'''

def test_macros(tmp_path):
  os.chdir(tmp_path)
  proc = macro_expander.MacroProcessor()

  assert proc.process(r"\shell{echo ' Hello World '}") == " Hello World \n"
  assert proc.process(r"\shell[strip]{echo ' Hello World '}") == "Hello World"
  assert proc.process(r"q1.1 \shell[strip]{echo ' Hello World '}") == "q1.1 Hello World"
  proc.addMacro("shell", lambda s,a,o : "PROCESSED")
  assert proc.process(r"\shell{echo Hello World}").strip() == "PROCESSED"
  assert proc.process(r"\example{}").strip() == "Processed by user-defined macro."
  assert proc.process(r"\exampletwo{}").strip() == "Processed by user-defined macro 2."
  assert proc.process(r"\otherexample{}").strip() == "Processed by other user-defined macro."

def test_latex(tmp_path):
  os.chdir(tmp_path)
  proc = macro_expander.MacroProcessor()

  assert proc.process(r"\frac{1}{2}") == r"\frac{1}{2}"
  assert proc.process(r"\frac{{1}}{{2}}") == r"\frac{{1}}{{2}}"

def test_shell(tmp_path):
  os.chdir(tmp_path)

  proc = macro_expander.MacroProcessor()

  assert proc.process(r"\shell{echo Hello World}") == "Hello World\n"
  assert proc.process(r"\shell{echo;echo Hello World}") == "\nHello World\n"
  assert proc.process(r"\shell[lstrip]{echo;echo Hello World}") == "Hello World\n"
  assert proc.process(r"\shell[rstrip]{echo;echo Hello World}") == "\nHello World"
  assert proc.process(r"\shell[strip]{echo;echo Hello World}") == "Hello World"

def test_write(tmp_path):
  os.chdir(tmp_path)
  proc = macro_expander.MacroProcessor()

  assert proc.process(r'\write[filename="write_macro.out"]{test}') == ""
  with open("write_macro.out") as f:
    assert f.read() == "test"

def test_img(tmp_path):
  os.chdir(tmp_path)
  proc = macro_expander.MacroProcessor()

  assert macro_expander.our_macros._img("file.png",output="markdown") == "![](./file.png)"
  assert macro_expander.our_macros._img("file.png",output="latex") == r"\includegraphics{./file.png}"

def test_file(tmp_path):
  os.chdir(tmp_path)
  proc = macro_expander.MacroProcessor()

  with open("file1.txt","w") as f:
    f.write("line one\n")
    f.write("line two\n")
    f.write("line three\n")
    f.write("line four\n")


  assert proc.process(r"\file{file1.txt}") == "line one\nline two\nline three\nline four\n"
  assert proc.process(r"\file[b=1,e=1]{file1.txt}") == "line one\n"
  assert proc.process(r"\file[b=2,e=3]{file1.txt}") == "line two\nline three\n"
  assert proc.process(r"\file[b=2,n=1]{file1.txt}") == "line two\n"
  assert proc.process(r"\file[b=2,n=3]{file1.txt}") == "line two\nline three\nline four\n"
  assert proc.process(r"\file[b=/two/,n=2]{file1.txt}") == "line two\nline three\n"
  assert proc.process(r"\file[b=/two/,e=/two/]{file1.txt}") == "line two\n"
  assert proc.process(r"\file[b=/two/,e=/line/]{file1.txt}") == "line two\n"
  assert proc.process(r"\file[b=/two/,e=/line/+1]{file1.txt}") == "line two\nline three\n"
  assert proc.process(r"\file[b=/two/,e=/three/]{file1.txt}") == "line two\nline three\n"
  assert proc.process(r"\file[filter=/two/]{file1.txt}") == "line two\n"
  assert proc.process(r"\file[filter=/(two|four)/]{file1.txt}") == "line two\nline four\n"
  assert proc.process(r"\file[transform=/two/three/]{file1.txt}") == "line one\nline three\nline three\nline four\n"
  assert proc.process(r"\file[b=2,e=3,transform=/two/three/]{file1.txt}") == "line three\nline three\n"
  assert proc.process(r"\file[transform=/two/three/,transform=/line/text/]{file1.txt}") == "text one\ntext three\ntext three\ntext four\n"
  assert proc.process(r"\file[transform=/line//]{file1.txt}") == " one\n two\n three\n four\n"

def test_mathimg_macro(tmp_path):
  os.chdir(tmp_path)
  proc = macro_expander.MacroProcessor()
  proc.process(r"\mathimg{\nabla \rho = 0}")

def test_shell_macro(tmp_path):
  os.chdir(tmp_path)
  proc = macro_expander.MacroProcessor()
  proc.process(r"\shell{ls}")


def test_macro_in_middle(tmp_path):
  os.chdir(tmp_path)
  proc = macro_expander.MacroProcessor()
  assert proc.process(r"Preamble| \example{} |Postamble").strip() == "Preamble| Processed by user-defined macro. |Postamble"

def test_caching(tmp_path):
  os.chdir(tmp_path)
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

  assert len(proc.cache) == 0
  proc.process(r' \macro{} ')
  assert len(proc.cache) == 0

  proc.use_cache = True

  proc.process(r' \macro{} ')
  assert len(proc.cache) == 1
  assert list(proc.cache.keys())[0] == r'\macro{}'
  proc.clearCache()
  assert len(proc.cache) == 0
  proc.process(r' \macro{} ')
  assert len(proc.cache) == 1

  proc.writeCache("tmp.cache")
  proc.clearCache()
  assert len(proc.cache) == 0

  assert pathlib.Path("tmp.cache").is_file()

  proc.readCache("tmp.cache")

  assert len(proc.cache) == 1
  assert list(proc.cache.keys())[0] == r'\macro{}'



