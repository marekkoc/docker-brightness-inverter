# # Image Brightness Inverter - Commands Reference 

Complete guide for running the `Image Brightness Iverter`using standard `Docker Compose commands`.

## Prerequisites

Make sure you have Docker and Docker Compose installed on your system.

## 1. Prepare Environment

```bash
# Create directory structure
mkdir -p shared/input
mkdir -p shared/queue  
mkdir -p shared/output
mkdir -p shared/processed
mkdir -p logs

# Verify structure
ls -la shared/
```

## 2. Build System

```bash
# Build containers
docker compose build

# Build without cache (force rebuild)
docker compose build --no-cache

# Build specific service only
docker compose build image-monitor
docker compose build image-processor
```

## 3. Start System

```bash
# Start in detached mode (background)
docker compose up -d

# Start with logs in foreground
docker compose up

# Start specific service
docker compose up -d image-processor
```

## 4. Check System Status

```bash
# Check container status
docker compose ps

# Detailed container information
docker compose ps -a

# Check resource usage
docker stats

# Check system-wide Docker info
docker system df
```

## 5. View Logs

```bash
# All logs
docker compose logs

# Live logs (follow)
docker compose logs -f

# Logs from specific container
docker compose logs image-monitor
docker compose logs image-processor

# Last 50 lines of logs
docker compose logs --tail=50

# Logs with timestamps
docker compose logs -t

# Live logs from specific container
docker compose logs -f image-monitor
```

## 6. Access Container Internals

### Enter Container with Bash

```bash
# Enter monitor container
docker compose exec image-monitor bash

# Enter processor container  
docker compose exec image-processor bash

# Alternative method using container names
docker exec -it image-monitor bash
docker exec -it image-processor bash
```

### Execute Commands Inside Containers

```bash
# Check files in shared directory
docker compose exec image-monitor ls -la /app/shared/
docker compose exec image-processor ls -la /app/shared/

# Check Python processes
docker compose exec image-monitor ps aux
docker compose exec image-processor ps aux

# Check disk usage inside container
docker compose exec image-monitor df -h

# Check environment variables
docker compose exec image-monitor env

# Run Python commands
docker compose exec image-monitor python3 -c "import os; print(os.listdir('/app/shared'))"
```

### Useful Container Inspection Commands

```bash
# Check mounted volumes
docker compose exec image-monitor mount | grep shared

# Check container network
docker compose exec image-monitor ip addr

# Check container hostname
docker compose exec image-monitor hostname

# Check running processes
docker compose exec image-monitor top

# Check system information
docker compose exec image-monitor uname -a
```

## 7. Test System

### Create Test Image

```bash
# Copy existing image
cp /path/to/your/image.jpg shared/input/

# Create test image programmatically (requires Python with PIL)
python3 -c "
from PIL import Image, ImageDraw
import random
import datetime

# Create simple test image
img = Image.new('RGB', (200, 200), color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
draw = ImageDraw.Draw(img)
draw.rectangle([50, 50, 150, 150], fill=(255, 255, 255))
draw.text((75, 90), 'TEST', fill=(0, 0, 0))

# Save with timestamp
timestamp = datetime.datetime.now().strftime('%H%M%S')
img.save(f'shared/input/test_image_{timestamp}.jpg')
print(f'Test image created: test_image_{timestamp}.jpg')
"
```

### Monitor Test Results

```bash
# Watch directories for changes
watch -n 2 'ls -la shared/input/ shared/queue/ shared/output/ shared/processed/'

# Check file counts
echo "Input: $(ls shared/input 2>/dev/null | wc -l) files"
echo "Queue: $(ls shared/queue 2>/dev/null | wc -l) files"  
echo "Output: $(ls shared/output 2>/dev/null | wc -l) files"
echo "Processed: $(ls shared/processed 2>/dev/null | wc -l) files"
```

## 8. Check Results

```bash
# List files in all directories
ls -la shared/input/      # Should be empty (files moved)
ls -la shared/queue/      # Task files or empty
ls -la shared/output/     # Processed images (inverted_*)
ls -la shared/processed/  # Original files

# Check directory sizes
du -sh shared/*

# Check log files
ls -la logs/
cat logs/monitor.log
cat logs/processor.log
```

