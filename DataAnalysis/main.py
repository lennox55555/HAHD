import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import random
from pathlib import Path
import scipy.ndimage as ndimage
from matplotlib.colors import LinearSegmentedColormap
from tqdm import tqdm
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GazeVisualizer:
    def __init__(self, base_dir):
        """
        Initialize visualizer using base directory from Data setup

        Args:
            base_dir: Base directory containing eye_gaze_research folder
        """
        # Use same directory structure as Data setup
        self.eye_gaze_dir = Path(base_dir) / "eye_gaze_research"
        self.gaze_data_path = self.eye_gaze_dir / "gaze_data" / "hazardous_detection_gaze_data.csv"
        self.image_dir = self.eye_gaze_dir / "cityscapes"

        # Verify data exists
        if not self.gaze_data_path.exists():
            raise FileNotFoundError(f"Gaze data not found at {self.gaze_data_path}. Please run Data setup first.")
        if not self.image_dir.exists():
            raise FileNotFoundError(f"Image directory not found at {self.image_dir}. Please run Data setup first.")

        logger.info("Loading gaze data...")
        self.gaze_df = pd.read_csv(self.gaze_data_path)

        # Get all gaze coordinate columns
        self.gaze_columns = [(f'gaze{i}X', f'gaze{i}Y', f'gaze{i}Time')
                             for i in range(1, 90)
                             if f'gaze{i}X' in self.gaze_df.columns]

        logger.info(f"Found {len(self.gaze_df)} gaze records")
        logger.info(f"Each record has up to {len(self.gaze_columns)} gaze points")

        # Create custom colormaps
        self.heatmap_cmap = LinearSegmentedColormap.from_list('custom', [(0, 0, 0, 0), (0, 1, 0, 0.7), (1, 1, 0, 0.7),(1, 0, 0, 0.7)])

        # Colors for different viewers
        self.viewer_colors = [
            (0.7, 0, 0.7, 0.5), 
            (0, 0, 1, 0.5),
            (0, 0.7, 0, 0.5),
            (1, 0.5, 0, 0.5),
            (0, 0.7, 0.7, 0.5),
            (0.7, 0, 0, 0.5),
            (0.5, 0.5, 0, 0.5),
            (0.5, 0, 0.5, 0.5),
            (0, 0.5, 0.5, 0.5),
            (0.7, 0.4, 0, 0.5),
        ]

    def get_valid_gazes(self, row):
        """Extract all valid gaze points from a row"""
        valid_gazes = []
        for x_col, y_col, t_col in self.gaze_columns:
            if pd.notna(row[x_col]) and pd.notna(row[y_col]):
                valid_gazes.append({
                    'x': float(row[x_col]),
                    'y': float(row[y_col]),
                    'time': float(row[t_col]) if pd.notna(row[t_col]) else None
                })
        return valid_gazes

    def select_random_images(self, n=3):
        """Select n random unique images that have gaze data"""
        # Group by test set and image to get count of samples
        image_counts = self.gaze_df.groupby(['testSet', 'questionImage']).size()

        # Select images with multiple samples
        valid_images = [(test_set, img) for (test_set, img), count in image_counts.items()
                        if count > 2]  # Ensure at least 3 samples

        if len(valid_images) < n:
            logger.warning(f"Only found {len(valid_images)} valid images")
            n = len(valid_images)

        selected = random.sample(valid_images, n)
        logger.info(f"Selected images: {selected}")
        return selected

    def get_image_path(self, test_set, image_name):
        """Get full path to an image"""
        return self.image_dir / image_name

    def create_aggregate_heatmap(self, test_set, image_name, sigma=30):
        """Create aggregate heatmap of all gazes for an image"""
        img_path = self.get_image_path(test_set, image_name)
        img = Image.open(img_path)
        width, height = img.size

        heatmap = np.zeros((height, width))

        # Get all gaze data for this image
        image_gazes = self.gaze_df[
            (self.gaze_df['testSet'] == test_set) &
            (self.gaze_df['questionImage'] == image_name)
            ]

        for _, row in image_gazes.iterrows():
            gazes = self.get_valid_gazes(row)
            for gaze in gazes:
                x = min(max(int(gaze['x']), 0), width - 1)
                y = min(max(int(gaze['y']), 0), height - 1)
                heatmap[y, x] += 1

        heatmap = ndimage.gaussian_filter(heatmap, sigma=sigma)
        if np.max(heatmap) > 0:
            heatmap = heatmap / np.max(heatmap)

        return img, heatmap

    def create_viewer_separated_heatmap(self, test_set, image_name, sigma=30):
        """Create heatmap with different colors for different viewers"""
        img_path = self.get_image_path(test_set, image_name)
        img = Image.open(img_path)
        width, height = img.size

        image_gazes = self.gaze_df[
            (self.gaze_df['testSet'] == test_set) &
            (self.gaze_df['questionImage'] == image_name)
            ]

        viewer_heatmaps = []

        for i, (_, viewer_data) in enumerate(image_gazes.groupby('timestamp')):
            heatmap = np.zeros((height, width))

            for _, row in viewer_data.iterrows():
                gazes = self.get_valid_gazes(row)
                for gaze in gazes:
                    x = min(max(int(gaze['x']), 0), width - 1)
                    y = min(max(int(gaze['y']), 0), height - 1)
                    heatmap[y, x] += 1

            heatmap = ndimage.gaussian_filter(heatmap, sigma=sigma)
            if np.max(heatmap) > 0:
                heatmap = heatmap / np.max(heatmap)

            color = self.viewer_colors[i % len(self.viewer_colors)]
            viewer_heatmaps.append((heatmap, color))

        return img, viewer_heatmaps

    def create_temporal_heatmap(self, test_set, image_name, viewer_index=0, sigma=30):
        """Create temporal heatmap showing gaze progression for one viewer"""
        img_path = self.get_image_path(test_set, image_name)
        img = Image.open(img_path)
        width, height = img.size

        image_gazes = self.gaze_df[
            (self.gaze_df['testSet'] == test_set) &
            (self.gaze_df['questionImage'] == image_name)
            ]

        viewer_groups = list(image_gazes.groupby('timestamp'))
        if not viewer_groups:
            return img, np.zeros((height, width, 3))

        if viewer_index >= len(viewer_groups):
            viewer_index = 0

        viewer_data = viewer_groups[viewer_index][1]
        heatmap = np.zeros((height, width, 3))

        # Collect all gaze points with times
        all_gazes = []
        for _, row in viewer_data.iterrows():
            gazes = self.get_valid_gazes(row)
            all_gazes.extend(gazes)

        if all_gazes:
            times = [gaze['time'] for gaze in all_gazes if gaze['time'] is not None]
            if times:  # Check if we have valid timestamps
                min_time = min(times)
                max_time = max(times)
                time_range = max_time - min_time

                for gaze in all_gazes:
                    if gaze['time'] is None:
                        continue

                    x = min(max(int(gaze['x']), 0), width - 1)
                    y = min(max(int(gaze['y']), 0), height - 1)

                    time_progress = (gaze['time'] - min_time) / time_range if time_range > 0 else 0

                    if time_progress < 0.5:
                        color = [1, time_progress * 2, 0]
                    else:
                        color = [2 - time_progress * 2, 1, 0]

                    heatmap[y, x] = color

                for i in range(3):
                    heatmap[:, :, i] = ndimage.gaussian_filter(heatmap[:, :, i], sigma=sigma)

                max_val = np.max(heatmap)
                if max_val > 0:
                    heatmap = heatmap / max_val

        return img, heatmap

    def visualize_all(self, output_dir):
        """Create all three types of visualizations for 3 random images"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        selected_images = self.select_random_images(3)

        for test_set, image_name in selected_images:
            logger.info(f"\nProcessing {test_set}/{image_name}")

            plt.figure(figsize=(20, 7))

            # 1. Aggregate heatmap
            plt.subplot(131)
            img, heatmap = self.create_aggregate_heatmap(test_set, image_name)
            plt.imshow(img)
            plt.imshow(heatmap, cmap=self.heatmap_cmap)
            plt.title(f"Aggregate Attention\n{test_set}/{image_name}", fontsize=14)
            plt.axis('off')

            # 2. Viewer-separated heatmap
            plt.subplot(132)
            img, viewer_heatmaps = self.create_viewer_separated_heatmap(test_set, image_name)
            plt.imshow(img)
            for heatmap, color in viewer_heatmaps:
                plt.imshow(heatmap, cmap=LinearSegmentedColormap.from_list('custom',
                                                                           [(0, 0, 0, 0), color]))
            plt.title(f"Viewer-Separated Attention\n({len(viewer_heatmaps)} viewers)", fontsize=14)
            plt.axis('off')

            # 3. Temporal heatmap
            plt.subplot(133)
            img, temporal_heatmap = self.create_temporal_heatmap(test_set, image_name)
            plt.imshow(img)
            plt.imshow(temporal_heatmap, alpha=0.6)
            plt.title("Temporal Attention\n(Single Viewer)", fontsize=14)
            plt.axis('off')

            plt.tight_layout()

            # Save high-resolution version
            output_path = output_dir / f"attention_{test_set}_{image_name}.png"
            plt.savefig(output_path, bbox_inches='tight', dpi=300)
            logger.info(f"Saved visualization to {output_path}")
            plt.show()
            plt.close()


def main():
    parser = argparse.ArgumentParser(description="Analyze and visualize gaze data")
    parser.add_argument("--base-dir", type=str, default=os.getcwd(),
                        help="Base directory containing eye_gaze_research folder")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Directory to save visualizations (default: eye_gaze_research/visualizations)")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Create visualizer
        visualizer = GazeVisualizer(args.base_dir)

        # Set up output directory
        if args.output_dir:
            output_dir = Path(args.output_dir)
        else:
            output_dir = visualizer.eye_gaze_dir / "visualizations"

        # Create visualizations
        visualizer.visualize_all(output_dir)

        logger.info(f"Visualizations saved to {output_dir}")

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        if args.debug:
            raise
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
