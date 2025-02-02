#!/usr/bin/env python3

from markupdown import *

# Copy files to the site directory
cp("pages/**/*.md", relative_to="pages")
cp("css/*.css")
cp("js/*.js")
cp("images/*.[jpg|jpeg|png]")
cp("*.ico")

# Update markdown frontmatter
title("site/**/*.md")
index("site/**/*.md")
nav("site/**/*.md")

# Render pages
render("site/**/*.md", site={"title": "My Site"})