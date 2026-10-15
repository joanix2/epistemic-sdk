"""Recursive M3 syntax; object-language terms are represented by these nodes."""
from typing import TypeAlias

from .application import Application
from .constant import Constant
from .variable import Variable

Term: TypeAlias = Variable | Constant | Application
