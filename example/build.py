#!/usr/bin/env python3

from markupdown import *

site = Site()
site = index(site)
site = nav(site)
site = render(site)

serve(site)