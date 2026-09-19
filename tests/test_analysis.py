import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd
from analysis.analyze_experiment import analyze, sample_size_per_variant


class AnalysisTests(unittest.TestCase):
    def test_returns_expected_fields(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "observations.csv"
            pd.DataFrame({"variant":["A","B"], "visitors":[1000,1000], "purchases":[100,120]}).to_csv(path,index=False)
            result = analyze(path)
            self.assertAlmostEqual(result.loc[0,"control_rate"], .10)
            self.assertAlmostEqual(result.loc[0,"treatment_rate"], .12)

    def test_sample_size_is_positive(self):
        self.assertGreater(sample_size_per_variant(.08, .012), 0)


if __name__ == "__main__": unittest.main()
