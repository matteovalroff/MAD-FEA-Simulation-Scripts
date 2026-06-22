# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:38:08 2026

@author: matte
"""
import os
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__)) # Recuperation of the file's path
os.chdir(script_dir) # Change the working file to make sure we're in the right one

#========== Closest node table file read ======================

# Upload the file
cnt = pd.read_csv("closest_node_tab.txt", sep=None, engine='python', decimal=",", dtype={"PDL mesh Node": int,"Closest Inner PDL Node": int,"Distance": float})

# Extraction of the column (cnt = closest node table)

cnt_mesh_node = cnt["PDL mesh Node"]    # Identification node number
cnt_closest_node = cnt["Closest Inner PDL Node"] # Closest node on the inner PDL surface number
cnt_distance  = cnt["Distance"] # Distance between the node and the closest node on the inner PDL surface
cnt_posx = cnt["Pos X"] # Node position in X
cnt_posy = cnt["Pos Y"] # Node position in Y
cnt_posz = cnt["Pos Z"] # Node position in Z

#========== X deformation inner PDL node file read ======================

# Upload the file
xdipdl = pd.read_csv("X_Directional_Deformation_PDL.txt", sep=None, engine='python', decimal=",", dtype={"Node Number": int,"X Location (mm)": float,"Y Location (mm)": float,"Z Location (mm)": float,"Directional Deformation (mm)": float})

# Extraction of the column (xdipdl = X deformation inner PDL)

xdipdl_node_nb = xdipdl["Node Number"]    # Identification node number
xdipdl_node_pos = xdipdl["X Location (mm)"] # Node position X after displacement
xdipdl_node_posy = xdipdl["Y Location (mm)"] # Node position Y after displacement
xdipdl_node_posz = xdipdl["Z Location (mm)"] # Node position Z after displacement
xdipdl_x_deformation = xdipdl["Directional Deformation (mm)"] #

#========== Y deformation inner PDL node file read ======================

# Upload the file
ydipdl = pd.read_csv("Y_Directional_Deformation_PDL.txt", sep=None, engine='python', decimal=",", dtype={"Node Number": int,"X Location (mm)": float,"Y Location (mm)": float,"Z Location (mm)": float,"Directional Deformation (mm)": float})

# Extraction of the column (ydipdl = Y deformation inner PDL)

ydipdl_node_nb = ydipdl["Node Number"]    # Identification node number
ydipdl_node_posx = ydipdl["X Location (mm)"] # Node position X after displacement
ydipdl_node_posy = ydipdl["Y Location (mm)"] # Node position Y after displacement
ydipdl_node_pos = ydipdl["Z Location (mm)"] # Node position Z after displacement
ydipdl_y_deformation = ydipdl["Directional Deformation (mm)"] #

#========== Z deformation inner PDL node file read ======================

# Upload the file
zdipdl = pd.read_csv("Z_Directional_Deformation_PDL.txt", sep=None, engine='python', decimal=",", dtype={"Node Number": int,"X Location (mm)": float,"Y Location (mm)": float,"Z Location (mm)": float,"Directional Deformation (mm)": float})

# Extraction of the column (zdipdl = Z deformation inner PDL)

zdipdl_node_nb = zdipdl["Node Number"]    # Identification node number
zdipdl_node_posx = zdipdl["X Location (mm)"] # Node position X after displacement
zdipdl_node_posy = zdipdl["Y Location (mm)"] # Node position Y after displacement
zdipdl_node_posz = zdipdl["Z Location (mm)"] # Node position Z after displacement
zdipdl_z_deformation = zdipdl["Directional Deformation (mm)"] 


#========== Inner PDL node file read ======================

# Upload the file
ipdl = pd.read_csv("inner_pdl_nodes.txt", sep=None, engine='python', decimal=",", dtype={"Node Number": int,"X Location (mm)": float,"Y Location (mm)": float,"Z Location (mm)": float})

# Extraction of the column (ipdl = inner PDL)

ipdl_node_nb = ipdl["Node Number"]    # Identification node number
ipdl_node_posx = ipdl["X Location (mm)"] # Node position X coordinate
ipdl_node_posy  = ipdl["Y Location (mm)"] # Node position Y coordinate
ipdl_node_posz  = ipdl["Z Location (mm)"] # Node position Z coordinate

#print(ipdl_node_nb);
#print(ipdl_node_posx);


#========== Full PDL node file read ======================

# Upload the file
fpdl = pd.read_csv("full_pdl_nodes.txt", sep=None, engine='python', decimal=",", dtype={"Node Number": int,"X Location (mm)": float,"Y Location (mm)": float,"Z Location (mm)": float})

# Extraction of the column (fpdl = full PDL)

fpdl_node_nb = fpdl["Node Number"]    # Identification node number
fpdl_node_posx = fpdl["X Location (mm)"] # Node position X coordinate
fpdl_node_posy  = fpdl["Y Location (mm)"] # Node position Y coordinate
fpdl_node_posz  = fpdl["Z Location (mm)"] # Node position Z coordinate

#print(fpdl_node_nb);
#print(fpdl_node_posx);



#========== Previous position file read ======================

# Upload the file
dit = pd.read_csv("disp_info_tab_pdl.txt", sep=None, engine='python', decimal=",", dtype={"Node Number": int,"New X position": float,"New Y position": float,"New Z position": float,"X displacement": float,"Y displacement": float,"Z displacement": float})

# Extraction of the column (dit = displacement information table)

dit_node_nb = dit["Node Number"]    # Identification node number
dit_node_posx = dit["New X position"] # Node position X coordinate (last iter)
dit_node_posy  = dit["New Y position"] # Node position Y coordinate (last iter)
dit_node_posz  = dit["New Z position"] # Node position Z coordinate (last iter)
dit_x_disp = dit["X displacement"] # X displacement (last iter)
dit_y_disp = dit["Y displacement"] # Y displacement (last iter)
dit_z_disp = dit["Z displacement"] # Z displacement (last iter)


#================ Security =======================

            
if not np.array_equal(xdipdl_node_nb.values, ipdl_node_nb.values):  # Compare the node number and exits if it is not the same

    print("ERROR : X displacement node order mismatch")
    raise SystemExit

elif not np.array_equal(ydipdl_node_nb.values, ipdl_node_nb.values):

    print("ERROR : Y displacement node order mismatch")
    raise SystemExit

elif not np.array_equal(zdipdl_node_nb.values, ipdl_node_nb.values):

    print("ERROR : Z displacement node order mismatch")
    raise SystemExit

elif not np.array_equal(cnt_mesh_node.values, dit_node_nb.values):

    print("ERROR : Previous iteration node order mismatch")
    raise SystemExit
    
    
#================ Global variables =======================

fpdl_tot_node = np.shape(fpdl_node_nb)[0]; # Total number of nodes in the full PDL mesh
ipdl_tot_node = np.shape(ipdl_node_nb)[0]; # Total number of nodes in the inner PDL surface

k=0;
i=0;

disp_info_tab = np.empty((fpdl_tot_node,7)); # Creation of the displacement table
disp_info_tab[:,0] = cnt_mesh_node; # First column is the number of nodes (sorted by the closest node on the inner PDL)


for i in range (fpdl_tot_node):
    if cnt_closest_node[i]==ipdl_node_nb[k]:
        disp_info_tab[i,4] = xdipdl_x_deformation[k]; # Node displacement in X
        disp_info_tab[i,5] = ydipdl_y_deformation[k]; # Node displacement in Y
        disp_info_tab[i,6] = zdipdl_z_deformation[k]; # Node displacement in Z
        
        disp_info_tab[i,1] = dit_node_posx[i] + disp_info_tab[i,4]; # New position in X
        disp_info_tab[i,2] = dit_node_posy[i] + disp_info_tab[i,5]; # New position in Y
        disp_info_tab[i,3] = dit_node_posz[i] + disp_info_tab[i,6]; # New position in Z
        
    else:
        k+=1
        disp_info_tab[i,4] = xdipdl_x_deformation[k]; # Node displacement in X
        disp_info_tab[i,5] = ydipdl_y_deformation[k]; # Node displacement in Y
        disp_info_tab[i,6] = zdipdl_z_deformation[k]; # Node displacement in Z
        
        disp_info_tab[i,1] = dit_node_posx[i] + disp_info_tab[i,4]; # New position in X
        disp_info_tab[i,2] = dit_node_posy[i] + disp_info_tab[i,5]; # New position in Y
        disp_info_tab[i,3] = dit_node_posz[i] + disp_info_tab[i,6]; # New position in Z
 
     
        
tab = pd.DataFrame(disp_info_tab, columns=["Node Number", "New X position", "New Y position", "New Z position","X displacement","Y displacement","Z displacement"]);
tab["Node Number"] = tab["Node Number"].astype(int)
tab.to_csv('disp_info_tab_pdl.txt', sep='\t', index=False);


    
