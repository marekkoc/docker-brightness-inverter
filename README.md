# Simple Image Brightness Inversion System

A simple Docker/Docker Compose-based system for automatic 2D image brightness inversion for testing directory sharing. The system monitors a directory for new 2D images and performs color inversion on them. The System is a simplified modificaton of [Data transfer station for image AI in the hospital](https://github.com/HaukeBartsch/data-transfer-station/tree/main) platform. 

## Architecture

The system consists of 2 Docker containers:

1. **image-monitor** - monitors `shared/input` directory for new images
2. **image-processor** - processes images from queue and performs color inversion

## Directory Structure
The
```
simple-image-system/
├── shared/                    # Shared directory between containers
│   ├── input/                # Input directory - place images here
│   ├── queue/                # Processing queue
│   ├── output/               # Processed images (with inversion)
│   └── processed/            # Archive of original images
├── logs/                     # System logs
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile.monitor        # Monitor container
├── Dockerfile.processor      # Processor container
├── monitor.py               # Monitoring script
├── processor.py             # Processing script
└── README.md               # This documentation
```

## Quick Start

### 1. Clone or create project directory

```bash
mkdir simple-image-system
cd simple-image-system
```

### 2. Copy all files from artifacts

### 3. Run the system

```bash
# Prepare environment and run
mkdir -p shared/{input,queue,output,processed} logs
docker compose build
docker compose up -d
```

### 4. Test the system

```bash
# Add a test image
cp /path/to/your/image.jpg shared/input/

# Check logs
docker compose logs -f

# Check status
docker compose ps
```

## How to Use

1. **Drop an image** into `shared/input/` directory
2. **Monitor detects** the new file and moves it to queue
3. **Processor** performs color inversion
4. **Result** can be found in `shared/output/` as `inverted_[filename]`
5. **Original file** is moved to `shared/processed/`

## Supported Formats

- JPG/JPEG
- PNG
- BMP
- TIFF
- GIF

## Testing Directory Sharing

The system is designed to identify directory sharing issues between Docker containers:

### Check permissions:
```bash
ls -la shared/
ls -la shared/input/
```

### Check volume mounting:
```bash
docker compose exec image-monitor ls -la /app/shared/
docker compose exec image-processor ls -la /app/shared/
```

### Check problem logs:
```bash
# Container logs
docker compose logs image-monitor
docker compose logs image-processor

# Log files
cat logs/monitor.log
cat logs/processor.log
```

## Troubleshooting

### Problem: Files are not detected
- Check `shared/input/` directory permissions
- Check if containers have access to shared directory
- Check monitor logs

### Problem: Images are not processed
- Check if processor has access to `shared/queue/` directory
- Check image format (if supported)
- Check processor logs

### Problem: No access to directories
```bash
# Fix permissions
chmod -R 755 shared/
chmod -R 755 logs/

# Restart system
docker compose down
docker compose up -d
```

## Configuration

Environment variables in `docker-compose.yml`:

- `WATCH_DIR` - monitored directory (default: `/app/shared/input`)
- `QUEUE_DIR` - queue directory (default: `/app/shared/queue`)
- `OUTPUT_DIR` - output directory (default: `/app/shared/output`)
- `LOG_LEVEL` - logging level (INFO, DEBUG, ERROR)

## Basic Commands

```bash
# Build system
docker compose build

# Start system
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs
docker compose logs -f    # live logs

# Stop system
docker compose down

# Clean up containers and images
docker compose down --rmi all
```

---
# Shared folder issues:
1. 
2.

# Additional resources:
1. [DCMTK](https://dcmtk.org/en/) - DICOM Toolkit; collection of libraries and applications implementing large parts of the DICOM standard.
