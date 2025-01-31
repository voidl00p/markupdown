#!/usr/bin/env python3

import markupdown

# Stage the `pages` markdown files
markupdown.stage()

# Transform the frontmatter in the staged markdown files
markupdown.site(
    title="Example Site",
)
markupdown.index()
markupdown.nav()

# Render the staged markdown files as HTML
markupdown.css()
markupdown.render()