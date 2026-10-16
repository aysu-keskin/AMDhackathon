import os

# Arrow's default allocator keeps ~100 MB it never hands back after reading the parquet; the system
# allocator returns it. Must be set before pyarrow loads (memory on the free hosting tier).
os.environ.setdefault("ARROW_DEFAULT_MEMORY_POOL", "system")
