#!/usr/bin/env python
"""
Convert CellProfiler pipeline files (.cppipe) to JSON format (v6).

Usage:
  pixi run -e dev python scripts/cppipe_to_json.py input.cppipe [output.json]
  pixi run -e dev python scripts/cppipe_to_json.py --batch /path/to/pipelines/

Quick test:
  pixi run -e dev python scripts/cppipe_to_json.py --batch scripts/example_pipelines/
"""

import sys
import os
from pathlib import Path
import typer
from typing import Optional

try:
    from cellprofiler_core.pipeline import Pipeline
    from cellprofiler_core.preferences import set_plugin_directory
except ImportError:
    print(
        "ERROR: CellProfiler not found. Run this script in the CellProfiler environment.",
        file=sys.stderr,
    )
    print(
        "Example: pixi run -e dev python scripts/cppipe_to_json.py <input.cppipe>",
        file=sys.stderr,
    )
    sys.exit(1)

# Load plugins if environment variable is set
plugins_dir = os.environ.get("CELLPROFILER_PLUGINS")
if plugins_dir and os.path.exists(plugins_dir):
    sys.path.insert(0, plugins_dir)
    set_plugin_directory(plugins_dir)
    print(f"Loaded plugins from: {plugins_dir}")

app = typer.Typer(help="Convert CellProfiler pipeline files (.cppipe) to JSON format")


def convert_file(
    input_file: Path, output_file: Optional[Path] = None, verbose: bool = True
) -> bool:
    """Convert a single CPPipe file to JSON format."""
    try:
        # Generate output filename if not provided
        if output_file is None:
            output_file = input_file.with_suffix(".json")

        if verbose:
            print(f"Converting: {input_file} -> {output_file}")

        # Load the pipeline
        pipeline = Pipeline()
        pipeline.load(str(input_file))

        # Save as JSON (version 6 format)
        with open(output_file, "w") as f:
            from cellprofiler_core.pipeline.io._v6 import dump

            dump(pipeline, f, save_image_plane_details=True)

        if verbose:
            module_count = len(pipeline.modules(False))
            print(f"  ✓ Successfully converted {module_count} modules")

        return True

    except Exception as e:
        print(f"  ✗ Error converting {input_file}: {e}", file=sys.stderr)
        return False


@app.command()
def convert(
    input: Path = typer.Argument(
        ...,
        help="Input .cppipe file or directory (with --batch)",
        exists=True,
    ),
    output: Optional[Path] = typer.Argument(
        None, help="Output .json file (auto-generated if not provided)"
    ),
    batch: bool = typer.Option(
        False, "--batch", "-b", help="Batch convert all .cppipe files in directory"
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress status messages"),
):
    """Convert CellProfiler pipeline files (.cppipe) to JSON format."""

    verbose = not quiet

    if batch:
        # Batch mode - convert all .cppipe files in directory
        directory = input
        cppipe_files = list(directory.glob("*.cppipe"))

        if not cppipe_files:
            print(f"No .cppipe files found in {directory}")
            raise typer.Exit(0)

        if verbose:
            print(f"Found {len(cppipe_files)} .cppipe files to convert")

        successful = 0
        failed = 0

        for cppipe_file in cppipe_files:
            if convert_file(cppipe_file, verbose=verbose):
                successful += 1
            else:
                failed += 1

        if verbose:
            print(f"\nConversion complete: {successful} successful, {failed} failed")

        raise typer.Exit(0 if failed == 0 else 1)

    else:
        # Single file mode
        if not input.is_file():
            print(f"Error: {input} is not a file", file=sys.stderr)
            raise typer.Exit(1)

        success = convert_file(input, output, verbose=verbose)
        raise typer.Exit(0 if success else 1)


if __name__ == "__main__":
    app()
