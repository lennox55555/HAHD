
import os
import sys
import shutil
from pathlib import Path
import requests
from PIL import Image
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download
from tqdm import tqdm
import yaml
import argparse
from getpass import getpass

class DatasetSetup:
    def __init__(self):
        self.hf_token = None
        self.base_dir = Path.cwd() / "eye_gaze_research"
        self.cityscapes_dir = self.base_dir / "cityscapes"
        self.gaze_data_dir = self.base_dir / "gaze_data"
        self.mapping_file = None
        
    def setup_directories(self):
        """Create necessary directories"""
        print("Setting up directories...")
        self.base_dir.mkdir(exist_ok=True)
        self.cityscapes_dir.mkdir(exist_ok=True)
        self.gaze_data_dir.mkdir(exist_ok=True)
        
    def login_to_huggingface(self):
        """Handle Hugging Face login"""
        print("\nPlease enter your Hugging Face credentials")
        username = input("Username: ")
        token = getpass("Token (from https://huggingface.co/settings/tokens): ")
        
        # Verify credentials
        api = HfApi()
        try:
            api.whoami(token)
            self.hf_token = token
            print("Successfully logged in to Hugging Face!")
        except Exception as e:
            print(f"Login failed: {str(e)}")
            sys.exit(1)
            
    def download_gaze_dataset(self):
        """Download gaze dataset from Hugging Face"""
        print("\nDownloading gaze dataset from Hugging Face...")
        try:
            # Download dataset files
            dataset_files = [
                "mapping.csv",
                "gaze_data.csv",
                "README.md"
            ]
            
            for file in dataset_files:
                hf_hub_download(
                    repo_id="Lennyox/hazardous_driving_eye_gaze",
                    filename=file,
                    token=self.hf_token,
                    local_dir=self.gaze_data_dir
                )
            
            self.mapping_file = self.gaze_data_dir / "mapping.csv"
            print("Gaze dataset downloaded successfully!")
            
        except Exception as e:
            print(f"Error downloading gaze dataset: {str(e)}")
            sys.exit(1)
            
    def download_cityscapes(self):
        """Download and process Cityscapes dataset"""
        print("\nDownloading Cityscapes dataset...")
        try:
            # Use mapping file to know which images to keep
            mapping_df = pd.read_csv(self.mapping_file)
            needed_images = set(mapping_df['cityscapeName'].unique())
            
            # Download leftImg8bit_trainvaltest.zip
            # Note: This requires Cityscapes account
            print("Please enter your Cityscapes credentials")
            cityscapes_username = input("Cityscapes Username: ")
            cityscapes_password = getpass("Cityscapes Password: ")
            
            url = 'https://www.cityscapes-dataset.com/file-handling/?packageID=3'
            response = requests.post(
                'https://www.cityscapes-dataset.com/login/',
                data={
                    'username': cityscapes_username,
                    'password': cityscapes_password
                }
            )
            
            if 'login' in response.url.lower():
                print("Cityscapes login failed!")
                sys.exit(1)
                
            print("Downloading Cityscapes dataset (this may take a while)...")
            with requests.get(url, stream=True, cookies=response.cookies) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                
                zip_path = self.cityscapes_dir / "cityscapes.zip"
                with open(zip_path, 'wb') as f:
                    with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                                
            # Extract only needed files
            print("\nExtracting and processing images...")
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if any(needed_image in file for needed_image in needed_images):
                        zip_ref.extract(file, self.cityscapes_dir)
            
            # Convert PNGs to JPGs and rename
            self._process_images(mapping_df)
            
            # Cleanup
            zip_path.unlink()
            print("Cityscapes processing complete!")
            
        except Exception as e:
            print(f"Error processing Cityscapes dataset: {str(e)}")
            sys.exit(1)
            
    def _process_images(self, mapping_df):
        """Convert and rename images according to mapping"""
        print("Converting images to JPG format...")
        for _, row in tqdm(mapping_df.iterrows(), total=len(mapping_df)):
            png_path = self.cityscapes_dir / row['cityscapeName']
            if png_path.exists():
                # Convert to JPG
                img = Image.open(png_path)
                jpg_path = self.cityscapes_dir / row['imageName']
                img.convert('RGB').save(jpg_path, 'JPEG', quality=95)
                # Remove original PNG
                png_path.unlink()
                
    def setup(self):
        """Run complete setup process"""
        self.setup_directories()
        self.login_to_huggingface()
        self.download_gaze_dataset()
        self.download_cityscapes()
        
        print("\nSetup complete! Environment ready for eye gaze research.")
        print(f"Data location: {self.base_dir}")

def main():
    parser = argparse.ArgumentParser(description="Setup eye gaze research environment")
    parser.add_argument('--no-cityscapes', action='store_true',
                      help="Skip Cityscapes download")
    args = parser.parse_args()
    
    setup = DatasetSetup()
    
    if args.no_cityscapes:
        setup.setup_directories()
        setup.login_to_huggingface()
        setup.download_gaze_dataset()
    else:
        setup.setup()

if __name__ == "__main__":
    main()
