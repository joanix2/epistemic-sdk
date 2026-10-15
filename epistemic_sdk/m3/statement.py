from typing import TypeAlias
from .equation import Equation
from .membership import Membership
from .rewrite_rule import RewriteRule

Statement: TypeAlias = Equation | Membership | RewriteRule
