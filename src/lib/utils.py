###############
# Module import/check
#
import importlib

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
