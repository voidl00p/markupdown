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
python -c"import markupdown; markupdown.init()"
```

This will create a scaffolding with default files and directories.

Let's build your site:

```bash
./build.py
```

You should see a `site` directory created in the current directory. The `site` directory will contain the generated files. Poke around in there.

You can serve the site by running:

```bash
python -c"import markupdown; markupdown.serve()"
```

If you have a directory structure like this:

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
│   ├── index.liquid
│   └── layout.liquid
└── build.py
```

Run `./build.py` will generate a `site` directory like this:

```text
.
├── css
│   └── style.css
├── img
│   └── image.png
└── site
    ├── index.html
    ├── index.md
    └── posts
        ├── index.html
        ├── index.md
        ├── post1.html
        ├── post1.md
        ├── post2.html
        └── post2.md
```

You can also call `serve(site)` at the end of `build.py` to start a local HTTP server.

Most of these methods take additional arguments. Go read the docs to see what you can do.
