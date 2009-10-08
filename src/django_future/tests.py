"""
Tests for django_future.
"""

import unittest
import doctest


def suite():
    return doctest.DocFileSuite('tests.txt')


def sample_job():
    print 'Simple job executed.'

def job_with_args(n, k=5):
    print 'Job with arguments: n = %d, k = %d' % (n, k)
