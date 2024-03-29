import waterz
import daisy
import numpy as np
from scipy import ndimage
from scipy.ndimage import gaussian_filter, label
from skimage.feature import peak_local_max
from skimage.morphology import watershed

def find_seeds(dist):
    #smoothed = gaussian_filter(dist, sigma=sigma)
    return label(peak_local_max(dist, indices=False))[0]

def normalize_distances(predicted_distances):
    normalized_distances = gaussian_filter(predicted_distances.astype(np.float32), sigma=3.0)/255.0
    normalized_distances -= 126/255.0
    normalized_distances[normalized_distances<0] = 0
    normalized_distances /= 129/255.0
    return normalized_distances

def blockwise_segmentation_function(array_in, roi, thresholds, quantile):
	#Materialize region of interest
	predicted_distances = array_in.to_ndarray(roi, fill_value=0)

	#Normalizing distances
	normalized_distances = normalize_distances(predicted_distances)
	predicted_distances = None

    #Find seeds
	seeds = find_seeds(normalized_distances)

	#Watershed fragments
	fragments = watershed(-normalized_distances, seeds, mask = (normalized_distances.astype(bool))).astype(np.uint64)

	#Creating affinity arrays
	affs = np.stack([normalized_distances.data]*3)

	#Agglolmerate
	agglomeration = []
	for s in waterz.agglomerate(
	    affs=affs,
	    fragments=fragments,
	    thresholds=[thresholds],
	    scoring_function = 1 - waterz.QuantileAffinity(quantile, init_with_max=False)):
		agglomeration = s

	return agglomeration

def blockwise_save_watershed_fragments_function(array_in, roi):
	#Materialize region of interest
	predicted_distances = array_in.to_ndarray(roi, fill_value=0)

	#Normalizing distances
	normalized_distances = normalize_distances(predicted_distances)
	predicted_distances = None

	#Find seeds
	seeds = find_seeds(normalized_distances)

	#Watershed fragments
	fragments = watershed(-normalized_distances, seeds, mask = (normalized_distances.astype(bool))).astype(np.uint64)

	return fragments

def blockwise_segmentation_function_using_contact_area(array_in, roi, thresholds, quantile):
	#Materialize region of interest
	predicted_distances = array_in.to_ndarray(roi, fill_value=0)

	#Normalizing distances
	normalized_distances = normalize_distances(predicted_distances)
	predicted_distances = None

    #Find seeds
	seeds = find_seeds(normalized_distances)

	#Watershed fragments
	fragments = watershed(-normalized_distances, seeds, mask = (normalized_distances.astype(bool))).astype(np.uint64)

	#Creating affinity arrays
	normalized_distances/=20 #divide by 20 since that is maximum, https://www.wolframalpha.com/input/?i=%28%28128*tanh%28sqrt%281%2Fpi%29%2F12.5%29%2B127%29-126%29%2F129
	affs = np.stack([normalized_distances.data]*3) 
	#print(f"maximum: {np.amax(normalized_distances)}")
	#Agglolmerate
	agglomeration = []
	for s in waterz.agglomerate(
	    affs=affs,
	    fragments=fragments,
	    thresholds=[thresholds],
	    #max is 20: https://www.wolframalpha.com/input/?i=%28%28128*tanh%28sqrt%281%2Fpi%29%2F12.5%29%2B127%29-126%29%2F129
	    scoring_function = 1.0 - waterz.QuantileAffinity(quantile, init_with_max=False)/np.tanh( waterz.ContactArea())):
		agglomeration = s

	return agglomeration
