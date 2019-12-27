#!/usr/bin/env python3
"""
Integer encodes both profiles (go terms) and input classes (phenotypes)
"""

import argparse
import logging
import gzip
import numpy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--annotations', '-a', type=str, required=True,
                    help="Gzipped three column annotation file from pheno-to-go.py")
parser.add_argument('--go', '-g', type=str, required=True,
                    help="Text file containing go classes, line number will "
                         "become it's integer encoding")
parser.add_argument('--max', '-m', type=int, required=False,
                    help="Length of the longest profile for zero padding",
                    default=1075)

parser.add_argument('--output', '-o', type=str, required=False,
                    help="Location of output file, npz in batch mode, npy otherwise",
                    default="./go-encoded.npz")
parser.add_argument('--label', '-l', type=str, required=False,
                    help="Location of output label file",
                    default="./labels.txt")


args = parser.parse_args()

output_labels = open(args.label, 'w')

go_terms = []
word_matrix = []

count = 0
index = 0

with open(args.go, 'r') as go_file:
    for line in go_file:
        go_terms.append(line.rstrip())

with gzip.open(args.annotations, 'rb') as annotations:
    for line in annotations:
        line = line.decode()
        if line.startswith('#'): continue
        phenotype, gene, functions = line.rstrip("\n").split("\t")[0:3]
        go_profile = functions.split(",")
        phenotype_profile = set()

        word_vec = \
            [go_terms.index(func) for func in go_profile if func in go_terms]

        word_matrix.append(numpy.array(word_vec, dtype=numpy.uint16))
        count += 1
        index += 1
        output_labels.write("{}\n".format(phenotype))

        if count % 1000 == 0:
            logger.info("Converted {} profiles to integers".format(count))


# similar to keras.preprocessing.sequence.pad_sequences
padded = numpy.zeros([len(word_matrix), args.max], dtype=numpy.uint16)

for index, value in enumerate(word_matrix):
    padded[index][0:len(value)] = value

numpy.save(args.output, numpy.array(padded, dtype=numpy.uint16))

output_labels.close()

logger.info("Converted {} profiles to integers".format(count))
