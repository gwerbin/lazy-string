import sys

if sys.version_info >= (3, 9):
  from collections.abc import Callable
  from collections.abc import Mapping
  List  = list
  Tuple = tuple
  if sys.version_info >= (3, 10):
    from typing import ParamSpec
  else:
    from typing_extensions import ParamSpec
else:
  from typing import Callable
  from typing import Mapping
  from typing import List
  from typing import Tuple

from collections import UserString

from typing import Any, TypeVar, Union, overload


_P = ParamSpec('_P')
_Self = TypeVar("_Self", bound='LazyString')


class LazyString(UserString):
  """
  A string with delayed evaluation.

  :param func: Callable (e.g., function) returning a string.
  :param args: Optional positional arguments which will be passed to the ``func``.
  :param kwargs: Optional keyword arguments which will be passed to the ``func``.
  """

  __slots__ = ("_func", "_args", "_kwargs")
  
  _func: Callable[_P, str]
  _args: _P.args
  _kwargs: _P.kwargs

  @overload
  def __new__(cls, func: Callable[_P, str], *args: _P.args, **kwargs: _P.kwargs) -> UserString: ...
  @overload
  def __new__(cls, func: str) -> str: ...
  def __new__(cls, func: Union[_P, str], str], *args: _P.args, **kwargs: _P.kwargs) -> Union[UserString, str]:
    if isinstance(func, str):
      # Many `UserString` functions like `lower` and `__add__` wrap
      # returned values with a call to `self.__class__(...)` to ensure that
      # the result is of the same type as the original class.
      # However, the result of all of such methods is always a string,
      # so there's no need to create a new instance of a `LazyString`.
      return func
    else:
      return UserString.__new__(cls)

  def __init__(self, func: Callable[_P, str], *args: _P.args, **kwargs: _P.kwargs) -> None:
    self._func = func
    self._args = args
    self._kwargs = kwargs

  # Custom methods

  @property
  def data(self) -> str:
    return self._func(*self._args, **self._kwargs)

  def __copy__(self: _Self) -> _Self:
    return LazyString(self._func, *self._args, **self._kwargs)

  def __repr__(self) -> str:
    return f"{self.__class__.__name__}({self._func!r}, *{self._args!r}, **{self._kwargs!r})"

  def __getnewargs_ex__(self) -> Tuple[Tuple, Mapping]:
    args = (self._func, ) + self._args
    return (args, self._kwargs)

  # Proxy methods

  def __getstate__(self) -> Tuple[Callable, Tuple, Mapping]:
    return (self._func, self._args, self._kwargs)

  def __setstate__(self, state: Tuple[Callable, Tuple, Mapping]) -> None:
    self._func, self._args, self._kwargs = state

  # TODO: Is this needed? Why wouldn't it already be part of UserString?
  def __getattr__(self, name: str) -> Any:
    return getattr(self.data, name)
