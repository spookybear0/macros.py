import codecs
from encodings import utf_8
from io import StringIO
import tokenize
import encodings
import types
import re
import black
import traceback
from tokenize import NAME, OP, STRING, ENDMARKER, DEDENT, INDENT, NL, NEWLINE

__all__ = ("import_with_macros", "get_macro", "get_all_macros", "get_translated_code", "create_macro")

macro_re = re.compile("(.*)\(([^)]+?)\)")

debug = False

class PreprocessorError(Exception):
    pass

class Macro:
    def __init__(self, name, code, func_sig=""):
        self.name = name
        self.code = tokenize.untokenize(code)
        self.tokens = code
        self.func_sig = func_sig
        
        if func_sig == "()":
            self.args = []
        elif func_sig:
            self.args = macro_re.findall(func_sig)[0][1].split(",")
        else:
            self.args = []
        
    
    def execute(self, *args):
        """
        Executes a macro to the best ability at runtime
        
        More limited than compile time
        
        Not guarenteed to work
        """
        final_tokens = []
        
        # args
        arg_loop = False
        args_replaced = 0
        type_p, name_p = None, None
        for type, name in self.tokens:
            if arg_loop:
                if type == OP and name == ")":
                    arg_loop = False
                elif type == NAME:
                    name = args[args_replaced]
                    args_replaced += 1
                final_tokens.append((type, name))
            elif type == OP and type_p == NAME: # func call
                arg_loop = True
                final_tokens.append((type, name))
            else:
                final_tokens.append((type, name))
            type_p, name_p = type, name_p

        exec(tokenize.untokenize(final_tokens))
        
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
_translated_code = ["",] # make it mutuable

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
    
    indent_level = 0
    
    indented = False
    start_indent_level = 0
    
    # preprocess macros
    for type, name, token_start, token_end, line_data in tokenize.generate_tokens(readline):
        line = token_start[0]
        char = token_start[1]
        
        if type == INDENT:
            indent_level += 1
        elif type == DEDENT:
            indent_level -= 1
        
        # end marker
        if type == ENDMARKER:
            break

        # ignore macro, def, and args so we don't get a syntax error
        if (type == NAME and name_p == "def" and type_pp == NAME and name_pp == "macro")\
            or (type_p == NAME and type == NAME and name == "def")\
            or (type == NAME and name == "macro"):
            pass

        # ignore macro name token
        elif _macros.by_name(name):
            pass
        elif type == NAME and name == "macros":
            #__import__("sys").modules["macros"]
            yield NAME, "__import__"
            yield OP, "("
            yield STRING, '"sys"'
            yield OP, ")"
            yield OP, "."
            yield NAME, "modules"
            yield OP, "["
            yield STRING, '"macros"'
            yield OP, "]"
        # start looking for arguments to call
        # NAME(
        elif _macros.by_name(name_p) and type == OP and name == "(":
            func_arg_loop = True
            func_arg_name = name_p
            func_args = ""
            func_args_types = []
        # func macro
        # macro def NAME
        elif (name_ppp == "macro" and name_pp == "def" and type_p == NAME):
            start_indent_level = indent_level # should always be zero
            
            create_loop = True
            code = []
            
            # has args
            if name == "(":
                func_sig = f"{mcr_name}("
                func_arg_create_loop = True
            elif name == ":":
                pass
            else:
                code.append((type, name))
                
            mcr_name = name_p
            
            mode = None
            
        # add to func_signature, but if end of the signature stop loop
        elif func_arg_create_loop:
            func_sig += name
            if type == OP and name == ")":
                func_arg_create_loop = False
        elif create_loop:
            # make sure we are still checking for macro chars and if it uses one
            # of our ending sequences (\n, ;), stop the loop and define the macro
            if mode and (name in mode or mode in name):
                indented = False
                create_loop = False
                
                new = []
                copy = code.copy()
                copy.reverse()
                keep_adding = True

                for x in copy:
                    if "\n" in x and keep_adding:
                        pass
                    else:
                        new.append(x)
                        keep_adding = False
    
                new.reverse()
                code = new
            
                _macros.append(Macro(mcr_name, code, func_sig))
            elif type in (NL, NEWLINE) and not indented:
                pass
            elif type == INDENT and not indented:
                indented = True
            elif type == DEDENT and start_indent_level == indent_level:
                indented = False
                create_loop = False
                
                new = []
                copy = code.copy()
                copy.reverse()
                keep_adding = True

                for x in copy:
                    if ("\n" in x[1] or "\r" in x[1]) and keep_adding:
                        pass
                    else:
                        new.append(x)
                        keep_adding = False
    
                new.reverse()
                code = new
                
                _macros.append(Macro(mcr_name, code, func_sig))
            elif name_p == ")" and name == ":":
                pass
            else:
                # add token to code to yield when used
                code.append((type, name))
        elif func_arg_loop:
            # end the loop, call macro with replacing arguments
            if name == ")":
                func_args += ")"
                
                func_args = func_args.strip("()").split(",")
                
                macro = _macros.by_name(func_arg_name)
                func_arg_loop = False
                
                if len(func_args) != len(macro.args):
                    exc_args = str(tuple(x for x in macro.args)).replace("'", "")
                    try:
                        raise PreprocessorError(f"macro !{func_arg_name}{exc_args} was given too many positional arguments")
                    except PreprocessorError:
                        # so we actually get traceback
                        traceback.print_exc()
                        exit(1)
                
                # create func now with args
                for type, name in macro.tokens:
                    if type == NAME and name in macro.args:
                        indx = macro.args.index(name)
                        
                        try:
                            name = func_args[indx]
                            type = func_args_types[indx]
                        except IndexError: # not supplied enough args
                            exc_args = str(tuple(x for x in macro.args)).replace("'", "")
                            try:
                                raise PreprocessorError(f"macro !{func_arg_name}{exc_args} is missing a required positional argument")
                            except PreprocessorError:
                                # so we actually get traceback
                                traceback.print_exc()
                                exit(1)
                    yield type, name
            # add to func args while searching
            else:
                func_args += name
                func_args_types.append(type)
        # use macro, since our macro isn't actually defined as a variable
        # we have to prevent it from erroring by checking beforehand
        # and then executing the macro by yielding tokens
        elif type_p == NAME and _macros.by_name(name_p):
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
    try:
        code, length = utf_8.decode(source, errors)
        
        final = str(tokenize.untokenize(translate(StringIO(code).readline)))
        if debug:
            print(final)
        
        if final != "":
            try:
                _translated_code[0] = black.format_str(final, mode=black.FileMode(line_length=99999))
            except Exception:
                _translated_code[0] = final
        
        return final, length
    except Exception:
        if debug:
            traceback.print_exc()
            print()
            for m in get_all_macros():
                print(m, "\n", m.code, m.tokens)

class MacroIncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(self, input, errors, final=False):
        if final:
            return macro_decode(input, errors)

        else:
            return "", 0

def search_function(s):
    global debug
    if not "macros" in s:
        return None
    elif "debug" in s:
        debug = True
    
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

def get_translated_code():
    return _translated_code[0]

if __name__ == "__main__":
    import_with_macros("D:/code/python/projects/macros.py/examples/until.py")
