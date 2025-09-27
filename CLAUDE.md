# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a development environment for CellProfiler 4.2.x, an open-source image analysis software for biologists. The project uses Pixi for dependency management and contains multiple submodules including the main CellProfiler application, CellProfiler Core, and supporting libraries.

## Essential Commands

### Environment Setup

```bash
# Install/update dependencies (run from project root only)
pixi install --all

# Activate the development environment
pixi shell -e dev

# Update pixi dependencies
pixi update
```

### Running CellProfiler

```bash
# Run CellProfiler with logging level 10
pixi run -e dev cp

# Run with Python warnings enabled
pixi run -e dev cpwd

# From within activated shell
python -m cellprofiler -L 10
```

### Testing

```bash
# Run tests for the main CellProfiler module
cd cp && pytest

# Run tests for CellProfiler Core
cd core && pytest

# Run specific test file
pytest tests/test_specific.py

# Run single test
pytest tests/test_file.py::test_function_name
```

### Code Quality

```bash
# Format code with Black (pre-commit hook exists)
black cellprofiler/

# Type checking for core module (has mypy.ini)
cd core && mypy cellprofiler_core/
```

### Git Submodules

```bash
# Initialize and update submodules after cloning
git submodule init
git submodule update --remote
```

## Architecture Overview

### Repository Structure

- **cp/** - Main CellProfiler application with GUI and processing modules
- **core/** - CellProfiler Core library with fundamental data structures and algorithms
- **centrosome/** - Image processing algorithms submodule
- **python-bioformats/** - Biological file format support submodule
- **python-javabridge/** - Java bridge for BioFormats integration submodule
- **distribution/** - Distribution and packaging files

### Key Components

#### CellProfiler Main (cp/)

- **cellprofiler/**main**.py** - Entry point for the application
- **cellprofiler/modules/** - Image processing modules (95+ modules for various operations)
- **cellprofiler/gui/** - wxPython-based graphical interface
- **cellprofiler/knime_bridge.py** - Integration with KNIME analytics platform

#### CellProfiler Core (core/)

- **cellprofiler_core/pipeline/** - Pipeline execution engine
- **cellprofiler_core/measurement/** - Data measurement and storage
- **cellprofiler_core/object/** - Object detection and manipulation
- **cellprofiler_core/image/** - Image data structures
- **cellprofiler_core/module/** - Base classes for processing modules

### Module System

CellProfiler uses a modular architecture where each image processing operation is a separate module in `cp/cellprofiler/modules/`. Modules inherit from base classes in `cellprofiler_core` and implement standard interfaces for settings, validation, and execution.

### Data Flow

1. Images are loaded through the pipeline system
2. Modules process images sequentially as defined in the pipeline
3. Measurements are collected and stored in the Measurements object
4. Results can be exported to various formats

## Development Notes

### Platform-Specific Configuration

- macOS uses python.app for GUI support (configured in pixi.toml)
- Windows requires specific JAVA_HOME configuration for BioFormats
- Linux uses pre-built wxPython wheels to avoid compilation

### Java Integration

The project requires Java 11 for BioFormats support through python-javabridge. JAVA_HOME is automatically configured by Pixi based on platform.

### Testing Framework

- Uses pytest for testing (v7.4.1)
- Test files follow `test_*.py` naming convention
- Tests are located in `tests/` directories within each module

### Important Environment Variables

- `JAVA_HOME` - Set automatically by Pixi for Java bridge
- `PYTHONEXECUTABLE` - Used on macOS for python.app compatibility
- `MYSQLCLIENT_CFLAGS/LDFLAGS` - MySQL client configuration on Unix systems
