import requests
import os
from pathlib import Path

# Make sure the directory exists
images_dir = Path("static/images/categories")
images_dir.mkdir(parents=True, exist_ok=True)

# Path to save the image
image_path = images_dir / "pet-food.jpg"

try:
    # Save the image directly from the user-provided URL
    image_url = "https://i.imgur.com/vLBuQzb.jpg"
    
    # Download the image
    response = requests.get(image_url)
    response.raise_for_status()
    
    # Save the image
    with open(image_path, 'wb') as f:
        f.write(response.content)
    
    print(f"Successfully downloaded image to {image_path}")
except Exception as e:
    print(f"Error downloading image: {e}") 