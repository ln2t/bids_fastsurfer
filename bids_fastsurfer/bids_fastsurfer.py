import os.path
from bids import BIDSLayout
from pathlib import Path
import argparse
import json
import nibabel as nib
import numpy as np
import warnings

from nilearn.image import resample_img

def make_parent_dir(file_path):
    """
    Ensure that the directory for a given file path exists.
    If it does not exist, create it.

    Args:
    file_path (str): The full path to the file, including the filename.

    Example:
    ensure_directory("/path/to/my/directory/filename.txt")
    """
    Path(file_path).parents[0].mkdir(exist_ok=True, parents=True)


def write_dataset_description(output_dir):
    """
    Create the dataset_description.json file, mandatory if outputs are to be indexed by BIDSLayout.
    """
    description = {
        "Name": "bids_fastsurfer",
        "BIDSVersion": "1.6.0",
        "PipelineDescription": {
            "Name": "bids_fastsurfer",
            "Version": "1.0.0",
            "CodeURL": "https://github.com/ln2t/bids_fastsurfer"
        }
    }
    dataset_description_path = os.path.join(output_dir, "dataset_description.json")
    make_parent_dir(dataset_description_path)
    with open(dataset_description_path, 'w') as f:
        json.dump(description, f, indent=4)


def ensure_min_resolution(image_path, derivatives_dir, target_resolution=(0.5, 0.5, 0.5)):
    # Load the NIfTI image
    img = nib.load(image_path)

    # Get the current resolution from the affine matrix
    affine = img.affine
    zooms = np.sqrt(np.sum(affine[:3, :3] ** 2, axis=0))

    # Check if any dimension has a resolution below the target resolution
    if np.any(zooms < target_resolution):
        # Calculate the new affine matrix for the target resolution
        new_zooms = np.maximum(zooms, target_resolution)
        scale_factor = new_zooms / zooms
        new_affine = np.copy(affine)
        new_affine[:3, :3] = affine[:3, :3] @ np.diag(scale_factor)

        # Resample the image to the new resolution
        warnings.warn("Images are being resampled to decrease resolution. This will deteriorate the quality of your images!")
        img_resampled = resample_img(img, target_affine=new_affine, interpolation='continuous', force_resample=True)

        # Copy the header from the original image to the resampled image
        img_resampled_with_header = nib.Nifti1Image(img_resampled.get_fdata(), img_resampled.affine, header=img.header)

        # Save the resampled image with the original header
        output_path = os.path.join(derivatives_dir, "sourcedata", os.path.basename(image_path).replace('.nii', '_resampled.nii'))
        make_parent_dir(output_path)
        nib.save(img_resampled_with_header, output_path)
        print(f"Image resampled and saved to {output_path}")
    else:
        output_path = image_path

    return output_path


parser = argparse.ArgumentParser(
        description="bids_fastsurfer: tool to run fastsurfer on a BIDS dataset")
parser.add_argument("bids_dir", type=str, help="BIDS root directory containing the dataset.")
parser.add_argument("derivatives_dir", type=str, help="Directory for the outputs.")
parser.add_argument("analysis_level", nargs="?", choices=["participant", "group"],
                        help="Analysis level: either 'participant' or 'group'.")
parser.add_argument("--participant_label", nargs="?", help="Subjects to process (e.g. 01)")
parser.add_argument("--fs_license", nargs="?", help="Path to the FreeSurfer license")
parser.add_argument("--docker", help="Output the docker command", action="store_true")
parser.add_argument("--singularity", help="Output the singularity command", action="store_true")
parser.add_argument("--seg_only", help="Only perform segmentation (no surface is reconstructed)", action="store_true")

args = parser.parse_args()

print("Indexing BIDS dataset...")
layout = BIDSLayout(args.bids_dir)
write_dataset_description(args.derivatives_dir)
layout.add_derivatives(args.derivatives_dir)

if args.participant_label not in layout.get_subjects():
    raise ValueError(f"Invalid participant label {args.participant_label}. Detected subjects: {layout.get_subjects()}")
elif type(args.participant_label) == list:
    if not len(args.participant_label) == 1:
        raise ValueError(f"Only one participant_label is currently supported.")

if args.fs_license and not args.seg_only:
    if not os.path.isfile(args.fs_license):
        raise FileNotFoundError(f"License file {args.fs_license} not found.")
    else:
        fs_license_dir = os.path.dirname(args.fs_license)
        fs_license_file = os.path.basename(args.fs_license)

try:
    anat_path = layout.get(return_type="filename", subject=args.participant_label, space=None, suffix="T1w", extension=".nii.gz")[0]
except:
    FileNotFoundError(f"Anatomical images not found for subject {args.participant_label}")

anat_path = ensure_min_resolution(anat_path, args.derivatives_dir)
anat_dir = os.path.dirname(anat_path)
anat_file = os.path.basename(anat_path)

if args.docker:
    if args.seg_only:
        docker_cmd = f"sudo docker run --gpus all -v {anat_dir}:/data -v {args.derivatives_dir}:/output --rm --user $(id -u):$(id -g) deepmi/fastsurfer:latest --t1 /data/{anat_file} --asegdkt_segfile /output/sub-{args.participant_label}/aparc.DKTatlas+aseg.deep.mgz --conformed_name /output/sub-{args.participant_label}/conformed.mgz --sd /output --sid sub-{args.participant_label} --seg_only --3T --threads 2"
    else:
        docker_cmd = f"sudo docker run --gpus all -v {anat_dir}:/data -v {args.derivatives_dir}:/output -v {fs_license_dir}:/fs_license --rm --user $(id -u):$(id -g) deepmi/fastsurfer:latest --fs_license /fs_license/{fs_license_file} --t1 /data/{anat_file} --sid sub-{args.participant_label} --sd /output --3T --threads 2"

    print("======================== Docker Command ========================")
    print(docker_cmd)

if args.singularity:
    singularity_sif_path = "fastsurfer-gpu.sif"
    if not os.path.isfile(singularity_sif_path):
        print("Make sure to adapt the path to the singularity image")

    if args.seg_only:
        singularity_cmd = f"singularity exec --nv --no-home -B {anat_dir}:/data -B {args.derivatives_dir}:/output {singularity_sif_path} /fastsurfer/run_fastsurfer.sh --t1 /data/{anat_file} --asegdkt_segfile /output/sub-{args.participant_label}/aparc.DKTatlas+aseg.deep.mgz --conformed_name /output/sub-{args.participant_label}/conformed.mgz --sd /output --sid sub-{args.participant_label} --seg_only --3T --threads 2"
    else:
        singularity_cmd = f"singularity exec --nv --no-home -B {anat_dir}:/data -B {args.derivatives_dir}:/output -B {fs_license_dir}:/fs_license {singularity_sif_path} /fastsurfer/run_fastsurfer.sh --fs_license /fs_license/{fs_license_file} --t1 /data/{anat_file} --sid sub-{args.participant_label} --sd /output --3T --threads 2"

    print("===================== Singularity Command ======================")
    print(singularity_cmd)