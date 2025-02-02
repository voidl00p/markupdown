# Markupdown

Markupdown is a dead-simple static site generator toolkit. It comes with a collection of commands to help you manage a static site. You write a `build.py` file that calls the commands you want and run it. That's it!

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

## Commands

Markupdown ships with the following commands:

- `cp`: Copies files to the site directory
- `index`: Generates `pages` frontmatter for index.md files
- `init`: Initializes a new site
- `ls`: Lists files in the site directory
- `nav`: Updates `site.yaml` with navigation links
- `render`: Renders the markdown using [liquid](https://shopify.github.io/liquid/) templates
- `serve`: Starts a local HTTP server to view the site
- `title`: Updates the `title` field in the markdown frontmatter

I'll probably add more (`rss`, `sitemap`, `minify`, `social`, etc.). It's a work in progress.

## Philosophy

Markupdown is designed to be pretty dumb. It's just a collection of functions that help you do three things:

- Stage your `site` directory with markdown, css, js, images, and so forth (using `cp`)
- Transform the files in `site` to add metadata or create new files (using `title`, `index`, `nav`, etc.)
- Render the markdown using liquid templates (using `render`)

That's it. Stupid simple. Worse is better.

## Usage

Install it:

```bash
pip install markupdown
```

After you install Markupdown, go to an empty directory and initialize it:

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
