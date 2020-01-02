#!/usr/bin/env python3
"""
Integer encodes both profiles (go terms) and input classes (phenotypes)
"""

import argparse
import logging
import gzip
import numpy
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--annotations', '-a', type=str, required=True,
                    help="Gzipped three column annotation file from pheno-to-go.py")
parser.add_argument('--go', '-g', type=str, required=True,
                    help="Text file containing go classes, line number will "
                         "become its integer encoding")
parser.add_argument('--phenotype', '-p', type=str, required=True,
                    help="Text file containing phenotypes classes, line number will "
                         "become its integer encoding")
parser.add_argument('--max', '-m', type=int, required=False,
                    help="Length of the longest profile for zero padding",
                    default=1075)
parser.add_argument('--validation', '-v', type=int, required=False,
                    help="number of samples to use for validation, takes the from the top",
                    default=100)
parser.add_argument('--output', '-o', type=str, required=False,
                    help="Location of output directory",
                    default="./output/")


args = parser.parse_args()

outpath = Path(args.output)
outpath.mkdir(parents=True, exist_ok=True)

output_labels = outpath / 'labels.npy'
validation_labels = outpath / 'validation-labels.npy'
output_encodings = outpath / 'go-encoded.npy'
validation_encodings = outpath / 'validation.npy'

go_terms = []
pheno_terms = []

wordvec_labels = []
wordvec_matrix = []
valid_labels = []
validation_matrix = []

count = 0

with open(args.go, 'r') as go_file:
    for line in go_file:
        go_terms.append(line.rstrip())

with open(args.phenotype, 'r') as pheno_file:
    for line in pheno_file:
        pheno_terms.append(line.rstrip())

with gzip.open(args.annotations, 'rb') as annotations:
    for line in annotations:
        line = line.decode()
        if line.startswith('#'): continue
        gene, phenotypes, functions = line.rstrip("\n").split("\t")[0:3]
        go_profile = functions.split(",")
        phenotype_profile = phenotypes.split(",")

        word_vec = \
            [go_terms.index(func) for func in go_profile if func in go_terms]

        bitset = [1 if feature in phenotype_profile else 0 for feature in pheno_terms]

        if count < args.validation:
            validation_matrix.append(numpy.array(word_vec, dtype=numpy.uint16))
            valid_labels.append(numpy.array(bitset, dtype=numpy.uint8))

        else:
            wordvec_matrix.append(numpy.array(word_vec, dtype=numpy.uint16))
            wordvec_labels.append(numpy.array(bitset, dtype=numpy.uint8))

        count += 1

        if count % 1000 == 0:
            logger.info("Converted {} profiles to integers".format(count))


numpy.save(validation_labels, numpy.array(valid_labels, dtype=numpy.uint8))
numpy.save(output_labels, numpy.array(wordvec_labels, dtype=numpy.uint8))

# similar to keras.preprocessing.sequence.pad_sequences
padded = numpy.zeros([len(wordvec_matrix), args.max], dtype=numpy.uint16)
padded_val = numpy.zeros([len(validation_matrix), args.max], dtype=numpy.uint16)

for index, value in enumerate(wordvec_matrix):
    padded[index][0:len(value)] = value

for index, value in enumerate(validation_matrix):
    padded_val[index][0:len(value)] = value

numpy.save(output_encodings, numpy.array(padded, dtype=numpy.uint16))
numpy.save(validation_encodings, numpy.array(padded_val, dtype=numpy.uint16))


logger.info("Converted {} profiles to integers".format(count))
