import os, re, subprocess, tempfile, urlparse, urllib, base64, hashlib

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


  options = self.parse_options_str( opts )

  extra_opts=""
  if 'tex2im_opts' in options:
    extra_opts = options['tex2im_opts']


  cmd = "tex2im -o %%s %s -- '%s' "%(extra_opts,args[0])
  print '%s'%cmd
  # create a hash of the command used to create the image to use as the image
  # name. this way we can tell if the image has already been created before.
  hash = hashlib.sha1(cmd).hexdigest()
  ofn = "mathimg-%s-image.png"%hash
  lfn = "mathimg-%s-image.log"%hash
  cmd = cmd%ofn
  print "creating image with:'"+cmd+"'"
  if os.path.exists(ofn):
    print "\tskipping because '"+ofn+"' already exists. please delete it if you want to force a rebuild."
  else:
    with open(lfn,'w') as f:
      status = subprocess.call(cmd,shell=True,stdout=f,stderr=f)
      if status != 0:
        print "\tWARNING: there was a problem running tex2im."
        print "\tWARNING: command output was left in %s"%(lfn)
        print "\tWARNING: replacing with $...$, which may not work..."
        return "$"+args[0]+"$"

  if 'o' in options:
    options['output'] = options['o']
  if 'output' in options:
    output = options['output']
  else:
    output= "markdown"

  return _img(ofn,output=output)

def scriptimg(self,args,opts):
  '''Create an image by running a script and include it.'''

  if len(args) < 1: # don't do anything if no argument was given
    return None

  options = self.parse_options_str( opts )


  text = re.sub( "^\s*#!","#!",args[0] ) # strip off any whitespace before the shebang
  hash = hashlib.sha1(text).hexdigest()

  sfn = "scriptimg-%s-script.txt"%hash
  ofn = "scriptimg-%s-image.png"%hash
  lfn = "scriptimg-%s-image.log"%hash

  with open(sfn,'w') as f:
    f.write(text)

  cmd = "chmod +x %s; ./%s; mv out.png %s"%(sfn,sfn,ofn)
  print "creating image from script with:'"+cmd+"'"
  with open(lfn,'w') as f:
    status = subprocess.call(cmd,shell=True,stdout=f,stderr=f)
    if status != 0:
      print "\tWARNING: there was a problem running script."
      print "\tWARNING: the script and its output were left in %s and %s"%(sfn,lfn)
      return "ERROR: could not create image"


  if 'o' in options:
    options['output'] = options['o']
  if 'output' in options:
    output = options['output']
  else:
    output= "markdown"

  return _img(ofn,output=output)

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

def file(self,args,opts ):
  '''Return lines from a file.'''

  options = self.parse_options_str( opts )

  lines = list()
  for arg in args:
    with open(arg) as f:
      lines += f.readlines()

  if 'filter' in options:
    filt = options['filter']
    char = filt[0]
    pattern = filt.strip(char)
    lines = filter( lambda line : re.search(pattern,line), lines )

  if 'transform' in options:
    transforms = options['transform']
    if not isinstance(transforms,list):
      transforms = [transforms]
    for transform in transforms:
      char = transform[0]
      toks = transform.strip(char).split(char)
      pattern = toks[0]
      replace = toks[1] if len(toks) > 1 else ""
      lines = [ re.sub(pattern,replace,line) for line in lines ]

  b = 1
  e = len(lines)

  if 'b' in options:
    try:
      b = int(options['b'])
    except:
      pattern = options['b'].strip("/")
      for i in range(len(lines)):
        if re.search(pattern,lines[i]):
          b = i+1 # b is 1 offset, not zero offset
          break


  if 'e' in options:
    try:
      e = int(options['e'])
    except:
      pattern = options['e'].strip("/")
      for i in range(b-1,len(lines)):
        if re.search(pattern,lines[i]):
          e = i+1
          break


  elif 'n' in options:
    e = b+int(options['n'])-1



  return "".join( lines[b-1:e] )







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

