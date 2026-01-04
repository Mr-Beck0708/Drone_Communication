#!/bin/bash
# Deployment script for Raspberry Pi
# Usage: ./deploy_to_raspi.sh user@raspberry_pi_ip

set -e

if [ $# -eq 0 ]; then
    echo "Usage: ./deploy_to_raspi.sh user@raspberry_pi_ip"
    echo "Example: ./deploy_to_raspi.sh pi@192.168.1.50"
    exit 1
fi

TARGET=$1
PROJECT_NAME="Drone_Communication"
REMOTE_DIR="/home/$(echo $TARGET | cut -d'@' -f1)/${PROJECT_NAME}"

echo "========================================"
echo "Deploying to Raspberry Pi: $TARGET"
echo "========================================"

# Step 1: Create remote directory
echo ""
echo "[1/5] Creating remote directory..."
ssh $TARGET "mkdir -p ${REMOTE_DIR}"

# Step 2: Copy source files
echo "[2/5] Copying source files..."
rsync -avz --progress \
    --exclude='venv/' \
    --exclude='__pycache__/' \
    --exclude='.git/' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache/' \
    --exclude='*.log' \
    ./ $TARGET:${REMOTE_DIR}/

# Step 3: Copy setup script
echo "[3/5] Running setup script on Pi..."
ssh $TARGET "cd ${REMOTE_DIR} && chmod +x setup_raspi.sh"

# Step 4: Ask user if they want to run setup
echo ""
echo "[4/5] Setup script copied to Pi"
read -p "Do you want to run setup_raspi.sh now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running setup..."
    ssh -t $TARGET "cd ${REMOTE_DIR} && ./setup_raspi.sh"
fi

# Step 5: Test connection
echo ""
echo "[5/5] Testing connection..."
ssh $TARGET "cd ${REMOTE_DIR} && python3 --version && echo 'Python OK'"

echo ""
echo "========================================"
echo "✓ Deployment complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. SSH to Pi: ssh $TARGET"
echo "2. Go to project: cd ${REMOTE_DIR}"
echo "3. Activate venv: source venv/bin/activate"
echo "4. Update config: Edit config/drone_config.json with your laptop IP"
echo "5. Run drone: python3 drone_app.py --host <LAPTOP_IP>"
echo ""
