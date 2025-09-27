#!/usr/bin/env python
"""
Convert CellProfiler pipeline files (.cppipe) to JSON format (v6).

COMPLETE STANDALONE SETUP FROM GIST:

  # 1. Clone the CellProfiler development environment
  git clone https://github.com/gnodar01/cp-42x-dev.git
  cd cp-42x-dev

  # 2. Create scripts directory and download this converter from Gist
  mkdir -p scripts
  curl -o scripts/cppipe_to_json.py https://gist.github.com/YOUR_USERNAME/GIST_ID/raw/cppipe_to_json.py
  # OR: wget https://gist.github.com/YOUR_USERNAME/GIST_ID/raw/cppipe_to_json.py -O scripts/cppipe_to_json.py

  # 3. Install all dependencies (this will take a few minutes)
  pixi install --all

  # 4. (Optional) Clone CellProfiler plugins if you need custom modules
  git clone https://github.com/CellProfiler/CellProfiler-plugins.git
  export CELLPROFILER_PLUGINS=$(pwd)/CellProfiler-plugins/active_plugins

  # 5. Run the converter
  pixi run -e dev python scripts/cppipe_to_json.py <input.cppipe> [output.json]

QUICK START (after initial setup):
  cd cp-42x-dev
  pixi run -e dev python scripts/cppipe_to_json.py pipeline.cppipe

REQUIREMENTS:
- Pixi package manager (install from: https://pixi.sh/latest/#installation)
- Git
- The cp-42x-dev repository provides:
  - CellProfiler and cellprofiler_core packages
  - Java 11 (for BioFormats support)
  - All scientific Python dependencies (numpy, scipy, scikit-image, etc.)
  - Proper platform-specific configurations

OPTIONAL PLUGINS:
- CellProfiler-plugins repository contains additional modules not in core CellProfiler
- Modules like CallBarcodes, CompensateColors, RunStarDist, etc.
- Clone from: https://github.com/CellProfiler/CellProfiler-plugins.git
- Set environment variable: export CELLPROFILER_PLUGINS=/path/to/CellProfiler-plugins/active_plugins

Key behaviors:
- Loads plugin modules if CELLPROFILER_PLUGINS is set to ensure all modules are available
- Uses CellProfiler's native serialization (pipeline.dump with v6 format)
- Preserves image plane details when available in the pipeline
- Without plugins, some modules may be silently skipped during conversion

Usage examples:
  # Single file conversion
  pixi run -e dev python scripts/cppipe_to_json.py input.cppipe
  pixi run -e dev python scripts/cppipe_to_json.py input.cppipe output.json

  # Batch conversion of all .cppipe files in current directory
  pixi run -e dev python scripts/cppipe_to_json.py --batch .

  # Batch conversion with specific directory
  pixi run -e dev python scripts/cppipe_to_json.py --batch /path/to/pipelines/

  # Batch conversion of example pipelines (real working example)
  pixi run -e dev python scripts/cppipe_to_json.py --batch scripts/example_pipelines/

  # QUICK TEST FOR DEVELOPMENT - Test script and check for consistency:
  # (Assumes example_pipelines/*.json are committed to git)
  cd /Users/shsingh/Documents/GitHub/nf/cp-42x-dev && \
    pixi run -e dev python scripts/cppipe_to_json.py --batch scripts/example_pipelines/ && \
    git diff --stat scripts/example_pipelines/*.json && \
    echo "No differences = ✓ Conversion is consistent" || echo "Changes detected above"

  # With plugins loaded
  CELLPROFILER_PLUGINS=/path/to/CellProfiler-plugins/active_plugins pixi run -e dev python scripts/cppipe_to_json.py input.cppipe

  # Quiet mode (suppress status messages)
  pixi run -e dev python scripts/cppipe_to_json.py --quiet input.cppipe

  # Verbose mode (show module details)
  pixi run -e dev python scripts/cppipe_to_json.py -vv input.cppipe
"""

import sys
import os
import argparse
from pathlib import Path

