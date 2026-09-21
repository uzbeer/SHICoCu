###############
# Module import/check
#
import importlib, sys, time, os, re
import datetime as dt           # standard

def extmodule(module: str, obj=None):
    try:
        mod = importlib.import_module(module)
        return getattr(mod, obj) if obj else mod
    except (ImportError, ModuleNotFoundError):
        err(f"Module \"{module}\" is missing.")
        raise Exception("Missing module")
    except AttributeError:
        err(f"Module \"{module}\" seems to be missing: {obj}")
        raise Exception("Error with module")

#################
# Sanitize filepath
#
def sanitize(filepath: str, dir = "", ext = "", fix_dir = False) -> str | None:
    if filepath.endswith(("/", "\\")):
        raise ValueError(f"Invalid path: {filepath} must point a filename.")

    if not ext.startswith("."):
        ext = f".{ext}"

    if not filepath.endswith(ext):
        filepath += ext

    if os.path.isabs(filepath) or os.path.dirname(filepath):
        abspath = os.path.abspath(filepath)
    else:
        abspath = os.path.abspath(os.path.join(dir, filepath))

    unsafe_chars_pattern = r'[\x00-\x1f\x7f<>:"|?*\n\r;\&`$~]'
    if re.search(unsafe_chars_pattern, abspath):
        raise ValueError(f"Insecure path detected: {abspath}")

    if not abspath.startswith(os.getcwd()):
        raise ValueError("Invalid path detected. Output should be inside working directory.")

    if (fix_dir) and (not os.path.exists(os.path.dirname(abspath))):
        os.makedirs(os.path.dirname(abspath))

    return abspath

#################
# Bifurcate class
#
class Bif:
    def __init__(self):
        self._streams = [ sys.stdout ]

    def add(self, stream):
        self._streams.append(stream)

    def write(self, data):
        for s in self._streams:
            s.write(data)

    def flush(self):
        for s in self._streams:
            s.flush()


###############
# Parser class
#
class Parser:
    def __init__(self, argv: list | None = None, help_text: str | None = None):
        self.argv = argv if (argv) else sys.argv[1:]
        self.help_text = help_text if (help_text) else __doc__
        self.args = {}
        self.tokens = []

        # print("\nArguments passed:", self.argv)
        self._loading_args()

    def __call__(self, key: str):
        return self.args.get(key)

    def __contains__(self, key):
        try:
            self.args.get(key)
            return True
        except (KeyError, IndexError):
            return False

    def _loading_args(self):
        i = 0
        while i < (len(self.argv)):
            arg = self.argv[i]
            if arg.startswith("--"):
                #It is a Keyword, check for assigned value
                if self.argv[i+1].startswith("-"):
                    self.args[arg] = None
                else:
                    i += 1
                    self.args[arg] = self.argv[i]
            elif arg.startswith("-"):
                #It is 1 or more Flags
                for f in arg[1:]:
                    self.args[f"-{f}"] = True
            else:
                #It is a Token
                self.args[arg] = True
                self.tokens.append(arg)
            i += 1
        # cy(self.args, "\n")



###############
# Print() options
#

def ora(*args, **kwargs): # True Orange
    _encoded_print("\033[38;5;208m", *args, **kwargs) # orange colour

def cy(*args, **kwargs): # Cyan
    _encoded_print("\033[96m", *args, **kwargs) # cyan colour

def ora2(*args, **kwargs): # Yellowy Orange: R=255 G=165 B=0
    _encoded_print("\033[38;2;255;165;0m", *args, **kwargs)

def pur(*args, **kwargs): # Dim purple 96 69 96
    _encoded_print("\033[38;2;146;69;146m", *args, **kwargs)

def err(*args, **kwargs):
    bold()
    _encoded_print("\033[38;2;226;69;76m", *args, **kwargs)
    rst("\n\n")

def bold(): # Just sets the start code for BOLD
    _encoded_print("\033[1m")

def ita(): # ITALIC
    _encoded_print("\033[3m")

# def dim(): # DIM TEXT
#     _encoded_print("\033[2m")

def blink(): # BLINK
    _encoded_print("\033[5m")

def inv(): # INVERT
    _encoded_print("\033[7m")

def rst(*args, **kwargs): # Reset ANSI codes
    _encoded_print("\033[0m", *args, **kwargs)

def _encoded_print(code: str, *args, **kwargs):
    print(code, *args, sep="", **kwargs, end="")

###############
# Printing timestamps
#
def timestamp(t0 = None, label:str = ""):
    t1 = time.perf_counter()
    cy("[")
    ora2(dt.datetime.now().strftime("%H:%M:%S.%f")[:-4])
    cy("]")
    ora(label)
    if (t0):
        cy(f"{t1 - t0:.2f}s\n")
    rst()
    return t1



######
# \n New line
# \r Return to beginning of the line
# \b Back the cursor 1 character
#
# Other ANSI codes:
# Style	            Code	    Reset Code
# Bold	            \033[1m	    \033[22m
# Dim / Faint	    \033[2m	    \033[22m
# Italic	        \033[3m	    \033[23m
# Underline	        \033[4m	    \033[24m
# Blink	            \033[5m	    \033[25m
# Invert (Reverse)	\033[7m	    \033[27m
# Hidden	        \033[8m	    \033[28m
# Strikethrough	    \033[9m	    \033[29m
#
# \033[0m to reset all styles and colors
