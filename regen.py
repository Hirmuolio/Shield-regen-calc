#!/usr/bin/env python3

import math
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np

#Things that happen when you press the button
#Do math, show results, draw figure
def plot_figure(*args):
	#Simulation deltas pulled from nowhere
	#1/100 of a seconds
	delta = 8 #0.08*100
	
	#Check if cycle time is given. If it is t hen cycle accurate simulation is used.
	try:
		cycle = float(input_cycle.get())
		#Convert to 1/100 second. Round to integer.
		cycle = int( round(cycle,2)*100 )
		cycle_simulate = True
	except ValueError:
		#no cycle time. Cycle on every delta
		cycle_simulate = False
		cycle = delta
		
	try:
		max_hp = int(input_max_hp.get())
		recharge_time = int(input_recharge_time.get())
		resist = int(input_resist.get())/100
		dps = int(input_dps.get())
		
		#Do the math and then plot the figure
		eff_dps = dps*(1-resist)
		#regen_term = 10*max_hp/recharge_time


		cycle = cycle - cycle%delta
		volley = eff_dps*(cycle/100)
		
		stop = False
		hp = []
		time_list = []
		current_hp = max_hp
		stability_check_counter = 0
		iteration_count = 0
		anchor_time = 0
		anchor_hp = current_hp

		while stop == False:
			#1. apply damage
			#2. check if died
			#3. if not dead apply regeneration
			old_hp = current_hp
			
			current_time = iteration_count * delta/100
			
			#cycle accurate damage
			if (iteration_count*delta)%cycle == 0:
				current_hp = current_hp - volley
				anchor_hp = current_hp
				anchor_time = current_time
			
			#Check if died
			if current_hp <= 0:
				#you died
				current_hp = 0
				stop = True
				stable = False
			else:
				#current_hp = min(current_hp + (delta/100) * regen_term *( math.sqrt(current_hp / max_hp) - (current_hp / max_hp) ), max_hp)
				
				current_hp = max_hp * ( 1 + math.exp(5*(anchor_time-current_time)/recharge_time) * ( math.sqrt(anchor_hp/max_hp) -1) )**2
			
			old_percentage = round(old_hp/max_hp, 2)
			new_percentage = round(current_hp/max_hp, 2)
			#Save the situation if:
			#hp percentage has changed
			#or if on next cycle is damage (only if user gave cycle)
			if old_percentage != new_percentage or (((iteration_count+1)*delta)%cycle == 0 and cycle_simulate):
				time_list.append(current_time)
				hp.append(current_hp)
				
				#Check if shields have stabilized. Checked every 80 second (or cycle time + 2).
				#If current shield level less than 2 less than the max shield level in past 80 seconds then assume shields stable
				#In practice stability checker doesn't work if cycle time over 80 seconds.
				if stability_check_counter > max(1000, int(100*cycle/delta)):
					if math.ceil(current_hp) >= math.floor(max(hp[-1000:]))-2:
						stop = True
						stable = True
			
			#Timeout after 24 hours. Literally impossible to tank for lnger than that.
			if current_time>86400:
				print('Timeup')
				stop = True
				stable = True
			stability_check_counter = stability_check_counter+1
			iteration_count = iteration_count+1	
			
					

		shield_percentage = 100*np.array(hp)/max_hp
		
		#Show results
		peak_regen.set( str(round(2.5*max_hp/(recharge_time*(1-resist))))+' EHP/s ('+ str(round(2.5*max_hp/recharge_time)) + ' HP/s)')
		
		print(len(hp))
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
input_cycle = StringVar()

#Outputs
peak_regen = StringVar()
tank_time = StringVar()
damage_tanked = StringVar()

#Input field labels
ttk.Label(window, text="Shield max HP: ").grid(column=1, row=1, sticky=E)
ttk.Label(window, text="Shield recharge time:").grid(column=1, row=2, sticky=E)
ttk.Label(window, text="Shield resist (%):").grid(column=1, row=3, sticky=E)
ttk.Label(window, text="Incoming DPS:").grid(column=1, row=4, sticky=E)
ttk.Label(window, text="Cycle duration:").grid(column=1, row=5, sticky=E)
ttk.Label(window, text="(optional)").grid(column=3, row=5, sticky=W)

#input fields
max_hp_entry = ttk.Entry(window, width=7, textvariable=input_max_hp)
recharge_time_entry = ttk.Entry(window, width=7, textvariable=input_recharge_time)
resist_entry = ttk.Entry(window, width=7, textvariable=input_resist)
dps_entry = ttk.Entry(window, width=7, textvariable=input_dps)
cycle_entry = ttk.Entry(window, width=7, textvariable=input_cycle)

#Input field positions
max_hp_entry.grid(column=2, row=1, sticky=(W, E))
recharge_time_entry.grid(column=2, row=2, sticky=(W, E))
resist_entry.grid(column=2, row=3, sticky=(W, E))
dps_entry.grid(column=2, row=4, sticky=(W, E))
cycle_entry.grid(column=2, row=5, sticky=(W, E))

#Output field labels
ttk.Label(window, text="Peak regen:").grid(column=1, row=7, sticky=E)
ttk.Label(window, text="Tank time:").grid(column=1, row=8, sticky=E)
ttk.Label(window, text="Damage received:").grid(column=1, row=9, sticky=E)

#Output fields
ttk.Label(window, textvariable=peak_regen).grid(column=2, row=7, sticky=(W, E))
ttk.Label(window, textvariable=tank_time).grid(column=2, row=8, sticky=(W, E))
ttk.Label(window, textvariable=damage_tanked).grid(column=2, row=9, sticky=(W, E))

#Buttons
ttk.Button(window, text="Plot", command=plot_figure).grid(column=2, row=6, sticky=W)
ttk.Button(window, text="Clear", command=clear_all).grid(column=3, row=6, sticky=W)

for child in window.winfo_children(): child.grid_configure(padx=5, pady=5)

max_hp_entry.focus()
root.bind('<Return>', plot_figure)

root.mainloop()
