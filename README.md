# markupdown

markupdown is a dead-simple static site generator. Here's how it works:

1. Crawl a directory structure and copy all markdown files to a staging directory.
2. Run transformations on the staged markdown files and their frontmatter metadata.
3. Render the metadata and markdown content using [liquid](https://shopify.github.io/liquid/) templates.

That's it. Stupid simple.

## Modules

markupdown comes with the following add-on modules:

- backref: Generates backreference frontmatter
- changelog: Generates changelog frontmatter
- images: Processes images
- index: Generates index frontmatter for index.md files
- lint: Checks all markdown files for syntax, grammar, readability, and style.
- minify: Minifies CSS, JS, and HTML
- og: Generates Open Graph frontmatter
- twitter: Generates Twitter card frontmatter
- related: Generates related content frontmatter
- rss: Generates an RSS feed
- sitemap: Generates a sitemap.xml
- stage: Copies files matching a pattern from one directory structure to another

These modules are all optional and may be run in any order.

## Installation

Install the package using pip:

```bash
pip install markupdown
```

To install an add-on module, run:

```bash
pip install markupdown[module_name]
```

If you want all the modules, run:

```bash
pip install markupdown[all]
```

## Usage

From your project's root directory, run:

```bash
$ python -c"import markupdown; markupdown.init()"
```

This will bootstrap the project with a directory structure like this:

```
.
├── build
│   ├── site
│   └── staging
├── css
│   └── style.css
├── img
│   └── image.png
├── pages
│   ├── index.md
│   └── blog
│       ├── index.md
│       ├── post1.md
│       └── post2.md
├── templates
│   ├── index.liquid
│   ├── home.liquid
│   └── blog.liquid
└── build.py
```

`build.py` will contain the following code:

```python
import markupdown

# Stage the `pages` markdown files
markupdown.stage()

# Transform the frontmatter in the staged markdown files
markupdown.index()
markupdown.changelog()
markupdown.backref()
markupdown.related()

# Generate static site
markupdown.images()
markupdown.render()
markupdown.sitemap()
markupdown.rss()
markupdown.minify()
```

All of the module methods can take configuration parameters, but they ship with sane defaults that match the directory structure shown above.