"""
src/config.py
=============
Centralized configuration management for the MapReduce Log Analysis System.

Responsibilities:
- Define default input and output directories.
- Configure worker concurrency parameters (Map workers, Reduce workers).
- Set result display parameters (Top-N frequent tokens/events).
- Provide a centralized configuration container so that values are not
  hardcoded across different modules.

Primary Ownership: Shared / Maintained across all members.
"""

from dataclasses import dataclass
from pathlib import Path


# Project Root Directory Resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Config:
    """Configuration settings for the MapReduce pipeline execution."""

    # File and Directory Paths
    input_dir: Path = PROJECT_ROOT / "input"
    output_dir: Path = PROJECT_ROOT / "output"
    output_file_name: str = "analysis_summary.txt"

    # Worker Concurrency Settings (Default values for initial testing)
    map_workers: int = 4
    reduce_workers: int = 2

    # Data Processing Parameters
    top_n_results: int = 10
    case_sensitive: bool = False
    
    # Log token filtering settings
    min_word_length: int = 2

    @property
    def output_file_path(self) -> Path:
        """Returns the full path to the final output file."""
        return self.output_dir / self.output_file_name


# Default shared configuration instance
DEFAULT_CONFIG = Config()
