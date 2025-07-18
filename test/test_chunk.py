from pymilvus import connections, Collection
import os
from dotenv import load_dotenv
load_dotenv()

connections.connect(host=os.getenv("MILVUS_HOST", "localhost"),
                    port=os.getenv("MILVUS_PORT", "19530"))

coll = Collection(os.getenv("MILVUS_COLLECTION", "jdchunks"))

for field in coll.schema.fields:
    print(f"- {field.name}: {field.dtype}")

VECTOR_FIELD = "embedding"

# 1) Đảm bảo có index
if not coll.indexes:                       # KHÔNG truyền 'embedding' vào has_index()
    print("⏳  Create first index…")
    coll.create_index(
        field_name=VECTOR_FIELD,
        index_name="embedding_idx",
        index_params={"index_type": "IVF_FLAT",
                      "metric_type": "L2",
                      "params": {"nlist": 128}}
    )
    coll.flush()

# 2) Load
coll.load()
print("✅  Loaded, entities =", coll.num_entities)

# 3) Query sample
rows = coll.query(expr="", output_fields=["chunk_id", "jd_id"], limit=10)
print(rows)

from pymilvus import connections, Collection
import os
from dotenv import load_dotenv

# 1. Kết nối
load_dotenv()
connections.connect(
    alias="default",
    host=os.getenv("MILVUS_HOST", "localhost"),
    port=os.getenv("MILVUS_PORT", "19530")
)

# 2. Mở collection
coll = Collection(os.getenv("MILVUS_COLLECTION", "jdchunks"))

# 3. Chỉ lấy 10 vectors đầu tiên để test (tránh tải nguyên bộ nếu lớn)
results = coll.query(
    expr="",                              # lấy tất cả entities
    output_fields=["chunk_id", "embedding"],
    limit=10                              # chỉnh số lượng theo nhu cầu
)

for entry in results:
    print("Available keys:", list(entry.keys()))
    break


# 4. In vector ra
for entry in results:
    # chunk_index = entry["chunk_index"]
    chunk_id = entry["chunk_id"]
    vector = entry["embedding"]          # list[float]
    print(f"chunk_id={chunk_id}")
    print(f" vector length = {len(vector)}")
    print(f" vector[:5]    = {vector[:5]} …\n")
    
