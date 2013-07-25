#!/usr/bin/env python

import xnt

@xnt.target
def clean():
    xnt.rm('**.pyc',
           '**/**.pyc',
           '**/__pycache__')
