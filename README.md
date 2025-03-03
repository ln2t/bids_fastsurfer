# bids_fastsurfer

Tool to create appropriate docker command to run fastsurfer from a BIDS dataset.
Also ensure resolution is not too small for fastsurfer memory requirement. If too small (<0.5mm), resample the data first (see Warning below).

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



# WARNING

FastSurfer for images of very high spatial resolution (<0.5mm) might crash due to GPU-memory issues. To circumvent this, bids_fastsurfer checks that the resolution in each direction is larger than 0.5mm. If not, it will **downsample** the data, which irremediably destroy information. Make sure you understand what this mean before using this tool.
The downsampled data are stored in derivatives_dir/sourcedata and have the `_resampled` suffix.
