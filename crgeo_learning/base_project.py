from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from functools import partial
from typing import Callable, Dict, List, Optional, Type, Union
import logging
from crgeo.debugging.profiling import profile
from crgeo.common.logging import setup_logging


logger = logging.getLogger(__name__)



def register_run_command(func):
    def _decorator(self, *args, **kwargs):
        if self.cfg.profile:
            profile(partial(func, self=self), args=args, kwargs=kwargs)
        else:
            func(self, *args, **kwargs)
    _decorator.tagged = True
    return _decorator


class BaseProject(metaclass=ABCMeta):
    _commands: Dict[str, Callable[[], None]]

    def __init__(self) -> None:
        pass

    def __init_subclass__(cls) -> None:
        methods = dict((attr, getattr(cls, attr)) for attr in dir(cls) if not attr.startswith('__'))
        commands: Dict[str, Callable[[], None]] = {}
        for name, method in methods.items():
            if isinstance(method, property):
                method = method.fget
            if hasattr(method, 'tagged'):
                commands[name] = method
        cls._commands = commands

    def run(self, cmd: str) -> None:
        subcommands = cmd.split(' ')
        subcommands = [s.strip() for s in subcommands]

        logger.info(f"Commands to be executed: {subcommands}")

        for subcmd in subcommands:
            if subcmd not in self._commands:
                raise ValueError(f"Received undefined command '{subcmd}'. Available commands are: {self._commands.keys()}")

        for idx, subcmd in enumerate(subcommands):
            logger.info(f"Running command {idx+1}/{len(subcommands)}: '{subcmd}'")
            self._commands[subcmd](self)
