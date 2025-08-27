#!/usr/bin/env python3
"""
Static Blog Generator for yasserius.github.io
Converts markdown files to HTML using Jinja2 templates
"""

import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import markdown
from jinja2 import Environment, FileSystemLoader
import random

# Configuration - Edit these to customize your blog styling
CONFIG = {
    'site': {
        'title': 'Full Stack Developer',
        'description': 'Building the future, one line of code at a time.',
        'author': 'Your Name',
        'github': 'https://github.com/yasserius',
        'email': 'contact@example.com',
        'nav_max_width': '6xl'  # Tailwind max-width class
    },
    
    'skills': [
        'Python', 'FastAPI', 'React', 'TypeScript', 
        'PostgreSQL', 'Docker', 'AWS', 'Next.js'
    ],
    
    'css_variables': '''
        :root {
            --vscode-bg: #1e1e1e;
            --vscode-sidebar: #252526;
            --vscode-editor: #1e1e1e;
            --vscode-blue: #007acc;
            --vscode-light-blue: #4fc1ff;
            --vscode-green: #4ec9b0;
            --vscode-orange: #ce9178;
            --vscode-purple: #c586c0;
            --vscode-text: #d4d4d4;
            --vscode-text-muted: #969696;
        }
    ''',
    
    'styling': {
        'body': {
            'font_family': 'Inter',
            'background': 'var(--vscode-bg)',
            'color': 'var(--vscode-text)',
            'line_height': '1.6'
        },
        'h1': {
            'color': 'var(--vscode-light-blue)',
            'font_size': '2.5rem',
            'font_weight': '700',
            'margin': '2.5rem 0 1.5rem 0',
            'border_bottom': '3px solid #3c3c3c',
            'padding_bottom': '0.75rem'
        },
        'h2': {
            'color': 'var(--vscode-light-blue)',
            'font_size': '1.875rem',
            'font_weight': '600',
            'margin': '2rem 0 1rem 0',
            'border_bottom': '2px solid #3c3c3c',
            'padding_bottom': '0.5rem'
        },
        'h3': {
            'color': 'var(--vscode-green)',
            'font_size': '1.5rem',
            'font_weight': '600',
            'margin': '1.5rem 0 1rem 0'
        },
        'paragraph': {
            'margin': '1rem 0',
            'color': 'var(--vscode-text)'
        },
        'code_block': {
            'background': 'var(--vscode-editor)',
            'border': '1px solid #3c3c3c',
            'border_radius': '8px',
            'padding': '1rem',
            'margin': '1.5rem 0',
            'overflow_x': 'auto'
        },
        'inline_code': {
            'background': 'rgba(79, 193, 255, 0.1)',
            'color': 'var(--vscode-light-blue)',
            'padding': '0.25rem 0.5rem',
            'border_radius': '4px',
            'font_size': '0.875rem'
        },
        'table': {
            'width': '100%',
            'border_collapse': 'collapse',
            'margin': '1.5rem 0',
            'background': 'var(--vscode-sidebar)',
            'border_radius': '8px',
            'overflow': 'hidden'
        },
        'table_header': {
            'background': '#2d2d30',
            'color': 'var(--vscode-light-blue)',
            'font_weight': '600',
            'padding': '0.75rem 1rem',
            'text_align': 'left',
            'border_bottom': '1px solid #3c3c3c'
        },
        'table_cell': {
            'padding': '0.75rem 1rem',
            'text_align': 'left',
            'border_bottom': '1px solid #3c3c3c'
        },
        'link': {
            'color': 'var(--vscode-light-blue)',
            'text_decoration': 'none'
        },
        'image': {
            'max_width': '100%',
            'height': 'auto',
            'border_radius': '8px',
            'margin': '1rem 0'
        }
    },
    
    'tag_colors': [
        'blue', 'green', 'purple', 'yellow', 'red', 'orange', 
        'pink', 'cyan', 'indigo', 'teal'
    ],
    
    'post_colors': [
        'green', 'blue', 'orange', 'purple', 'red', 'yellow', 
        'pink', 'cyan', 'indigo', 'teal'
    ]
}

