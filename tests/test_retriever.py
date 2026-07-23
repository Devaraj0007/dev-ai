import tempfile
import unittest
from pathlib import Path

from src.ingest import build_index
from src.retriever import Retriever


class RetrieverIntegrationTests(unittest.TestCase):
    def test_retrieves_relevant_chunk_from_temporary_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_dir = temp_path / "sources"
            source_dir.mkdir()
            (source_dir / "handbook.txt").write_text(
                "Remote work may happen up to three days per week. Fully remote arrangements require approval.",
                encoding="utf-8",
            )
            (source_dir / "manual.txt").write_text(
                "PulseBoard requires Docker Engine 24.0 and supports Snowflake.",
                encoding="utf-8",
            )

            index_path = temp_path / "index.pkl"
            build_index(source_dir=str(source_dir), index_path=str(index_path))

            retriever = Retriever(index_path=str(index_path))
            results = retriever.retrieve("Do fully remote arrangements need approval?", top_k=2, min_score=0.01)

            self.assertGreaterEqual(len(results), 1)
            self.assertEqual(results[0]["source"], "handbook.txt")
            self.assertGreater(results[0]["score"], 0)


if __name__ == "__main__":
    unittest.main()