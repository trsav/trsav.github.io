#!/bin/bash

# Run Python script
python posts/dead/script.py

# Render Quarto
quarto render

# Add all changes to git
git add -A

# Commit changes with message
git commit -m "updated rotting post"

git push 
