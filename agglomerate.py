import waterz
import daisy
import numpy as np
from scipy import ndimage

test_roi = daisy.Roi((0, 0, 0), (501, 501, 501))
test_file = 'test_mito.n5'
fragments_ds = 'actual_fragments'
dist_max_ds = 'actual_dist_max'
thresholds = [0.01, 0.05, 0.1, 0.2, 0.3]

if __name__ == '__main__':
    print("Reading fragments and distances...")
    fragments = daisy.open_ds(test_file, fragments_ds)[test_roi]
    dist_max = daisy.open_ds(test_file, dist_max_ds)[test_roi]
    fragments.materialize()
    dist_max.materialize()

    print("Creating affinity arrays...")
    affs = np.stack([dist_max.data]*3)
    print(f"{affs.shape}")

    print("Agglomerating...")
    inverted_thresholds = 1.0 - np.array(thresholds)
    for s, t in zip(waterz.agglomerate(
        affs=affs,
        fragments=fragments.data,
        thresholds=inverted_thresholds), thresholds):

        print("Storing segmentation...")
        segmentation_ds = daisy.prepare_ds(
            test_file,
            'actual_segmentation_%.3f'%t,
            total_roi=fragments.roi,
            voxel_size=fragments.voxel_size,
            dtype=np.uint64)
        segmentation_ds[test_roi] = s
