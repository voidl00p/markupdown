# markupdown

markupdown is a dead-simple static site generator toolkit.

## Installation

Install everything:

```bash
pip install markupdown[all]
```

Or just the core:

```bash
pip install markupdown
```

Or some add-on modules:
```bash
pip install markupdown[minify,rss]
```

## Usage

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

And the `build.py` file looks like this:

```python
from markupdown import *

site = Site()
# Generate index pages for the site
site = index(site)
# Generate navigation links
site = nav(site)
# Render the markdown as HTML
site = render(site)
```

Run `./build.py` will generate a `site` directory like this:

```text
.
├── css
│   └── style.css
├── img
│   └── image.png
├── site
│   ├── index.html
│   ├── index.md
│   └── posts
│       ├── index.html
│       ├── index.md
│       ├── post1.html
│       ├── post1.md
│       ├── post2.html
│       └── post2.md
```

Of course, most of these methods take additional arguments. Go read the docs to see what you can do.

## Modules

markupdown comes with the following core modules:

- index: Generates index frontmatter for index.md files
- nav: Updates site.yaml with navigation links
- render: Renders the markdown using [liquid](https://shopify.github.io/liquid/) templates.

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

## How it works

markupdown does the following:

1. Creates a `Site` object and markupdown will create a `site` directory and copy over the CSS, JS, and template files.
2. Run various functions to create, modify, or delete staged files.

That's it. Stupid simple. Worse is better.

## But why?

