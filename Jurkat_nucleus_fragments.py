from blockwise_segmentation_function import *
import funlib.segment.arrays as fsa
import argparse

input_file = '/nrs/cosem/cosem/training/v0003.2/setup35/Jurkat_Cell1_4x4x4nm/Jurkat_Cell1_FS96-Area1_4x4x4nm_it600000.n5'
output_file = '/groups/cosem/cosem/ackermand/Jurkat_Cell1_4x4x4nm_setup35_it600000_results.n5'
dataset = 'nucleus'

if __name__ == '__main__':

	array_in = daisy.open_ds(input_file, dataset)

	array_out = daisy.prepare_ds(output_file,
								f'{dataset}_smoothed_fragments',
								array_in.roi,
								voxel_size = array_in.voxel_size,
								write_size= [180*4, 180*4, 180*4],
								dtype = np.uint64)

	fsa.segment_blockwise(array_in,
						   array_out,
						   block_size = [180*4,180*4,180*4],
						   context = (200,200,200),
						   num_workers = 48,
						   segment_function = lambda array_in,roi: blockwise_save_watershed_fragments_function(array_in, roi))
