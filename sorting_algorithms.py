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

def mergeSort(arr):
	if len(arr) > 1:

		# Finding the mid of the array
		mid = len(arr)//2

		# Dividing the array elements
		L = arr[:mid]

		# into 2 halves
		R = arr[mid:]

		# Sorting the first half
		mergeSort(L)

		# Sorting the second half
		mergeSort(R)

		i = j = k = 0

		# Copy data to temp arrays L[] and R[]
		while i < len(L) and j < len(R):
			if L[i] < R[j]:
				arr[k] = L[i]
				i += 1
			else:
				arr[k] = R[j]
				j += 1
			k += 1

		# Checking if any element was left
		while i < len(L):
			arr[k] = L[i]
			i += 1
			k += 1

		while j < len(R):
			arr[k] = R[j]
			j += 1
			k += 1

def dummy_sorting_alg(alg):
	data = pd.read_csv (r'PT 042021-032022.csv')   
	arr = data['carbon_intensity_production_avg'].tolist()
	if alg == "stooge":
		n = len(arr)
		stoogesort(arr, 0, 500)
	else:
		mergeSort(arr)

def main():
	dummy_sorting_alg("stooge")

if __name__ == "__main__":
	main()

