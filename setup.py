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

import os.path
from setuptools import setup, find_packages

# I owe Marius Gedminas for this snippet.
changes_file = os.path.join(os.path.dirname(__file__), 'NEWS')
changes = file(changes_file).read().split('\n\n\n')
latest_changes = '\n\n\n'.join(changes[:3])


setup(name='django-future',
    version='0.1.3',
    description='Scheduled jobs in Django',
    long_description=open('README').read() + '\n\n' + latest_changes,
    author='Shrubbery Software',
    author_email='team@shrubberysoft.com',
    url='http://github.com/shrubberysoft/django-future',
    packages=find_packages('src'),
    package_dir={'' : 'src'},
    package_data={'django_future': ['*.txt']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ]
)
