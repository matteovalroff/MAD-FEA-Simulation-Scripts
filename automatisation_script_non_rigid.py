import os
import subprocess
import time
import math
 
# ========================= PARAMETERS =========================
 
simulation_time = 10.0 # Ending condition refferring to the desired clinical time (in days)
 
workdir = r"C:\Users\matte\Documents\POLYTECH\stage\ancone\stage\Non rigid simulation" # Path of the work directory
 
python_exe = r"C:\Users\matte\AppData\Local\spyder-6\envs\spyder-runtime\python.exe" # Path of the python executer
 
scripts = ["node_displacement_update_pdl.py", # Name of the scripts used in the subprocess
           "node_displacement_update_tooth.py",
           "inp_creation_file.py"]
 
# ========================= INITIALIZATION =========================
 
i = 0

mean_stress_pdl = 1.213233362e-003 # All these values correspont to the results of the simulation at iter1
mean_deformation_pdl = 9.398160853e-004
mean_bone_remodeling_velocity = 0.9
x_disp_center_mass = 7.165835715e-004 
y_disp_center_mass = 9.992549445e-005
z_disp_center_mass = 7.316950875e-005 
iter_disp_center_mass = 7.27207602e-004
tot_disp_center_mass = math.sqrt(x_disp_center_mass**2 + y_disp_center_mass**2 + z_disp_center_mass**2) # Allows to measure the displacement of the gravity center of the tooth
 
iter_time = mean_deformation_pdl/(mean_bone_remodeling_velocity*mean_stress_pdl)
 
total_time = iter_time
 
time_file = os.path.join(workdir, "clinical_time.txt")
 
with open(time_file, "w") as f: # Creation of the clinical time file
 
    f.write("Iter {} = {} days. Total time = {} days. Stress = {:.8e}, Deformation = {:.8e}\n".format(
            i+1,
            iter_time,
            total_time,
            mean_stress_pdl,
            mean_deformation_pdl))

center_disp_file = os.path.join(workdir, "center_mass_disp.txt")
 
with open(center_disp_file, "w") as f: # Creation of the center displacement file
 
    f.write("Iter {}: Mass center displacent = {}; Total displacement = {}\n".format(
            i+1,
            iter_disp_center_mass,
            tot_disp_center_mass))

 
# ========================= ANSYS OBJECTS =========================
 
analysis = ExtAPI.DataModel.Project.Model.Analyses[0]
solution = analysis.Solution
 
# ========================= ITERATIVE LOOP =========================
 
i += 1
 
simulation_start_time = time.time()   # Beginning of the real time of the simulation
 
while total_time<simulation_time:
 
    ExtAPI.Log.WriteMessage(
        "===== ITERATION {} =====".format(i + 1)
    )
 
    iter_start_time = time.time()   # Beginning of the real time of the iteration
 
    # ------------------------ SOLVE -----------------------
 
    solution.ClearGeneratedData()
    solution.Solve(True)            # Solve of the model
    solution.EvaluateAllResults()
 
    # ------------------------------------------------------------
    # GET UPDATED RESULTS
    # ------------------------------------------------------------
 
    stress_pdl = DataModel.GetObjectById(83) # Aaffectation to a valiable of a solution with its ID
    deformation_pdl = DataModel.GetObjectById(84)
    mass_center_disp = DataModel.GetObjectById(324)
 
    mean_stress_pdl = stress_pdl.Average.Value # Lecture of the results
    mean_deformation_pdl = deformation_pdl.Average.Value
    iter_disp_center_mass = mass_center_disp.TotalDeformation.Value
    x_disp_center_mass += mass_center_disp.MaximumXAxis.Value
    y_disp_center_mass += mass_center_disp.MaximumYAxis.Value
    z_disp_center_mass += mass_center_disp.MaximumZAxis.Value
 
 
    ExtAPI.Log.WriteMessage(
        "Stress = {:.8e}".format(mean_stress_pdl))
 
    ExtAPI.Log.WriteMessage(
        "Deformation = {:.8e}".format(mean_deformation_pdl))
 
    # ------------------------------------------------------------
    # EXPORT RESULTS
    # ------------------------------------------------------------
 
    for child in solution.Children: # Export of the results in text files and format them to the right name
 
        if hasattr(child, "ExportToTextFile"):
 
            try:
 
                filename = child.Name.replace(" ", "_")
 
                # fichier courant
                path_current = os.path.join(
                    workdir,
                    filename + ".txt")
 
                child.ExportToTextFile(path_current)
 
            except:
                pass
 
    # ------------------------------------------------------------
    # CLINICAL TIME
    # ------------------------------------------------------------
 
    iter_time = mean_deformation_pdl/(mean_bone_remodeling_velocity*mean_stress_pdl)
    total_time += iter_time # Calculation of the clinical time simulated
    
    tot_disp_center_mass = math.sqrt(x_disp_center_mass**2 + y_disp_center_mass**2 + z_disp_center_mass**2) # Calculation of the center of gravity displacement
    
 
    # --- Duration of the iteration (in real time) ---
    iter_duration_sec = time.time() - iter_start_time
    h, rem = divmod(iter_duration_sec, 3600)
    m, s = divmod(rem, 60)
    iter_duration_str = "{:02.0f}h{:02.0f}m{:02.0f}s".format(h, m, s)
 
    # --- Duration of the simulation (in real time) ---
    total_duration_sec = time.time() - simulation_start_time
    H, remT = divmod(total_duration_sec, 3600)
    M, S = divmod(remT, 60)
    total_duration_str = "{:02.0f}h{:02.0f}m{:02.0f}s".format(H, M, S)
 
    with open(time_file, "a") as f: # Write the results in the clinical time file
 
        f.write("Iter {} = {} days. Total time = {} days. Stress = {:.8e}, Deformation = {:.8e}. "
                "Iteration duration = {}. Total simulation duration = {}.\n".format(
                i + 1,
                iter_time,
                total_time,
                mean_stress_pdl,
                mean_deformation_pdl,
                iter_duration_str,
                total_duration_str))

    with open(center_disp_file, "a") as f: # Write the results in the gravity center's displacement file
 
        f.write("Iter {}: Mass center displacent = {}; Total displacement = {}\n".format(
            i+1,
            iter_disp_center_mass,
            tot_disp_center_mass))
            

    # --------------- UPDATE MESH ----------
 
    for script in scripts: # Run of the python scripts in subprocess
 
        script_path = os.path.join(workdir, script)
 
        env = os.environ.copy()
        env["ITERATION"] = str(i + 1)
 
        process = subprocess.Popen(
            [python_exe, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env)
 
        process.wait()
 
        if process.returncode != 0:
 
            stdout, stderr = process.communicate()
 
            raise Exception("Script failed : {}\n{}".format(
                            script,
                            stderr.decode("utf-8")))
 
    ExtAPI.Log.WriteMessage("Mesh update file generated")
 
    i+=1
 
ExtAPI.Log.WriteMessage("===== FINISHED =====")



