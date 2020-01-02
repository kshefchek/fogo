### Classification of upper ontology terms

As a first test we aim to create to a multilabel classifier of the
upper ontology terms in Upheno:

    'UBERON:0001434PHENOTYPE': 'Skeletal system',
    'UBERON:0002101PHENOTYPE': 'Limbs',
    'UBERON:0001016PHENOTYPE': 'Nervous system',
    'UBERON:0007811PHENOTYPE': 'Head or neck',
    'MP:0005376': 'Metabolism/homeostasis',
    'UBERON:0004535PHENOTYPE': 'Cardiovascular system',
    'UBERON:0002416PHENOTYPE': 'Integument',
    'UBERON:0004122PHENOTYPE': 'Genitourinary system',
    'UBERON:0000970PHENOTYPE': 'Eye',
    'UBERON:0001015PHENOTYPE': 'Musculature',
    'MPATH:218PHENOTYPE': 'Neoplasm',
    'UBERON:0001007PHENOTYPE': 'Digestive system',
    'UBERON:0002405PHENOTYPE': 'Immune system',
    'UBERON:0002390PHENOTYPE': 'Blood and blood-forming tissues',
    'UBERON:0000949PHENOTYPE': 'Endocrine',
    'UBERON:0001004PHENOTYPE': 'Respiratory system',
    'UBERON:0001690PHENOTYPE': 'Ear',
    'UBERON:0002384PHENOTYPE': 'Connective tissue',
    'UBERON:0000323PHENOTYPE': 'Prenatal development or birth',
    'GO:0040007PHENOTYPE': 'Growth',
    'CL:0000000PHENOTYPE': 'Cellular'

#### Project setup
    virtualenv venv -p /usr/bin/python3.7
    source venv/bin/activate
    pip install -r requirements.txt
    
##### Fetch data phenotype-go term associations from monarch solr
    scripts/pheno-to-go.py -p phenotypes.txt
    
##### Shuffle output
    shuf output.tsv > shuffled.tsv

##### For prototyping limit the annotations to some small number
    ./scripts/trim-output.sh ./phenotypes.txt ./output.tsv 600 >>trimmed.tsv

##### Integer encode data
    ./scripts/int-encode.py -a ../trimmed.tsv.gz -p phenotypes.txt -g ../go-terms.txt