try:
    # Try importing CellProfiler - will fail if not in proper environment
    from cellprofiler_core.pipeline import Pipeline
    from cellprofiler_core.preferences import set_plugin_directory
except ImportError as e:
    print(
        "ERROR: CellProfiler not found. Please run this script in a CellProfiler environment.",
        file=sys.stderr,
    )
    print(
        "Example: pixi run -e dev python cppipe_to_json.py <input.cppipe>",
        file=sys.stderr,
    )
    print(f"Details: {e}", file=sys.stderr)
    sys.exit(1)

# Load plugins if environment variable is set
plugins_dir = os.environ.get("CELLPROFILER_PLUGINS")
if plugins_dir and os.path.exists(plugins_dir):
    sys.path.insert(0, plugins_dir)
    set_plugin_directory(plugins_dir)
    print(f"Loaded plugins from: {plugins_dir}")
elif plugins_dir:
    print(
        f"Warning: CELLPROFILER_PLUGINS set but directory not found: {plugins_dir}",
        file=sys.stderr,
    )


def convert_cppipe_to_json(input_file, output_file=None, verbose=True):
    """Convert a single CPPipe file to JSON format."""
    try:
        # Generate output filename if not provided
        if output_file is None:
            output_file = str(Path(input_file).with_suffix(".json"))

        if verbose:
            print(f"Converting: {input_file} -> {output_file}")

        # Load the pipeline
        pipeline = Pipeline()
        pipeline.load(input_file)

        # Save as JSON (version 6 format)
        with open(output_file, "w") as f:
            # Use version 6 for JSON output
            from cellprofiler_core.pipeline.io._v6 import dump

            dump(pipeline, f, save_image_plane_details=True)

        if verbose:
            # Get some basic info about the pipeline
            module_count = len(pipeline.modules(False))
            module_names = [m.module_name for m in pipeline.modules(False)]
            print(f"  ✓ Successfully converted {module_count} modules")
            if verbose > 1:
                print(
                    f"    Modules: {', '.join(module_names[:5])}"
                    + ("..." if len(module_names) > 5 else "")
                )

        return True

    except Exception as e:
        print(f"  ✗ Error converting {input_file}: {e}", file=sys.stderr)
        return False


def batch_convert(directory=".", pattern="*.cppipe", verbose=True):
    """Convert all CPPipe files in a directory to JSON format."""
    directory = Path(directory)
    cppipe_files = list(directory.glob(pattern))

    if not cppipe_files:
        print(f"No .cppipe files found in {directory}")
        return 0, 0

    print(f"Found {len(cppipe_files)} .cppipe files to convert")

    successful = 0
    failed = 0

    for cppipe_file in cppipe_files:
        if convert_cppipe_to_json(str(cppipe_file), verbose=verbose):
            successful += 1
        else:
            failed += 1

    return successful, failed


def main():
    parser = argparse.ArgumentParser(
        description="Convert CellProfiler pipeline files (.cppipe) to JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "input", nargs="?", help="Input .cppipe file or directory for batch mode"
    )
    parser.add_argument(
        "output", nargs="?", help="Output .json file (auto-generated if not provided)"
    )
    parser.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="Batch convert all .cppipe files in directory",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress status messages"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=1,
        help="Increase verbosity (can be used multiple times)",
    )

    args = parser.parse_args()

    # Adjust verbosity
    if args.quiet:
        verbose = 0
    else:
        verbose = args.verbose

    # Batch mode
    if args.batch:
        directory = args.input if args.input else "."
        successful, failed = batch_convert(directory, verbose=verbose)

        if verbose:
            print(f"\nConversion complete: {successful} successful, {failed} failed")

        # Exit with error code if any conversions failed
        sys.exit(0 if failed == 0 else 1)

    # Single file mode
    else:
        if not args.input:
            parser.print_help()
            sys.exit(1)

        if not os.path.exists(args.input):
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)

        success = convert_cppipe_to_json(args.input, args.output, verbose=verbose)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
