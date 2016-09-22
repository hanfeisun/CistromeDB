# CistromeDB

A new portal to browser public ChIP-seq and DNase-seq datasets. 
Besides providing a comprehensive knowledgebase of all of the publicly 
available ChIP-Seq and DNase-Seq data in mouse and human, it also provides 
functions to analysis and visualize these datasets.

## Notes

This is a snapshot of an old-version of CistromeDB. The latest version 
of CistromeDB is served at cistrome.org/db and under internal development.

## Text mining

The text mining module locates at ncbiAdapter folder, which contains two features

* Rule-based text-mining is used to extract and normalize terms from GEO metadata - [link](https://github.com/hanfeisun/CistromeDB/blob/newdc/ncbiAdapter/geo.py)
* Naive Bayes classifier is used to classify samples into categories - [link](https://github.com/hanfeisun/CistromeDB/tree/newdc/ncbiAdapter/classifiers)
