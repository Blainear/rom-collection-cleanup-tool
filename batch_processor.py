"""
Batch processing utilities for ROM cleanup operations.

This module provides optimized batch processing for large ROM collections,
including progress tracking and memory-efficient file operations.
"""

import logging
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Tracks and reports progress of batch operations."""

    def __init__(
        self,
        total_items: int,
        update_callback: Optional[Callable[[float, str], None]] = None,
    ):
        """Initialize progress tracker.

        Args:
            total_items: Total number of items to process
            update_callback: Optional callback for progress updates (progress_percent, status_message)
        """
        self.total_items = total_items
        self.processed_items = 0
        self.start_time = time.time()
        self.update_callback = update_callback
        self.last_update_time = 0
        self.update_interval = 0.1  # Update at most every 100ms

    def update(self, increment: int = 1, status: str = "") -> None:
        """Update progress and call callback if provided.

        Args:
            increment: Number of items processed
            status: Optional status message
        """
        self.processed_items += increment
        current_time = time.time()

        # Throttle updates to avoid overwhelming the UI
        if current_time - self.last_update_time >= self.update_interval:
            progress_percent = (self.processed_items / self.total_items) * 100

            if self.update_callback:
                self.update_callback(progress_percent, status)

            self.last_update_time = current_time

    def get_eta(self) -> Optional[float]:
        """Calculate estimated time to completion in seconds.

        Returns:
            Estimated seconds remaining, or None if cannot calculate
        """
        if self.processed_items == 0:
            return None

        elapsed_time = time.time() - self.start_time
        rate = self.processed_items / elapsed_time
        remaining_items = self.total_items - self.processed_items

        if rate > 0:
            return remaining_items / rate
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get current processing statistics.

        Returns:
            Dictionary with processing stats
        """
        elapsed_time = time.time() - self.start_time
        rate = self.processed_items / elapsed_time if elapsed_time > 0 else 0
        eta = self.get_eta()

        return {
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "progress_percent": (self.processed_items / self.total_items) * 100,
            "elapsed_time": elapsed_time,
            "processing_rate": rate,
            "eta_seconds": eta,
        }


