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

class MacroParser:
    name = Word(alphas)
    opts_delimiters = ('[',']')
    options = originalTextFor( nestedExpr( *opts_delimiters ) )
    args_delimiters = ('{','}')
    arguments = originalTextFor( nestedExpr( *args_delimiters ) )

    macro = Combine( WordStart('\\') + Literal('\\') + name('name') + Optional(options('options')) + OneOrMore(arguments)('arguments') )
    macro.parseWithTabs()

def expand_macro( macro_processor, parsed_tokens ):
    '''This function is called to expand a macro that has been parsed by pyparsing.
       It recieves a MacroExpansionAction that contains everything need to perform the expansion.

       It will recieve the matched elements as a ParseResult in the parsed_tokens argument.
       The macro name of the macro that was found will be in parsed_tokens["name"]. The macro options and arguments will
       be in parsed_tokens["options"] and parsed_tokens["arguments"]. The original text that was matched will be in parsed_tokens[0]
       
       It should process the macro and return the text that will replace it, or None.

       If self.use_cache is True, the expanded text is written to cache. If the same macro is found again (it must be identical),
       the cached value will be used for expansion.
       '''

    if macro_processor.use_cache and parsed_tokens[0] in macro_processor.cache:
      return macro_processor.cache[parsed_tokens[0]]

    name = str(parsed_tokens.name)
    # options and arguments are nested expressions. the token we get
    # will be wrapped in [] (for options) and {} (for arguments), so we need
    # to strip them off.
    options   = parsed_tokens.options[len(MacroParser.opts_delimiters[0]):-len(MacroParser.opts_delimiters[1])]
    arguments = [   argument[len(MacroParser.args_delimiters[0]):-len(MacroParser.args_delimiters[1])] for argument in parsed_tokens.arguments]


    # Order matters here. The first handler found will be used. Handlers are
    # looked for in:
    # 1. the user macros.py file.
    # 2. the added_macros member (macro handlers added with the addMacro method)
    # 3. our macros.py file
    handler = macro_processor.macroCallbacks.get(name, None)

    if handler is None:
      return parsed_tokens[0]

    nargs = macro_processor.macroCallbacksArity[name]
    if nargs == 3:
      replacement = handler(self,arguments,options)
    elif nargs == 2:
      replacement = handler(arguments,options)
    elif nargs == 1:
      replacement = handler(arguments)

    if replacement is None:
      return parsed_tokens[0]

    if self.use_cache:
      self.cache[parsed_tokens[0]] = replacement
    

    return replacement


class MacroProcessor:
  def __init__(self,use_cache=False):
    # define macro grammer
    self.macroParser = MacroParser.macro

    self.added_macros = {}

    self.cache = {}
    self.use_cache = use_cache

    self.macroCallbacks = {}
    self.macroCallbacksArity = {}
    self._updateMacroCallbacksWithOurMacros()
    self._updateMacroCallbacksWithUserMacros()

  def addParserAction(self,func):
    self.macroParser.addParserAction(func)

  def addMacro(self,name,func):
    self.added_macros[name] = func
    self.macroCallbacks[name] = func
    self._updateMacroCallbacksWithUserMacros()

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

  def _updateMacroCallbacksWithOurMacros(self):
    self.macroCallbacks = dict( inspect.getmembers(our_macros, lambda m: inspect.isfunction(m) and m.__module__ == our_macros.__name__ and not m.__name__.startswith("_")) )
    self._updateMacroCallbacksArity()
    

  def _updateMacroCallbacksWithUserMacros(self):
    if 'user_macros' in sys.modules:
      self.macroCallbacks.update( dict( inspect.getmembers(user_macros, lambda m: inspect.isfunction(m) and m.__module__ == user_macros.__name__ and not m.__name__.startswith("_")) ) )
      self._updateMacroCallbacksArity()

  def _updateMacroCallbacksArity(self):
    for k,v in self.macroCallbacks.items():
      self.macroCallbacksArity[k] = len(inspect.signature(v).parameters)


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
      output_parts = []
      parsed_macros = []
      macro_part_mapping = []
      last_i = 0
      for parsed_tokens,si,ei in results:
        output_parts.append(text[last_i:si])
        # only add macros we don't have a chached value for.
        if self.use_cache and parsed_tokens[0] in self.cache:
          output_parts.append(self.cache[parsed_tokens[0]])
        else:
          parsed_macros.append(parsed_tokens)
          macro_part_mapping.append(len(output_parts))
          output_parts.append(None)
        last_i = ei
      output_parts.append(text[last_i:])

      # process all of the macros
      expanded_macros = map(self._expand_macro, parsed_macros)

      for i,e in enumerate(expanded_macros):
        output_parts[macro_part_mapping[i]] = e
        if self.use_cache:
          self.cache[parsed_macros[i][0]] = e
    


      newtext = "".join(output_parts)


      if newtext == text or repeat == False:
        break
      text = newtext


    return text

  def _expand_macro(self,parsed_toks):
    '''This function is called to expand a macro that has been parsed by pyparsing.
       It will recieve the matched elements as a dict in the parsed_toks argument.
       The macro name of the macro that was found will be in parsed_toks["name"]. The macro options and arguments will
       be in parsed_toks["options"] and parsed_toks["arguments"]. The original text that was matched will be in parsed_toks[0]
       
       It should process the macro and return the text that will replace it, or None.

       If self.use_cache is True, the expanded text is written to cache. If the same macro is found again (it must be identical),
       the cached value will be used for expansion.
       '''

    if self.use_cache and parsed_toks[0] in self.cache:
      return self.cache[parsed_toks[0]]

    name = str(parsed_toks.name)
    # options and arguments are nested expressions. the token we get
    # will be wrapped in [] (for options) and {} (for arguments), so we need
    # to strip them off.
    options   = parsed_toks.options[len(MacroParser.opts_delimiters[0]):-len(MacroParser.opts_delimiters[1])]
    arguments = [   argument[len(MacroParser.args_delimiters[0]):-len(MacroParser.args_delimiters[1])] for argument in parsed_toks.arguments]


    # Order matters here. The first handler found will be used. Handlers are
    # looked for in:
    # 1. the user macros.py file.
    # 2. the added_macros member (macro handlers added with the addMacro method)
    # 3. our macros.py file
    handler = self.macroCallbacks.get(name, None)

    if handler is None:
      return parsed_toks[0]

    nargs = self.macroCallbacksArity[name]
    if nargs == 3:
      replacement = handler(self,arguments,options)
    elif nargs == 2:
      replacement = handler(arguments,options)
    elif nargs == 1:
      replacement = handler(arguments)

    if replacement is None:
      return parsed_toks[0]

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

