'''Preprocess a markdown file by doing macro expansion an other things.'''

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

import our_macros


class MacroProcessor(object):
  def __init__(self):
    # define macro grammer
    name = Word(alphas)
    self.opts_delimiters = ('[',']')
    options = originalTextFor( nestedExpr( *self.opts_delimiters ) )
    self.args_delimiters = ('{','}')
    arguments = originalTextFor( nestedExpr( *self.args_delimiters ) )

    self.macroParser = Combine( WordStart('\\') + Literal('\\') + name('name') + Optional(options('options')) + ZeroOrMore(arguments)('arguments') )
    self.macroParser.setParseAction( self.expand )

    self.added_macros = {}

  def addParserAction(self,func):
    self.macroParser.addParserAction(func)

  def addMacro(self,name,func):
    self.added_macros[name] = func

  def process(self,text,repeat=True):
    '''Process a string. Macros found in the string that have handlers will be replaced with the output of the handler.'''

    while True:
      newtext = self.macroParser.transformString( text )

      if newtext == text or repeat == False:
        break
      text = newtext

    return text

  def expand(self,text,loc,toks):
    '''This function is called each time a macro is found by pyparsing.
       It will recieve the matched elements as a dict in the toks argument. The macro name
       of the macro that was found will be in toks["name"]. The macro options and arguments will
       be in toks["options"] and toks["arguments"].'''
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

    replacement = None
    nargs=len(inspect.getargspec( handler ).args)
    if nargs == 3:
      replacement = handler(self,arguments,options)
    elif nargs == 2:
      replacement = handler(arguments,options)
    elif nargs == 1:
      replacement = handler(arguments)

    return replacement


  def parse_options_str(self, opts_str):
    '''Parse a string of comma separated options and return a dict.'''

    if isinstance( opts_str, list ):
      return [ parse_options_str(o) for o in opts_str ]


    key = Word(alphas, alphanums+'_')
    val = QuotedString(quoteChar='"') | QuotedString(quoteChar="'") | Word(alphanums+"/|()_")
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

