#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 15:38:05 2022

Analysis of past time mortality

The objective of this script is to analyse how life expectancy evolved throught the last 200 years.

Many say that life expectancy in the 1800s was lower than 50 years.
This can indeed simply a mean of the age of death during this period.
However, a major contribution to this early death was infant mortality.
Computing a mean death age during where a period where this mortality was still high may therefore a biased
estimate.
Indeed, once a human has reached adulthood, is life expectancy (knowing that he did not die a child) is actually higher.
This is what we intend to compute in this script.

The studied country if France. Data is obtained from "mortality.org".

@author: lfrancoi
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.interpolate
import scipy.optimize

#%% Load the file
datapath='civilian_france_death_1816_2020.txt'
# datapath='all_france_death_1816_2020.txt'
print('Loading data...')
data=pd.read_csv(datapath, delimiter=',')

#%% Organise data into a 3D matrix:
# the 3 axis are: date, age, sexe
# the (i,j,k)-th element of the matrix is the number of persons of sex k who
# died within the j-th age interval during the i-th year
ages = np.hstack(([0,1],np.arange(5,105.1,5))) # ages interval
sexs = np.array(['f', 'm']) # we ignore potential 'both'-type sex declaration
sexnames = ['women', 'men']

def getTypedData(d,key,typ):
  res=[]
  for val in d[key]:
    try:
      current_val = typ(val)
      res.append(current_val)
    except ValueError: # not a number (i.e. 'TOT' o 'UNK')
      pass
  return np.unique(res)

years     = getTypedData(d=data,key='Year',typ=int)
data_ages = getTypedData(d=data,key='Age',typ=int)

#%% Parse input data:
# for each entry, we add the number of dead persons to the corresponding
# age-interval / sex / year element in the 3D matrix
# This allows to cope with different levels of refinment in terms of age-interval
# in  the original data

# Here, we first set, for all ages found in the input data, the age-class it
# will be attributed to
candidates_ages = np.arange(0,130,1)
index_age = np.zeros_like(candidates_ages)
for i, candi_age in enumerate(candidates_ages):
  # print(candi_age)
  bFound=False
  for ii in range(len(ages)):
    if ages[ii] >= candi_age:
      index_age[i] = ii
      bFound=True
      # print(' -->', ages[ii])
      break
    if ages[-1]<=candi_age:
      index_age[i] = len(ages)-1
      bFound=True
  assert bFound
  
#%% Fill in the 3D matrix
from tqdm import tqdm
mat3D = np.zeros((years.size, ages.size, sexs.size))
print('Organising data\n')
for iyear, year in enumerate(tqdm(years)):
  # print(year)
  Iy = np.where(data['Year']==year)[0]
  for isex, sex in enumerate(sexs): 
    Iys = np.where(data['Sex'][Iy] == sex)[0]
    I = Iy[Iys] # sub-subset
    # assert np.all( mat3D[iyear, :, isex] == 0 )
    for i in range(len(I)):
      # if str(data['Area'][I[i]])[-1]=='0': # only keep data on the whole territory
      if np.mod(data['Area'][I[i]],10)==0: # only keep data on the whole territory
        try:
          age = int( data['Age'][I[i]] )
        except ValueError:
          # print( data['Age'][I[i]] )
          continue # age was not an integer
        iage = index_age[age]
        # add contribution to the matrix
        mat3D[iyear, iage, isex] += data['Deaths'][I[i]]


#%% Plot total deaths
current_matrix = mat3D.copy()
# current_matrix[:,np.where(ages<15)[0],:] = 0 # remove infant deaths

plt.figure()
for isex in range(len(sexs)):
  plt.plot(years, np.sum(current_matrix[:,:,isex],axis=1), label=sexnames[isex])
plt.grid()
plt.legend()
plt.xlabel('year')
plt.ylabel('total deaths')
plt.ylim(0,None)

#%% Plot proportion of infant death
current_matrix = mat3D.copy()
current_matrix[:,np.where(ages<15)[0],:] = 0 # remove infant deaths

plt.figure()
for isex in range(len(sexs)):
  deaths_with_infants    = np.sum(mat3D[:,:,isex],axis=1)
  deaths_without_infants = np.sum(current_matrix[:,:,isex],axis=1)
  plt.plot(years, 100*(deaths_with_infants - deaths_without_infants) / deaths_with_infants, label=sexnames[isex])
plt.grid()
plt.legend()
plt.xlabel('year')
plt.ylabel('%')
plt.title('Contribution of infant mortality to overall mortality')
plt.ylim(0,None)

#%% Prepare infant-mortality-free data
mat3D_without_infant = mat3D.copy()
mat3D_with_infant    = mat3D.copy()

mat3D_without_infant[:,np.where(ages<15)[0],:] = 0 # remove infant deaths

# normalize death count to one for each year
mat3D_with_infant_proportion    = np.zeros_like(mat3D_with_infant)
mat3D_without_infant_proportion = np.zeros_like(mat3D_without_infant)
for i in range(len(years)):
  for isex in range(len(sexs)):
    mat3D_without_infant_proportion[i,:,isex] = mat3D_without_infant[i,:,isex] / np.sum( mat3D_without_infant[i,:,isex] )
    mat3D_with_infant_proportion[i,:,isex]   =     mat3D_with_infant[i,:,isex] / np.sum(    mat3D_with_infant[i,:,isex] )

