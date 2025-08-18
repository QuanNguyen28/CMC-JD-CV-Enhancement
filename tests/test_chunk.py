from pymilvus import connections, Collection
import os
from dotenv import load_dotenv
load_dotenv()

connections.connect(host=os.getenv("MILVUS_HOST"),
                    port=os.getenv("MILVUS_PORT", "19530"))

# 2. Mở collection
coll = Collection(os.getenv("MILVUS_COLLECTION", "courses_embeddings"))

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
    
