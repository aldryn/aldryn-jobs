# -*- coding: utf-8 -*-
import sys
import os

import django


cmd = 'coverage run `which djangocms-helper` aldryn_jobs test --cms --extra-settings=test_settings'

sys.exit(os.system(cmd))
