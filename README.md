# Blender Headless Rendering Setup Guide

This guide explains how to set up Blender for headless rendering of NLOS (Non-Line-of-Sight) dataset generation.

## Prerequisites

- Linux, Windows, or macOS
- Python 3.7+
- GPU with CUDA support (for optimal rendering performance)
- At least 16GB RAM recommended
- Storage space for rendered images (EXR format)

## Installation Steps

### 1. Install Blender

#### Ubuntu/Debian
```bash
# Add Blender repository
sudo add-apt-repository ppa:blender/blender
sudo apt-get update

# Install Blender
sudo apt-get install blender
```

#### Windows
1. Download Blender from [official website](https://www.blender.org/download/)
2. Run the installer
3. Add Blender to system PATH

#### macOS
```bash
# Using Homebrew
brew install blender
```

### 2. Required Files Setup

1. Create a project directory:
```bash
mkdir nlos_rendering
cd nlos_rendering
```

2. Place the following files in your project directory:
- `rendering.py` (main rendering script)
- `drone.fbx` (drone 3D model)

3. Create output directory:
```bash
mkdir nlos_dataset
```

## Running Headless Rendering

### Basic Usage

```bash
blender --background --python rendering.py
```

### Advanced Usage with GPU

```bash
blender --background --python rendering.py -- --cycles-device CUDA
```

### Environment Variables (Optional)

```bash
# Set number of CPU threads
export BLENDER_THREADS=8

# Set GPU device index
export CUDA_VISIBLE_DEVICES=0
```

## Script Configuration

Key parameters in `rendering.py` that you might want to modify:

```python
# Set the number of frames per folder
frames_per_folder = 1000

# Starting folder number
starting_folder_number = 5
```

## Output Structure

The script generates:

```
nlos_dataset/
├── seq_0005/
│   ├── seq_0005_0001.exr
│   ├── seq_0005_0001.json
│   ├── seq_0005_0002.exr
│   ├── seq_0005_0002.json
│   └── ...
├── seq_0006/
└── ...
```

Each .json file contains:
- Timestamp
- Drone poses (position and orientation)
- Image path

## Troubleshooting

### Common Issues

1. **GPU Not Detected**
   ```bash
   # Check GPU status
   blender --background --python-expr "import bpy; print(bpy.context.preferences.addons['cycles'].preferences.get_devices())"
   ```

2. **Memory Issues**
   - Reduce `frames_per_folder`
   - Lower render quality settings
   - Increase system swap space

3. **Missing drone.fbx**
   - Ensure the drone model is in the same directory as the script
   - Check file permissions

### Performance Optimization

1. Adjust render settings in the script:
```python
bpy.context.scene.cycles.samples = 1024  # Decrease for faster rendering
bpy.context.scene.cycles.tile_x = 1024   # Adjust based on GPU memory
bpy.context.scene.cycles.tile_y = 1024
```

2. Use multiple GPUs:
```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3
blender --background --python rendering.py
```

