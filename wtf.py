#!/usr/bin/env python

import time

import settings
import sites
import tests

if settings.tests_to_run == "ALL":
    settings.tests_to_run = settings.tests.keys()

if __name__ == "__main__":
    for tr in settings.tests_to_run:
        print tr
        tConfig = settings.tests[tr]
        runner = tests.tests[tConfig['runner']]
        try:
            runner.test(tConfig)
        except:
            raise
