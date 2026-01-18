# Windows Installation Guide

This guide covers installation of the Drone Communication System on Windows 10/11.

## Prerequisites

### 1. Python 3.12+
Download and install from [python.org](https://www.python.org/downloads/)
- ✅ Check "Add Python to PATH" during installation

### 2. Git
Download from [git-scm.com](https://git-scm.com/download/win)

### 3. CMake (for liboqs compilation)
Download from [cmake.org](https://cmake.org/download/)
- Choose "Add CMake to system PATH" during installation

### 4. Visual Studio Build Tools (for liboqs compilation)
Download from [Visual Studio Downloads](https://visualstudio.microsoft.com/downloads/)
- Install "Desktop development with C++" workload
- OR install "Build Tools for Visual Studio" (lighter option)

## Installation Steps

### 1. Clone Repository
```powershell
git clone https://github.com/yourusername/Drone_Communication.git
cd Drone_Communication
```

### 2. Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> **Note**: If you get an execution policy error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 3. Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**What happens during installation:**
- The `liboqs-python` package will automatically download and compile `liboqs` 0.15.0
- This process may take 5-15 minutes on first install
- You'll see CMake build output - this is normal
- The compiled library will be installed to `C:\Users\<YourUsername>\_oqs`

### 4. Verify Installation
```powershell
python -c "import oqs; print(f'liboqs version: {oqs.oqs_version()}')"
```

Expected output: `liboqs version: 0.15.0` (or similar)

## Running the Control Station

### Option 1: Using PowerShell Script (Recommended)
```powershell
# Connect to default drone IP
.\run_control_station.ps1

# Or specify custom IP and port
.\run_control_station.ps1 -Host 192.168.1.100 -Port 8443
```

### Option 2: Direct Python Execution
```powershell
python control_station_app.py --host 192.168.29.123 --port 8443
```

## Troubleshooting

### Issue: liboqs installation fails

**Symptom**: Error like "fatal: Remote branch X.X.X not found"

**Solution**:
1. Make sure you have the latest `requirements.txt`:
   ```powershell
   git pull origin main
   pip install --upgrade pip
   pip install --upgrade -r requirements.txt
   ```

2. If still failing, manually install liboqs:
   ```powershell
   # Clone liboqs
   git clone --depth 1 --branch 0.15.0 https://github.com/open-quantum-safe/liboqs.git C:\temp\liboqs
   cd C:\temp\liboqs
   
   # Build
   mkdir build
   cd build
   cmake -G "Visual Studio 17 2022" -DBUILD_SHARED_LIBS=ON -DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=TRUE ..
   cmake --build . --config Release
   cmake --install . --prefix C:\liboqs
   
   # Add to PATH (PowerShell, run as Administrator)
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\liboqs\bin", "Machine")
   ```

3. Then reinstall liboqs-python:
   ```powershell
   pip install --force-reinstall liboqs-python
   ```

### Issue: "Module not found" errors

**Solution**: Make sure virtual environment is activated:
```powershell
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` prefix in your prompt.

### Issue: Cannot connect to drone

**Checklist**:
- ✅ Drone (Raspberry Pi) is powered on and running `drone_app.py`
- ✅ Both devices are on the same network
- ✅ Firewall allows connections on port 8443
- ✅ Correct IP address (check with `ping 192.168.29.123`)

### Issue: Dummy crypto implementations being used

**Symptom**: Warning messages like "Using dummy Kyber/Dilithium implementation"

**Cause**: liboqs not properly installed

**Solution**: See "Issue: liboqs installation fails" above

## Testing Without liboqs

For quick testing without full cryptographic validation, the system automatically falls back to dummy implementations. This allows you to test:
- Network connectivity
- Data transmission
- UI functionality

However, **DO NOT use dummy mode for production or real security testing** - it provides no actual cryptographic protection.

## Network Configuration

### Finding Your Drone IP

On Raspberry Pi:
```bash
hostname -I
```

On Windows (to find your PC IP):
```powershell
ipconfig
# Look for "IPv4 Address" under your active network adapter
```

### Firewall Configuration

If connection fails, allow Python through Windows Firewall:
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Click "Change settings"
4. Find "Python" or add it via "Allow another app..."
5. Check both "Private" and "Public" boxes

## Next Steps

After installation:
1. Start the drone server on Raspberry Pi: `./run_drone.sh`
2. Run control station on Windows: `.\run_control_station.ps1`
3. Watch the secure key exchange and WiFi scan data streaming!

For deployment to Raspberry Pi, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).
