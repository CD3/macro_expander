# standard modules
import sys, inspect
import pprint

# non-standard modules
from pyparsing import *

# local modules
try:
  # support for user defined macro handlers
  import macros as user_macros
  sys.modules['user_macros'] = user_macros
  del sys.modules['macros']
except:
  pass

from . import our_macros 

try:
  import cPickle as pickle
except:
  import pickle


class MacroProcessor(object):
  def __init__(self,use_cache=False):
    # define macro grammer
    name = Word(alphas)
    self.opts_delimiters = ('[',']')
    options = originalTextFor( nestedExpr( *self.opts_delimiters ) )
    self.args_delimiters = ('{','}')
    arguments = originalTextFor( nestedExpr( *self.args_delimiters ) )

    self.macroParser = Combine( WordStart('\\') + Literal('\\') + name('name') + Optional(options('options')) + OneOrMore(arguments)('arguments') )

    self.added_macros = {}

    self.cache = {}
    self.use_cache = use_cache

  def addParserAction(self,func):
    self.macroParser.addParserAction(func)

  def addMacro(self,name,func):
    self.added_macros[name] = func

  def clearCache(self):
    '''Clear current cache.'''
    self.cache = {}

  def updateCache(self,c):
    '''Update cache with another cache.'''
    self.cache.update(c)

  def writeCache(self,fn):
    '''Write cache to a file.'''
    with open(fn,'wb') as fh:
      pickle.dump(self.cache,fh)

  def readCache(self,fn):
    '''Read cache from a file. Current cache will be lost.'''
    with open(fn,'rb') as fh:
      self.cache = pickle.load(fh)


  def process(self,text,repeat=True):
    '''Process a string. Macros found in the string that have handlers will be replaced with the output of the handler.'''

    # repeat processing until we don't get any changes.
    # this allows nested macros
    while True:

      # first we parse the string and get a list of parts.
      # parts are either a tuple of the text matched by pyparsing and the ParseResult returned,
      # or the text between matches.
      # benchmarks indicate that this is actually fater than using pyparsing's transformString
      # and it allows for macro expansion to be done in parallel.
      results = self.macroParser.scanString( text )
      parts = []
      last_i = 0
      for r in results:
        parts.append(text[last_i:r[1]])
        parts.append( (text[r[1]:r[2]],r[0])  )
        last_i = r[2]
      parts.append(text[last_i:])

      # now process all of the parts, performing macro expansion on the macros that have been parsed.
      newtext = "".join([self._process_part(p) for p in parts])


      if newtext == text or repeat == False:
        break
      text = newtext


    return text

  def _process_part(self,part):
    if isinstance(part,tuple):
      replace = self.expand(part[0],0,part[1])
      if replace is None:
        return part[0]
      return replace

    return part

  def expand(self,match,loc,toks):
    '''This function is called to expand a macro that has been parsed by pyparsing.
       It will recieve the matched elements as a dict in the toks argument. The original string, and
       its location in the text are also padded (i.e., this function can be used as a parseAction). The macro name
       of the macro that was found will be in toks["name"]. The macro options and arguments will
       be in toks["options"] and toks["arguments"].
       
       It should process the macro and return the text that will replace it, or None.

       If self.use_cache is True, the expanded text is written to cache. If the same macro is found again (it must be identical),
       the cached value will be used for expansion.
       '''

    if self.use_cache and match in self.cache:
      return self.cache[match]

    name = str(toks.name)
    # options and arguments are nested expressions. the token we get
    # will be wrapped in [] (for options) and {} (for arguments), so we need
    # to strip them off.
    options   = toks.options[len(self.opts_delimiters[0]):-len(self.opts_delimiters[1])]
    arguments = [   argument[len(self.args_delimiters[0]):-len(self.args_delimiters[1])] for argument in toks.arguments]


    # Order matters here. The first handler found will be used. Handlers are
    # looked for in:
    # 1. the user macros.py file.
    # 2. the added_macros member (macro handlers added with the addMacro method)
    # 3. our macros.py file
    handler = lambda x,y,z : None
    if 'user_macros' in sys.modules and hasattr(user_macros,name):
      handler = getattr(user_macros,name)
    elif name in self.added_macros:
      handler = self.added_macros[name]
    elif hasattr(our_macros,name):
      handler = getattr(our_macros,name)

    nargs=len(inspect.signature( handler ).parameters)
    if nargs == 3:
      replacement = handler(self,arguments,options)
    elif nargs == 2:
      replacement = handler(arguments,options)
    elif nargs == 1:
      replacement = handler(arguments)

    if self.use_cache:
      self.cache[match] = replacement


    return replacement


  def parse_options_str(self, opts_str):
    '''Parse a string of comma separated options and return a dict.'''

    if isinstance( opts_str, list ):
      return [ parse_options_str(o) for o in opts_str ]


    key = Word(alphas, alphanums+'_')
    val = QuotedString(quoteChar='"') | QuotedString(quoteChar="'") | Word(alphanums+"/|()_.:;!^$#*-=+")
    opt = key("key") + Optional("=" + val("val"))


    options = dict()
    for o in opt.searchString( opts_str ):
      if 'val' in o:
        if not o['key'] in options:
          options[o['key']] = o['val']
        else:
          if not isinstance(options[o['key']],list):
            tmp = options[o['key']]
            options[o['key']] = list()
            options[o['key']].append(tmp)

          options[o['key']].append(o['val'])

      else:
        options[o['key']] = True

    return options

