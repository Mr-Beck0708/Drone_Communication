# Quick Start Guide - Windows Testing Mode

If you're having trouble installing `liboqs` on Windows and want to quickly test the drone communication system, you can use the **fallback dummy crypto implementations**.

## What are Dummy Implementations?

The crypto modules (`kyber.py`, `dilithium.py`) automatically fall back to dummy implementations when `liboqs` is not available. These provide:
- ✅ **Full system functionality** - All features work normally
- ✅ **Network connectivity testing** - Verify drone-operator communication  
- ✅ **UI/UX validation** - Test the control station interface
- ⚠️ **NO cryptographic security** - Not suitable for production

## Quick Test Steps

### 1. Run the Control Station

Since `liboqs` installation failed, the system will automatically use dummy crypto:

```powershell
# Using the PowerShell script
.\run_control_station.ps1 -Host 192.168.29.123

# OR directly
python control_station_app.py --host 192.168.29.123
```

You'll see warnings like:
```
Warning: liboqs not available (...). Using dummy Kyber implementation.
Warning: liboqs not available (...). Using dummy Dilithium implementation.
```

**This is expected and OK for testing!**

### 2. What Works

- ✅ Connection establishment
- ✅ Key exchange (dummy keys)
- ✅ WiFi scan data transmission
- ✅ Real-time network monitoring display
- ✅ Session management
- ✅ Command/response protocol

### 3. What Doesn't Work

- ❌ Actual post-quantum cryptographic security
- ❌ Real signature verification
- ❌ Protection against eavesdropping or tampering

## For Full Cryptographic Security

To get real post-quantum cryptography working on Windows, you have two options:

### Option A: Manual liboqs Build (Advanced)

Follow the detailed instructions in [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md#issue-liboqs-installation-fails), section "Manual Installation".

**Prerequisites**: Visual Studio 2022 Build Tools, CMake, Git

### Option B: Use WSL (Recommended for Production)

Windows Subsystem for Linux provides easier liboqs installation:

```bash
# In WSL Ubuntu
sudo apt-get install cmake ninja-build libssl-dev
git clone --depth 1 --branch 0.14.0 https://github.com/open-quantum-safe/liboqs.git
cd liboqs
mkdir build && cd build
cmake -GNinja -DBUILD_SHARED_LIBS=ON ..
ninja
sudo ninja install
sudo ldconfig
```

Then install Python packages in WSL.

## Conclusion

For **testing and development**, dummy mode is perfectly fine and lets you verify all functionality except cryptographic security.

For **production/research/dissertation**, you'll need real liboqs - use WSL or the manual build process.
