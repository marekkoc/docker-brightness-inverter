#!/usr/bin/env python3
import os
import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Logging configuration
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - MONITOR - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImageHandler(FileSystemEventHandler):
    def __init__(self, watch_dir, queue_dir):
        self.watch_dir = Path(watch_dir)
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported image formats
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Check if it's a supported image format
        if file_path.suffix.lower() in self.supported_formats:
            logger.info(f"New image detected: {file_path.name}")
            self.process_image(file_path)
    
    def on_moved(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.dest_path)
        
        if file_path.suffix.lower() in self.supported_formats:
            logger.info(f"Moved image detected: {file_path.name}")
            self.process_image(file_path)
    
    def process_image(self, file_path):
        try:
            # Wait a moment for file copying to complete
            time.sleep(1)
            
            # Check if file still exists and is accessible
            if not file_path.exists():
                logger.warning(f"File {file_path.name} no longer exists")
                return
                
            # Move file to processing queue
            queue_file = self.queue_dir / file_path.name
            shutil.move(str(file_path), str(queue_file))
            
            logger.info(f"File {file_path.name} moved to processing queue")
            
            # Save task to file
            task_file = self.queue_dir / f"{file_path.stem}.task"
            with open(task_file, 'w') as f:
                f.write(f"image_file={queue_file.name}\n")
                f.write(f"timestamp={time.time()}\n")
                f.write(f"status=queued\n")
                
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")

def main():
    watch_dir = os.getenv('WATCH_DIR', '/app/shared/input')
    queue_dir = os.getenv('QUEUE_DIR', '/app/shared/queue')
    
    logger.info(f"Starting image monitor...")
    logger.info(f"Monitored directory: {watch_dir}")
    logger.info(f"Queue directory: {queue_dir}")
    
    # Create directories if they don't exist
    Path(watch_dir).mkdir(parents=True, exist_ok=True)
    Path(queue_dir).mkdir(parents=True, exist_ok=True)
    
    # Check existing files in directory
    existing_files = list(Path(watch_dir).glob('*'))
    if existing_files:
        logger.info(f"Found {len(existing_files)} existing files")
        handler = ImageHandler(watch_dir, queue_dir)
        for file_path in existing_files:
            if file_path.is_file() and file_path.suffix.lower() in handler.supported_formats:
                handler.process_image(file_path)
    
    # Configure watchdog
    event_handler = ImageHandler(watch_dir, queue_dir)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    
    try:
        observer.start()
        logger.info("Monitor started. Waiting for files...")
        
        while True:
            time.sleep(10)
            # Periodic status logging
            queue_files = list(Path(queue_dir).glob('*.task'))
            if queue_files:
                logger.debug(f"Files in queue: {len(queue_files)}")
                
    except KeyboardInterrupt:
        logger.info("Stopping monitor...")
        observer.stop()
    
    observer.join()
    logger.info("Monitor stopped")

if __name__ == "__main__":
    main()