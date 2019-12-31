#!/usr/bin/env python3

"""pheno-to-go.py

Script for pulling phenotype to go term associations by joining
gene to phenotype and gene to gene function associations

Outputs a three column file in the format:
HP:1,HP:2   Gene:1    GO:1,GO:2,GO:3
HP:2,HP:3   Gene:2    GO:1,GO:4,GO:5

Prints summary statistics:
GO profiles per class,
Maximum length GO profile for a class for zero padding downstream
"""

import argparse
import requests

solr = "https://solr-dev.monarchinitiative.org/solr/golr/select/"

parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--phenotypes', '-p', type=str, required=True,
                    help='List of phenotypes')
parser.add_argument('--annotations', '-a', required=False,
                    default="./output.tsv", help='output annotations file')
parser.add_argument('--go', '-g', required=False,
                    default="./go-terms.tsv", help='output unique set of go terms')
args = parser.parse_args()

max_profile = 0
counter = 0
class_stats = {}
output_fh = open(args.annotations, 'w')
go_fh = open(args.go, 'w')
all_go = set()

gene_dict = {}

# Iterate over phenotype classes and fetch GO profiles
with open(args.phenotypes, 'r') as input_file:
    for phenotype in input_file:
        phenotype = phenotype.rstrip()
        class_stats[phenotype] = 0

        # Fetch associated genes
        params = {
            'wt': 'json',
            'rows': 0,
            'facet': 'true',
            'facet.mincount': 1,
            'facet.limit': 100000,
            'facet.field': 'subject',
            'json.nl': 'arrarr',
            'q': '*:*',
            'fq': [
                'association_type:gene_phenotype',
                'object_closure:"{}"'.format(phenotype),
            ],
        }
        req = requests.get(solr, params)
        resp = req.json()

        for gene_facet in resp['facet_counts']['facet_fields']['subject']:
            gene = gene_facet[0]
            if gene in gene_dict:
                gene_dict[gene][0].add(phenotype)
                class_stats[phenotype] += 1
                continue

            gene_dict[gene] = [{phenotype}]

            counter += 1
            go_profile = set()
            has_go = False

            # Fetch associated genes
            params = {
                'wt': 'json',
                'rows': 0,
                'facet': 'true',
                'facet.mincount': 1,
                'facet.limit': 100000,
                'facet.field': 'object_closure',
                'json.nl': 'arrarr',
                'q': '*:*',
                'fq': [
                    'association_type:gene_function',
                    'subject:"{}"'.format(gene),
                ],
            }

            req = requests.get(solr, params)
            resp = req.json()

            for go_facet in resp['facet_counts']['facet_fields']['object_closure']:
                if go_facet[0].startswith('GO'):
                    has_go = True
                    go_profile.add(go_facet[0])
                    all_go.add(go_facet[0])

            if has_go:
                class_stats[phenotype] += 1
                gene_dict[gene].append(go_profile)

                if len(go_profile) > max_profile:
                    max_profile = len(go_profile)

            if counter != 0 and counter % 1000 == 0:
                print("processed {} genes".format(counter))

print("processed {} genes".format(counter))

print(class_stats)
print(max_profile)

for gene, data in gene_dict.items():
    if len(data) > 1:
        output_fh.write("{}\t{}\t{}\n".format(gene, ','.join(data[0]), ','.join(data[1])))

for go in all_go:
    go_fh.write("{}\n".format(go))

go_fh.close()
output_fh.close()
