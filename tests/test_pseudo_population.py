import unittest
import numpy as np
import pandas as pd
from pycausalgps.pseudo_population import PseudoPopulation

class TestPseudoPopulationWeighting(unittest.TestCase):

    def setUp(self):

        self.data = pd.DataFrame({
                        "id": range(1, 101),
                        "exposure": np.random.random(100),
                        "num_feature_1": np.random.random(100),
                        "num_feature_2": np.random.random(100),
                        "cat_feature": np.random.choice(["A", "B", "C"], 100)})
        
        gps_data = pd.DataFrame({
                        "id": range(1, 101),
                        "gps": np.random.random(100),
                        "gps_standardized": np.random.random(100),
                        "e_gps_pred": np.random.random(100),
                        "e_gps_std_pred": np.random.random(100),
                        "w_resid": np.random.random(100)})
        
        self.gps_data = {
            "data": gps_data,
            "gps_density": "normal",
        }

        self.params = {
            'approach': PseudoPopulation.APPROACH_WEIGHTING,
            'exposure_column': 'exposure',
            'covariate_column_num': ['num_feature_1', 'num_feature_2'],
            'covariate_column_cat': ['cat_feature']}

    def test_init(self):
        pspop = PseudoPopulation(self.data, self.gps_data, self.params)
        results = pspop.get_results()

        self.assertIn("data", results)
        self.assertIn("params", results)
        self.assertIn("compiling_report", results)
        self.assertIn("covariate_balance", results)
        self.assertEqual(results.get("data").shape[0], 100)
        self.assertEqual(results.get("covariate_balance").shape[0], 3)


if __name__ == "__main__":
    unittest.main()