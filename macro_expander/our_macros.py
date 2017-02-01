import os, re, subprocess, tempfile, urlparse, urllib

def example(self,args,opts):
  '''Macro handlers will be passed three argument
  1. refernce to the MacroProcessor object. this can be used to access helper method provided by the MacroProcessor class.
  2. list of arguments. 
  3. option string. this will be a single string that the function is responsible for parsing. the MacroProcessor.parse_option_str() method can be used
     to parse a list of key="value" style options into a dict. for example 'a="A", b="B"' would get parsed to { 'a' : 'A', 'b' : 'B' }.
  '''

  return "Processed by example handler."

def mathimg(self,args,opts):
  '''Create an image from LaTeX code and include it.'''

  if len(args) < 1: # don't do anything if no argument was given
    return None

  # create an image file of the equation using our tex2im
  if not hasattr(self,'mathimg_num'):
    self.mathimg_num = 0
  self.mathimg_num += 1

  extra_opts=""
  if len(opts) > 1:
    extra_opts = opts[1]


  ifn = "eq-%d.png"%(self.mathimg_num)
  ofn = "eq-%d.log"%(self.mathimg_num)
  cmd = "tex2im -o %s %s '%s' "%(ifn,extra_opts,args[0])
  print "creating image of equation with:'"+cmd+"'"
  with open(ofn,'w') as f:
    status = subprocess.call(cmd,shell=True,stdout=f,stderr=f)
    if status != 0:
      print "\tWARNING: there was a problem running tex2im."
      print "\tWARNING: command output was left in %s"%(ofn)
      print "\tWARNING: replacing with $...$, which may not work..."
      return "$"+args[0]+"$"


  options = parse_options_str( opts )

  size = None
  if len(options) > 0:
    if 'size' in options[0]:
      size = options[0]['size']
    else:
      size = '{width}x{height}'.format( width=options[0].get('width','W'), height=options[0].get('height','H') )
        
    if size:
      ifn = "eq-%d_%s.png"%(self.mathimg_num,size)

  # now replace the macro with markdown that points at the image
  md = '![](./%s)'%ifn

  return md

def scriptimg(self,args,opts):
  '''Create an image from a script and include it.'''

  if len(args) < 1: # don't do anything if no argument was given
    return None

  # create an image file of the equation using our tex2im
  if not hasattr(self,'scriptimg_num'):
    self.scriptimg_num = 0
  self.scriptimg_num += 1

  extra_opts=""
  if len(opts) > 1:
    extra_opts = opts[1]


  sfn = "sc-%d.txt"%(self.scriptimg_num)
  ifn = "sc-%d.png"%(self.scriptimg_num)
  ofn = "sc-%d.log"%(self.scriptimg_num)

  with open(sfn,'w') as f:
    f.write(re.sub( "^\s*#","#",args[0] ) )

  cmd = "chmod +x %s; ./%s; mv out.png %s"%(sfn,sfn,ifn)
  print "creating image from script with:'"+cmd+"'"
  with open(ofn,'w') as f:
    status = subprocess.call(cmd,shell=True,stdout=f,stderr=f)
    if status != 0:
      print "\tWARNING: there was a problem running script."
      print "\tWARNING: the script and its output were left in %s and %s"%(sfn,ofn)
      return "ERROR: could not create image"


  options = parse_options_str( opts )

  size = None
  if len(options) > 0:
    if 'size' in options[0]:
      size = options[0]['size']
    else:
      size = '{width}x{height}'.format( width=options[0].get('width','W'), height=options[0].get('height','H') )
        
    if size:
      ifn = "sc-%d_%s.png"%(self.scriptimg_num,size)

  # now replace the macro with markdown that points at the image
  md = '![](./%s)'%ifn

  return md

def image(self,args,opts):
  '''Insert a (possibly remote) image.'''
  fn = args[0]
  options = parse_options_str( opts )

  url = urlparse.urlparse(fn)
  if url.scheme == '':
    url = url._replace(scheme='file')

  if url.scheme == 'file':
    fn = os.path.join( os.getcwd(), fn)
    fn = os.path.normpath(fn)
    if not os.path.isfile( fn ):
      raise RuntimeError("ERROR: could not find image file '%s'." % fn )
    url = url._replace(path=fn)

  lfn = os.path.basename(url.path)
  url = url.geturl()

  # get size from options
  size = None
  if len(options) > 0:
    if 'size' in options[0]:
      size = options[0]['size']
    else:
      size = '{width}x{height}'.format( width=options[0].get('width','W'), height=options[0].get('height','H') )
        
    if size:
      n,e = os.path.splitext(lfn)
      lfn = "%s_%s%s"%(n,size,e)


  if fn != lfn:
    # download the image
    with open(lfn,'wb') as lf:
      f = urllib.urlopen(url)
      lf.write(f.read())
      f.close()

  return '![](./%s)'%lfn

includegraphics = image


def shell(self,args,opts):
  '''Run shell command and return output.'''
  with tempfile.TemporaryFile() as fp:
    cmd = ';'.join(args)
    subprocess.call( cmd, shell=True, stdout=fp )
    fp.seek(0)
    stdout = fp.read()

  return stdout

def write(self,args,opts):
  '''Write text to a file. Useful for creating "library" scripts for the scriptimg command.'''

  if len(args) < 1: # don't do anything if no argument was given
    return None

  fn = None
  options = parse_options_str( opts )
  if len(options) > 0:
    if 'filename' in options[0]:
      fn = options[0]['filename']

  if fn is None:
    print "\tWARNING: no filename found in write macro."
    print '\tWARNING: please specify a filename in the macro options with [filename="NAME"], where NAME is the name of the file to write.'
    return None

  with open(fn,'w') as f:
    f.write(args[0])

  return ""

