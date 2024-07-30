# read version from installed package
from importlib.metadata import version
__version__ = version("firepydaq")
print("Importing FIREpyDAQ v."+__version__)
