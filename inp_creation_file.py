# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:45:35 2026

@author: matte
"""
import os
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__)) # Recuperation of the file's path
os.chdir(script_dir) # Change the working file to make sure we're in the right one

# ================= Read displacement table =================

tab = pd.read_csv("disp_info_tab_pdl.txt",sep="\t")

tab2 = pd.read_csv("disp_info_tab_tooth.txt",sep="\t")



# ================= Create APDL backup iterative file ========================

iteration = os.environ.get("ITERATION", "0") # Gathers the iteration number from Ansys, if doesn't exists yet, use 0

output_dir = "inp_iterations" # file where will be stocked INP files for each iterations

if not os.path.exists(output_dir): # If the output file doesn't exist, create it
    os.makedirs(output_dir)

backup = os.path.join(output_dir,"update_mesh_iter_{}.inp".format(iteration)) # Export of the INP file in the good file and with the good name

with open(backup, "w") as f: # Creation/overwrite of the file used by Ansys to displace the mesh

    for i in range(len(tab)): # Read the first table line after line

        node = int(tab["Node Number"][i])

        x = tab["New X position"][i]
        y = tab["New Y position"][i]
        z = tab["New Z position"][i]

        f.write(f"NMODIF,{node},{x},{y},{z}\n") # Write in the inp file (NMODIF is the command use by Ansys (APDL) to displace a node)
        
    for k in range(len(tab2)):

        node2 = int(tab2["Node Number"][k]) # Read the second table line after line

        x2 = tab2["New X position"][k]
        y2 = tab2["New Y position"][k]
        z2 = tab2["New Z position"][k]

        f.write(f"NMODIF,{node2},{x2},{y2},{z2}\n") # Write in the inp file (NMODIF is the command use by Ansys (APDL) to displace a node)

# ============================ Create APDL file for Ansys (overwrite) =================================

filename = os.path.join(script_dir,"update_mesh.inp") # Export of the INP file in the good file and with the good name

with open(filename, "w") as f: # Creation/overwrite of the file used by Ansys to displace the mesh

    for i in range(len(tab)): # Read the first table line after line

        node = int(tab["Node Number"][i])

        x = tab["New X position"][i]
        y = tab["New Y position"][i]
        z = tab["New Z position"][i]

        f.write(f"NMODIF,{node},{x},{y},{z}\n") # Write in the inp file (NMODIF is the command use by Ansys (APDL) to displace a node)
        
    for k in range(len(tab2)):

        node2 = int(tab2["Node Number"][k]) # Read the second table line after line

        x2 = tab2["New X position"][k]
        y2 = tab2["New Y position"][k]
        z2 = tab2["New Z position"][k]

        f.write(f"NMODIF,{node2},{x2},{y2},{z2}\n") # Write in the inp file (NMODIF is the command use by Ansys (APDL) to displace a node)

print("update_mesh.inp created")



    