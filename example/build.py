#!/usr/bin/env python3

from markupdown import *

# Copy files to the site directory
cp("pages/**/*.md", relative_to="pages")
cp("css/*.css")
cp("js/*.js")
cp("images/*.[jpg|jpeg|png]")
cp("*.ico")

title("site/**/*.md")
