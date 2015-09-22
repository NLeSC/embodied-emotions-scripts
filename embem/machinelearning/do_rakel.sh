#!/bin/bash
# Run all RAKEL experiments

echo "HEEM Complete"
python embem/machinelearning/rakel_clf.py /home/jvdzwaan/data/embem_ml/multilabel/ /tmp/home/jvdzwaan/data/ml/rakel/multilabel/
python embem/machinelearning/rakel_clf.py /home/jvdzwaan/data/embem_ml/multilabel-normalized/ /tmp/home/jvdzwaan/data/ml/rakel/multilabel-normalized/

echo "HEEM basic emotions"
python embem/machinelearning/rakel_clf.py /home/jvdzwaan/data/embem_ml/heem_basic/ /tmp/home/jvdzwaan/data/ml/rakel/basic/
python embem/machinelearning/rakel_clf.py /home/jvdzwaan/data/embem_ml/heem_basic-normalized/ /tmp/home/jvdzwaan/data/ml/rakel/basic-normalized/

echo "Posneg"
python embem/machinelearning/rakel_clf.py /home/jvdzwaan/data/embem_ml/posneg/ /tmp/home/jvdzwaan/data/ml/rakel/posneg/
python embem/machinelearning/rakel_clf.py /home/jvdzwaan/data/embem_ml/posneg-normalized/ /tmp/home/jvdzwaan/data/ml/rakel/posneg-normalized/ 
