# Vulnerabilities in Reused Software
This repository contains the necessary scripts in order to build a dataset of open-source projects and analyze how their reuse characteristics are related to their security vulnerabiltities.

For the ICSR'19 paper version of this dataset checkout the ```icsr19``` branch.

This document presents:
- [Folder structure](#folders)
- [Setting up study environment](#setup)
- [Steps for data collection](#data_collection)
- [Steps for analysis](#data_analisis)

<a id="folders"></a>
## Folder structure
This repository consists of two main directories: 
- _data_: stores all files that will be analyzed
- _tooling_: stores all scripts for building and analyzing the dataset

<a id="setup"></a>
## Setting up study environment

The analysis was performed using the following tools:
- Linux Mint (v 19.3)
- Python (v 3)
- Anaconda (v. 4.5.12)
- Java (v > 8)
- Maven (v. 3.6)

### Steps to set up study environment
1. Install Anaconda
2. From a terminal, create a conda environment for the study.
```sh
$ conda create -n study-env
$ conda activate study-env
```
3. From a terminal, install the necessary packages.
```sh
$ conda install -c conda-forge notebook maven xmltodict numpy scipy pandas matplotlib seaborn
```
4. Now, from a terminal, execute the 
```sh
$ tooling/download-vendor-tools.sh
```
5. Next, open the ```tooling/script.py``` and replace the ```STUDY_HOME``` path variable with the path of your locally 
cloned repository.

6. Finally, create a ```JAVA_HOME``` system variable and export to the ```PATH```. See more instructions [here](https://stackoverflow.com/a/24641640).

<a id="data_collection"></a>
## Steps for data collection
The steps for the data collection are described in the ```tooling/DataCollection.ipynb``` and ```tooling/DataCollectionRQ3.ipynb``` jupyter notebooks. 
More specific instruction for each substep are included before each substep.

<a id="data_analisis"></a>
## Steps for analysis
The steps for the data analysis are described in the ```tooling/DataVisualization.ipynb``` jupyter notebook. 
The execution of the steps is linear, and thus it should be executed from the top to the bottom. 
Analyzing the dataset requires a local Maven ```.m2``` directory which have all built projects and their dependencies ```jars```. 

An additional notebook for analysis is available in the ```tooling/ExtraAnalysis.ipynb``` jupyter notebook.
This script provide statistical information related to the most common vulnerability types as reported by Spotbugs




