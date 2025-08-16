#!/bin/bash

# Script to copy media files to static folder for Railway deployment
# This is needed because Railway doesn't serve media files properly

echo "Copying media files to static folder for Railway deployment..."

# Create directories if they don't exist
mkdir -p clubs/static/clubs/members/profiles

# Copy profile pictures from media to static
if [ -d "media/members/profiles" ]; then
    cp media/members/profiles/*.jpg clubs/static/clubs/members/profiles/ 2>/dev/null || true
    cp media/members/profiles/*.png clubs/static/clubs/members/profiles/ 2>/dev/null || true
    echo "Profile pictures copied to static folder"
else
    echo "No media/members/profiles directory found"
fi

# Run collectstatic to update staticfiles
echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Media files copied to static successfully!"
echo "Remember to commit and deploy these changes to Railway."
