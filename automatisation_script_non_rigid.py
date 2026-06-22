import os
import subprocess
import time
 
# ========================= PARAMETERS =========================
 
simulation_time = 10.0
 
workdir = r"C:\Users\matte\Documents\POLYTECH\stage\ancone\stage\Non rigid simulation"
 
python_exe = r"C:\Users\matte\AppData\Local\spyder-6\envs\spyder-runtime\python.exe"
 
scripts = ["node_displacement_update_pdl.py",
           "node_displacement_update_tooth.py",
           "inp_creation_file.py"]
 
# ========================= INITIALIZATION =========================
 
i = 0
 
mean_stress_pdl = 1.213233362e-003
mean_deformation_pdl = 9.398160853e-004
mean_bone_remodeling_velocity = 0.9
x_disp_center_mass = 0.0
y_disp_center_mass = 0.0
z_disp_center_mass = 0.0
iter_disp_center_mass = 0.0
tot_disp_center_mass = math.sqrt(x_disp_center_mass**2 + y_disp_center_mass**2 + z_disp_center_mass**2)
 
iter_time = mean_deformation_pdl/(mean_bone_remodeling_velocity*mean_stress_pdl)
 
total_time = iter_time
 
time_file = os.path.join(workdir, "clinical_time.txt")
 
with open(time_file, "w") as f:
 
    f.write("Iter {} = {} days. Total time = {} days. Stress = {:.8e}, Deformation = {:.8e}\n".format(
            i+1,
            iter_time,
            total_time,
            mean_stress_pdl,
            mean_deformation_pdl))

center_disp_file = os.path.join(workdir, "center_mass_disp.txt")
 
with open(center_disp_file, "w") as f:
 
    f.write("Iter {}: Mass center displacent = {}; Total displacement = {}\n".format(
            i+1,
            iter_disp_center_mass,
            tot_disp_center_mass))

 
# ========================= ANSYS OBJECTS =========================
 
analysis = ExtAPI.DataModel.Project.Model.Analyses[0]
solution = analysis.Solution
 
# ========================= ITERATIVE LOOP =========================
 
i += 1
 
simulation_start_time = time.time()   # Debut de la simulation entiere (temps reel)
 
while total_time<simulation_time:
 
    ExtAPI.Log.WriteMessage(
        "===== ITERATION {} =====".format(i + 1)
    )
 
    iter_start_time = time.time()   # Debut de l'iteration courante (temps reel)
 
    # ------------------------------------------------------------
    # SOLVE
    # ------------------------------------------------------------
 
    solution.ClearGeneratedData()
    solution.Solve(True)
    solution.EvaluateAllResults()
 
    # ------------------------------------------------------------
    # GET UPDATED RESULTS
    # ------------------------------------------------------------
 
    stress_pdl = DataModel.GetObjectById(102)
    deformation_pdl = DataModel.GetObjectById(105)
    mass_center_disp = DataModel.GetObjectById(324)
 
    mean_stress_pdl = stress_pdl.Average.Value
    mean_deformation_pdl = deformation_pdl.Average.Value
    iter_disp_center_mass = mass_center_disp.TotalDeformation
    x_disp_center_mass += mass_center_disp.MaximumXAxis
    y_disp_center_mass += mass_center_disp.MaximumYAxis
    z_disp_center_mass += mass_center_disp.MaximumZAxis
 
 
    ExtAPI.Log.WriteMessage(
        "Stress = {:.8e}".format(mean_stress_pdl))
 
    ExtAPI.Log.WriteMessage(
        "Deformation = {:.8e}".format(mean_deformation_pdl))
 
    # ------------------------------------------------------------
    # EXPORT RESULTS
    # ------------------------------------------------------------
 
    for child in solution.Children:
 
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
 
    total_time += iter_time
    tot_disp_center_mass = math.sqrt(x_disp_center_mass**2 + y_disp_center_mass**2 + z_disp_center_mass**2)
    
 
    # --- Duree (temps reel) de l'iteration courante ---
    iter_duration_sec = time.time() - iter_start_time
    h, rem = divmod(iter_duration_sec, 3600)
    m, s = divmod(rem, 60)
    iter_duration_str = "{:02.0f}h{:02.0f}m{:02.0f}s".format(h, m, s)
 
    # --- Duree (temps reel) totale depuis le debut de la simulation ---
    total_duration_sec = time.time() - simulation_start_time
    H, remT = divmod(total_duration_sec, 3600)
    M, S = divmod(remT, 60)
    total_duration_str = "{:02.0f}h{:02.0f}m{:02.0f}s".format(H, M, S)
 
    with open(time_file, "a") as f:
 
        f.write("Iter {} = {} days. Total time = {} days. Stress = {:.8e}, Deformation = {:.8e}. "
                "Iteration duration = {}. Total simulation duration = {}.\n".format(
                i + 1,
                iter_time,
                total_time,
                mean_stress_pdl,
                mean_deformation_pdl,
                iter_duration_str,
                total_duration_str))

    with open(center_disp_file, "a") as f:
 
        f.write("Iter {}: Mass center displacent = {}; Total displacement = {}\n".format(
            i+1,
            iter_disp_center_mass,
            tot_disp_center_mass))
            

    # ------------------------------------------------------------
    # UPDATE MESH
    # ------------------------------------------------------------
 
    for script in scripts:
 
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