class BlogPost:
    """Represents a blog post with metadata and content"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.slug = file_path.stem
        self.filename = f"{self.slug}.py"  # Display filename
        self.content = ""
        self.title = ""
        self.description = ""
        self.date = ""
        self.tags = []
        self.color = random.choice(CONFIG['post_colors'])
        self._parse_file()
    
    def _parse_file(self):
        """Parse markdown file and extract frontmatter"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for YAML frontmatter
        if content.startswith('---'):
            try:
                _, frontmatter, markdown_content = content.split('---', 2)
                metadata = yaml.safe_load(frontmatter.strip())
                
                self.title = metadata.get('title', self._title_from_slug())
                self.description = metadata.get('description', self._generate_description(markdown_content))
                self.date = metadata.get('date', self._get_file_date())
                self.tags = self._process_tags(metadata.get('tags', []))
                self.content = self._markdown_to_html(markdown_content.strip())
                
            except ValueError:
                # No proper frontmatter, process as regular markdown
                self._process_without_frontmatter(content)
        else:
            self._process_without_frontmatter(content)
    
    def _process_without_frontmatter(self, content: str):
        """Process markdown without frontmatter"""
        self.title = self._title_from_slug()
        self.description = self._generate_description(content)
        self.date = self._get_file_date()
        self.tags = self._extract_tags_from_content(content)
        self.content = self._markdown_to_html(content)
    
    def _title_from_slug(self) -> str:
        """Generate title from filename slug"""
        return ' '.join(word.capitalize() for word in self.slug.split('-'))
    
    def _generate_description(self, content: str) -> str:
        """Generate description from content"""
        # Remove markdown syntax for description
        text = re.sub(r'[#*`\[\]()]', '', content)
        text = re.sub(r'\n+', ' ', text).strip()
        words = text.split()[:30]  # First 30 words
        return ' '.join(words) + ('...' if len(text.split()) > 30 else '')
    
    def _get_file_date(self) -> str:
        """Get file modification date"""
        timestamp = self.file_path.stat().st_mtime
        return datetime.fromtimestamp(timestamp).strftime('%b %Y')
    
    def _extract_tags_from_content(self, content: str) -> List[Dict]:
        """Extract programming languages and technologies from content as tags"""
        tech_keywords = {
            'python': 'blue', 'javascript': 'yellow', 'react': 'cyan',
            'fastapi': 'green', 'docker': 'blue', 'postgresql': 'blue',
            'sql': 'orange', 'html': 'red', 'css': 'blue', 'typescript': 'blue',
            'node': 'green', 'api': 'purple', 'database': 'orange',
            'web3': 'yellow', 'crypto': 'green', 'async': 'purple'
        }
        
        found_tags = []
        content_lower = content.lower()
        
        for keyword, color in tech_keywords.items():
            if keyword in content_lower:
                found_tags.append({
                    'name': keyword.title() if keyword != 'api' else 'API',
                    'color': color
                })
                if len(found_tags) >= 3:  # Limit to 3 tags
                    break
        
        return found_tags
    
    def _process_tags(self, tags: List[str]) -> List[Dict]:
        """Process tags from frontmatter"""
        processed_tags = []
        for tag in tags[:3]:  # Limit to 3 tags
            processed_tags.append({
                'name': tag,
                'color': random.choice(CONFIG['tag_colors'])
            })
        return processed_tags
    
    def _markdown_to_html(self, content: str) -> str:
        """Convert markdown to HTML with extensions"""
        md = markdown.Markdown(
            extensions=[
                'codehilite',
                'tables', 
                'fenced_code',
                'toc'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': False  # Use highlight.js instead
                }
            }
        )
        return md.convert(content)

