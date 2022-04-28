import energyusage
import pandas as pd

def stoogesort(arr, l, h):
	if l >= h:
		return

	# If first element is smaller
	# than last, swap them
	if arr[l]>arr[h]:
		t = arr[l]
		arr[l] = arr[h]
		arr[h] = t

	# If there are more than 2 elements in
	# the array
	if h-l + 1 > 2:
		t = (int)((h-l + 1)/3)

		# Recursively sort first 2 / 3 elements
		stoogesort(arr, l, (h-t))

		# Recursively sort last 2 / 3 elements
		stoogesort(arr, l + t, (h))

		# Recursively sort first 2 / 3 elements
		# again to confirm
		stoogesort(arr, l, (h-t))

def dummy_sorting_alg():
    data = pd.read_csv (r'PT 042021-032022.csv')   
    arr = data['carbon_intensity_production_avg'].tolist()
    n = len(arr)
    stoogesort(arr, 0, n-1)
    print("Array has been sorted!")

def main():
    energyusage.evaluate(dummy_sorting_alg, pdf=True)

if __name__ == "__main__":
    main()

