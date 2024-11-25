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
        """
        Initializes the DatasetSetup class with all necessary file paths.

        Sets up paths for:
        - Base directory: Root folder for all data
        - Cityscapes: Directory for city scene images
        - Gaze data: Directory for eye tracking data
        - Mapping file: CSV that maps between original and renamed images
        - Temporary storage: Directory for temporary downloaded files
        """
        self.script_dir = Path(__file__).parent
        self.base_dir = Path.cwd() / "eye_gaze_research"
        self.cityscapes_dir = self.base_dir / "cityscapes"
        self.gaze_data_dir = self.base_dir / "gaze_data"
        self.mapping_file = self.script_dir / "cityscapes_mapping.csv"
        self.temp_dir = self.base_dir / "temp"

    def setup_directories(self):
        """
        Creates all required directories for data storage and processing.

        Creates the following directory structure:
        eye_gaze_research/
        ├── cityscapes/     - stores cityscape images
        ├── gaze_data/      - stores eye tracking data
        └── temp/           - temporary download storage

        Notes:
            - Uses exist_ok=True to prevent errors if directories exist
            - Creates parent directories if they don't exist
        """
        logger.info("Setting up directories...")
        for directory in [self.base_dir, self.cityscapes_dir,
                          self.gaze_data_dir, self.temp_dir]:
            directory.mkdir(exist_ok=True)

    def verify_mapping_file(self):
        """
       Verifies existence and validity of the mapping CSV file.

       The mapping file maps between original Cityscapes image names
       and the renamed versions used in the gaze dataset.

       Returns:
           pandas.DataFrame: DataFrame containing the mapping information
               with columns 'cityscapeName' and 'imageName'

       Raises:
           SystemExit: If mapping file doesn't exist or can't be read
               - Code 1: File not found
               - Code 1: File read error (invalid CSV format)
       """
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
        """
       Downloads the eye tracking dataset from Hugging Face repository.

       Attempts multiple download methods in the following order:
       1. Using Hugging Face API
       2. Using Hugging Face Hub download
       3. Using direct HTTPS request

       The dataset contains eye gaze coordinates collected while users
       viewed Cityscapes images and identified hazards.

       Authentication:
           Requires a Hugging Face token from:
           https://huggingface.co/settings/tokens

       Notes:
           - Will try all download methods before failing
           - Copies mapping file to output directory for reference
           - Uses secure token input (not displayed while typing)

       Raises:
           SystemExit: If all download methods fail or other errors occur
               - Displays troubleshooting steps before exit
       """
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
        """
       Uses Hugging Face API to access the gaze dataset repository.

       This is the first attempted download method. Lists available files
       in the repository to verify access and authentication.

       Args:
           token (str): Hugging Face authentication token

       Returns:
           bool: True if repository access is successful

       Notes:
           - Private method used by download_gaze_dataset
           - Validates repository access and authentication
           - Repository: Lennyox/hazardous_driving_eye_gaze
       """
        api = HfApi()
        files = api.list_repo_files(
            repo_id="Lennyox/hazardous_driving_eye_gaze",
            repo_type="dataset",
            token=token
        )
        logger.info(f"Found files in repository: {files}")
        return True

    def _download_using_hub(self, token):
        """
       Downloads gaze dataset using Hugging Face's hub_download utility.

       This is the second attempted download method, used if API method fails.
       Directly downloads the gaze data CSV file from the repository.

       Args:
           token (str): Hugging Face authentication token

       Returns:
           bool: True if file download is successful

       Notes:
           - Private method used by download_gaze_dataset
           - Downloads specific file: hazardous_detection_gaze_data.csv
           - Saves to gaze_data_dir directory
           - Uses hub_download for reliable large file handling
       """
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
        """
       Downloads gaze dataset using direct HTTPS request.

       This is the final fallback download method, used if both API and hub methods fail.
       Downloads the data file directly using authenticated HTTPS request with
       streaming to handle large file size efficiently.

       Args:
           token (str): Hugging Face authentication token

       Returns:
           bool: True if download completes successfully

       Notes:
           - Private method used by download_gaze_dataset
           - Uses chunked downloading with progress bar
           - Handles large files efficiently with streaming
           - Chunk size: 8192 bytes for optimal performance

       Raises:
           requests.exceptions.RequestException: If download fails or authentication error occurs
       """
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
        """
           Displays steps to resolve common download issues.

           Shows a series of troubleshooting steps when dataset download fails,
           focusing on common issues like:
               - Token validation
               - Repository access
               - Terms acceptance
               - Web interface access

           Notes:
               - Private method called by download_gaze_dataset
               - Provides URLs for manual verification
               - Guides user through authentication process
               - Suggests web interface as fallback
        """
        """Print troubleshooting steps for download issues"""
        logger.info("\nTroubleshooting steps:")
        logger.info("1. Verify your token at https://huggingface.co/settings/tokens")
        logger.info("2. Check if you can access: https://huggingface.co/datasets/Lennyox/hazardous_driving_eye_gaze")
        logger.info("3. Make sure you have accepted any necessary terms of use")
        logger.info("4. Try accessing the dataset through the web interface first")

    def download_cityscapes(self, mapping_df):
        """
       Downloads and processes required images from Cityscapes dataset.

       Handles the complete process of:
           - Authentication with Cityscapes
           - Downloading the dataset ZIP
           - Extracting only needed images
           - Converting images to appropriate format
           - Cleaning up temporary files

       Args:
           mapping_df (pd.DataFrame): DataFrame containing mapping between
               Cityscapes image names and our renamed versions.
               Required columns: ['cityscapeName', 'imageName']

       Notes:
           - Requires valid Cityscapes account credentials
           - Downloads large ZIP file (11GB+)
           - Uses streaming download with progress bar
           - Only extracts images listed in mapping file
           - Converts PNG to JPG format
           - Cleans up temporary files after processing

       Raises:
           SystemExit: If login fails, download fails, or processing error occurs
               - Code 1: Authentication failure
               - Code 1: Download or processing error
       """
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
        """
       Converts Cityscapes PNG images to JPG format and renames them.

       Processes images by:
           - Creating lookup dictionary for efficient name mapping
           - Finding all PNG files in Cityscapes directory
           - Converting each PNG to JPG format with high quality
           - Renaming according to mapping file
           - Removing original PNG files
           - Cleaning up empty directories

       Args:
           mapping_df (pd.DataFrame): DataFrame containing image name mappings
               Required columns:
               - cityscapeName: original Cityscapes image names
               - imageName: new names for gaze dataset

       Notes:
           - Private method used by download_cityscapes
           - Uses high quality (95) JPEG compression
           - Converts from PNG to prevent format issues
           - Removes original files to save space
           - Shows progress bar during conversion
           - Maintains RGB color space

       Technical Details:
           - Input: PNG files with '_leftImg8bit.png' suffix
           - Output: JPEG files with names from mapping
           - Quality: 95/100 for minimal loss
           - Color Space: RGB conversion for consistency
       """
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
        """
       Verifies that all required files and directories are present.

       Checks for:
           - Existence of gaze data CSV file
           - Presence of converted JPG images
           - Proper directory structure

       This verification ensures that both the gaze dataset download
       and Cityscapes image processing completed successfully.

       Returns:
           bool: True if all required files exist and are accessible
                 False if any component is missing

       Notes:
           - Checks specific file: 'hazardous_detection_gaze_data.csv'
           - Looks recursively for JPG images
           - Logs detailed error messages for missing components
           - Used as final step in setup process
       """
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
        """
       Executes complete environment setup for eye gaze research.

       Performs setup in the following order:
           1. Verifies mapping file existence and validity
           2. Creates necessary directory structure
           3. Downloads eye tracking dataset from Hugging Face
           4. Downloads and processes Cityscapes images
           5. Verifies all components are properly set up
           6. Generates setup summary

       The setup process ensures all required data is downloaded,
       processed, and organized in the correct directory structure
       for eye gaze analysis.

       Returns:
           None

       Raises:
           SystemExit: If any part of setup fails
               - Code 1: Mapping file issues
               - Code 1: Download failures
               - Code 1: Verification failures

       Notes:
           - Requires internet connection
           - Needs valid authentication for both repositories
           - Creates all necessary directories
           - Provides detailed progress logging
           - Generates summary of completed setup
       """
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
    """
       Entry point for the eye gaze dataset setup script.

       Command line arguments:
           --no-cityscapes: Skip downloading Cityscapes dataset
               Useful when only gaze data is needed
               Default: False (downloads both datasets)

           --debug: Enable detailed debug logging
               Shows additional processing information
               Default: False (shows only info and errors)

       Setup Process:
           1. Parses command line arguments
           2. Configures logging level
           3. Initializes dataset setup
           4. Either:
              - Downloads only gaze data (with --no-cityscapes)
              - Performs complete setup (default)

       Usage Examples:
           Complete setup:
               python main.py

           Gaze data only:
               python main.py --no-cityscapes

           Debug mode:
               python main.py --debug

       Notes:
           - Requires internet connection
           - Needs authentication tokens/credentials
           - Creates directory structure automatically
           - Logs progress to console
    """
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
