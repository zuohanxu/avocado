# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; specifically version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright: RedHat 2013-2014
# Author: Ruda Moura <rmoura@redhat.com>

"""Plugin Managers."""

from avocado.plugins.builtin import load_builtins
from avocado.plugins.plugin import Plugin

DefaultPluginManager = None


class PluginManager(object):

    """
    Base class for plugins manager.

    You'll inherit from this to write you own plugins manager.
    """

    def __init__(self):
        self.plugins = []
        self.disabled_plugins = []

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    def load_plugins(self):
        raise NotImplementedError('Managers must implement the method load_plugins')

    def configure(self, app_parser, cmd_parser):
        for plugin in self.plugins:
            if plugin.enabled:
                plugin.configure(app_parser, cmd_parser)

    def activate(self, app_args):
        for plugin in self.plugins:
            if plugin.configured:
                plugin.activate(app_args)

class BuiltinPluginManager(PluginManager):

    """
    Builtins plugin manager.
    """

    def load_plugins(self):
        for plugin in load_builtins():
            self.add_plugin(plugin())


class ExternalPluginManager(PluginManager):

    """
    Load external plugins.
    """

    def load_plugins(self, path, pattern='avocado_*.py'):
        from glob import glob
        import os
        import imp
        if path:
            candidates = glob(os.path.join(path, pattern))
            candidates = [(os.path.splitext(os.path.basename(x))[0], path) for x in candidates]
            candidates = [(x[0], imp.find_module(x[0], [path])) for x in candidates]
            for candidate in candidates:
                mod = imp.load_module(candidate[0], *candidate[1])
                for name in mod.__dict__:
                    x = getattr(mod, name)
                    if isinstance(x, type) and issubclass(x, Plugin):
                        self.add_plugin(x())

    def add_plugins(self, plugins):
        for plugin in plugins:
            self.add_plugin(plugin)


class AvocadoPluginManager(BuiltinPluginManager, ExternalPluginManager):

    """
    Avocado Plugin Manager.

    Load builtins and external plugins.
    """

    def __init__(self):
        BuiltinPluginManager.__init__(self)
        ExternalPluginManager.__init__(self)

    def load_plugins(self, path=None):
        BuiltinPluginManager.load_plugins(self)
        ExternalPluginManager.load_plugins(self, path)


def get_plugin_manager():
    """
    Get default plugin manager.
    """
    global DefaultPluginManager
    if DefaultPluginManager is None:
        DefaultPluginManager = AvocadoPluginManager()
    return DefaultPluginManager
