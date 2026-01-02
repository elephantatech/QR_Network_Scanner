
import PyInstaller.__main__
import shutil
import os
import plistlib
import subprocess

def build():
    print("Building QR Network Scanner...")
    
    # Clean up previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    PyInstaller.__main__.run([
        'launcher.py',
        '--name=QRNetworkScanner',
        '--windowed', # Create a .app bundle
        '--icon=assets/icon.png', # App Icon
        '--add-data=assets/icon.png:assets', # Include in bundle
        '--add-data=assets/help.html:assets', # Include HTML help
        '--clean',
        '--noconfirm',
        '--noconfirm',
        # Hidden imports often needed for these libraries
        '--hidden-import=rich',
        '--hidden-import=zxingcpp',
        '--hidden-import=pkg_resources.extern',
        '--collect-all=rich',
    ])
    
    # Update Info.plist with Camera Permissions
    plist_path = 'dist/QRNetworkScanner.app/Contents/Info.plist'
    if os.path.exists(plist_path):
        print("Updating Info.plist with Camera Usage Description...")
        with open(plist_path, 'rb') as f:
            plist = plistlib.load(f)
        
        plist['NSCameraUsageDescription'] = "This app needs access to the camera to scan QR codes for WiFi networks."
        
        with open(plist_path, 'wb') as f:
            plistlib.dump(plist, f)
        print("Info.plist updated.")

    # Sign the application with entitlements (Ad-hoc signing)
    app_path = "dist/QRNetworkScanner.app"
    print("Signing application with entitlements...")
    try:
        subprocess.run([
            "codesign", "--force", "--deep", 
            "--sign", "-", # Ad-hoc signing
            "--entitlements", "entitlements.plist",
            app_path
        ], check=True)
        print("Application signed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error signing application: {e}")

    print("Build complete. Check dist/QRNetworkScanner.app")

if __name__ == '__main__':
    build()
