from pymilvus import connections, utility, Collection
import os
from dotenv import load_dotenv
load_dotenv()

connections.connect(host=os.getenv("MILVUS_HOST"),
                    port=os.getenv("MILVUS_PORT", "19530"))


# 2) Lấy danh sách collections
cols = utility.list_collections()
print("Collections:", cols)
if not cols:
    raise SystemExit("Chưa có collection nào. Hãy reindex trước.")

# 3) Chọn 1 collection bất kỳ (vd: lấy cái đầu tiên)
name = cols[0]                   # hoặc name = "jdchunks"
print("Inspecting:", name)

# 4) Gắn vào collection và (optional) load
col = Collection(name)
try:
    col.load()                   # giúp đọc num_entities nhanh hơn
except Exception:
    pass

# 5) Thông tin cơ bản
print("Entities:", col.num_entities)

print("\nFields:")
for f in col.schema.fields:
    meta = []
    if getattr(f, "is_primary", False): meta.append("PK")
    if hasattr(f, "max_length"): meta.append(f"max_len={f.max_length}")
    print(f" - {f.name}: {f.dtype} {' '.join(meta)}")

print("\nIndexes:")
if col.indexes:
    for idx in col.indexes:
        print(" -", idx.index_name, idx.params)
else:
    print(" (no index)")

# 6) Lấy vài dòng mẫu (đổi expr & fields theo schema của bạn)
try:
    rows = col.query(
        expr="embedding",                         # hoặc expr khác
        output_fields=["chunk_id","jd_id","chunk_index","object_url", "embedding"],  # thêm "embedding" nếu muốn xem vector
        limit=3
    )
    print("\nSample rows:", rows)
except Exception as e:
    print("Query sample error:", e)