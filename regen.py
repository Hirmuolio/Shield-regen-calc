#!/usr/bin/env python3

import math
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np

#Things that happen when you press the button
#Do math, show results, draw figure
def plot_figure(*args):
	try:
		max_hp = int(input_max_hp.get())
		recharge_time = int(input_recharge_time.get())
		resist = int(input_resist.get())/100
		dps = int(input_dps.get())

		#Do the math and then plot the figure
		eff_dps = dps*(1-resist)
		regen_term = 10*max_hp/recharge_time

		#Simulation delta pulled from nowhere
		delta = 0.04
		
		stop = False
		hp = []
		time_list = []
		time_list.append(0)
		hp.append(max_hp)
		

		while stop == False:
			time_list.append(time_list[-1]+delta)
			#1. apply damage
			#2. check if died
			#3. if not dead apply regeneration
			
			new_hp = hp[-1] - delta*eff_dps
			
			#Check if died
			if new_hp <= 0:
				#you died
				hp.append(0)
				stop = True
				stable = False
			else:
				new_hp = min(new_hp + delta * regen_term *( math.sqrt(new_hp / max_hp) - (new_hp / max_hp) ), max_hp)
				hp.append(new_hp)
				
				#Check if there is any change
				#Start doing this check only after 10 iterations
				if len(hp) > 10:
					if math.isclose(hp[-1], hp[-10], rel_tol=0.00001, abs_tol=0.0):
						stop = True
						stable = True

		
		shield_percentage = 100*np.array(hp)/max_hp
		
		#Show results
		peak_regen.set( str(round(2.5*max_hp/(recharge_time*(1-resist))))+' EHP/s ('+ str(round(2.5*max_hp/recharge_time)) + ' HP/s)')
		
		if stable == False:
			minutes = math.floor(time_list[-1]/60)
			seconds = math.floor(time_list[-1]-60*minutes)
			tank_time.set(  str(minutes) +' min ' + str(seconds) + ' s')
			damage_tanked.set( round(time_list[-1]*dps) )
		else:
			tank_time.set('Stable at '+str(round(shield_percentage[-1], 1))+'%')
			damage_tanked.set('Infinite')
		
		
		plt.plot(time_list, shield_percentage)
		plt.ylabel('Shield HP (%)')
		plt.xlabel('Time (s)')
		plt.grid(True)
		axes = plt.gca()
		axes.set_ylim([0,100])
		axes.set_xlim([0,max(axes.get_xlim()[1], time_list[-1])])
		plt.show()

	except ValueError:
		print('Something went wrong. Probably invalid input.')
		pass

#Clear all things
def clear_all(*args):
	peak_regen.set( '' )
	tank_time.set( '' )
	damage_tanked.set( '' )
	plt.clf()
	plt.show()



#The input window code:
root = Tk()
root.title("Shield regen calc")


window = ttk.Frame(root, padding="3 3 12 12")
window.grid(column=0, row=0, sticky=(N, W, E, S))

#Inputs
input_max_hp = StringVar()
input_recharge_time = StringVar()
input_resist = StringVar()
input_dps = StringVar()

#Outputs
peak_regen = StringVar()
tank_time = StringVar()
damage_tanked = StringVar()

#Input field labels
ttk.Label(window, text="Shield max HP: ").grid(column=1, row=1, sticky=E)
ttk.Label(window, text="Shield recharge time:").grid(column=1, row=2, sticky=E)
ttk.Label(window, text="Shield resist (%):").grid(column=1, row=3, sticky=E)
ttk.Label(window, text="Incoming DPS:").grid(column=1, row=4, sticky=E)

#input fields
max_hp_entry = ttk.Entry(window, width=7, textvariable=input_max_hp)
recharge_time_entry = ttk.Entry(window, width=7, textvariable=input_recharge_time)
resist_entry = ttk.Entry(window, width=7, textvariable=input_resist)
dps_entry = ttk.Entry(window, width=7, textvariable=input_dps)

#Input field positions
max_hp_entry.grid(column=2, row=1, sticky=(W, E))
recharge_time_entry.grid(column=2, row=2, sticky=(W, E))
resist_entry.grid(column=2, row=3, sticky=(W, E))
dps_entry.grid(column=2, row=4, sticky=(W, E))

#Output field labels
ttk.Label(window, text="Peak regen:").grid(column=1, row=6, sticky=E)
ttk.Label(window, text="Tank time:").grid(column=1, row=7, sticky=E)
ttk.Label(window, text="Damage received:").grid(column=1, row=8, sticky=E)

#Output fields
ttk.Label(window, textvariable=peak_regen).grid(column=2, row=6, sticky=(W, E))
ttk.Label(window, textvariable=tank_time).grid(column=2, row=7, sticky=(W, E))
ttk.Label(window, textvariable=damage_tanked).grid(column=2, row=8, sticky=(W, E))

#Buttons
ttk.Button(window, text="Plot", command=plot_figure).grid(column=2, row=5, sticky=W)
ttk.Button(window, text="Clear", command=clear_all).grid(column=3, row=5, sticky=W)

for child in window.winfo_children(): child.grid_configure(padx=5, pady=5)

max_hp_entry.focus()
root.bind('<Return>', plot_figure)

root.mainloop()
