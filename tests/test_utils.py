import unittest


class TestSum(unittest.TestCase):

    def test_sum(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

    def test_sum_tuple(self):
        self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")

if __name__ == '__main__':
    unittest.main()

#initialize_files(powerlog_filename, process_filename, nvidia_smi_filename)
#find_nearest(array, value)
#read_txt(name)
#read_csv(name)
#plot_power(df)
#plot_usage()
#print_results(elapsed_time,cpu_consumption,gpu_consumption,dram_consumption)
#time_to_microsecs(string)
#datatime_to_microsecs(string)
#array_to_microseconds(array,function)