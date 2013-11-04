from flycrow.xilinx.xc2000_dumper import *
import argparse		


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Dump old format Xilinx bitstream to raw bit (RBT) format')
	parser.add_argument('input')
	parser.add_argument('--verbose', action='store_true')
	parser.add_argument('--prefix', action='store_true')
	parser.add_argument('--core', action='store_true')
	args = parser.parse_args()
	options = Options()
	options.verbose = args.verbose
	options.prefix = args.prefix
	options.core = args.core
	dumper = BitstreamDumper(open(args.input).read(), options=options)
	dumper.dump()

