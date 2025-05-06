import os
import requests
from pathlib import Path

def download_image():
    # Create the directory if it doesn't exist
    image_dir = Path('static/products/images')
    image_dir.mkdir(parents=True, exist_ok=True)
    
    # URL of a cute puppies in basket image from a more reliable source
    image_url = "https://images-na.ssl-images-amazon.com/images/G/01/AmazonServices/Site/US/Product/FBA/Outlet/Merchandising/AMZN_OutletDeals_Template_March_2021_Hero_1500x300.jpg"
    
    # Path to save the image
    image_path = image_dir / 'puppies-basket.jpg'
    
    try:
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Save the image
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Image successfully downloaded to {image_path}")
    except Exception as e:
        print(f"Error downloading image: {e}")

if __name__ == "__main__":
    download_image() 