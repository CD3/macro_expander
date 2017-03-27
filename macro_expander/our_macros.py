import os, re, subprocess, tempfile, urlparse, urllib, base64

def example(self,args,opts):
  '''Macro handlers will be passed three argument
  1. refernce to the MacroProcessor object. this can be used to access helper method provided by the MacroProcessor class.
  2. list of arguments. 
  3. option string. this will be a single string that the function is responsible for parsing. the MacroProcessor.parse_options_str() method can be used
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

  options = self.parse_options_str( opts )

  extra_opts=""
  if 'tex2im_opts' in options:
    extra_opts = options['tex2im_opts']


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



  if 'o' in options:
    options['output'] = options['o']
  if 'output' in options:
    output = options['output']
  else:
    output= "markdown"

  return _img(ifn,output=output)

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


  options = self.parse_options_str( opts )

  size = None
  if len(options) > 0:
    if 'size' in options:
      size = options['size']
    else:
      size = '{width}x{height}'.format( width=options.get('width','W'), height=options.get('height','H') )
        
    if size:
      ifn = "sc-%d_%s.png"%(self.scriptimg_num,size)

  return _img(ifn)

def image(self,args,opts):
  '''Insert a (possibly remote) image.'''
  fn = args[0]
  options = self.parse_options_str( opts )

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
    if 'size' in options:
      size = options['size']
    else:
      size = '{width}x{height}'.format( width=options.get('width','W'), height=options.get('height','H') )
        
    if size:
      n,e = os.path.splitext(lfn)
      lfn = "%s_%s%s"%(n,size,e)


  if fn != lfn:
    # download the image
    with open(lfn,'wb') as lf:
      f = urllib.urlopen(url)
      lf.write(f.read())
      f.close()

  return _img(ifn)

includegraphics = image


def shell(self,args,opts):
  '''Run shell command and return output.'''
  with tempfile.TemporaryFile() as fp:
    cmd = ';'.join(args)
    subprocess.call( cmd, shell=True, stdout=fp )
    fp.seek(0)
    stdout = fp.read()

  options = self.parse_options_str( opts )
  for f in ["lstrip", "rstrip", "strip"]:
    if f in options:
      if isinstance(options[f], str):
        stdout = getattr(stdout,f)(options[f])
      else:
        stdout = getattr(stdout,f)()

  return stdout

def write(self,args,opts):
  '''Write text to a file. Useful for creating "library" scripts for the scriptimg command.'''

  if len(args) < 1: # don't do anything if no argument was given
    return None

  fn = None
  options = self.parse_options_str( opts )
  if len(options) > 0:
    if 'filename' in options:
      fn = options['filename']

  if fn is None:
    print "\tWARNING: no filename found in write macro."
    print '\tWARNING: please specify a filename in the macro options with [filename="NAME"], where NAME is the name of the file to write.'
    return None

  with open(fn,'w') as f:
    f.write(args[0])

  return ""

def _img( filename, output="markdown", fmt=None, opts="" ):
  '''Return code to insert an image into document for various formats.'''

  if output == "markdown":
    return '![](./%s)'%filename

  if output == "latex":
    return r'\includegraphics{./%s}'%filename

  if output == "html":
    url = urlparse.urlparse(filename)
    if url.scheme == '':
      url = url._replace(scheme='file')

    if url.scheme == 'file':
      filename = os.path.join( os.getcwd(), filename)
      filename = os.path.normpath(filename)
      if not os.path.isfile( filename ):
        raise RuntimeError("ERROR: could not find image file '%s'." % filename )
      url = url._replace(path=filename)


    url = url.geturl()

    if fmt is None:
      fmt = os.path.splitext( filename )[-1][1:] # use extension for file format

    # we use urllib here so we can support specifying remote images
    f = urllib.urlopen(url)
    code  = base64.b64encode(f.read())
    f.close()
    text  = r'''<img src="data:image/{fmt};base64,{code}" {opts}>'''.format(fmt=fmt,code=code,opts=opts)

    return text

  return None
