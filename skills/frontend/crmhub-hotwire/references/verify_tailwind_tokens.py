#!/usr/bin/env python3
"""
Verify Tailwind CSS custom tokens are compiled correctly.
Run after: bundle exec bin/rails tailwindcss:build

Usage:
    python3 references/verify_tailwind_tokens.py
    python3 references/verify_tailwind_tokens.py --fix  # apply arbitrary value replacements
"""
import sys
import os
import re
import argparse

PROJECT_ROOT = "/home/deeone/projects/crm_hub"
VIEWS_DIR = os.path.join(PROJECT_ROOT, "app/views")
CSS_SRC = os.path.join(PROJECT_ROOT, "app/assets/tailwind/application.css")
CSS_OUT = os.path.join(PROJECT_ROOT, "app/assets/builds/tailwind.css")

# Tokens that MUST be in compiled output
REQUIRED_TOKENS = [
    "page-title", "section-heading", "label-caps", "card-title",
    "accent-hover", "surface-container", "pure-surface", "on-surface-variant",
    "on-secondary-container", "on-tertiary-fixed-variant",
    "hover:bg-accent-hover", "hover:bg-primary-hover",
    "font-page-title", "font-card-title", "font-section-heading",
    "font-label-caps", "font-meta-mono", "font-body-relaxed",
    "active:translate-y-px", "active:scale-95",
]

# Arbitrary values that should NOT be in compiled output (scanner drops them)
FORBIDDEN_PATTERNS = [
    r'text-\[[0-9]+px\]',
    r'active:scale-\[0\.[0-9]+\]',
    r'active:translate-y-\[[0-9]+px\]',
]

ARBITRARY_REPLACEMENTS = [
    ('text-[9px]', 'text-xs'), ('text-[10px]', 'text-xs'), ('text-[11px]', 'text-xs'), ('text-[12px]', 'text-xs'),
    ('text-[13px]', 'text-sm'), ('text-[14px]', 'text-sm'), ('text-[15px]', 'text-sm'), ('text-[16px]', 'text-sm'),
    ('text-[18px]', 'text-lg'), ('text-[20px]', 'text-xl'), ('text-[24px]', 'text-2xl'), ('text-[28px]', 'text-2xl'),
    ('text-[32px]', 'text-3xl'),
    ('active:scale-[0.98]', 'active:scale-95'), ('active:scale-[0.97]', 'active:scale-97'),
    ('active:translate-y-[1px]', 'active:translate-y-px'),
]

def check_css_output():
    """Verify required tokens are in compiled CSS."""
    if not os.path.exists(CSS_OUT):
        print(f"ERROR: Compiled CSS not found: {CSS_OUT}")
        print("  Run: bundle exec bin/rails tailwindcss:build")
        return False
    
    with open(CSS_OUT) as f:
        css = f.read()
    
    missing = []
    found = []
    for token in REQUIRED_TOKENS:
        if token in css:
            found.append(token)
        else:
            missing.append(token)
    
    if missing:
        print(f"ERROR: {len(missing)} required tokens NOT in compiled CSS:")
        for t in missing:
            print(f"  - {t}")
        print(f"\nFix: Add missing tokens to @layer components in {CSS_SRC}")
        return False
    
    print(f"OK: All {len(found)} required tokens present in compiled CSS")
    print(f"  Compiled CSS size: {os.path.getsize(CSS_OUT) / 1024:.1f} KB")
    return True

def check_views_for_arbitraries():
    """Find arbitrary-value classes still in views."""
    violations = []
    for root, dirs, files in os.walk(VIEWS_DIR):
        for fname in files:
            if fname.endswith('.erb'):
                fpath = os.path.join(root, fname)
                with open(fpath) as f:
                    content = f.read()
                for pat in FORBIDDEN_PATTERNS:
                    matches = re.findall(pat, content)
                    if matches:
                        violations.append((fpath, pat, matches))
    return violations

def apply_fixes():
    """Replace all arbitrary-value classes in ERB files."""
    fixed_count = 0
    for root, dirs, files in os.walk(VIEWS_DIR):
        for fname in files:
            if not fname.endswith('.erb'):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath) as f:
                content = f.read()
            original = content
            for old, new in ARBITRARY_REPLACEMENTS:
                content = content.replace(old, new)
            if content != original:
                with open(fpath, 'w') as f:
                    f.write(content)
                print(f"  Fixed: {fpath}")
                fixed_count += 1
    print(f"\nFixed {fixed_count} files")
    print("  Now rebuild: bundle exec bin/rails tailwindcss:build")
    print("  Then restart server: kill $(cat tmp/pids/server.pid) && bundle exec rails server -b 0.0.0.0 -p 3000")

def main():
    parser = argparse.ArgumentParser(description="Verify Tailwind CSS token compilation")
    parser.add_argument('--fix', action='store_true', help='Apply arbitrary-value replacements to ERB files')
    args = parser.parse_args()
    
    if args.fix:
        print("Applying arbitrary-value replacements...")
        apply_fixes()
        return
    
    print("=== Checking compiled CSS for required tokens ===")
    css_ok = check_css_output()
    
    print("\n=== Checking views for arbitrary-value classes ===")
    violations = check_views_for_arbitraries()
    if violations:
        print(f"WARNING: Found {len(violations)} files with forbidden arbitrary values:")
        for fpath, pat, matches in violations:
            rel = fpath.replace(VIEWS_DIR + '/', '')
            print(f"  {rel}: {set(matches)} (pattern: {pat})")
        print("\n  Run with --fix to replace: python3 references/verify_tailwind_tokens.py --fix")
    else:
        print("OK: No arbitrary-value violations found in views")
    
    if not css_ok or violations:
        sys.exit(1)
    print("\nAll checks passed!")

if __name__ == '__main__':
    main()