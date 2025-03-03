# bids_fastsurfer

Tool to create appropriate docker command to run fastsurfer from a BIDS dataset.
Also ensure resolution is not too small for fastsurfer memory requirement. If too small (<1mm), resample the data first.

This is a BIDS app, so it complies with the command line call structure: `bids_fastsurfer bids_dir derivatives_dir participant`. See Usage below for details.

# Usage

## Example: singularity, full pipeline

```bash
git clone git@github.com:ln2t/bids_fastsurfer.git
cd bids_fastsurfer
source venv/bin/activate
pip install -r requirements.txt
python bids_fastsurfer.py /path/to/BIDS/dataset /path/to/output/folder/bids_fastsurfer participant --participant_label 42 --singularity
```
This will output a bash command to call singularity.
Ensure the path to the singularity image is correct. A part from that, is it ready to run.

## Example: singularity, segmentation only

```bash
git clone git@github.com:ln2t/bids_fastsurfer.git
cd bids_fastsurfer
source venv/bin/activate
pip install -r requirements.txt
python bids_fastsurfer.py /path/to/BIDS/dataset /path/to/output/folder/bids_fastsurfer participant --participant_label 42 --singularity --seg_only
```
This will output a bash command to call singularity.
Ensure the path to the singularity image is correct. A part from that, is it ready to run.
## Example: docker, full pipeline

```bash
git clone git@github.com:ln2t/bids_fastsurfer.git
cd bids_fastsurfer
source venv/bin/activate
pip install -r requirements.txt
python bids_fastsurfer.py /path/to/BIDS/dataset /path/to/output/folder/bids_fastsurfer participant --participant_label 42 --docker
```
This will output a bash command calling docker, with all paths and arguments already nice and ready to run.

## Example: docker, segmentation only

```bash
git clone git@github.com:ln2t/bids_fastsurfer.git
cd bids_fastsurfer
source venv/bin/activate
pip install -r requirements.txt
python bids_fastsurfer.py /path/to/BIDS/dataset /path/to/output/folder/bids_fastsurfer participant --participant_label 42 --docker --seg_only
```
This will output a bash command calling docker, with all paths and arguments already nice and ready to run.


