#!/usr/bin/env python3

import markupdown

# Stage the `pages` markdown files
markupdown.stage()

# Transform the frontmatter in the staged markdown files
markupdown.index()

# Render the staged markdown files as HTML
markupdown.render()