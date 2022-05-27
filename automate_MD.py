#Create directories for P2,3,8 and T0.1-0.3
import pandas as pd
import os
import subprocess
import shutil

pwd = os.getcwd()
if not os.path.exists(pwd + '/new_MD_LAMMPS'):
    os.makedirs(pwd + '/new_MD_LAMMPS')

new_path = pwd + '/new_MD_LAMMPS'
particle = [2,3,8]
for i in particle:
    path_particle = new_path + "/p_" + str(i)
    os.makedirs(path_particle)
T = [0.10,0.20,0.30]
for i in particle:
    for item in T:
        path =  new_path + "/p_" + str(i) + "/T_" + str(item)
        path_1 =  new_path + "/p_" + str(i) + "/T_" + str(item) + "/dump_" + str(item)
        os.makedirs(path)
        os.makedirs(path_1)


#%% COPY TEMPLATE FILES TO RESPECTIVE DIRECTORIES
for i in particle:
    for item in T:
        path = new_path + "/p_" + str(i) + "/T_" + str(item)

        shutil.copy(pwd + '/in.lammps', path + '/in_'+str(item) + '.lammps')
    shutil.copy(pwd + '/'+str(i)+'_particle.data', new_path + '/p_' + str(i) + '/particle_'+str(i)+'.data')
    shutil.copy(pwd + '/1.lammps', new_path + '/p_' + str(i) + '/1_'+str(i)+'.lammps')

#%% MODIFYING INPUT SCRIPTS
#mdst = [[2, 1270],[3,1360],[8,2540],[16,2620],[50,3970]]

mdst = [1000,120,240]
for i in (particle):
    for item in T:
        path = new_path + "/p_" + str(i) + "/T_" + str(item)
        path_particle = new_path + "/p_" + str(i)
        
        input_file = open(path + "/in_" + str(item) + ".lammps", "r")
        list_of_lines = input_file.readlines()
        list_of_lines[5] = 'read_restart  ' + path_particle + '/ifinal.restart\n'
        list_of_lines[6] = 'read_dump  ' + path_particle + '/isystem.dump ' + str(mdst[particle.index(i)]) + ' x y z\n'
        
        list_of_lines[71] = 'fix sys_energy all print 2000 "$t $e $m" file ' + path + '/energy_${Temperature}.dat screen no\n'
        list_of_lines[73] = 'dump      1 all custom 500 ' + path + '/system.dump id mol type x y z vx vy vz\n'
        list_of_lines[74] = 'dump      2 NP custom 2000 ' + path + '/dump_' + str(item) + '/frame.*.dump id mol type x y z vx vy vz\n'
        
        list_of_lines[77] = 'write_data ' + path + '/system_equi${Temperature}.data\n'
        list_of_lines[78] = 'write_restart ' + path + '/equifinal${Temperature}.restart\n'
        
        input_file = open(path + "/in_" + str(item) + ".lammps", "w")
        input_file.writelines(list_of_lines)
        input_file.close()
    
    input_file_1 = open(path_particle + "/1_" + str(i) + ".lammps", "r")
    list_of_lines = input_file_1.readlines()
    list_of_lines[5] = 'read_data  '+path_particle+'/particle_'+str(i)+'.data\n'
    list_of_lines[74] = 'dump      1 all custom 10 '+path_particle+'/isystem.dump id mol type x y z vx vy vz\n'
    list_of_lines[78] = 'write_data '+path_particle+'/system_equi_.data\n'
    list_of_lines[79] = 'write_restart '+path_particle+'/ifinal.restart\n'    
    input_file = open(path_particle + "/1_" + str(i) + ".lammps", "w")
    input_file.writelines(list_of_lines)
    input_file_1.close()

#%%EQUILIBRIATION
for i in (particle):
    path_particle = new_path + "/p_" + str(i)
    subprocess.call('nohup mpirun -np 1 /home/user/softwares/lmp_mpi -var Temperature 1.0 -in ' + path_particle + '/1_'+str(i)+'.lammps', shell=True)        

#%%DATA SAMPLING/GENERATION
for i in (particle):
    for item in T:
        path = new_path + "/p_" + str(i) + "/T_" + str(item)
        subprocess.call('nohup mpirun -np 4 /home/user/softwares/lmp_mpi -var Temperature ' + str(item) + ' -in ' + path + '/in_'+ str(item)+ '.lammps > '+ path+'/Temp_' + str(item) +'.screen', shell=True)

#%% HISTOGRAM FROM SAMPLING DATA
save_energy = []
for i in (particle):
    for j in T:
        path = new_path + "/p_" + str(i) + "/T_" + str(j)
        path_particle = new_path + "/p_" + str(i)
        
        energy_df = pd.read_csv(pwd + "/new_MD_LAMMPS/p_" + str(i) + "/T_" + str(j)+ "/energy_" + str(j) + ".dat", sep=" ", skiprows=1 ,names=["timestep", "energy_1", "energy_2"], header=None)
        en_1 = energy_df["energy_1"]
        for line in en_1:
            save_energy.append(line)
            
        with open(pwd + "/histogram.dat", "w+") as f:
            for item in save_energy:
                f.write("%s\n" % item)

