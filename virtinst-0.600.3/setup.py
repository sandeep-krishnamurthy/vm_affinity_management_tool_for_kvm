#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free  Software Foundation; either version 2 of the License, or
# (at your option)  any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA.

import os
import sys
import glob

from distutils.core import setup, Command
from distutils.command.sdist import sdist
from distutils.command.build import build
from unittest import TextTestRunner, TestLoader

VERSION = "0.600.3"

# translation installing
def _build_po_list():
    ret = {}
    for filename in glob.glob(os.path.join(os.getcwd(), 'po', '*.po')):
        filename = os.path.basename(filename)
        lang = os.path.basename(filename)[0:len(filename) - 3]
        langdir = os.path.join("build", "mo", lang, "LC_MESSAGES")

        newname = os.path.join(langdir, "virtinst.mo")
        ret[lang] = (filename, newname)
    return ret

def _build_lang_data():
    ret = []
    for lang, (ignore, newname) in _build_po_list().items():
        targetpath = os.path.join("share", "locale", lang, "LC_MESSAGES")
        ret.append((targetpath, [newname]))
    return ret

# Config file building
config_files = ["virtinst/_config.py", "virtconv/_config.py"]
config_template = """
__version__ = "%(VERSION)s"
__version_info__ = tuple([ int(num) for num in __version__.split('.')])
rhel6defaults = bool(%(RHEL6DEFAULTS)s)
"""

class TestBaseCommand(Command):

    user_options = [('debug', 'd', 'Show debug output')]
    boolean_options = ['debug']

    def initialize_options(self):
        self.debug = 0
        self._testfiles = []
        self._dir = os.getcwd()

    def finalize_options(self):
        if self.debug and "DEBUG_TESTS" not in os.environ:
            os.environ["DEBUG_TESTS"] = "1"

    def run(self):
        try:
            # Use system 'coverage' if available
            import coverage
            use_coverage = True
        except:
            use_coverage = False

        tests = TestLoader().loadTestsFromNames(self._testfiles)
        t = TextTestRunner(verbosity=1)

        if use_coverage:
            coverage.erase()
            coverage.start()

        result = t.run(tests)

        if use_coverage:
            coverage.stop()

        sys.exit(int(bool(len(result.failures) > 0 or
                          len(result.errors) > 0)))

class TestCommand(TestBaseCommand):

    description = "Runs a quick unit test suite"
    user_options = TestBaseCommand.user_options + \
                   [("testfile=", None, "Specific test file to run (e.g "
                                        "validation, storage, ...)"),
                    ("skipcli", None, "Skip CLI tests")]

    def initialize_options(self):
        TestBaseCommand.initialize_options(self)
        self.testfile = None
        self.skipcli = None

    def finalize_options(self):
        TestBaseCommand.finalize_options(self)

    def run(self):
        '''
        Finds all the tests modules in tests/, and runs them.
        '''
        testfiles = []
        for t in glob.glob(os.path.join(self._dir, 'tests', '*.py')):
            if (t.endswith("__init__.py") or
                t.endswith("urltest.py")):
                continue

            base = os.path.basename(t)
            if self.testfile:
                check = os.path.basename(self.testfile)
                if base != check and base != (check + ".py"):
                    continue
            if self.skipcli and base.count("clitest"):
                continue

            testfiles.append('.'.join(['tests', os.path.splitext(base)[0]]))

        if not testfiles:
            raise RuntimeError("--testfile didn't catch anything")

        self._testfiles = testfiles
        TestBaseCommand.run(self)

class TestURLFetch(TestBaseCommand):

    description = "Test fetching kernels and isos from various distro trees"

    user_options = TestBaseCommand.user_options + \
                   [("match=", None, "Regular expression of dist names to "
                                     "match [default: '.*']"),
                    ("path=", None, "Paths to local iso or directory or check"
                                    " for installable distro. Comma separated")]

    def initialize_options(self):
        TestBaseCommand.initialize_options(self)
        self.match = None
        self.path = ""

    def finalize_options(self):
        TestBaseCommand.finalize_options(self)
        if self.match is None:
            self.match = ".*"

        origpath = str(self.path)
        if not origpath:
            self.path = []
        else:
            self.path = origpath.split(",")

    def run(self):
        import tests
        self._testfiles = ["tests.urltest"]
        tests.urltest.MATCH_FILTER = self.match
        if self.path:
            for p in self.path:
                tests.urltest.LOCAL_MEDIA.append(p)
        TestBaseCommand.run(self)

class CheckPylint(Command):
    user_options = []
    description = "Run static analysis script against codebase."

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def run(self):
        os.system("tests/pylint-virtinst.sh")

