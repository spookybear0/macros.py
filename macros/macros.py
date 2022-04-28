import codecs
from encodings import utf_8
from io import StringIO
import tokenize
import encodings
import types
import re
import sys

from black import token
__all__ = ("import_with_macros", "get_macro", "get_all_macros")

macro_re = re.compile("(.*)\(([^)]+?)\)")

class Macro:
    def __init__(self, name, code, func_sig=""):
        self.name = name
        self.code = tokenize.untokenize(code)
        self.tokens = code
        self.func_sig = func_sig
        
        if func_sig:
            self.args = macro_re.findall(func_sig)[0][1].split(",")
        else:
            self.args = []
        
    def __repr__(self):
        return f'Macro(name="{self.name}", func_sig="{self.func_sig}")'
        
class MacroList(list):
    def by_name(self, name):
        for mcr in self:
            if mcr.name == name:
                return mcr
            
    def __repr__(self):
        final = "["
        i = 0
        for mcr in self:
            final += mcr.name + mcr.func_sig.replace(",", ", ") # add spacing
            
            if i == len(self):
                final += ", "
            i += 1
        final += "]"
        
        return final
            
_macros = MacroList()

def translate(readline):
    # iteration variables
    type_p, name_p, type_pp, name_pp, type_ppp, name_ppp = None, None, None, None, None, None
    
    create_loop = False
    code = []
    mcr_name = ""
    mode = "\n"
    
    func_arg_create_loop = False
    func_sig = ""
    
    func_arg_loop = False
    func_args = ""
    func_args_types = []
    func_arg_name = ""
    
    # preprocess macros
    for type, name,_,_,_ in tokenize.generate_tokens(readline):
        # end marker
        if type == tokenize.ENDMARKER:
            break

        # ignore !, !!, and the name of the macro so we don't get a syntax error
        if type == tokenize.ERRORTOKEN or (type_p == tokenize.ERRORTOKEN and type == tokenize.NAME):
            pass
        # ignore macro name token
        elif _macros.by_name(name):
            pass
        elif type == tokenize.NAME and name == "macros":
            #__import__("sys").modules["macros"]
            yield tokenize.NAME, "__import__"
            yield tokenize.OP, "("
            yield tokenize.STRING, '"sys"'
            yield tokenize.OP, ")"
            yield tokenize.OP, "."
            yield tokenize.NAME, "modules"
            yield tokenize.OP, "["
            yield tokenize.STRING, '"macros"'
            yield tokenize.OP, "]"
        # start looking for arguments
        elif _macros.by_name(name_p) and type == tokenize.OP and name == "(":
            func_arg_loop = True
            func_arg_name = name_p
            func_args = ""
            func_args_types = []
        elif type_p == tokenize.NAME and type_pp == tokenize.ERRORTOKEN:
            # show that we need to loop until macro definition ends
            create_loop = True
            code = []
            
            # has args
            if type == tokenize.OP and name == "(":
                func_sig = f"{mcr_name}("
                func_arg_create_loop = True
            else:
                code.append((type, name))
            
            mcr_name = name_p
            
            # if !! make it multiline (macros have to be ended with ;)
            if type_ppp == tokenize.ERRORTOKEN and name_ppp == "!":
                mode = ";"
            else:
                mode = "\n" # default, just one !
        # add to func_signature, but if end of the signature stop loop
        elif func_arg_create_loop:
            func_sig += name
            if type == tokenize.OP and name == ")":
                func_arg_create_loop = False
        elif create_loop:
            # make sure we are still checking for macro chars and if it uses one
            # of our ending sequences (\n, ;), stop the loop and define the macro
            if name in mode or mode in name:
                create_loop = False
                _macros.append(Macro(mcr_name, code, func_sig))
            else:
                # add token to code to yield when used
                code.append((type, name))
        elif func_arg_loop:
            # end the loop, call macro with replacing arguments
            if type == tokenize.OP and name == ")":
                func_args += ")"
                
                func_args = func_args.strip("()").split(",")
                
                macro = _macros.by_name(func_arg_name)
                func_arg_loop = False
                
                # create func now with args
                for type, name in macro.tokens:
                    if type == tokenize.NAME and name in macro.args:
                        indx = macro.args.index(name)
                        
                        try:
                            name = func_args[indx]
                            type = func_args_types[indx]
                        except IndexError: # not supplied enough args
                            exc_args = str(tuple(x for x in macro.args)).replace("'", "")
                            raise TypeError(f"macro !{func_arg_name}{exc_args} is missing a required positional argument")
                    yield type, name
            # add to func args while searching
            else:
                func_args += name
                func_args_types.append(type)
        # use macro, since our macro isn't actually defined as a variable
        # we have to prevent it from erroring by checking beforehand
        # and then executing the macro by yielding tokens
        elif type_p == tokenize.NAME and _macros.by_name(name_p):
            macro = _macros.by_name(name_p)

            # convert code to tokens and execute it
            for type, name in macro.tokens:
                yield type, name
        else:
            # no special stuff found, just return normal values
            yield type, name

        # used for getting values of previous iterations
        # its a little weird but it works
        type_ppp, name_ppp = type_pp, name_pp
        type_pp, name_pp = type_p, name_p
        type_p, name_p = type, name

class MacroStreamReader(utf_8.StreamReader):
    def __init__(self, *args, **kwargs):
        codecs.StreamReader.__init__(self, *args, **kwargs)
        data = tokenize.untokenize(translate(self.stream.readline))
        self.stream = StringIO(data)

# it just works okay
def macro_decode(source, errors="strict"):
    code, length = utf_8.decode(source, errors)
    
    return str(tokenize.untokenize(translate(StringIO(code).readline))), length

class MacroIncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(self, input, errors, final=False):
        if final:
            return macro_decode(input, errors)

        else:
            return "", 0

def search_function(s):
    if s != "macros": return None
    utf8 = encodings.search_function("utf8") # assume utf8 encoding
    
    return codecs.CodecInfo(
        name="macros",
        encode=utf8.encode,
        decode=macro_decode,
        incrementalencoder=utf8.incrementalencoder,
        incrementaldecoder=MacroIncrementalDecoder,
        streamreader=MacroStreamReader,
        streamwriter=utf8.streamwriter,
    )

codecs.register(search_function)

def import_with_macros(filename):
    mod = types.ModuleType(filename)
    f=open(filename)
    data = tokenize.untokenize(translate(f.readline))
    
    exec(data, mod.__dict__)
    return mod

def create_macro(name, code):
    _macros.append(Macro(name, code))

def get_macro(name):
    return _macros.by_name(name)

def get_all_macros():
    return _macros

if __name__ == "__main__":
    import_with_macros("D:/code/python/projects/macros.py/examples/max.py")