#%% Compute means
mean_without_infant = np.zeros((years.size, sexs.size))
mean_with_infant = np.zeros((years.size, sexs.size))
for iyear in range(len(years)):
  for isex in range(len(sexs)):
    deces = mat3D_without_infant[iyear,:,isex]
    mean_without_infant[iyear,isex] = np.sum( deces*ages ) / np.sum( deces )
    
    deces = mat3D_with_infant[iyear,:,isex]
    mean_with_infant[iyear,isex] = np.sum( deces*ages ) / np.sum( deces )
    
#%% Compute quartiles of death age
# What are the ages 25%, 25%, 75% of the people die before at each year ?
cumulatedProportion_without_infant = np.cumsum(a=mat3D_without_infant_proportion, axis=1) # sums up to one for each year
cumulatedProportion_with_infant    = np.cumsum(a=mat3D_with_infant_proportion, axis=1)

quantiles_points = np.array((0.25, 0.5, 0.75))
def getQuantiles(proportion_matrix):
  # compute quartiles on given proportion array
  quantiles = np.zeros((quantiles_points.size, years.size, sexs.size))
  # corresponding_proportions = np.zeros((quantiles_points.size, years.size, sexs.size))
  for iyear in range(years.size):
    # print(iyear)
    for isex in range(sexs.size):
      for iquart, quart in enumerate(quantiles_points):
        func = scipy.interpolate.interp1d(x=ages, y=proportion_matrix[iyear,:,isex] - quart,
                                          kind='linear')
        try:
          quantiles[iquart, iyear, isex] = scipy.optimize.brentq(f=func,
                                                                  a=ages[0], b=ages[-1],
                                                                  xtol=1e-10, rtol=1e-10, maxiter=100)
        except ValueError: # solution is at the low bound
          quantiles[iquart, iyear, isex] = ages[0]
  
        # age_index = scipy.interpolate.interp1d(x=range(len(ages)), y=ages, kind='linear')
        # # func_index = func(ages[0] + index*(ages[-1]-ages[0]))
        # def func_index(index): # linear interpolation of cumulated prop based on age
        #   floor_i = int(np.floor(index)) 
        #   yi   = proportion_matrix[iquart, floor_i,   isex]
        #   yip1 = proportion_matrix[iquart, floor_i+1, isex]
        #   return yi + (yip1-yi)*(index-floor_i)
          
        # # find the (decimal) inteporlated index
        # index = scipy.optimize.brentq(f=func_index,
        #                               a=0, b=len(ages)-2,
        #                               xtol=1e-10, rtol=1e-10, maxiter=100)
        # quantiles[iquart, iyear, isex] = age_index(index)
        # corresponding_proportions[iquart, iyear, isex] = func_index(index)
  return quantiles

quantiles_without_infant = getQuantiles(cumulatedProportion_without_infant)
quantiles_with_infant    = getQuantiles(cumulatedProportion_with_infant)

#%% Plot quantiles
plt.figure()
colors = ['tab:blue', 'tab:orange', 'tab:green']
alpha_infant = 0.6
for isex in range(len(sexs)):
  linestyle = ['--', '-'][isex]
  for iquant, quantile_val in enumerate(quantiles_points):
    plt.plot(years, quantiles_without_infant[iquant, :, isex], label=None, color=colors[iquant],
             linestyle=linestyle)

# add quartiles
for isex in range(len(sexs)):
  linestyle = ['--', '-'][isex]
  for iquant, quantile_val in enumerate(quantiles_points):
    plt.plot(years, quantiles_with_infant[iquant, :, isex], label=None, color=colors[iquant],
             linestyle=linestyle, alpha=alpha_infant)

# add means
colormean = 'tab:purple'
for isex in range(len(sexs)):
  linestyle = ['--', '-'][isex]
  plt.plot(years, mean_with_infant[:,isex],    linestyle=linestyle, linewidth=2,
           color=colormean, alpha=1, label=None)
  plt.plot(years, mean_without_infant[:,isex], linestyle=linestyle, linewidth=2,
           color=colormean, alpha=alpha_infant, label=None)


# legend hack
for iquant, quantile_val in enumerate(quantiles_points):
  plt.plot(np.nan, np.nan, linestyle='-', color=colors[iquant], label='{:.0f}%'.format(quantile_val*100))
plt.plot(np.nan, np.nan, linestyle='--', color=[0,0,0], label="women")
plt.plot(np.nan, np.nan, linestyle='-', color=[0,0,0], label="men")
plt.plot(np.nan, np.nan, linestyle='-', color=colormean, label='mean')


plt.legend(loc='lower right', ncol=2)
plt.grid()
plt.xlabel('year')
plt.ylabel('age')
plt.xlim(years[0], years[-1])
plt.ylim(0,100)
plt.title('Evolution of death age in France')
plt.savefig('france_mortality.png', dpi=200)

#%% Surface plot of mortality distribution
xx,yy = np.meshgrid(years, ages)

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
isex=1
surf = ax.plot_surface(xx, yy, mat3D_without_infant_proportion[:,:,0].T, cmap=plt.cm.coolwarm,
                       antialiased=True)
fig.colorbar(surf, shrink=0.5, aspect=5, label='proportion')
fig.suptitle('Relative mortality for {} (without infant mortality)'.format(sexnames[isex]))