import requests
import os
from pathlib import Path

# URL of a reliable puppy image from Unsplash
image_url = "https://images.unsplash.com/photo-1548199973-03cce0bbc87b"

# Make sure the directory exists
images_dir = Path("static/images")
images_dir.mkdir(parents=True, exist_ok=True)

# Path to save the image
image_path = images_dir / "puppies-basket.jpg"

try:
    # Download the image
    response = requests.get(image_url)
    response.raise_for_status()
    
    # Save the image
    with open(image_path, 'wb') as f:
        f.write(response.content)
    
    print(f"Successfully downloaded image to {image_path}")
except Exception as e:
    print(f"Error downloading image: {e}") 