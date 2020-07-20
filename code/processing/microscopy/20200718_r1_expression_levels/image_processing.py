# %%
import os
import git
import glob

# Our numerical workhorses
import numpy as np
import pandas as pd
import scipy.special

# Useful plotting libraries
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
import seaborn as sns

# Image analysis libraries
import skimage.io
import skimage.filters
import skimage.segmentation
import scipy.ndimage

# Import package for project
import fit_seq

# Set plotting style
# mpl.use('Agg')
fit_seq.viz.pboc_style_mpl()

# Save it to the output file
if not os.path.exists('./output'):  # Check if directyr exists
    os.mkdir('./output')  # Generate directory if required

# %%

# Define username
USERNAME = "mrazomej"
# Define interpixel distance
IPDIST = 0.065  # µm / pixel

# List promoters
prom = ["auto", "lacUV5", "WTlac", "3.19kBT"]
# List volume markers
vmark = ["mCherry", "CFP"]

# Find home directory for repo
repo = git.Repo("./", search_parent_directories=True)
homedir = repo.working_dir

# Find date
workdir = os.getcwd().split('/')[-1]
DATE = int(workdir.split('_')[0])

# Define the data directory.
datadir = f'{homedir}/data/microscopy/{DATE}/'

# Glob images.
files = glob.glob(f'{datadir}*.tif')

# %%

# Initialize dataframe to save segmentation output
df = pd.DataFrame([])

# Select random image for segmentation example
ex_im = np.random.choice(files)

# Loop through unique promoters
for i, p in enumerate(prom):
    # Loop through unique volume markers
    for j, v in enumerate(vmark):
        print(f"{p} - {v}")
        # List files
        flist = glob.glob(f"{datadir}*{p}*{v}*.tif")
        print(f"number of files: {len(flist)}")

        # Loop through images
        for f in flist:
            # Read image
            im = skimage.io.imread(f)
            # List all images with 1) BF, 2) YFP, 3) Volume marker
            bf = im[:, :, 0]
            yfp = im[:, :, 1]
            vol = im[:, :, 2]

            # Segment the volume marker channel.
            vol_seg = fit_seq.image.log_segmentation(
                vol, thresh=1E-5, label=True
            )

            # Print example segmentation for the random image
            if f == ex_im:
                print(f)
                merge = fit_seq.image.example_segmentation(
                    vol_seg, bf, 10/IPDIST
                )
                skimage.io.imsave('./output/example_segmentation.png', merge)

            # Extract the measurements.
            try:
                im_df = fit_seq.image.props_to_df(
                    vol_seg, physical_distance=IPDIST, intensity_image=yfp,
                )
            except ValueError:
                break

            # Add information to dataframe
            im_df = im_df.assign(
                date=[DATE] * len(im_df),
                username = [USERNAME] * len(im_df),
                promoter=[p] * len(im_df),
                volume_marker = [v] * len(im_df),
            )
            # Append to DataFrame
            df = pd.concat([df, im_df], ignore_index=True)

# Concatenate the dataframe
df.to_csv(f'./output/{DATE}_raw_segmentation.csv', index=False)

# %%