## 9. Debugging and Troubleshooting

### Check Container Health

```bash
# Inspect containers
docker compose exec image-monitor ps aux
docker compose exec image-processor ps aux

# Check if processes are running
docker compose exec image-monitor pgrep -f monitor.py
docker compose exec image-processor pgrep -f processor.py

# Check Python installation
docker compose exec image-monitor python3 --version
docker compose exec image-processor python3 --version

# Check installed packages
docker compose exec image-monitor pip list
docker compose exec image-processor pip list
```

### File System Debugging

```bash
# Check permissions
docker compose exec image-monitor ls -la /app/
docker compose exec image-monitor ls -la /app/shared/

# Check if directories are writable
docker compose exec image-monitor touch /app/shared/test_write
docker compose exec image-monitor rm /app/shared/test_write

# Check file system type
docker compose exec image-monitor df -T

# Find files by name
docker compose exec image-monitor find /app -name "*.jpg" 2>/dev/null
docker compose exec image-processor find /app -name "*.task" 2>/dev/null
```

### Network and Process Debugging

```bash
# Check container networking
docker compose exec image-monitor ping image-processor
docker compose exec image-processor ping image-monitor

# Check container resource usage
docker stats image-monitor image-processor

# Check container logs in real-time
docker compose logs -f --tail=0
```

## 10. System Control

### Restart System

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart image-monitor
docker compose restart image-processor

# Stop and start (full restart)
docker compose down
docker compose up -d
```

### Rebuild and Restart

```bash
# Rebuild and restart
docker compose up -d --build

# Force rebuild specific service
docker compose up -d --build image-monitor

# Rebuild from scratch
docker compose down
docker compose build --no-cache
docker compose up -d
```

## 11. Stop System

```bash
# Stop containers (graceful)
docker compose down

# Stop containers and remove volumes
docker compose down -v

# Stop containers and remove images
docker compose down --rmi all

# Force stop (if containers are unresponsive)
docker compose kill
docker compose down
```

## 12. Cleanup

```bash
# Remove stopped containers
docker compose down

# Remove all project containers, networks, images
docker compose down --rmi all --volumes --remove-orphans

# Clean system (careful - affects all Docker resources)
docker system prune

# Clean everything including volumes (DESTRUCTIVE)
docker system prune -a --volumes
```

## Complete Workflow Example

```bash
# 1. Prepare environment
mkdir -p shared/{input,queue,output,processed} logs

# 2. Build and start system
docker compose build
docker compose up -d

# 3. Check status
docker compose ps

# 4. Add test image
cp image.jpg shared/input/

# 5. Monitor logs in real-time
docker compose logs -f

# 6. Check results (in another terminal)
ls -la shared/output/

# 7. Enter containers for debugging (if needed)
docker compose exec image-monitor bash

# 8. Stop system when done
docker compose down
```

## Emergency Commands

```bash
# Force kill all containers
docker kill $(docker ps -q)

# Remove all containers
docker rm $(docker ps -a -q)

# Remove all images
docker rmi $(docker images -q)

# Nuclear option - remove everything
docker system prune -a --volumes --force
```

## Tips and Best Practices

1. **Always use `-d` flag** for production to run in background
2. **Monitor logs regularly** with `docker compose logs -f`
3. **Check container status** with `docker compose ps` before debugging
4. **Use `exec` instead of `run`** for entering running containers
5. **Clean up regularly** to save disk space
6. **Backup important data** before using cleanup commands
7. **Use `--tail` with logs** to avoid overwhelming output
8. **Test with small images first** to verify system works

## Common Issues and Solutions

| Issue | Command to Check | Solution |
|-------|------------------|----------|
| Container won't start | `docker compose logs` | Check build errors, fix Dockerfile |
| Files not processed | `docker compose exec image-monitor ls /app/shared/` | Check permissions, restart containers |
| No logs appearing | `docker compose logs -f` | Check if containers are running |
| Permission denied | `ls -la shared/` | Fix directory permissions with `chmod` |
| Out of space | `docker system df` | Clean up with `docker system prune` |