"""
Tests for django_future.
"""

import unittest
import doctest

from django_future import job_as_parameter


def suite():
    return doctest.DocFileSuite('tests.txt')


def sample_job():
    print 'Simple job executed.'


def job_with_args(n, k=5):
    print 'Job with arguments: n = %d, k = %d' % (n, k)


def failjob():
    raise ValueError('fail')


@job_as_parameter
def job_job(job):
    print 'Got job as argument:', repr(job)
