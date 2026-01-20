#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Define color replacements
replacements = {
    # Background colors
    'bg-brown-100': 'bg-green-500',
    'bg-brown-200': 'bg-green-500',
    'bg-brown-300': 'bg-green-500',
    'bg-brown-400': 'bg-green-500',
    'bg-brown-500': 'bg-green-600',
    'bg-brown-600': 'bg-green-600',
    'bg-brown-700': 'bg-green-700',
    'bg-brown-50': 'bg-cream-500',
    'bg-cream-100': 'bg-cream-500',
    'bg-cream-200': 'bg-cream-500',
    'bg-cream-50': 'bg-cream-500',
    
    # Error/warning backgrounds
    'bg-red-50': 'bg-salmon-50',
    'bg-red-100': 'bg-salmon-100',
    'bg-red-200': 'bg-salmon-200',
    'bg-red-500': 'bg-salmon-500',
    'bg-red-600': 'bg-salmon-500',
    'bg-yellow-50': 'bg-pink-50',
    'bg-yellow-100': 'bg-pink-100',
    'bg-yellow-500': 'bg-pink-500',
    'bg-yellow-600': 'bg-pink-500',
    'bg-amber-50': 'bg-pink-50',
    'bg-amber-200': 'bg-pink-200',
    
    # Border colors
    'border-brown-100': 'border-green-100',
    'border-brown-200': 'border-green-200',
    'border-brown-300': 'border-green-300',
    'border-brown-400': 'border-green-400',
    'border-brown-500': 'border-green-500',
    'border-brown-600': 'border-green-600',
    'border-cream-100': 'border-cream-500',
    'border-cream-200': 'border-cream-500',
    'border-red-200': 'border-salmon-200',
    'border-red-500': 'border-salmon-500',
    'border-yellow-200': 'border-pink-200',
    'border-yellow-300': 'border-pink-300',
    
    # Text colors
    'text-brown-300': 'text-green-300',
    'text-brown-400': 'text-cream-600',
    'text-brown-500': 'text-green-600',
    'text-brown-600': 'text-green-600',
    'text-brown-700': 'text-green-700',
    'text-brown-800': 'text-green-800',
    'text-brown-900': 'text-green-900',
    'text-cream-200': 'text-cream-500',
    'text-cream-100': 'text-cream-500',
    'text-cream-600': 'text-cream-600',
    'text-cream-700': 'text-cream-700',
    'text-red-500': 'text-salmon-500',
    'text-red-600': 'text-salmon-500',
    'text-red-700': 'text-salmon-500',
    'text-red-800': 'text-salmon-500',
    'text-yellow-600': 'text-pink-500',
    'text-yellow-700': 'text-pink-500',
    'text-yellow-800': 'text-pink-500',
    'text-amber-800': 'text-pink-500',
    'text-amber-700': 'text-pink-500',
    'text-amber-900': 'text-pink-500',
    
    # Hover states
    'hover:bg-brown-100': 'hover:bg-green-100',
    'hover:bg-brown-200': 'hover:bg-green-200',
    'hover:bg-brown-50': 'hover:bg-green-50',
    'hover:bg-cream-50': 'hover:bg-pink-500',
    'hover:bg-brown-300': 'hover:bg-green-300',
    'hover:bg-brown-600': 'hover:bg-green-600',
    'hover:bg-brown-700': 'hover:bg-green-700',
    'hover:text-brown-600': 'hover:text-green-600',
    'hover:text-brown-700': 'hover:text-green-700',
    'hover:text-brown-800': 'hover:text-green-800',
    
    # Focus states
    'focus:ring-brown-400': 'focus:ring-green-400',
    'focus:ring-brown-500': 'focus:ring-green-500',
    'focus:ring-brown-600': 'focus:ring-green-600',
    'focus:border-brown-300': 'focus:border-green-300',
    'focus:border-brown-400': 'focus:border-green-400',
    'focus:border-brown-500': 'focus:border-green-500',
    'focus:ring-yellow-500': 'focus:ring-pink-500',
    'focus:border-yellow-300': 'focus:border-pink-300',
}

def replace_colors(content):
    """Replace all old colors with new colors"""
    for old, new in replacements.items():
        content = content.replace(old, new)
    return content

def process_file(filepath):
    """Process a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        new_content = replace_colors(content)
        
        if new_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    templates_dir = Path('templates')
    html_files = list(templates_dir.rglob('*.html'))
    
    modified_count = 0
    modified_files = []
    
    for filepath in html_files:
        if process_file(filepath):
            modified_count += 1
            modified_files.append(str(filepath))
    
    print(f"\n{'='*60}")
    print(f"Modified {modified_count} out of {len(html_files)} HTML files")
    print(f"{'='*60}\n")
    
    if modified_files:
        print("Modified files:")
        for f in sorted(modified_files):
            print(f"  - {f}")

if __name__ == '__main__':
    main()
