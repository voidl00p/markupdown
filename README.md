# markupdown

markupdown is a dead-simple static site generator toolkit. Most static site generators do too much; they're complicated. I wanted something dumb to manage my blog.

markupdown is a collection of commands that help you set up and manage a static site. You write a `build.py` file that calls the commands you want and run it. That's it!

Here's what a `build.py` file looks like:

```python
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
```

## Modules

markupdown ships with the following commands:

- `cp`: Copies files to the site directory
- `index`: Generates `pages` frontmatter for index.md files
- `init`: Initializes a new site
- `ls`: Lists files in the site directory
- `nav`: Updates `site.yaml` with navigation links
- `render`: Renders the markdown using [liquid](https://shopify.github.io/liquid/) templates
- `serve`: Starts a local HTTP server to view the site
- `title`: Updates the `title` field in the markdown frontmatter

## Philosophy

markupdown does the following:

1. Creates a `Site` object and markupdown will create a `site` directory and copy over the CSS, JS, and template files.
2. Run various functions to create, modify, or delete staged files.

That's it. Stupid simple. Worse is better.

## Usage

Install it:

```bash
pip install markupdown
```

After you install markupdown, go to an empty directory and initialize it:

```bash
python -m markupdown init
```

This will create a scaffolding with files and directories like this:

```text
.
├── css
│   └── style.css
├── img
│   └── image.png
├── pages
│   ├── index.md
│   └── posts
│       ├── index.md
│       ├── post1.md
│       └── post2.md
├── templates
│   ├── _footer_.liquid
│   ├── _head_.liquid
│   ├── _header_.liquid
│   ├── _pages_.liquid
│   └── default.liquid
├── .gitignore
└── build.py
```

Run `./build.py` to generate your site. The output will be in the `site` directory.

Markupdown comes with a server you can start with:

```bash
python -m markupdown serve
```

Open [http://localhost:8000](http://localhost:8000). You should see a (rather ugly) stub site.
