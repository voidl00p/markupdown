#!/usr/bin/env python3

from markupdown import *

# Copy files to the site directory
cp("pages/**/*.md", strip_leading_dir=False)
cp("css/*.css")
cp("js/*.js")
cp("img/*.[jpg|jpeg|png]")
cp("*.ico")
