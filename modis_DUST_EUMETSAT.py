#### SCRIPT PARA HACER RGB DE POLVO DEL EUMETSAT ####
#### POWERED BY HUAYRATORO ####

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import glob
from pyhdf.SD import SD, SDC
import scipy.io as sio
from matplotlib.ticker import FixedLocator
import pprint
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from os import listdir
import os
import pandas as pd

# Cargamos los límites de países y provincias para poder graficarlas en los mapas

states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='10m',
        facecolor='none',edgecolor='green')

countries = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_0_countries',
        scale='10m',
        facecolor='none',edgecolor='green')

salida='.../caso_de_estudio/modis/'

######################## LEYENDO LOS DATOS #########################
DataPath = '.../caso_de_estudio/modis/datos/'
Extension = 'hdf'
Filelist = glob.glob(DataPath+"*"+Extension)
file_name = Filelist[0]
file = SD(file_name, SDC.READ)
#print(file.info())
# el archivo contiene (EL PRIMER ELEMENTO DEL VECTOR DE NUMERO DE) set de datos
datasets_dic = file.datasets()

# PARA VER LOS SDS QUE CONTIENE EL ARCHIVO

#for idx,sds in enumerate(datasets_dic.keys()):
#    print (idx,sds)

# PARA SELECCIONAR UN SDS D LA LISTA ANTERIOR

sds_obj = file.select('EV_1KM_Emissive') # selecciona el SDS
DN = sds_obj.get() # extrae los datos del SDS
#print(DN.shape)

# INFORMACION SOBRE LAS BANDAS DEL SDS
#pprint.pprint(sds_obj.attributes())

###### CONVIRTIENDO LOS DATOS A RADIANCIA #######

for key, value in sds_obj.attributes().items():
#    print (key, value)
    if key == 'radiance_offsets':
        radiance_offsets = value  
    if key == 'radiance_scales':
        radiance_scales = value

# CANAL 
n = 8 # 8.7
B1 = radiance_scales[n] * ( DN[n,:,:] - radiance_offsets[n] )
B1 = B1*1e6 # Units: Watts/m^2/m/steradian

n = 10 # 10.7
B2 = radiance_scales[n] * ( DN[n,:,:] - radiance_offsets[n] )
B2 = B2*1e6 # Units: Watts/m^2/m/steradian

n = 11 # 12
B3 = radiance_scales[n] * ( DN[n,:,:] - radiance_offsets[n] )
B3 = B3*1e6 # Units: Watts/m^2/m/steradian

################### GEOREFERENCIACION ##############################

DataPath = '.../caso_de_estudio/modis/geoloc/'
Extension = 'hdf'
Filelist = glob.glob(DataPath+"*"+Extension)
file_name = Filelist[0]
file = SD(file_name, SDC.READ)
#print(file.info())

datasets_dic = file.datasets()
#for idx,sds in enumerate(datasets_dic.keys()):
#    print (idx,sds)

# HAY QUE QUEDARSE CON EL QUE DICE LATITUD Y LONGITUD
sds_obj = file.select('Latitude') # # selecciona el SDS
LAT = sds_obj.get() # extrae los datos del SDS

sds_obj = file.select('Longitude') # # selecciona el SDS
LON = sds_obj.get() # extrae los datos del SDS

########################## TRANF TBRILLO ###########################

si_no='yes'

# Estas constantes son las mismas para todo los canales emisivos
if si_no == 'yes' :

	c = 2.99792458e8  # Velocidad de la luz en el vacio [m/s]
	h = 6.6260755e-34 # Constante de Planck [J s]
	k = 1.380658e-23  # Constante de Boltzmann [J/K]

#####################################################################
###### IMPORTANTE CAMBIAR LA LONGITUD DE ONDA EN MICRONES EN L ######
#####################################################################	

	L = 8.7*1e-6 # Longitud de onda [m]
	C1 = h*c
	C2 = k*L
	C3 = 2*h*np.power(c,2)/np.power(L,5)

	TB1 = C1/(C2*np.log((C3/B1)+1)) # Temperatura de brillo en K
	TB1 = TB1	
	
	L = 10.7*1e-6 # Longitud de onda [m]
	C1 = h*c
	C2 = k*L
	C3 = 2*h*np.power(c,2)/np.power(L,5)

	TB2 = C1/(C2*np.log((C3/B2)+1)) # Temperatura de brillo en K
	TB2 = TB2

	L = 12*1e-6 # Longitud de onda [m]
	C1 = h*c
	C2 = k*L
	C3 = 2*h*np.power(c,2)/np.power(L,5)

	TB3 = C1/(C2*np.log((C3/B3)+1)) # Temperatura de brillo en K
	TB3 = TB3
	
############################### RGB #################################
####################################################################

# Definimos los limites del area a visualizar
lonwest = -70
loneast = -60
latsouth = -28
latnorth = -21.5

