<p align="center">
  <img src="logo.jpg" alt="BoumWave Logo" width="400">
</p>

# BoumWave

**The static blog generator that does exactly what it needs to. Nothing more.**

## Why BoumWave?

Static site generators were built in an older era. They've become overcomplicated with:
- Tag management
- Complex pagination
- Search functionality
- Modules and plugins everywhere
- 200-page documentation

**But what's really the purpose of a static site generator?**

1. You prepare your HTML template
2. You write your article in markdown
3. Boum, you generate it
4. Done

**That's exactly what BoumWave does.**

The goal: simplify the conversion from markdown to your template without having to copy-paste the template every time and manually update all the meta tags (Open Graph, Twitter Card, JSON-LD, canonical links...).

You initialize it, you design your template, you don't even need to read docs, and boom your blog is generated.

**No documentation needed.** The configuration file and templates contain detailed comments explaining what everything does. [Just read the files](https://github.com/CedricRaison/BoumWave/blob/master/src/boumwave/templates/default_config.toml).

If you want to add other features to your blog, like an about page or a contact page, that's not the job of a static site generator. You can add them easily yourself.

## Features

- **Simple**: 4 commands, that's it
- **Multilingual**: Native support for multiple languages
- **Your design**: Full HTML templates, do whatever you want
- **Automatic SEO**: Open Graph, Twitter Card, JSON-LD without thinking
- **Markdown**: Write in markdown, get HTML
- **Fast**: Generates your pages in a flash
- **Zero complex configuration**: One simple, clear TOML file

## Quick Start

```bash
# Install BoumWave
uv add boumwave

# Initialize your project
# this will create a boumwave.toml file
bw init

# Create the basic structure
bw scaffold

# Create your first post
bw new_post "My Awesome Post"

# Edit content/my_awesome_post/my_awesome_post.en.md

# Generate the HTML
bw generate my_awesome_post

# Done. Your post is in posts/en/my-awesome-post/
```

## Installation

### With uv (recommended)

```bash
uv add boumwave
```

## Usage

### 1. Initialize a project

```bash
bw init
```

Creates a `boumwave.toml` file with all the configuration.

### 2. Create the structure

```bash
bw scaffold
```

Creates the necessary folders and example templates:
- `templates/post.html`: The template for individual blog post pages
- `templates/link.html`: The template used to generate each post link in your index
- `index.html`: Your blog homepage with a list of all posts

**About index.html**: BoumWave generates a default `index.html` file, but you can bring your own. Just make sure it contains the markers `<!-- POSTS_START -->` and `<!-- POSTS_END -->` where you want the post list to appear. BoumWave will automatically insert your posts there, sorted by date.

You can customize all paths by editing the `boumwave.toml` file.

### 3. Create a post

```bash
bw new_post "Post Title"
```

Creates a folder with a markdown file for each configured language.

### 4. Generate HTML

```bash
bw generate post_name
```

Generates HTML with:
- Your template applied
- Open Graph meta tags
- Twitter Card
- JSON-LD for search engines
- Canonical link
- Automatic index.html update

## Configuration

One file: `boumwave.toml`

No hidden default values. Everything is explicit. You know exactly what's configured.


## Philosophy

**Do one thing, do it well.**

BoumWave doesn't handle:
- Comments (use Disqus, Giscus...)
- Search (add it yourself if you want)
- Analytics (Google Analytics, Plausible...)
- Deployment (use GitHub Pages, Netlify...)
- Tags and categories (Why use that in 2025 ?)

BoumWave handles:
- Markdown to HTML conversion
- Templates
- SEO meta tags
- Multilingual support
- Automatic index.html links

The rest is your site. Do what you want with it.

## Why the name?

**BoumWave** is a combination of my username **BoumTAC** and the word **"weave"**, which means to interlace or connect threads together. A static site generator weaves a link between a template and a text file, bringing them together into a final page.

**But here's the funny part:** when I started the project, I made a typo and wrote "wave" instead of "weave". It has a completely different meaning, but I kept it. The waves in the logo now make perfect sense, and it makes for a nice story.

Sometimes the best names come from happy accidents.

## License

MIT

## Contributing

Contributions are welcome! Open an issue or a PR.

## Author

Created for those who just want to write.
