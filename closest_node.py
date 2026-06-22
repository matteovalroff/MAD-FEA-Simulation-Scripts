# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:36:27 2026

@author: matte
"""

import os
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

script_dir = os.path.dirname(os.path.abspath(__file__)) # Recuperation of the file's path
os.chdir(script_dir) # Change the working file to make sure we're in the right one

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

# Extraction of the column (ipdl = inner PDL)

fpdl_node_nb = fpdl["Node Number"]    # Identification node number
fpdl_node_posx = fpdl["X Location (mm)"] # Node position X coordinate
fpdl_node_posy  = fpdl["Y Location (mm)"] # Node position Y coordinate
fpdl_node_posz  = fpdl["Z Location (mm)"] # Node position Z coordinate

# ================= Coordinates arrays =====================

ipdl_coords = np.column_stack((ipdl_node_posx, ipdl_node_posy, ipdl_node_posz)) # creation of 3D coordinate for each nodes. It linked one node to its XYZ position

fpdl_coords = np.column_stack((fpdl_node_posx, fpdl_node_posy, fpdl_node_posz)) # creation of 3D coordinate for each nodes. It linked one node to its XYZ position

print("Building KDTree...")

# ================= KDTree creation ========================
'''
This command divides and distributes nodes into regions of points that are
close to the others. The principle of KDTree is to progressively divide the 
space into several subregions. First, all points are divided into two groups 
based on their position on the X-axis. Next, each of these groups is further 
divided into two based on the Y-axis, then based on the Z-axis. This process 
is repeated successively on the resulting subregions until groups containing
only a small number of points are obtained. Geometrically close nodes are then
grouped together into small spatial regions. The major benefit is that this 
significantly speeds up proximity searches.
'''

tree = cKDTree(ipdl_coords)

print("Searching closest nodes...")

# ================= Closest node search ====================
'''
This command searches, for each node in the entire mesh, for the nearest node 
on the inner surface of the PDL. The algorithm first attempts to find a node 
close to the target node. The distance between the target node and its neighbor 
is defined as the current closest distance. Next, the algorithm checks whether 
there is a node closer than this first neighbor. To do this, it compares the 
minimum distance between the region and the node with the current closest 
distance. If the former is greater than the current closest distance, then the 
region is completely ignored. This eliminates the need to compare distances 
between every node, resulting in a significant reduction in computation time.
'''
distances, indices = tree.query(fpdl_coords)

print("Creating result table...")

# ================= Result table ===========================
'''
In the previous step, the nearest node is stored using an index based on its 
position in the array. In this line, the final array is created by replacing 
the indices with the corresponding node numbers in the mesh.
'''
closest_node_tab = pd.DataFrame({"PDL mesh Node": fpdl_node_nb.values, "Closest Inner PDL Node": ipdl_node_nb.iloc[indices].values, "Distance": distances, "Pos X": fpdl_node_posx, "Pos Y": fpdl_node_posy,"Pos Z": fpdl_node_posz});

# ================= Save file ==============================




closest_node_tab = closest_node_tab.sort_values(by="Closest Inner PDL Node") #test

closest_node_tab.to_csv("closest_node_tab.txt", sep="\t", index=False)

print("File saved : closest_node_tab.txt")

