import os
import sys
import shutil
from pathlib import Path
import pandas as pd
from huggingface_hub import hf_hub_download, HfApi
from tqdm import tqdm
import requests
from PIL import Image
from getpass import getpass
import zipfile
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatasetSetup:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.base_dir = Path.cwd() / "eye_gaze_research"
        self.cityscapes_dir = self.base_dir / "cityscapes"
        self.gaze_data_dir = self.base_dir / "gaze_data"
        self.mapping_file = self.script_dir / "cityscapes_mapping.csv"
        self.temp_dir = self.base_dir / "temp"

    def setup_directories(self):
        """Create necessary directories"""
        logger.info("Setting up directories...")
        for directory in [self.base_dir, self.cityscapes_dir,
                          self.gaze_data_dir, self.temp_dir]:
            directory.mkdir(exist_ok=True)

    def verify_mapping_file(self):
        """Verify the mapping file exists and is valid"""
        if not self.mapping_file.exists():
            logger.error(f"Mapping file not found at {self.mapping_file}")
            sys.exit(1)
        try:
            mapping_df = pd.read_csv(self.mapping_file)
            logger.info(f"Found mapping file with {len(mapping_df)} entries")
            return mapping_df
        except Exception as e:
            logger.error(f"Error reading mapping file: {str(e)}")
            sys.exit(1)

    def download_gaze_dataset(self):
        """Download gaze dataset from Hugging Face"""
        logger.info("\nDownloading gaze dataset from Hugging Face...")
        try:
            logger.info("Please enter your Hugging Face token")
            token = getpass("Token (from https://huggingface.co/settings/tokens): ")

            # Try multiple download methods
            download_methods = [
                self._download_using_api,
                self._download_using_hub,
                self._download_using_https
            ]

            success = False
            for method in download_methods:
                try:
                    success = method(token)
                    if success:
                        break
                except Exception as e:
                    logger.warning(f"Method failed: {str(e)}")
                    continue

            if not success:
                raise Exception("All download methods failed")

            # Copy mapping file
            shutil.copy2(self.mapping_file, self.gaze_data_dir / "mapping.csv")

        except Exception as e:
            logger.error(f"Error downloading gaze dataset: {str(e)}")
            self._print_troubleshooting_steps()
            sys.exit(1)

    def _download_using_api(self, token):
        """Download using HuggingFace API"""
        api = HfApi()
        files = api.list_repo_files(
            repo_id="Lennyox/hazardous_driving_eye_gaze",
            repo_type="dataset",
            token=token
        )
        logger.info(f"Found files in repository: {files}")
        return True

    def _download_using_hub(self, token):
        """Download using hf_hub_download"""
        local_path = hf_hub_download(
            repo_id="Lennyox/hazardous_driving_eye_gaze",
            filename="hazardous_detection_gaze_data.csv",
            repo_type="dataset",
            token=token,
            local_dir=self.gaze_data_dir
        )
        logger.info(f"Downloaded gaze data to: {local_path}")
        return True

    def _download_using_https(self, token):
        """Download using direct HTTPS request"""
        url = "https://huggingface.co/datasets/Lennyox/hazardous_driving_eye_gaze/raw/main/hazardous_detection_gaze_data.csv"
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            stream=True
        )
        response.raise_for_status()

        local_path = self.gaze_data_dir / "hazardous_detection_gaze_data.csv"
        total_size = int(response.headers.get('content-length', 0))

        with open(local_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

        logger.info(f"Downloaded gaze data using HTTPS to: {local_path}")
        return True

    def _print_troubleshooting_steps(self):
        """Print troubleshooting steps for download issues"""
        logger.info("\nTroubleshooting steps:")
        logger.info("1. Verify your token at https://huggingface.co/settings/tokens")
        logger.info("2. Check if you can access: https://huggingface.co/datasets/Lennyox/hazardous_driving_eye_gaze")
        logger.info("3. Make sure you have accepted any necessary terms of use")
        logger.info("4. Try accessing the dataset through the web interface first")

    def download_cityscapes(self, mapping_df):
        """Download and process Cityscapes dataset"""
        logger.info("\nDownloading Cityscapes dataset...")
        try:
            needed_images = set(mapping_df['cityscapeName'].unique())

            logger.info("Please enter your Cityscapes credentials")
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
                logger.error("Cityscapes login failed!")
                sys.exit(1)

            # Download dataset
            download_url = 'https://www.cityscapes-dataset.com/file-handling/?packageID=3'
            logger.info("\nDownloading Cityscapes dataset (this may take a while)...")

            response = session.get(download_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))

            zip_path = self.temp_dir / "cityscapes.zip"
            with open(zip_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True,
                          desc="Downloading Cityscapes") as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            # Extract only needed files
            logger.info("\nExtracting and processing images...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file in tqdm(zip_ref.namelist(), desc="Extracting files"):
                    if any(needed_image in file for needed_image in needed_images):
                        zip_ref.extract(file, self.cityscapes_dir)

            # Convert PNGs to JPGs and rename
            self._process_images(mapping_df)

            # Cleanup
            shutil.rmtree(self.temp_dir)
            logger.info("Cityscapes processing complete!")

        except Exception as e:
            logger.error(f"Error processing Cityscapes dataset: {str(e)}")
            sys.exit(1)

    def _process_images(self, mapping_df):
        """Convert and rename images according to mapping"""
        logger.info("Converting images to JPG format...")

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
                    logger.error(f"Error processing {png_path}: {str(e)}")

        # Remove empty directories
        for dirpath, dirnames, filenames in os.walk(self.cityscapes_dir, topdown=False):
            if not dirnames and not filenames:
                Path(dirpath).rmdir()

    def verify_setup(self):
        """Verify the setup was successful"""
        success = True

        # Check gaze data
        gaze_file = self.gaze_data_dir / "hazardous_detection_gaze_data.csv"
        if not gaze_file.exists():
            logger.error("Gaze data file is missing!")
            success = False

        # Check for converted images
        jpg_files = list(self.cityscapes_dir.rglob("*.jpg"))
        if not jpg_files:
            logger.error("No converted JPG images found!")
            success = False

        if success:
            logger.info("\nSetup verification successful!")
        else:
            logger.error("\nSetup verification failed!")

        return success

    def setup(self):
        """Run complete setup process"""
        logger.info("Starting environment setup...")

        # Verify mapping file first
        mapping_df = self.verify_mapping_file()

        self.setup_directories()
        self.download_gaze_dataset()
        self.download_cityscapes(mapping_df)

        # Verify setup
        if self.verify_setup():
            logger.info("\nSetup complete! Environment ready for eye gaze research.")
            logger.info(f"Data location: {self.base_dir}")

            # Print summary
            logger.info("\nSetup Summary:")
            logger.info("-" * 50)
            logger.info(f"Gaze data directory: {self.gaze_data_dir}")
            logger.info(f"Cityscapes directory: {self.cityscapes_dir}")
            logger.info(f"Total images processed: {len(mapping_df)}")
        else:
            logger.error("\nSetup incomplete. Please check the errors above.")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Setup eye gaze research environment")
    parser.add_argument('--no-cityscapes', action='store_true',
                        help="Skip Cityscapes download")
    parser.add_argument('--debug', action='store_true',
                        help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    setup = DatasetSetup()

    if args.no_cityscapes:
        setup.setup_directories()
        setup.download_gaze_dataset()
    else:
        setup.setup()


if __name__ == "__main__":
    main()