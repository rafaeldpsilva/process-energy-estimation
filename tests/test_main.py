import unittest
import os
from .. import process_cpu_usage, join_process_data, estimate_process_power_consumption, estimate_gpu_power_consumption, estimate_dram_power_consumption

class TestMain(unittest.TestCase):

    def test_estimate_process_power_consumption(self):
        time = [1,2,3]
        processor_power=
        self.assertEqual(estimate_process_power_consumption(df), x, "Should be x")
    
    def test_estimate_gpu_power_consumption(self):
        self.assertEqual(estimate_gpu_power_consumption(df), x, "Should be x")

    def test_estimate_dram_power_consumption(self):
        self.assertEqual(estimate_dram_power_consumption(df), x, "Should be x")

if __name__ == '__main__':
    unittest.main()

#estimate_process_power_consumption(df)
#estimate_gpu_power_consumption(df)
#estimate_dram_power_consumption(df)