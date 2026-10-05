import logging
from pathlib import Path

import pandas as pd

from src.config.constants import (
    CHROMA_INSERT_BATCH_SIZE, COLLECTION_NAME, EMBEDDING_BATCH_SIZE, EMBEDDING_MODEL_ID,
    PASSAGE_PREFIX, VECTOR_DISTANCE_METRIC, VECTORSTORE_REQUIRED_COLUMNS,
)
from src.config.settings import REVIEWS_PATH, VECTORSTORE_DIR
from src.data_prep.recompute_safety_flags import build_metadata
from src.exceptions.exceptions import DataFileMissingError
from src.utils.output import write_line
from src.utils.run_log import log_run

logger = logging.getLogger(__name__)


def load_reviews_for_indexing(path):
    path = Path(path)
    if not path.exists():
        raise DataFileMissingError(f"Scrubbed reviews file not found: {path.name}")
    df = pd.read_csv(path, low_memory=False)
    missing = [col for col in VECTORSTORE_REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise DataFileMissingError(
            f"{path.name} is missing columns: {', '.join(missing)}. "
            "Run recompute-safety-flags first."
        )
    return df


def run(scrubbed=None, chroma_dir=None, collection_name=COLLECTION_NAME):
    import chromadb
    from sentence_transformers import SentenceTransformer

    scrubbed = scrubbed or str(REVIEWS_PATH)
    chroma_dir = chroma_dir or str(VECTORSTORE_DIR)

    df = load_reviews_for_indexing(scrubbed)
    write_line(f"Loaded {len(df)} reviews from {scrubbed}")

    texts = df["review_text"].fillna("").astype(str).tolist()
    model = SentenceTransformer(EMBEDDING_MODEL_ID)
    embeddings = model.encode(
        [PASSAGE_PREFIX + text for text in texts],
        batch_size=EMBEDDING_BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    Path(chroma_dir).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=chroma_dir)
    existing = {getattr(c, "name", c) for c in client.list_collections()}
    if collection_name in existing:
        client.delete_collection(collection_name)
        logger.info("Replaced existing collection '%s'", collection_name)
    collection = client.create_collection(
        name=collection_name, metadata={"hnsw:space": VECTOR_DISTANCE_METRIC},
    )

    ids = [str(i) for i in df.index]
    metadatas = build_metadata(df)
    for start in range(0, len(df), CHROMA_INSERT_BATCH_SIZE):
        end = min(start + CHROMA_INSERT_BATCH_SIZE, len(df))
        collection.add(
            ids=ids[start:end],
            embeddings=embeddings[start:end].tolist(),
            documents=texts[start:end],
            metadatas=metadatas[start:end],
        )
        logger.info("Inserted %d / %d vectors", end, len(df))

    write_line(f"Saved {collection.count()} vectors to {chroma_dir}")
    log_run(
        script_name="build_vectorstore",
        params=f"scrubbed={scrubbed}, chroma_dir={chroma_dir}, model={EMBEDDING_MODEL_ID}",
        summary=f"vectors_stored={collection.count()}, collection={collection_name}",
    )
