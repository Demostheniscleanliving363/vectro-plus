QSTREAM (Vectro+ Quantized Streaming Format)

This file documents the simple streaming format used by `vectro_cli --quantize`.

Header and layout (all numbers little-endian):

- ASCII header: `VECTRO+QSTREAM1\n` (14 bytes)
- u32 table_count: number of quantization tables (number of dimensions)
- u32 dim: repeated dimension count (same as table_count; reserved)
- u32 tables_blob_len: length in bytes of the following bincode blob
- tables_blob: bincode(Vec<QuantTable>) where QuantTable = { min: f32, max: f32 }
- Repeated records: each record is:
  - u32 len (bytes)
  - bincode((id: String, qvec: Vec<u8>))

Notes:
- Each quantized vector stores one u8 per original dimension. QuantTable.quantize maps f32 -> u8 using a linear min/max scaling.
- The format is intentionally simple for streaming and backwards-compatibility with the non-quantized `VECTRO+STREAM1` format, which stores repeated `u32 len + bincode(Embedding)` records after header `VECTRO+STREAM1\n`.
- The loader expects little-endian values and uses `bincode` for typed blobs.
