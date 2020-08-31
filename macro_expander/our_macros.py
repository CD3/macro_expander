import os, re, subprocess, tempfile, urllib.parse, urllib.request, urllib.parse, urllib.error, base64, hashlib, pathlib
from pyparsing import *

def example(self,args,opts):
  '''Macro handlers will be passed three argument
  1. refernce to the MacroProcessor object. this can be used to access helper method provided by the MacroProcessor class.
  2. list of arguments. 
  3. option string. this will be a single string that the function is responsible for parsing. the MacroProcessor.parse_options_str() method can be used
     to parse a list of key="value" style options into a dict. for example 'a="A", b="B"' would get parsed to { 'a' : 'A', 'b' : 'B' }.
  '''

  return "Processed by example handler."

def mathimg(self,args,opts):
  '''Create an image from LaTeX code and include it.
  options:

    tex2im_opts: a string containing command line options that will be passed directly to the tex2im command.
    o : the output format. i.e. o='html' will produce an image that can be embedded in an html document.
  
  '''

  if len(args) < 1: # don't do anything if no argument was given
    return None


  options = self.parse_options_str( opts )

  extra_opts=""
  if 'tex2im_opts' in options:
    extra_opts = options['tex2im_opts']


  cmd = "tex2im -o %%s %s -- '%s' "%(extra_opts,args[0])
  print('%s'%cmd)
  # create a hash of the command used to create the image to use as the image
  # name. this way we can tell if the image has already been created before.
  scratch_dir = pathlib.Path("_macro_expander-scratch")
  if not scratch_dir.exists():
    scratch_dir.mkdir()
  hash = hashlib.sha1(cmd.encode('utf-8')).hexdigest()
  ofn = scratch_dir/f"mathimg-{hash}-image.png"
  lfn = scratch_dir/f"mathimg-{hash}-image.log"
  cmd = cmd%str(ofn)
  print("creating image with:'"+cmd+"'")
  if ofn.exists():
    print(f"\tskipping because '{str(ofn)}' already exists. please delete it if you want to force a rebuild.")
  else:
    with lfn.open('w') as f:
      status = subprocess.call(cmd,shell=True,stdout=f,stderr=f)
      if status != 0:
        print(f"\tWARNING: there was a problem running tex2im.")
        print(f"\tWARNING: command output was left in {str(lfn)}")
        print(f"\tWARNING: replacing with $...$, which may not work...")
        return "$"+args[0]+"$"

  if 'o' in options:
    options['output'] = options['o']
  if 'output' in options:
    output = options['output']
  else:
    output= "markdown"

  return _img(str(ofn),output=output)

def scriptimg(self,args,opts):
  '''Create an image by running a script and include it.'''

  if len(args) < 1: # don't do anything if no argument was given
    return None

  options = self.parse_options_str( opts )


  text = re.sub( "^\s*#!","#!",args[0] ) # strip off any whitespace before the shebang
  hash = hashlib.sha1(text.encode('utf-8')).hexdigest()

  scratch_dir = pathlib.Path("_macro_expander-scratch")
  if not scratch_dir.exists():
    scratch_dir.mkdir()
  sfn = scratch_dir/f"scriptimg-{hash}-script.txt"
  ofn = scratch_dir/f"scriptimg-{hash}-image.png"
  lfn = scratch_dir/f"scriptimg-{hash}-image.log"

  with sfn.open('w') as f:
    f.write(text)

  cmd = f"chmod +x {str(sfn)}; ./{str(sfn)}; mv out.png {str(ofn)}"
  print(f"creating image from script with:'{cmd}'")
  with lfn.open('w') as f:
    status = subprocess.call(cmd,shell=True,stdout=f,stderr=f)
    if status != 0:
      print(f"\tWARNING: there was a problem running script.")
      print(f"\tWARNING: the script and its output were left in {str(sfn)} and {str(lfn)}")
      return "ERROR: could not create image"


  if 'o' in options:
    options['output'] = options['o']
  if 'output' in options:
    output = options['output']
  else:
    output= "markdown"

  return _img(str(ofn),output=output)

def image(self,args,opts):
  '''Insert a (possibly remote) image.'''
  fn = args[0]
  options = self.parse_options_str( opts )

  url = urllib.parse.urlparse(fn)
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
      f = urllib.request.urlopen(url)
      lf.write(f.read())
      f.close()

  if 'o' in options:
    options['output'] = options['o']
  if 'output' in options:
    output = options['output']
  else:
    output = "markdown"

  return _img(str(fn),output=output)

