#
# config.py
# Copyright (c) 2012 Thorsten Philipp <kyrios@kyri0s.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in the 
# Software without restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import root
from twisted.web import error



class Config(root.KniveJsonApiResource):
    """All the sections"""

    sectionCache = {}

    def getChild(self, path, request):
        if path in self.sectionCache:
            return self.sectionCache[path]
        elif path in self.backend.config:
            self.sectionCache[path] = ConfigSection(self.backend.config, path)
            return self.sectionCache[path]
        else:
            return error.NoResource()

    def _GET(self, request):
        for section in self.backend.config:
            settings = []
            for setting in self.backend.config[section]:
                settings.append(setting)
            yield {'sectionName': section, 'settings': settings}

class ConfigSection(root.KniveJsonApiResource):
    """All the Settings within a section"""

    settingCache = {}
    config = None
    path = None

    def setup(self, config, path):
        self.config = config
        self.path = path

    def _GET(self, request):
        jsondata = {'sectionName': self.path}
        settings = []
        for setting in self.config[self.path]:
            settings.append({'key': setting, 'value': self.config[self.path][setting]})
        jsondata['settings'] = settings
        return jsondata

    def getChild(self, setting, request):
        if setting in self.settingCache:
            return self.settingCache[setting]
        elif setting in self.backend:
            self.settingCache[setting] = Setting(self.backend, setting)
            return self.settingCache[setting]
        else:
            return error.NoResource()

class Setting(root.KniveJsonApiResource):
    """A single setting"""

    section = None
    name = None

    def setup(self,section, name):
        self.section = section
        self.key = name
        self.value = section[name]

    def _GET(self, request):
        yield ({
            'key': self.key,
            'value': self.value,
        })

    def _PUT(self, request, data):
        self.backend = data['value']
        return self.render_GET(request)


        
