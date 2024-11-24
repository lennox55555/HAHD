import os
import sys
from pathlib import Path
import requests
from PIL import Image
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download
from tqdm import tqdm
import argparse
from getpass import getpass

class DatasetSetup:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.base_dir = Path.cwd() / "eye_gaze_research"
        self.cityscapes_dir = self.base_dir / "cityscapes"
        self.gaze_data_dir = self.base_dir / "gaze_data"
        self.mapping_file = self.script_dir / "cityscapes_mapping.csv"
        
    def setup_directories(self):
        """Create necessary directories"""
        print("Setting up directories...")
        self.base_dir.mkdir(exist_ok=True)
        self.cityscapes_dir.mkdir(exist_ok=True)
        self.gaze_data_dir.mkdir(exist_ok=True)
        
    def verify_mapping_file(self):
        """Verify the mapping file exists"""
        if not self.mapping_file.exists():
            print(f"Error: Mapping file not found at {self.mapping_file}")
            sys.exit(1)
        try:
            mapping_df = pd.read_csv(self.mapping_file)
            print(f"Found mapping file with {len(mapping_df)} entries")
            return mapping_df
        except Exception as e:
            print(f"Error reading mapping file: {str(e)}")
            sys.exit(1)
            
    def download_gaze_dataset(self):
        """Download gaze dataset from Hugging Face"""
        print("\nDownloading gaze dataset from Hugging Face...")
        try:
            print("Please enter your Hugging Face token")
            token = getpass("Token (from https://huggingface.co/settings/tokens): ")
            
            # Download the gaze data file
            print("\nDownloading hazardous_detection_gaze_data.csv...")
            gaze_file = hf_hub_download(
                repo_id="Lennyox/hazardous_driving_eye_gaze",
                filename="hazardous_detection_gaze_data.csv",
                token=token,
                local_dir=self.gaze_data_dir
            )
            
            # Download README if exists
            try:
                readme_file = hf_hub_download(
                    repo_id="Lennyox/hazardous_driving_eye_gaze",
                    filename="README.md",
                    token=token,
                    local_dir=self.gaze_data_dir
                )
            except Exception as e:
                print("Note: README.md not found or couldn't be downloaded")
            
            # Copy our local mapping file to the gaze data directory
            shutil.copy2(self.mapping_file, self.gaze_data_dir / "mapping.csv")
            
            print("Gaze dataset downloaded successfully!")
            
            # Verify the downloaded data
            try:
                gaze_df = pd.read_csv(gaze_file)
                print(f"Successfully loaded gaze data with {len(gaze_df)} records")
            except Exception as e:
                print(f"Warning: Could not verify gaze data: {str(e)}")
            
        except Exception as e:
            print(f"Error downloading gaze dataset: {str(e)}")
            sys.exit(1)
            
    def download_cityscapes(self, mapping_df):
        """Download and process Cityscapes dataset"""
        print("\nDownloading Cityscapes dataset...")
        try:
            needed_images = set(mapping_df['cityscapeName'].unique())
            
            print("Please enter your Cityscapes credentials")
            cityscapes_username = input("Cityscapes Username: ")
            cityscapes_password = getpass("Cityscapes Password: ")
            
            # Login to Cityscapes
            session = requests.Session()
            login_response = session.post(
                'https://www.cityscapes-dataset.com/login/',
                data={
                    'username': cityscapes_username,
                    'password': cityscapes_password,
                    'submit': 'Login'
                }
            )
            
            if 'login' in login_response.url.lower():
                print("Cityscapes login failed!")
                sys.exit(1)
            
            # Download dataset
            download_url = 'https://www.cityscapes-dataset.com/file-handling/?packageID=3'
            print("\nDownloading Cityscapes dataset (this may take a while)...")
            
            response = session.get(download_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            zip_path = self.cityscapes_dir / "cityscapes.zip"
            with open(zip_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, 
                         desc="Downloading Cityscapes") as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            # Extract only needed files
            print("\nExtracting and processing images...")
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file in tqdm(zip_ref.namelist(), desc="Extracting files"):
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
        
        # Create a lookup dictionary for faster processing
        rename_map = dict(zip(mapping_df['cityscapeName'], mapping_df['imageName']))
        
        # Find all PNG files recursively
        png_files = list(self.cityscapes_dir.rglob("*_leftImg8bit.png"))
        
        for png_path in tqdm(png_files, desc="Converting images"):
            if png_path.name in rename_map:
                try:
                    # Convert to JPG
                    with Image.open(png_path) as img:
                        jpg_path = self.cityscapes_dir / rename_map[png_path.name]
                        img.convert('RGB').save(jpg_path, 'JPEG', quality=95)
                    # Remove original PNG
                    png_path.unlink()
                except Exception as e:
                    print(f"Error processing {png_path}: {str(e)}")
                    
        # Remove empty directories
        for dirpath, dirnames, filenames in os.walk(self.cityscapes_dir, topdown=False):
            if not dirnames and not filenames:
                Path(dirpath).rmdir()
                
    def setup(self):
        """Run complete setup process"""
        print("Starting environment setup...")
        
        # Verify mapping file first
        mapping_df = self.verify_mapping_file()
        
        self.setup_directories()
        self.download_gaze_dataset()
        self.download_cityscapes(mapping_df)
        
        print("\nSetup complete! Environment ready for eye gaze research.")
        print(f"Data location: {self.base_dir}")
        
        # Print summary
        print("\nSetup Summary:")
        print("-" * 50)
        print(f"Gaze data directory: {self.gaze_data_dir}")
        print(f"Cityscapes directory: {self.cityscapes_dir}")
        print(f"Total images processed: {len(mapping_df)}")

def main():
    parser = argparse.ArgumentParser(description="Setup eye gaze research environment")
    parser.add_argument('--no-cityscapes', action='store_true',
                      help="Skip Cityscapes download")
    args = parser.parse_args()
    
    setup = DatasetSetup()
    
    if args.no_cityscapes:
        setup.setup_directories()
        setup.download_gaze_dataset()
    else:
        setup.setup()

if __name__ == "__main__":
    main()