class BlogGenerator:
    """Main blog generator class"""
    
    def __init__(self):
        self.posts_dir = Path('posts_md')
        self.templates_dir = Path('templates')
        self.output_dir = Path('.')
        
        # Create directories if they don't exist
        self.templates_dir.mkdir(exist_ok=True)
        
        # Setup Jinja2 environment
        self.env = Environment(loader=FileSystemLoader('.'))
        
    def _generate_css(self) -> str:
        """Generate CSS from configuration"""
        styles = CONFIG['styling']
        
        css = '''
        body {
            font-family: '%(font_family)s', sans-serif;
            background: %(background)s;
            color: %(color)s;
            line-height: %(line_height)s;
        }
        
        .font-mono {
            font-family: 'JetBrains Mono', monospace;
        }
        
        .gradient-text {
            background: linear-gradient(135deg, var(--vscode-light-blue), var(--vscode-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .code-window {
            background: var(--vscode-editor);
            border: 1px solid #3c3c3c;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .code-header {
            background: var(--vscode-sidebar);
            padding: 12px 16px;
            border-bottom: 1px solid #3c3c3c;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .code-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        
        .blog-card {
            background: var(--vscode-sidebar);
            border: 1px solid #3c3c3c;
            transition: all 0.3s ease;
        }
        
        .blog-card:hover {
            border-color: var(--vscode-blue);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 122, 204, 0.15);
        }
        
        .skill-tag {
            background: rgba(79, 193, 255, 0.1);
            border: 1px solid rgba(79, 193, 255, 0.3);
            color: var(--vscode-light-blue);
        }
        
        .typing-animation {
            border-right: 2px solid var(--vscode-light-blue);
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%%, 50%% { border-color: var(--vscode-light-blue); }
            51%%, 100%% { border-color: transparent; }
        }
        
        .glow-effect {
            box-shadow: 0 0 20px rgba(79, 193, 255, 0.3);
        }
        
        .blog-content h1 {
            color: %(h1_color)s;
            font-size: %(h1_font_size)s;
            font-weight: %(h1_font_weight)s;
            margin: %(h1_margin)s;
            border-bottom: %(h1_border_bottom)s;
            padding-bottom: %(h1_padding_bottom)s;
        }
        
        .blog-content h2 {
            color: %(h2_color)s;
            font-size: %(h2_font_size)s;
            font-weight: %(h2_font_weight)s;
            margin: %(h2_margin)s;
            border-bottom: %(h2_border_bottom)s;
            padding-bottom: %(h2_padding_bottom)s;
        }
        
        .blog-content h3 {
            color: %(h3_color)s;
            font-size: %(h3_font_size)s;
            font-weight: %(h3_font_weight)s;
            margin: %(h3_margin)s;
        }
        
        .blog-content p {
            margin: %(paragraph_margin)s;
            color: %(paragraph_color)s;
        }
        
        .blog-content pre {
            background: %(code_block_background)s;
            border: %(code_block_border)s;
            border-radius: %(code_block_border_radius)s;
            padding: %(code_block_padding)s;
            margin: %(code_block_margin)s;
            overflow-x: %(code_block_overflow_x)s;
        }
        
        .blog-content code {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.875rem;
        }
        
        .blog-content p code {
            background: %(inline_code_background)s;
            color: %(inline_code_color)s;
            padding: %(inline_code_padding)s;
            border-radius: %(inline_code_border_radius)s;
            font-size: %(inline_code_font_size)s;
        }
        
        .blog-content table {
            width: %(table_width)s;
            border-collapse: %(table_border_collapse)s;
            margin: %(table_margin)s;
            background: %(table_background)s;
            border-radius: %(table_border_radius)s;
            overflow: %(table_overflow)s;
        }
        
        .blog-content th {
            background: %(table_header_background)s;
            color: %(table_header_color)s;
            font-weight: %(table_header_font_weight)s;
            padding: %(table_header_padding)s;
            text-align: %(table_header_text_align)s;
            border-bottom: %(table_header_border_bottom)s;
        }
        
        .blog-content td {
            padding: %(table_cell_padding)s;
            text-align: %(table_cell_text_align)s;
            border-bottom: %(table_cell_border_bottom)s;
        }
        
        .blog-content a {
            color: %(link_color)s;
            text-decoration: %(link_text_decoration)s;
        }
        
        .blog-content a:hover {
            text-decoration: underline;
        }
        
        .blog-content img {
            max-width: %(image_max_width)s;
            height: %(image_height)s;
            border-radius: %(image_border_radius)s;
            margin: %(image_margin)s;
        }
        
        .related-posts {
            background: var(--vscode-sidebar);
            border: 1px solid #3c3c3c;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 2rem 0;
        }
        
        .post-card {
            background: var(--vscode-editor);
            border: 1px solid #3c3c3c;
            border-radius: 8px;
            padding: 1rem;
            transition: all 0.3s ease;
        }
        
        .post-card:hover {
            border-color: var(--vscode-blue);
            transform: translateY(-2px);
        }
        ''' % {
            **styles['body'],
            'h1_color': styles['h1']['color'],
            'h1_font_size': styles['h1']['font_size'],
            'h1_font_weight': styles['h1']['font_weight'],
            'h1_margin': styles['h1']['margin'],
            'h1_border_bottom': styles['h1']['border_bottom'],
            'h1_padding_bottom': styles['h1']['padding_bottom'],
            'h2_color': styles['h2']['color'],
            'h2_font_size': styles['h2']['font_size'],
            'h2_font_weight': styles['h2']['font_weight'],
            'h2_margin': styles['h2']['margin'],
            'h2_border_bottom': styles['h2']['border_bottom'],
            'h2_padding_bottom': styles['h2']['padding_bottom'],
            'h3_color': styles['h3']['color'],
            'h3_font_size': styles['h3']['font_size'],
            'h3_font_weight': styles['h3']['font_weight'],
            'h3_margin': styles['h3']['margin'],
            'paragraph_margin': styles['paragraph']['margin'],
            'paragraph_color': styles['paragraph']['color'],
            'code_block_background': styles['code_block']['background'],
            'code_block_border': styles['code_block']['border'],
            'code_block_border_radius': styles['code_block']['border_radius'],
            'code_block_padding': styles['code_block']['padding'],
            'code_block_margin': styles['code_block']['margin'],
            'code_block_overflow_x': styles['code_block']['overflow_x'],
            'inline_code_background': styles['inline_code']['background'],
            'inline_code_color': styles['inline_code']['color'],
            'inline_code_padding': styles['inline_code']['padding'],
            'inline_code_border_radius': styles['inline_code']['border_radius'],
            'inline_code_font_size': styles['inline_code']['font_size'],
            'table_width': styles['table']['width'],
            'table_border_collapse': styles['table']['border_collapse'],
            'table_margin': styles['table']['margin'],
            'table_background': styles['table']['background'],
            'table_border_radius': styles['table']['border_radius'],
            'table_overflow': styles['table']['overflow'],
            'table_header_background': styles['table_header']['background'],
            'table_header_color': styles['table_header']['color'],
            'table_header_font_weight': styles['table_header']['font_weight'],
            'table_header_padding': styles['table_header']['padding'],
            'table_header_text_align': styles['table_header']['text_align'],
            'table_header_border_bottom': styles['table_header']['border_bottom'],
            'table_cell_padding': styles['table_cell']['padding'],
            'table_cell_text_align': styles['table_cell']['text_align'],
            'table_cell_border_bottom': styles['table_cell']['border_bottom'],
            'link_color': styles['link']['color'],
            'link_text_decoration': styles['link']['text_decoration'],
            'image_max_width': styles['image']['max_width'],
            'image_height': styles['image']['height'],
            'image_border_radius': styles['image']['border_radius'],
            'image_margin': styles['image']['margin']
        }
        
        return css
    
    def collect_posts(self) -> List[BlogPost]:
        """Collect and parse all blog posts"""
        posts = []
        
        if not self.posts_dir.exists():
            print(f"Creating {self.posts_dir} directory...")
            self.posts_dir.mkdir()
            return posts
        
        for md_file in self.posts_dir.glob('*.md'):
            try:
                post = BlogPost(md_file)
                posts.append(post)
                print(f"Processed: {post.title}")
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
        
        # Sort by date (newest first)
        posts.sort(key=lambda p: p.date, reverse=True)
        return posts
    
    def generate_index(self, posts: List[BlogPost]):
        """Generate the main index.html page"""
        template = self.env.get_template('templates/index_template.html')
        
        html = template.render(
            page_title=f"{CONFIG['site']['title']} - Portfolio",
            posts=posts,
            skills=CONFIG['skills'],
            nav_max_width=CONFIG['site']['nav_max_width'],
            css_variables=CONFIG['css_variables'],
            custom_css=self._generate_css(),
            is_post=False
        )
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("Generated: index.html")
    
    def generate_post_pages(self, posts: List[BlogPost]):
        """Generate individual blog post pages"""
        template = self.env.get_template('templates/post_template.html')
        
        for post in posts:
            # Get related posts (randomly select 4 other posts)
            other_posts = [p for p in posts if p.slug != post.slug]
            related_posts = random.sample(other_posts, min(4, len(other_posts)))
            
            html = template.render(
                page_title=f"{post.title} - {CONFIG['site']['title']}",
                post=post,
                related_posts=related_posts,
                nav_max_width=CONFIG['site']['nav_max_width'],
                css_variables=CONFIG['css_variables'],
                custom_css=self._generate_css(),
                is_post=True
            )
            
            output_file = f"{post.slug}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"Generated: {output_file}")
    
    def run(self):
        """Main execution method"""
        print("Starting blog generation...")
        
        # Create template files if they don't exist
        self._create_template_files()
        
        # Collect and process posts
        posts = self.collect_posts()
        
        if not posts:
            print("No posts found. Please add .md files to the posts_md/ directory.")
            return
        
        # Generate pages
        self.generate_index(posts)
        self.generate_post_pages(posts)
        
        print(f"\nBlog generation complete! Generated {len(posts)} posts.")
        print("Files created:")
        print("- index.html")
        for post in posts:
            print(f"- {post.slug}.html")
    
    def _create_template_files(self):
        """Create template files if they don't exist"""
        # This would normally be handled by separate template files
        # but for simplicity, we're referencing them from the current directory
        pass

def main():
    """Main entry point"""
    generator = BlogGenerator()
    generator.run()

if __name__ == "__main__":
    main()