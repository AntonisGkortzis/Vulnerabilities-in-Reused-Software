# ICSR '19 - Gkortzis et al. - Data Analysis

This document presents:
- [Folder structure](#folders)
- [Setting up study environment](#setup)
- [Steps for data collection](#data_collection)
- [Steps for analysis](#data_analisis)

<a id="folders"></a>
## Folder structure


<a id="setup"></a>
## Setting up study environment

The analysis was performed using the following tools:
- Anaconda (v. 4.5.12)
- maven (v. 3.6)

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
4. Next, from a terminal, execute the 
```sh
$ tooling/download-vendor-tools.sh
```
5. Finally, open the ```tooling/script.py``` and replace the ```STUDY_HOME``` path variable with the path of your locally 
cloned repository.

<a id="data_collection"></a>
## Steps for data collection
The steps for the data collection are described in the ```tooling/DataCollection.ipynb``` jupyter notebook. 
More specific instruction for each substep are included before each substep.

<a id="data_analisis"></a>
## Steps for analysis
The steps for the data analysis are described in the ```tooling/DataVisualization.ipynb``` jupyter notebook. 
The execution of the steps is linear, and thus it should be executed from the top to the bottom. 

An additional notebook for analysis is available in the ```tooling/ExtraAnalysis.ipynb``` jupyter notebook.
This script provide statistical information related to the most common vulnerability types as reported by Spotbugs




