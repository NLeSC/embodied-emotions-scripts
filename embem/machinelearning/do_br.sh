#!/bin/bash
# Run all BR experiments

echo "HEEM Complete"
python embem/machinelearning/br_classifier.py /home/jvdzwaan/data/embem_ml/multilabel/ /home/jvdzwaan/data/ml/br/multilabel/
python embem/machinelearning/br_classifier.py /home/jvdzwaan/data/embem_ml/multilabel-normalized/ /home/jvdzwaan/data/ml/br/multilabel-normalized/

echo "HEEM basic emotions"
python embem/machinelearning/br_classifier.py /home/jvdzwaan/data/embem_ml/heem_basic/ /home/jvdzwaan/data/ml/br/basic/
python embem/machinelearning/br_classifier.py /home/jvdzwaan/data/embem_ml/heem_basic-normalized/ /home/jvdzwaan/data/ml/br/basic-normalized/

echo "Posneg"
python embem/machinelearning/br_classifier.py /home/jvdzwaan/data/embem_ml/posneg/ /home/jvdzwaan/data/ml/br/posneg/
python embem/machinelearning/br_classifier.py /home/jvdzwaan/data/embem_ml/posneg-normalized/ /home/jvdzwaan/data/ml/br/posneg-normalized/
