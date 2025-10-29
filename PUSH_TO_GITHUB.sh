#!/bin/bash
# Quest Agent SDK - GitHub Push Script
# Run this after creating the repository on GitHub

set -e

echo "🚀 Quest Agent SDK - GitHub Push Script"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: README.md not found. Are you in the quest-agent-sdk directory?"
    exit 1
fi

echo "Current directory: $(pwd)"
echo "Git status:"
git status
echo ""

# Prompt for GitHub organization/username
read -p "Enter your GitHub username or organization (e.g., 'erichillerbrand'): " GITHUB_ORG

if [ -z "$GITHUB_ORG" ]; then
    echo "❌ Error: GitHub username/organization cannot be empty"
    exit 1
fi

REPO_URL="https://github.com/${GITHUB_ORG}/quest-agent-sdk.git"

echo ""
echo "Will push to: $REPO_URL"
echo ""
read -p "Have you created the repository on GitHub? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "⏸️  Please create the repository first:"
    echo "   1. Go to https://github.com/new"
    echo "   2. Repository name: quest-agent-sdk"
    echo "   3. Description: Production-ready SDK for integrating external agents with Quest Agent Forge"
    echo "   4. Public or Private (your choice)"
    echo "   5. DO NOT initialize with README, .gitignore, or license"
    echo "   6. Click 'Create repository'"
    echo ""
    echo "Then run this script again."
    exit 0
fi

echo ""
echo "🔄 Adding remote and pushing..."
echo ""

# Add remote (remove if exists)
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

# Push to GitHub
echo "Pushing to main branch..."
git push -u origin main

echo ""
echo "✅ Success! Your SDK is now on GitHub!"
echo ""
echo "📍 Repository URL: https://github.com/${GITHUB_ORG}/quest-agent-sdk"
echo ""
echo "Next steps:"
echo "  1. Visit https://github.com/${GITHUB_ORG}/quest-agent-sdk"
echo "  2. Add topics/tags (Settings → Topics)"
echo "  3. Enable GitHub Actions (should auto-enable)"
echo "  4. Share with external developers!"
echo ""
echo "🎉 Your SDK is ready for the world!"
