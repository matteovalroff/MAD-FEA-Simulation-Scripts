# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:40:26 2026

@author: matte
"""
import os
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__)) # Recuperation of the file's path
os.chdir(script_dir) # Change the working file to make sure we're in the right one

#========== X deformation tooth node file read ======================

# Upload the file
xdtooth = pd.read_csv("X_Directional_Deformation_Tooth.txt", sep=None, engine='python', decimal=",", dtype={"Node Number": int,"X Location (mm)": float,"Y Location (mm)": float,"Z Location (mm)": float,"Directional Deformation (mm)": float})

# Extraction of the column (xdipdl = X deformation tooth)

xdtooth_node_nb = xdtooth["Node Number"]    # Identification node number
xdtooth_node_posx = xdtooth["X Location (mm)"] # Node position X after displacement
xdtooth_node_posy  = xdtooth["Y Location (mm)"] # Node position Y after displacement
xdtooth_node_posz  = xdtooth["Z Location (mm)"] # Node position Z after displacement
xdtooth_x_deformation  = xdtooth["Directional Deformation (mm)"] #

#========== Y deformation tooth node file read ======================

# Upload the file
ydtooth = pd.read_csv("Y_Directional_Deformation_Tooth.txt", sep=None, engine='python', decimal=",", dtype={"Node Number": int,"X Location (mm)": float,"Y Location (mm)": float,"Z Location (mm)": float,"Directional Deformation (mm)": float})

# Extraction of the column (ydipdl = Y deformation tooth)

ydtooth_node_nb = ydtooth["Node Number"]    # Identification node number
ydtooth_node_posx = ydtooth["X Location (mm)"] # Node position X after displacement
ydtooth_node_posy  = ydtooth["Y Location (mm)"] # Node position Y after displacement
ydtooth_node_posz  = ydtooth["Z Location (mm)"] # Node position Z after displacement
ydtooth_y_deformation  = ydtooth["Directional Deformation (mm)"] #

#========== X deformation tooth node file read ======================

# Upload the file
zdtooth = pd.read_csv("Z_Directional_Deformation_Tooth.txt", sep=None, engine='python', decimal=",", dtype={"Node Number": int,"X Location (mm)": float,"Y Location (mm)": float,"Z Location (mm)": float,"Directional Deformation (mm)": float})

# Extraction of the column (zdipdl = Z deformation tooth)

zdtooth_node_nb = zdtooth["Node Number"]    # Identification node number
zdtooth_node_posx = zdtooth["X Location (mm)"] # Node position X after displacement
zdtooth_node_posy  = zdtooth["Y Location (mm)"] # Node position Y after displacement
zdtooth_node_posz  = zdtooth["Z Location (mm)"] # Node position Z after displacement
zdtooth_z_deformation  = zdtooth["Directional Deformation (mm)"] #


#========== Inner PDL node file read ======================

# Upload the file
tooth = pd.read_csv("tooth_nodes.txt", sep=None, engine='python', decimal=",", dtype={"Node Number": int,"X Location (mm)": float,"Y Location (mm)": float,"Z Location (mm)": float})

# Extraction of the column 

tooth_node_nb = tooth["Node Number"] # Identification node number
tooth_node_posx = tooth["X Location (mm)"] # Node position X coordinate
tooth_node_posy  = tooth["Y Location (mm)"] # Node position Y coordinate
tooth_node_posz  = tooth["Z Location (mm)"] # Node position Z coordinate

#========== Previous position file read ======================



# Upload the file
dit = pd.read_csv("disp_info_tab_tooth.txt", sep=None, engine='python', decimal=",", dtype={"Node Number": int,"New X position": float,"New Y position": float,"New Z position": float,"X displacement": float,"Y displacement": float,"Z displacement": float})

# Extraction of the column (dit = displacement information table)

dit_node_nb = dit["Node Number"]    # Identification node number
dit_node_posx = dit["New X position"] # Node position X coordinate (last iter)
dit_node_posy  = dit["New Y position"] # Node position Y coordinate (last iter)
dit_node_posz  = dit["New Z position"] # Node position Z coordinate (last iter)
dit_x_disp = dit["X displacement"] # X displacement (last iter)
dit_y_disp = dit["Y displacement"] # Y displacement (last iter)
dit_z_disp = dit["Z displacement"] # Z displacement (last iter)

#================ Security =======================

if not np.array_equal(xdtooth_node_nb.values, tooth_node_nb.values):    # Compare the node number and exits if it is not the same

    print("ERROR : X displacement node order mismatch")
    raise SystemExit

elif not np.array_equal(ydtooth_node_nb.values, tooth_node_nb.values):

    print("ERROR : Y displacement node order mismatch")
    raise SystemExit

elif not np.array_equal(zdtooth_node_nb.values, tooth_node_nb.values):

    print("ERROR : Z displacement node order mismatch")
    raise SystemExit

elif not np.array_equal(dit_node_nb.values, tooth_node_nb.values):

    print("ERROR : Previous iteration node order mismatch")
    raise SystemExit
    

#================ Global variables =======================

tooth_tot_node = np.shape(tooth_node_nb)[0]; # Total number of nodes in the full tooth mesh


i=0;



disp_info_tab = np.empty((tooth_tot_node,7)); # Creation of the displacement table
disp_info_tab[:,0] = tooth_node_nb; # First column is the number of the nodes 

#================== Calculation =============================



for i in range (tooth_tot_node):
    disp_info_tab[i,4] = xdtooth_x_deformation[i]; # Node displacement in X
    disp_info_tab[i,5] = ydtooth_y_deformation[i]; # Node displacement in Y
    disp_info_tab[i,6] = zdtooth_z_deformation[i]; # Node displacement in Z
        
    disp_info_tab[i,1] = dit_node_posx[i] + disp_info_tab[i,4]; # New position in X
    disp_info_tab[i,2] = dit_node_posy[i] + disp_info_tab[i,5]; # New position in Y
    disp_info_tab[i,3] = dit_node_posz[i] + disp_info_tab[i,6]; # New position in Z

    
tab = pd.DataFrame(disp_info_tab, columns=["Node Number", "New X position", "New Y position", "New Z position","X displacement","Y displacement","Z displacement"]);
tab["Node Number"] = tab["Node Number"].astype(int)
tab.to_csv('disp_info_tab_tooth.txt', sep='\t', index=False);
























