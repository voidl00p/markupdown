# markupdown

markupdown is a dead-simple static site generator toolkit. Most static site generators do too much; they're complicated. I wanted something dead simple to manage my blog. So I built markupdown.

markupdown is simply a collection of modules that transform files (markdown, JS, CSS, HTML, images, and Liquid templates). You write a `build.py` file that calls the modules you want and run it. That's it!

Here's what a `build.py` file looks like:

```python
#!/usr/bin/env python3
from markupdown import *

# Copy files to the site directory
cp("pages/**/*.md")
cp("css/*.css", "css")
cp("js/*.js", "js")
cp("img/*.[jpg|jpeg|png]", "img")
cp("*.ico")

# Generate title frontmatter from first H1
transform("pages/**/*.md", title)

# Generate index.md files with `children` frontmatter field
transform("pages/**/*.md", index)

# Generate nav field in site.yaml
transform("pages/**/*.md", nav)

# Render the markdown as HTML
transform("pages/**/*.md", render)
```

## How it works

markupdown does the following:

1. Creates a `Site` object and markupdown will create a `site` directory and copy over the CSS, JS, and template files.
2. Run various functions to create, modify, or delete staged files.

That's it. Stupid simple. Worse is better.

## Modules

markupdown has the following core modules:

- index: Generates index frontmatter for index.md files
- init: Initializes a new site
- nav: Updates site.yaml with navigation links
- render: Renders the markdown using [liquid](https://shopify.github.io/liquid/) templates.
- serve: Starts a local HTTP server to view the site

And the following add-on modules:

- backref: Generates backreference frontmatter
- changelog: Generates changelog frontmatter
- lint: Checks all markdown files for syntax, grammar, readability, and style.
- minify: Minifies CSS, JS, and HTML
- og: Generates Open Graph frontmatter
- twitter: Generates Twitter card frontmatter
- related: Generates related content frontmatter
- rss: Generates an RSS feed
- sitemap: Generates a sitemap.xml

## Installation

Install everything:

```bash
pip install markupdown[all]
```

Just the core:

```bash
pip install markupdown
```

Or some add-on modules:
```bash
pip install markupdown[minify,rss]
```

## Usage

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