includegraphics = image


def shell(self,args,opts):
  '''Run shell command and return output.'''
  # run command, send output to a file, and read it into a list
  with tempfile.TemporaryFile() as fp:
    cmd = ';'.join(args)
    subprocess.call( cmd, shell=True, stdout=fp )
    fp.seek(0)
    lines = fp.readlines()
    lines = [ line.decode('utf-8') for line in lines if type(line) is bytes ]

  options = self.parse_options_str( opts )
  stdout = "".join( _filter_and_transform_lines(lines,options) )

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
    print("\tWARNING: no filename found in write macro.")
    print('\tWARNING: please specify a filename in the macro options with [filename="NAME"], where NAME is the name of the file to write.')
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

  return "".join( _filter_and_transform_lines(lines,options) )





def _filter_and_transform_lines( lines, options ):
  '''
  filters and transforms a set of lines based on options.

  lines is a list of strings. the result of applying each filter or transformation to this list is returned.

  options:

  filter : example -> filter="pattern"

    this option specifies a regex pattern. lines matching that pattern are passed through. lines not matching
    the pattern are removed.

  transform : example -> transform="/pattern/replace/"

    this option specifies a regex substition to perform on each line.

  b : example -> b="10"

    this option specifies the first line to pass through. all lines before this line are removed.
    note that filter and transform happend *before* considering line numbers. so if a filter removes
    lines from the input, the line numbers will differ.

    it is also possible to give a pattern with an offset here, in which case the first line matching the pattern, plus the offset
    is taken as the first line.

    example -> b="/^line one/-1"

    this will start on the line above the first line beginning with "line one"

  e : example -> e="20"

    this option specifies the last line to pass through. all lines after this line are removed.
    note that filter and transform happen *before* considering line numbers. so if a filter removes
    lines from the input, the line numbers will differ.

    it is also possible to give a pattern with an offset here, in which case the first line, *after the beginning line*,
    matching the pattern, plus the offset
    is taken as the last line.

    example -> e="/^last line/+1"

    this will end on the line below the first line beginning with "last line" that comes after the beginning line.

  '''

  line_number = Word(nums)
  line_offset = Word(nums+"+-")
  line_pattern = QuotedString(quoteChar='/') | QuotedString(quoteChar='|')
  line_spec = (line_number("lnumber") | line_pattern("lpattern")) + Optional( Word("+-")("osign") + line_offset("offset") )

  if 'filter' in options:
    filt = options['filter']
    char = filt[0]
    pattern = filt.strip(char)
    lines = [line for line in lines if re.search(pattern,line)]

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
    spec = line_spec.parseString( options['b'] )
    if 'lnumber' in spec:
      b = int(spec['lnumber'])

    if 'lpattern' in spec:
      pattern = spec['lpattern']
      for i in range(len(lines)):
        if re.search(pattern,lines[i]):
          b = i+1 # b is 1 offset, not zero offset
          break

    offset = 0
    if 'offset' in spec:
      offset = int(spec['offset'])
      if spec['osign'] == '-':
        offset *= -1

    b += offset



  if 'e' in options:
    spec = line_spec.parseString( options['e'] )
    if 'lnumber' in spec:
      e = int(spec['lnumber'])

    if 'lpattern' in spec:
      pattern = spec['lpattern']
      for i in range(b-1,len(lines)):
        if re.search(pattern,lines[i]):
          e = i+1
          break

    offset = 0
    if 'offset' in spec:
      offset = int(spec['offset'])
      if spec['osign'] == '-':
        offset *= -1

    e += offset


  elif 'n' in options:
    e = b+int(options['n'])-1

  return lines[b-1:e]




def _img( filename, output="markdown", fmt=None, opts="" ):
  '''Return code to insert an image into document for various formats.'''

  if output == "markdown":
    return '![](./%s)'%filename

  if output == "latex":
    return r'\includegraphics{./%s}'%filename

  if output == "html":
    url = urllib.parse.urlparse(filename)
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
    f = urllib.request.urlopen(url)
    code  = base64.b64encode(f.read()).decode('utf-8')
    f.close()
    text  = r'''<img src="data:image/{fmt};base64,{code}" {opts}>'''.format(fmt=fmt,code=code,opts=opts)

    return text

  return None