class BatchFileProcessor:
    """Efficiently processes large collections of files in batches."""

    def __init__(self, batch_size: int = 1000, max_memory_mb: int = 100):
        """Initialize batch processor.

        Args:
            batch_size: Number of files to process in each batch
            max_memory_mb: Maximum memory usage in MB before forcing cleanup
        """
        self.batch_size = batch_size
        self.max_memory_mb = max_memory_mb
        self.processed_count = 0
        self.error_count = 0
        self.errors: List[Tuple[Path, str]] = []

    def scan_files_batch(
        self,
        directory: Union[str, Path],
        extensions: Set[str],
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Iterator[List[Path]]:
        """Scan files in batches for memory efficiency.

        Args:
            directory: Directory to scan
            extensions: File extensions to include
            progress_callback: Optional progress callback

        Yields:
            Batches of file paths
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        logger.info(f"Starting batch scan of {directory_path}")

        # First pass: count files for progress tracking
        total_files = sum(
            1 for _ in self._iter_matching_files(directory_path, extensions)
        )
        logger.info(f"Found {total_files} files to process")

        if progress_callback:
            progress_tracker = ProgressTracker(total_files, progress_callback)
        else:
            progress_tracker = None

        # Second pass: yield files in batches
        current_batch = []

        for file_path in self._iter_matching_files(directory_path, extensions):
            current_batch.append(file_path)

            if progress_tracker:
                progress_tracker.update(1, f"Scanning: {file_path.name}")

            if len(current_batch) >= self.batch_size:
                yield current_batch
                current_batch = []

        # Yield remaining files
        if current_batch:
            yield current_batch

        logger.info(f"Completed batch scan of {total_files} files")

    def _iter_matching_files(
        self, directory: Path, extensions: Set[str]
    ) -> Iterator[Path]:
        """Iterate over files matching the given extensions.

        Args:
            directory: Directory to scan
            extensions: File extensions to match

        Yields:
            Matching file paths
        """
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in extensions:
                    yield file_path
        except (PermissionError, OSError) as e:
            logger.warning(f"Error accessing {directory}: {e}")

    def process_file_batches(
        self,
        file_batches: Iterator[List[Path]],
        processor_func: Callable[[Path], Tuple[bool, Any]],
        progress_callback: Optional[Callable[[float, str], None]] = None,
        total_items: Optional[int] = None,
        progress_tracker: Optional[ProgressTracker] = None,
    ) -> Dict[str, Any]:
        """Process file batches with error handling and progress tracking.

        Args:
            file_batches: Iterator yielding batches of file paths
            processor_func: Function to process each file, returns (success, result)
            progress_callback: Optional callback receiving
                ``(progress_percent, status_message)``
            total_items: Optional total number of items to process
            progress_tracker: Optional :class:`ProgressTracker` instance. If
                provided, it will be updated instead of using ``total_items``
                and ``progress_callback`` directly.

        Returns:
            Dictionary with processing results and statistics
        """
        results = []
        batch_count = 0

        logger.info("Starting batch file processing")

        if progress_tracker is None and progress_callback and total_items:
            progress_tracker = ProgressTracker(total_items, progress_callback)

        if progress_tracker:
            total_items = progress_tracker.total_items

        for batch in file_batches:
            batch_count += 1
            batch_start_time = time.time()

            logger.debug(f"Processing batch {batch_count} with {len(batch)} files")

            batch_results = []
            batch_errors = 0

            for file_path in batch:
                try:
                    success, result = processor_func(file_path)
                    if success:
                        batch_results.append(result)
                        self.processed_count += 1
                    else:
                        batch_errors += 1
                        self.error_count += 1
                        self.errors.append((file_path, str(result)))

                    if progress_tracker:
                        progress_tracker.update(1, f"Processing: {file_path.name}")
                    elif progress_callback and total_items:
                        progress = (self.processed_count / total_items) * 100
                        progress_callback(progress, f"Processing: {file_path.name}")

                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    batch_errors += 1
                    self.error_count += 1
                    self.errors.append((file_path, str(e)))

            results.extend(batch_results)

            batch_time = time.time() - batch_start_time
            logger.debug(
                f"Batch {batch_count} completed in {batch_time:.2f}s, "
                f"{len(batch_results)} successful, {batch_errors} errors"
            )

            # Force garbage collection after each batch to manage memory
            import gc

            gc.collect()

        logger.info(
            f"Batch processing completed: {self.processed_count} processed, "
            f"{self.error_count} errors"
        )

        return {
            "results": results,
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "errors": self.errors,
            "batch_count": batch_count,
        }


class ROMBatchScanner:
    """Specialized batch scanner for ROM files with caching and optimization."""

    def __init__(self, cache_enabled: bool = True):
        """Initialize ROM batch scanner.

        Args:
            cache_enabled: Whether to enable filename parsing cache
        """
        self.cache_enabled = cache_enabled
        self._name_cache: Dict[str, Tuple[str, str]] = (
            {}
        )  # filename -> (base_name, region)
        self.processor = BatchFileProcessor()

    def scan_roms_batch(
        self,
        directory: Union[str, Path],
        extensions: Set[str],
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, List[Tuple[Path, str, str]]]:
        """Scan ROMs in batches and group by canonical name.

        Args:
            directory: Directory to scan
            extensions: ROM file extensions
            progress_callback: Optional callback receiving
                ``(progress_percent, status_message)``

        Returns:
            Dictionary mapping canonical names to lists of (file_path, region, original_name) tuples
        """
        from rom_utils import get_base_name, get_region

        rom_groups = defaultdict(list)

        total_files = sum(
            1 for _ in self.processor._iter_matching_files(Path(directory), extensions)
        )

        def process_rom_file(
            file_path: Path,
        ) -> Tuple[bool, Optional[Tuple[str, str, str]]]:
            """Process a single ROM file.

            Returns:
                (success, (canonical_name, region, original_name)) or (False, error_message)
            """
            try:
                filename = file_path.name

                # Check cache first
                if self.cache_enabled and filename in self._name_cache:
                    base_name, region = self._name_cache[filename]
                else:
                    # Parse filename
                    base_name = get_base_name(filename)
                    region = get_region(filename)

                    # Cache the result
                    if self.cache_enabled:
                        self._name_cache[filename] = (base_name, region)

                if not base_name:
                    return False, f"Could not parse game name from {filename}"

                return True, (base_name, region, filename)

            except Exception as e:
                return False, str(e)

        # Process files in batches
        file_batches = self.processor.scan_files_batch(
            directory, extensions, progress_callback
        )
        batch_results = self.processor.process_file_batches(
            file_batches,
            process_rom_file,
            progress_callback,
            total_items=total_files,
        )

        # Group results by canonical name
        for result in batch_results["results"]:
            canonical_name, region, original_name = result
            # TODO: Track and expose the source file path for each result when
            # batch processing is enhanced to provide that information.

        logger.info(f"ROM batch scan completed: {len(rom_groups)} unique games found")

        return dict(rom_groups)

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "cache_enabled": self.cache_enabled,
            "cache_size": len(self._name_cache),
            "cache_memory_kb": len(str(self._name_cache).encode()) // 1024,
        }

    def clear_cache(self) -> None:
        """Clear the filename parsing cache."""
        self._name_cache.clear()
        logger.debug("ROM filename cache cleared")


class ParallelBatchProcessor:
    """Process batches in parallel for improved performance on multi-core systems."""

    def __init__(self, max_workers: Optional[int] = None):
        """Initialize parallel batch processor.

        Args:
            max_workers: Maximum number of worker threads (None for auto-detect)
        """
        self.max_workers = max_workers

    def process_batches_parallel(
        self,
        file_batches: List[List[Path]],
        processor_func: Callable[[List[Path]], List[Any]],
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> List[Any]:
        """Process file batches in parallel.

        Args:
            file_batches: List of file path batches
            processor_func: Function to process each batch
            progress_callback: Optional progress callback

        Returns:
            Combined results from all batches
        """
        try:
            from concurrent.futures import ThreadPoolExecutor, as_completed
        except ImportError:
            logger.warning(
                "concurrent.futures not available, falling back to sequential processing"
            )
            return self._process_batches_sequential(
                file_batches, processor_func, progress_callback
            )

        logger.info(
            f"Processing {len(file_batches)} batches in parallel with {self.max_workers} workers"
        )

        all_results = []
        completed_batches = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all batches
            future_to_batch = {
                executor.submit(processor_func, batch): i
                for i, batch in enumerate(file_batches)
            }

            # Collect results as they complete
            for future in as_completed(future_to_batch):
                batch_index = future_to_batch[future]

                try:
                    batch_results = future.result()
                    all_results.extend(batch_results)
                    completed_batches += 1

                    if progress_callback:
                        progress = (completed_batches / len(file_batches)) * 100
                        progress_callback(
                            progress,
                            f"Completed batch {completed_batches}/{len(file_batches)}",
                        )

                except Exception as e:
                    logger.error(f"Error processing batch {batch_index}: {e}")

        logger.info(f"Parallel processing completed: {len(all_results)} total results")
        return all_results

    def _process_batches_sequential(
        self,
        file_batches: List[List[Path]],
        processor_func: Callable[[List[Path]], List[Any]],
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> List[Any]:
        """Fallback sequential processing."""
        logger.info(f"Processing {len(file_batches)} batches sequentially")

        all_results = []

        for i, batch in enumerate(file_batches):
            try:
                batch_results = processor_func(batch)
                all_results.extend(batch_results)

                if progress_callback:
                    progress = ((i + 1) / len(file_batches)) * 100
                    progress_callback(
                        progress, f"Completed batch {i + 1}/{len(file_batches)}"
                    )

            except Exception as e:
                logger.error(f"Error processing batch {i}: {e}")

        return all_results
