import os
import unittest
from unittest.mock import patch

from src.agent import ResearchAgent


class GroundingValidationTests(unittest.TestCase):
    def setUp(self):
        self.agent = ResearchAgent.__new__(ResearchAgent)
        self.chunks = [
            {"id": 7, "source": "handbook.txt", "text": "Paid parental leave is 16 weeks."},
            {"id": 8, "source": "manual.txt", "text": "PulseBoard requires Docker 24.0."},
        ]

    def test_valid_citation_is_grounded_and_has_provenance(self):
        grounded, invalid, citations = self.agent._validate_grounding(
            "Paid leave is 16 weeks [1].", self.chunks, True
        )

        self.assertTrue(grounded)
        self.assertEqual(invalid, [])
        self.assertEqual(citations[0]["chunk_id"], 7)
        self.assertEqual(citations[0]["source"], "handbook.txt")

    def test_unknown_citation_is_not_grounded(self):
        grounded, invalid, citations = self.agent._validate_grounding(
            "Paid leave is 16 weeks [3].", self.chunks, True
        )

        self.assertFalse(grounded)
        self.assertEqual(invalid, ["[3]"])
        self.assertEqual(citations, [])

    def test_sufficient_answer_requires_a_citation(self):
        grounded, invalid, _ = self.agent._validate_grounding(
            "Paid leave is 16 weeks.", self.chunks, True
        )

        self.assertFalse(grounded)
        self.assertEqual(invalid, ["[missing citation]"])


class ConfigurationTests(unittest.TestCase):
    def test_invalid_environment_values_are_rejected(self):
        from src.agent import _positive_int_env, _score_env

        with patch.dict(os.environ, {"TEST_TOP_K": "nope"}):
            with self.assertRaises(ValueError):
                _positive_int_env("TEST_TOP_K", 4)
        with patch.dict(os.environ, {"TEST_MIN_SCORE": "not-a-number"}):
            with self.assertRaises(ValueError):
                _score_env("TEST_MIN_SCORE", 0.05)


if __name__ == "__main__":
    unittest.main()
