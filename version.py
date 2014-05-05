# This file is placed into the public domain.

"""Calculate the current package version number based on git tags.

This module provides `read_version_git` to read the output of "git describe"
and modify its output modified to conform to the versioning scheme that
setuptools uses (see PEP 386).  Releases must be tagged with the following
format:

    v<num>(.<num>)+ [ {a|b|c|rc} <num> (.<num>)* ]

This module also provides `read_version_file` and `write_version_file` to
read and write the version number to a file. These functions should be used
to write the git version to a file so that it can be used in a release
distribution and can be read at runtime.

To use this module, import it in your setup.py file, define a
get_version() function, and use its result as your package version:

    import os
    import version

    here = os.path.abspath(os.path.dirname(__file__))

    def get_version(*file_paths):
        try:
            # read version from git tags
            ver = version.read_version_git()
        except:
            # read version from file
            ver = version.read_version_file(here, *file_paths)
        else:
            # write version to file if we got it successfully from git
            version.write_version_file(ver, here, *file_paths)
        return ver

    setup(
        name="<SAMPLE>"
        version=get_version('<SAMPLE>', '_version.py'),
        .
        .
        .
    )

This will automatically update the '<SAMPLE>/_version.py' file, where
'<SAMPLE>' is assumed to be the package directory. The '_version.py' file
should *not* be checked into git but it *should* be included in sdist
tarballs (this will be done automatically if written as a '.py' file in the
package directory as suggested). You should also include this module in your
manifest. To do these things, run:

    echo include version.py >> MANIFEST.in
    echo _version.py >> <SAMPLE>/.gitignore

You can also import the package version at runtime by including the line

    from ._version import __version__

in the __init__.py file of your package <SAMPLE>.


With that setup, a new release can be labelled by simply invoking:

    git tag -s v1.0

The original idea for this module is due to Douglas Creager, with PEP 386
modifications by Michal Nazarewicz. Here is a nice write-up of the original:

    http://dcreager.net/2010/02/10/setuptools-git-version-numbers/

"""

import codecs
import os
import re
import subprocess

# http://www.python.org/dev/peps/pep-0386/
_PEP386_SHORT_VERSION_RE = r'\d+(?:\.\d+)+(?:(?:[abc]|rc)\d+(?:\.\d+)*)?'
_PEP386_VERSION_RE = r'^%s(?:\.post\d+)?(?:\.dev\d+)?$' % (
    _PEP386_SHORT_VERSION_RE)
_GIT_DESCRIPTION_RE = r'^v(?P<ver>%s)-(?P<commits>\d+)-g(?P<sha>[\da-f]+)$' % (
    _PEP386_SHORT_VERSION_RE)

# read version number using 'git describe'
def read_version_git():
    # read version number using 'git describe'
    cmd = 'git describe --tags --long --match v[0-9]*.*'.split()
    try:
        git_description = subprocess.check_output(cmd).decode().strip()
    except subprocess.CalledProcessError:
        raise RuntimeError('Unable to get version number from git tags')

    desc_match = re.search(_GIT_DESCRIPTION_RE, git_description)
    if not desc_match:
        raise ValueError('Git description (%s) is not a valid PEP386 version' %
                            (git_description,))
    commits = int(desc_match.group('commits'))
    if not commits:
        version = desc_match.group('ver')
    else:
        version = '%s.post%d.dev%d' % (
                    desc_match.group('ver'),
                    commits,
                    int(desc_match.group('sha'), 16)
                    )

    return version

# write the version number to a source file
def write_version_file(version, *file_paths):
    # write version number to source file
    version_msg = '# Do not edit this file, versioning is governed by git tags'
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(os.path.join(*file_paths), 'w', 'latin1') as f:
        f.write(version_msg + os.linesep
                + "__version__ = '{0}'".format(version))

# Read the version number from a source file.
# Why read it, and not import?
# see https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion
def read_version_file(*file_paths):
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(os.path.join(*file_paths), 'r', 'latin1') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string in source file.")

if __name__ == '__main__':
    print read_version_git()
