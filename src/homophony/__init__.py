# Copyright (c) 2009 Shrubbery Software
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import doctest
import unittest
from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler
import wsgi_intercept
import wsgi_intercept.mechanize_intercept
import zc.testbrowser.browser


__all__ = ['Browser', 'DocFileSuite', 'BrowserTestCase']


class Browser(zc.testbrowser.browser.Browser):
    """Extension of the Browser that interacts well with wsgi_intercept."""

    def __init__(self, *args, **kwargs):
        kwargs['mech_browser'] = wsgi_intercept.mechanize_intercept.Browser()
        browser = super(Browser, self).__init__(*args, **kwargs)


class BrowserTestCase(unittest.TestCase):
    """Base class for test cases that make use of the Browser."""

    def setUp(self):
        setUpBrowser()

    def tearDown(self):
        tearDownBrowser()


def DocFileSuite(*paths, **kwargs):
    """Extension of the standard DocFileSuite that sets up test browser for
    use in doctests."""
    print doctest._normalize_module(None)
    kwargs.setdefault('setUp', setUpBrowser)
    kwargs.setdefault('tearDown', tearDownBrowser)
    kwargs.setdefault('globs', {}).update(Browser=Browser)
    if 'package' not in kwargs:
        # Resolve relative names based on the caller's module
        kwargs['package'] = doctest._normalize_module(None)
        kwargs['module_relative'] = True
    return doctest.DocFileSuite(*paths, **kwargs)


def setUpBrowser(*args):
    settings.DEBUG = settings.TEMPLATE_DEBUG = True
    wsgi_intercept.urllib2_intercept.install_opener()
    wsgi_intercept.add_wsgi_intercept('testserver', 80, WSGIHandler)
    if 'django.contrib.sites' in settings.INSTALLED_APPS:
        from django.contrib.sites.models import Site
        Site.objects.get_current().domain = 'testserver'


def tearDownBrowser(*args):
    wsgi_intercept.remove_wsgi_intercept()
    wsgi_intercept.urllib2_intercept.uninstall_opener()