####################################################################
############### LA RECETA ESTA DENTRO DE http://eumetrain.org/RGBguide/recipes/RGB_recipes.pdf ###############
## se setean los valores de cada una de las bandas
## banda sola
## el canal azul es la IR10.7 va sola
rC08=TB2
minVal = 261 
maxVal = 289
dynamic = maxVal-minVal
DN_C08 = ((rC08-minVal)/dynamic)

DN_C08=np.clip(DN_C08,0,1)
## los canales verde y rojo son BTDs
    # BTD
## ROJO
BTD_1=TB3-TB2
minVal = -4
maxVal = 2
dynamic = maxVal-minVal
DN_BTD_1=((BTD_1-minVal)/dynamic)

DN_BTD_1=np.clip(DN_BTD_1,0,1)
## VERDE

BTD_2=TB2-TB1
minVal = 0 
maxVal = 15
dynamic = maxVal-minVal
DN_BTD_2=((BTD_2-minVal)/dynamic)
DN_BTD_2=np.clip(DN_BTD_2,0,1)

    
DN_C08gamma = 1.0*np.power(DN_C08,1)
    
DN_BTD_1gamma = 1.0*np.power(DN_BTD_1,1)
DN_BTD_2gamma = 1.0*np.power(DN_BTD_2,0.2)   
    
    # CANAL ROJO (RED)
R = DN_BTD_1gamma 

    # CANAL VERDE (GREEN)
G = DN_BTD_2gamma

    # CANAL AZUL (BLUE)
B = DN_C08gamma

RGB = np.dstack((R,G,B))

    # Creamos la tupla de colores para pcolormesh

    # Por como está configurado el pcolormesh, para que el gráfico sea correcto es necesario quitarle una columna
rgb = RGB[:,:-1,:]

    # Modificamos las dimensiones para ajustarlas a lo que necesita pcolormesh
colorTuple = rgb.reshape((rgb.shape[0] * rgb.shape[1]), 3) 

    # Agregamos una columna alfa (Truco para que grafique más rapido, no sé bien que hace)
colorTuple = np.insert(colorTuple, 3, 1.0, axis=1)

####################################################################
## GRAFICADO
####################################################################
fig=plt.figure(figsize=(12,9))

ax1 = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # Definimos el área de graficado y a qué proyección hay que transformar las coordenadas lat/lon

ax1.set_extent([lonwest, loneast, latsouth, latnorth], crs=ccrs.PlateCarree())

    # Graficamos

rgb_map=ax1.pcolormesh(LON,LAT, R, color=colorTuple, linewidth=0)
rgb_map.set_array(None) # Linea indispensable para que pcolormesh aplique la tupla de colores

# Agregamos la línea de costas
ax1.coastlines(resolution='10m',linewidth=0.9)

    # Agregamos los límites de los países
ax1.add_feature(countries,linewidth=2)

    # Agregamos los límites de las provincias
ax1.add_feature(states_provinces,linewidth=2)

    # Definimos donde aparecen los ticks con las latitudes y longitudes
ax1.set_yticks(np.arange(latsouth,latnorth,1), crs=ccrs.PlateCarree())
ax1.set_xticks(np.arange(lonwest,loneast,1), crs=ccrs.PlateCarree())

    # Le damos formato a las etiquetas de los ticks
lon_formatter = LongitudeFormatter(zero_direction_label=True)
lat_formatter = LatitudeFormatter()
ax1.xaxis.set_major_formatter(lon_formatter)
ax1.yaxis.set_major_formatter(lat_formatter)

plt.savefig(salida+'EUMETSAT_DUST_modis.png', dpi=250, bbox_inches = 'tight')
plt.close('all')

####################################################################
#### PARA GRAFICAR ALGUNA BANDA SOLA
interruptor = 'off'
if interruptor == 'on':

	vmin = -29
	vmax = 0
	cmap = 'gray'
	var = TB1

	fig=plt.figure(figsize=(15,15))

	ax3 = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
	    
	ax3.set_extent([lonwest, loneast, latsouth, latnorth], crs=ccrs.PlateCarree())
	    
	cm=ax3.pcolormesh(LON,LAT,var,cmap=cmap,vmin=vmin,vmax=vmax)

	ax3.coastlines(resolution='10m',linewidth=0.6)
	ax3.add_feature(countries,linewidth=0.4)
	ax3.add_feature(states_provinces,linewidth=0.4)
	ax3.set_yticks(np.arange(latsouth,latnorth,5), crs=ccrs.PlateCarree())
	ax3.set_xticks(np.arange(lonwest,loneast,5), crs=ccrs.PlateCarree())
	lon_formatter = LongitudeFormatter(zero_direction_label=True)
	lat_formatter = LatitudeFormatter()
	ax3.xaxis.set_major_formatter(lon_formatter)
	ax3.yaxis.set_major_formatter(lat_formatter)
	    
	cbar=plt.colorbar(cm,shrink=0.6)
	cbar.set_label('Grados K',fontsize=10)

	plt.savefig(salida+'imagen_modis.png', dpi=250, bbox_inches='tight')
	plt.close('all')


