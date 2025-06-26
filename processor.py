#!/usr/bin/env python3
import os
import time
import logging
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
"""
# Logging configuration
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - PROCESSOR - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/processor.log'),
        logging.StreamHandler()
    ]
)
"""
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Tylko to zostaw
    ]
)

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self, queue_dir, output_dir, processed_dir):
        self.queue_dir = Path(queue_dir)
        self.output_dir = Path(output_dir)
        self.processed_dir = Path(processed_dir)
        
        # Create directories
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
    def invert_image(self, input_path, output_path):
        """Performs image color inversion"""
        try:
            logger.info(f"Processing image: {input_path.name}")
            
            # Open image
            with Image.open(input_path) as img:
                # Convert to RGB if needed
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Perform color inversion
                if img.mode == 'RGB':
                    # For color images
                    img_array = np.array(img)
                    inverted_array = 255 - img_array
                    inverted_img = Image.fromarray(inverted_array)
                else:
                    # For grayscale images
                    inverted_img = ImageOps.invert(img)
                
                # Save processed image
                inverted_img.save(output_path, quality=95)
                
                logger.info(f"Image processed and saved: {output_path.name}")
                return True
                
        except Exception as e:
            logger.error(f"Error processing image {input_path.name}: {e}")
            return False
    
    def process_queue(self):
        """Processes files from queue"""
        task_files = list(self.queue_dir.glob('*.task'))
        
        if not task_files:
            return
            
        logger.info(f"Found {len(task_files)} tasks to process")
        
        for task_file in task_files:
            try:
                # Load task information
                task_info = {}
                with open(task_file, 'r') as f:
                    for line in f:
                        key, value = line.strip().split('=', 1)
                        task_info[key] = value
                
                image_file = self.queue_dir / task_info['image_file']
                
                if not image_file.exists():
                    logger.warning(f"Image file does not exist: {image_file}")
                    task_file.unlink()  # Remove task
                    continue
                
                # Determine output path
                output_file = self.output_dir / f"inverted_{image_file.name}"
                
                # Process image
                success = self.invert_image(image_file, output_file)
                
                if success:
                    # Move original file to processed directory
                    processed_file = self.processed_dir / image_file.name
                    image_file.rename(processed_file)
                    
                    # Update task status
                    with open(task_file, 'a') as f:
                        f.write(f"processed_at={time.time()}\n")
                        f.write(f"status=completed\n")
                        f.write(f"output_file={output_file.name}\n")
                    
                    # Move task file to processed directory
                    processed_task = self.processed_dir / task_file.name
                    task_file.rename(processed_task)
                    
                    logger.info(f"Task completed successfully: {image_file.name}")
                else:
                    # Mark task as failed
                    with open(task_file, 'a') as f:
                        f.write(f"failed_at={time.time()}\n")
                        f.write(f"status=failed\n")
                    
            except Exception as e:
                logger.error(f"Error processing task {task_file.name}: {e}")

def main():
    queue_dir = os.getenv('QUEUE_DIR', '/app/shared/queue')
    output_dir = os.getenv('OUTPUT_DIR', '/app/shared/output')
    processed_dir = os.getenv('PROCESSED_DIR', '/app/shared/processed')
    
    logger.info(f"Starting image processor...")
    logger.info(f"Queue directory: {queue_dir}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Processed directory: {processed_dir}")
    
    processor = ImageProcessor(queue_dir, output_dir, processed_dir)
    
    try:
        logger.info("Processor started. Waiting for tasks...")
        
        while True:
            processor.process_queue()
            time.sleep(5)  # Check queue every 5 seconds
            
    except KeyboardInterrupt:
        logger.info("Stopping processor...")
    
    logger.info("Processor stopped")

if __name__ == "__main__":
    main()
