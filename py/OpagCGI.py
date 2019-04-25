# coding=utf-8
# Copyright (C) Ottawa Python Author's Group
# Example of use:
# cgi = OpagCGI('template.html')
# rdict = {'email': 'msoulier@storm.ca'}
# print cgi.parse(rdict)

# (kwillett, 031303) make template a required arg to OPagCGI constructor;
# make replacement delimiters {} instead of %%; allow change to template
# so object is reusable; added out convenience method to print result

import os
import re

# The replacement dictionary for parsing the template.
replacement_dict = {}


class Replacer:
    """
    This class is a utility class used to provide a bound method to the
    re.sub() function.
    """

    def __init__(self, dict_):
        """
        The constructor. It's only duty is to populate itself with the
        replacement dictionary passed.
        """
        self._dict = dict_

    def replace(self, matchobj):
        """
        The replacement method. This is passed a match object by re.sub(),
        which it uses to index the replacement dictionary and find the
        replacement string.
        """
        match = matchobj.group(1)
        matchobj = re.search('(.*)=(.*)', match)
        if matchobj:
            key = matchobj.group(1)
            qual = matchobj.group(2)
        else:
            key = match
            qual = ''
        if key in self._dict:
            if qual == 'checked' or qual == self._dict[key]:
                return 'checked'
            else:
                return self._dict[key]
        else:
            return ''


class OpagCGI:
    """
    This class represents a running instance of a CGI on the OPAG website.
    It provides methods to give output from a CGI to a user's browser while
    maintaining the site's look and feel. It does this via template parsing of
    a standard template, permitting parsing of other templates as well.
    """

    def __init__(self, template=''):
        """
        OpagCGI(template) -> OpagCGI object
        The class constructor, taking the path to the template to use
        """
        self._dict = None
        self._header = False
        self._template = template

    def __str__(self):
        try:
            ret = self.parse()
        except Exception as e:
            raise e
        else:
            return ret
        finally:
            self._dict = None
            self._header = False

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, template):
        self._template = template
        if not os.path.exists(self._template):
            raise OpagMissingPrecondition("%s does not exist" % self._template)

    def parse(self):
        """
        parse(dict_) -> string
        This method parses the open file object passed, replacing any keys
        found using the replacement dictionary passed.
        """
        if not isinstance(self._dict, dict):
            raise TypeError("Second argument must be a dictionary")
        if not self._template:
            raise OpagMissingPrecondition("template path is not set")
        # Open the file if its not already open. If it is, seek to the
        # beginning of the file.
        with open(self._template) as f:
            # Instantiate a new bound method to do the replacement.
            replacer = Replacer(self._dict).replace
            # Read in the entire template into memory. I guess we'd better keep
            # the templates a reasonable size if we're going to keep doing this.
            buffer_ = f.read()
            replaced = ""
            if self._header:
                replaced = "Content-Type: text/html\n\n"
            replaced = replaced + re.sub("{(.+)}", replacer, buffer_)
        return replaced

    def out(self, dict_, header=False):
        print self.parse(dict_, header)

    def with_(self, dict_=None, header=False):
        self._dict = dict_
        self._header = header
        return self


class OpagRuntimeError(RuntimeError):
    """
    The purpose of this class is to act as the base class for all runtime
    errors in OPAG CGI code. More specific Exceptions should subclass this if
    they happen at runtime. We might want to get more specific than this in
    the future, and introduce subclasses for IO errors, type errors and such,
    but this will do for now.
    """


class OpagMissingPrecondition(OpagRuntimeError):
    """
    The purpose of this class is to represent all problems with missing
    preconditions in OPAG code, such as a file that is supposed to exist, but
    does not.
    """
