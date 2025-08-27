# Static Blog Generator for yasserius.github.io

A Python-powered static blog generator that converts Markdown files to beautiful HTML pages with a VSCode-inspired dark theme.

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Directory structure:**
```
yasserius.github.io/
├── posts_md/              # Your markdown blog posts
│   ├── hello-world.md
│   ├── python-tips.md
│   └── ...
├── images/                # Blog post images
├── templates/             # Template files
│   ├── base.html
│   ├── index_template.html
│   └── post_template.html
├── generate_blog.py       # Main generator script
├── requirements.txt
├── index.html            # Generated homepage
├── hello-world.html      # Generated blog posts
└── ...
```

## Usage

1. **Add your markdown files** to the `posts_md/` directory with dashed names:
   - `my-first-post.md`
   - `python-async-patterns.md`
   - `docker-best-practices.md`

2. **Run the generator:**
```bash
python generate_blog.py
```

3. **Push to GitHub:**
```bash
git add .
git commit -m "Update blog"
git push origin main
```

## Markdown Format

### With YAML frontmatter (recommended):
```markdown
---
title: "My Awesome Blog Post"
description: "A detailed guide on building amazing things"
date: "Dec 2024"
tags: ["Python", "FastAPI", "Docker"]
---

# My Awesome Blog Post

Your content here...
```

### Without frontmatter:
Just write regular markdown - the system will auto-generate metadata from the filename and content.

## Customization

Edit the `CONFIG` dictionary in `generate_blog.py` to customize:

- **Site info:** title, description, GitHub URL
- **Skills:** displayed on homepage
- **Colors:** CSS variables and theme colors
- **Typography:** font sizes, colors, spacing for all elements
- **Layout:** max widths, margins, padding

### Example CSS customization:
```python
CONFIG['styling']['h1'] = {
    'color': '#ff6b6b',           # Custom heading color
    'font_size': '3rem',          # Larger headings
    'margin': '3rem 0 2rem 0'     # More spacing
}
```

## Features

- ✅ **Markdown to HTML** conversion with syntax highlighting
- ✅ **YAML frontmatter** support
- ✅ **Auto-generated** titles, descriptions, and tags
- ✅ **Responsive design** with Tailwind CSS
- ✅ **VSCode dark theme** aesthetic
- ✅ **Code syntax highlighting** with Highlight.js
- ✅ **Related posts** section
- ✅ **SEO-friendly** URLs and meta tags
- ✅ **GitHub Pages** compatible

## File Types Supported

- **Code blocks:** ```python, ```javascript, etc.
- **Inline code:** `code snippets`
- **Images:** Local (`images/pic.jpg`) and external URLs
- **Links:** `[text](url)`
- **Tables:** Markdown table syntax
- **Custom HTML/CSS:** Mix HTML directly in markdown
- **YouTube embeds:** iframe embeds work perfectly

Happy blogging! 🚀