class myrpm(Command):

    user_options = []

    description = "Build a non-binary rpm."

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """
        Run sdist, then 'rpmbuild' the tar.gz
        """
        self.run_command('sdist')
        os.system('rpmbuild -ta dist/virtinst-%s.tar.gz' % VERSION)

class refresh_translations(Command):

    user_options = []

    description = "Regenerate POT file and merge with current translations."

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):

        # Generate POT file
        files = ["virtinst/*.py", "virtconv/*.py", "virtconv/parsers/*.py",
                  "virt-*"]
        pot_cmd = "xgettext --language=Python -o po/virtinst.pot"
        for f in files:
            pot_cmd += " %s " % f
        os.system(pot_cmd)

        # Merge new template with existing translations.
        for po in glob.glob(os.path.join(os.getcwd(), 'po', '*.po')):
            os.system("msgmerge -U po/%s po/virtinst.pot" %
                      os.path.basename(po))

class mysdist(sdist):
    """ custom sdist command, to prep virtinst.spec file for inclusion """

    def run(self):
        cmd = (""" sed -e "s/::VERSION::/%s/g" < python-virtinst.spec.in """ %
               VERSION) + " > python-virtinst.spec"
        os.system(cmd)

        # Update and generate man pages
        self._update_manpages()

        sdist.run(self)

    def _update_manpages(self):
        # Update virt-install.1 with latest os type/variant values
        import virtinst.osdict as osdict

        # Build list first
        ret = []
        for t in osdict.sort_helper(osdict.OS_TYPES):
            for v in osdict.sort_helper(osdict.OS_TYPES[t]["variants"]):
                label = osdict.OS_TYPES[t]["variants"][v]["label"]
                if osdict.lookup_osdict_key(None, None, t, v, "supported"):
                    ret.append((v, label))

        output = ""
        output += "=over 2\n\n"

        for v, label in ret:
            output += "=item %-20s : %s\n\n" % (v, label)

        output += "=back\n\n"

        infile = "man/en/virt-install.pod.in"
        outfile = "man/en/virt-install.pod"

        outfd = open(outfile, "w+")
        origout = outfd.read()
        outfd.close()

        infd  = open(infile, "r")
        inp = infd.read()
        infd.close()

        outp = inp.replace("::VARIANT VALUES::", output)
        if outp != origout or not(os.path.exists(outfile)):
            outfd = open(outfile, "w")
            outfd.write(outp)
            outfd.close()

        # Generate new manpages
        if os.system("make -C man/en"):
            raise RuntimeError("Couldn't generate man pages.")

        if os.system("grep -IRq 'Hey!' man/en") == 0:
            raise RuntimeError("man pages have errors in them! "
                               "(grep for 'Hey!')")


class mybuild(build):
    """ custom build command to compile i18n files"""

    user_options = (
        build.user_options + [
        ("rhel6defaults", None, "use rhel6 defaults in lib and tools"),
    ])

    def __init__(self, dist):
        build.__init__(self, dist)

        self.rhel6defaults = 0

    def run(self):
        config_opts = {
            "VERSION" : VERSION,
            "RHEL6DEFAULTS" : self.rhel6defaults,
        }

        config_data = config_template % config_opts
        print "Version              : %s" % VERSION
        print "RHEL6 defaults       : %s" % bool(self.rhel6defaults)

        for f in config_files:
            if os.path.exists(f):
                origconfig = file(f).read()
                if origconfig == config_data:
                    continue

            print "Generating %s" % f
            fd = open(f, "w")
            fd.write(config_data)
            fd.close()

        for filename, newname in _build_po_list().values():
            langdir = os.path.dirname(newname)
            if not os.path.exists(langdir):
                os.makedirs(langdir)

            print "Formatting %s to %s" % (filename, newname)
            os.system("msgfmt po/%s -o %s" % (filename, newname))

        build.run(self)

setup(
    name='virtinst',
    version=VERSION,
    description='Virtual machine installation',
    author='Jeremy Katz, Daniel Berrange, Cole Robinson',
    author_email='crobinso@redhat.com',
    license='GPL',
    url='http://virt-manager.org',
    package_dir={'virtinst': 'virtinst'},
    scripts=["virt-install", "virt-clone", "virt-image", "virt-convert"],
    packages=['virtinst', 'virtconv', 'virtconv.parsers'],

    data_files=[
        ('share/man/man1', [
            'man/en/virt-install.1',
            'man/en/virt-clone.1',
            'man/en/virt-image.1',
            'man/en/virt-convert.1']),
        ('share/man/man5', [
            'man/en/virt-image.5']),
    ] + _build_lang_data(),

    cmdclass={
        'test': TestCommand,
        'test_urls' : TestURLFetch,
        'pylint': CheckPylint,

        'rpm' : myrpm,
        'sdist': mysdist,
        'refresh_translations': refresh_translations,

        'build': mybuild,
    },
)
