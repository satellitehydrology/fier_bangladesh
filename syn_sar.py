import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras import models
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors

root_output_folder = 'Bangladesh/'

def tpc_predict(site, mode, value):
    tpc_mode = 'TF_model/site-%s_tpc%s'%(str(site), str(mode).zfill(2))

    in_model = models.load_model(root_output_folder + tpc_mode)

    return in_model.predict([value])[0][0]

def synthesize_sar(site, value,):

    sm_mode = 'RSM/%s/RSM_hydro.nc'%(site)
    RSM = xr.open_dataset(root_output_folder + sm_mode)

    for ct_mode in range(len(RSM.mode.values)):
        sm = RSM.spatial_modes.values[:,:,ct_mode]
        est_tpc = tpc_predict(site, ct_mode + 1, value)
        if ct_mode==0:
            syn_sar = sm*est_tpc
        else:
            syn_sar = syn_sar + sm*est_tpc

    all_meanVV_dir = 'stats_img/%s/all_meanVV.nc'%(site)
    all_meanVV = xr.open_dataset(root_output_folder + all_meanVV_dir)
    all_meanVV = all_meanVV.to_array().values[0,:,:]
    syn_sar = syn_sar + all_meanVV

    # Z-score
    zscore_threshold = -3

    dry_meanVV_dir = 'stats_img/%s/dry_meanVV.nc'%(site)
    dry_meanVV = xr.open_dataset(root_output_folder + dry_meanVV_dir)
    dry_meanVV = dry_meanVV.to_array().values[0,:,:]

    dry_stdVV_dir = 'stats_img/%s/dry_stdVV.nc'%(site)
    dry_stdVV = xr.open_dataset(root_output_folder + dry_stdVV_dir)
    dry_stdVV = dry_stdVV.to_array().values[0,:,:]

    z_score_img = (syn_sar-dry_meanVV)/dry_stdVV

    # Inundation Map

    # aoi_indx = np.argwhere(~np.isnan(dry_meanVV))
    water_indx = np.argwhere( z_score_img < zscore_threshold )
    water_map = np.zeros((syn_sar.shape[0], syn_sar.shape[1]))
    # water_map[aoi_indx[:,0], aoi_indx[:,1]] = 0
    water_map[water_indx[:,0], water_indx[:,1]] = 1

    # water_map = z_score_img.copy()
    # water_map[z_score_img < zscore_threshold] = 1
    # water_map[z_score_img >= zscore_threshold] = 0

    return syn_sar, z_score_img, water_map

def image_output(site, value):

    folder_name = 'output/' + site + '_%.2f'%(value)
    if not os.path.isdir(folder_name):
        os.makedirs(folder_name)
        sar_image, z_score_image, water_map_image = synthesize_sar(site, round(value,3))

        fig = plt.imshow(sar_image, cmap='gray')
        plt.axis('off')
        plt.savefig(folder_name +'/syn_sar.png', bbox_inches='tight', dpi=300, pad_inches = 0)

        fig = plt.imshow(z_score_image, cmap='jet', vmin=-3, vmax=3, interpolation='None')
        plt.savefig(folder_name +'/z_score.png', bbox_inches='tight', dpi=300, pad_inches = 0)
        print('Created', folder_name)

        water_cmap =  matplotlib.colors.ListedColormap(["silver","darkblue"])
        fig = plt.imshow(water_map_image, cmap = water_cmap)
        plt.clim(vmin=-0.5, vmax=1.5)
        plt.axis('off')
        plt.savefig(folder_name +'/water_map.png', bbox_inches='tight', dpi=300, interpolation='None', pad_inches = 0)

    else:
        print(folder_name,'existed')

    return folder_name #Directory of Synthesize Image
