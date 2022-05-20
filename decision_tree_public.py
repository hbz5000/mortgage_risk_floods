#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import geopandas as gpd
import rasterio.plot
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap
import scipy.stats as stats
import seaborn as sns
import os
from datetime import datetime

project_folder = os.getcwd()
#datestr = '_5_9_22' #the date the decision tree is run
datestr = '_' + datetime.today().strftime('%m_%d_%Y')
property_id_name = 'public_id' #id for tying everything together


##define filenames ##
damages_filename = project_folder+'/public_input_files/damage_output_public.csv'
parcel_ltv_filename = project_folder + '/public_input_files/ltv_output_public.csv'
nominal_value_filename = project_folder + '/public_input_files/pv_output_public.csv'


#create dictionary with all counties in model and fips codes
fips_list = [13, 15, 17, 19, 29, 31, 41, 47, 49, 51, 53, 55, 61, 65, 73, 79, 83, 85, 93, 91, 95, 101, 103, 107, 
             117, 127, 129, 131, 133, 137, 139, 141, 143, 147, 155, 163, 165, 177, 187, 191, 195] 


counties_dict = {"Beaufort":13,"Bertie":15,"Bladen":17, "Brunswick":19, "Camden":29, "Carteret":31, "Chowan":41,"Columbus":47, "Craven":49, 
              "Cumberland":51,"Currituck":53, "Dare":55, "Duplin":61, "Edgecombe":65, "Gates":73, "Greene":79, "Harnett":85,"Halifax":83, 
                "Hertford":91, "Hoke":93, "Hyde":95, "Johnston":101,"Jones":103,"Lenoir":107,"Martin":117,"Nash":127, "New Hanover":129, 
                "Northampton":131,"Onslow":133,"Pamlico":137,"Pasquotank":139,"Pender":141,"Perquimans":143,"Pitt":147,"Robeson":155,
                "Sampson":163, "Scotland":165,"Tyrrell":177, "Washington":187,"Wayne":191,"Wilson":195} 

##########################################
###########define new data columns#############
#########before joining together#############
property_value_at_event_id = 'pre event value'#id column for krigged property value on date of event
property_value_after_event_id = 'post event pv'

value_range_start = 68
value_range_end = 83
pre_event_quarter_list = ['71', '72', '73', '74']
post_event_quarter_list = ['79', '80', '81', '82'] #one year following Florence, i.e. 2019Q3

#Read synthetic LTV data
parcels_ltv = pd.read_csv(parcel_ltv_filename)
#Read property value data
use_cols_pv = [property_id_name, '68','69','70','71','72','73','74','75','76','77','78','79','80','81','82','83']
parcel_pv = pd.read_csv(nominal_value_filename, usecols = use_cols_pv)
#Read damage filename 
#"damage" field is predicted; "claim" is observed, insured
parcel_damage = pd.read_csv(damages_filename)


#drop any rows that have empty property_id_names otherwise we can't convert to int
parcel_damage.dropna(subset = [property_id_name], inplace=True)
parcels_ltv.dropna(subset = [property_id_name], inplace=True)
parcel_pv.dropna(subset = [property_id_name], inplace=True)

#make sure public_id is integer so all dataframes can be tied together
parcel_damage[property_id_name] = parcel_damage[property_id_name].astype(int) 
parcel_pv[property_id_name] = parcel_pv[property_id_name].astype(int)   
parcels_ltv[property_id_name] = parcels_ltv[property_id_name].astype(int) 

#drop duplicate parcels
parcel_damage = parcel_damage.drop_duplicates(subset=property_id_name)
parcel_pv=parcel_pv.drop_duplicates(subset=property_id_name)
parcels_ltv = parcels_ltv.drop_duplicates(subset=property_id_name)

damage_column_names = [property_id_name, 'damage', 'claim']     

#find average parcel value before & after event     
parcel_pv['before'] = np.zeros(len(parcel_pv.index))
parcel_pv['after'] = np.zeros(len(parcel_pv.index))
for x in pre_event_quarter_list:
    parcel_pv['before'] += parcel_pv[x].astype(float)/len(pre_event_quarter_list)
for x in post_event_quarter_list:
    parcel_pv['after'] += parcel_pv[x].astype(float)/len(post_event_quarter_list)

parcel_pv['change'] = parcel_pv['after'] - parcel_pv['before']
pv_column_names = [property_id_name, 'before', 'after', 'change']
for x in range(68, 83):
    pv_column_names.append(str(x))

#merge LTV data with damage estimations to get residential
parcels_ltv = parcels_ltv.merge(parcel_damage[damage_column_names], on = property_id_name, how = 'left')
parcels_ltv.loc[pd.isnull(parcels_ltv['damage']), 'damage'] = np.zeros(len(parcels_ltv.loc[pd.isnull(parcels_ltv['damage']), 'damage']))
#Then merge LTV, damage dataframe with property values, too
parcels_ltv = parcels_ltv.merge(parcel_pv[pv_column_names], on = property_id_name, how = 'inner')

#Calculate loan balance at the time of the storm using the pre-flood property value and the LTV
parcels_ltv['loan balance'] = parcels_ltv['ltv_2018']*parcels_ltv['before']

#Calculate risk amounts by risk-holder
#0 is NFIP (insureD) --> these are observed losses
#1 is homeowner
#2 is bank
#3 is gov

damages_type = np.zeros(4)
depreciation_type = np.zeros(4)

#insured damage held by NFIP
damages_type[0] = np.sum(parcels_ltv['claim'])

#also store results in a numpy array
#later we will add as new columns to parcels_ltv
#store 9 values
#all the PV, then the damage, then the tax stuff
new_NFIP_dam = np.zeros((len(parcels_ltv.index),8))

#'NFIP_dep':0, 'home_dep':1, 'bank_dep':2, 'gov_dep':3, 
#'NFIP_dam':4, 'home_dam':5, 'bank_dam':6, 'gov_dam':7, 
counter = 0

for index, row in parcels_ltv.iterrows():
  #only calculate losses for damaged parcels
    if row['damage'] > 0.0 or row['claim'] > 0.0:
    #total equity in the parcel at the time of the event
        total_equity = row['before'] - row['loan balance']
        new_NFIP_dam[counter,4] = row['claim']
    #if property value change is less than homeowner equity
    #depreciation risk is held by homeowner
        if total_equity + row['change'] > 0.0:
            depreciation_type[1] += max(row['change'] * (-1.0), 0.0)
            new_NFIP_dam[counter,1] = max(row['change'] * (-1.0), 0.0)
      #if damages + depreciation are still less than total equity
      #damage risk is held by homeowner
            if total_equity + row['change'] - row['damage'] > 0.0:
                damages_type[1] += row['damage']
                new_NFIP_dam[counter,5] = row['damage']
          #if the damages are greater than the post-event property value
          #the local government pays $20,000 to demolish the building
          #homeowner loses their remaining equity, mortgage holder loses loan amount
            elif row['damage'] > row['after']:
                damages_type[3] += 20000.0
                damages_type[1] += total_equity - max(row['change'] * (-1.0), 0.0)
                damages_type[2] += row['loan balance']
                new_NFIP_dam[counter,7] = 20000.0
                new_NFIP_dam[counter,5] = total_equity - max(row['change'] * (-1.0), 0.0)
                new_NFIP_dam[counter,6] = row['loan balance']
            else:
                damages_type[1] += total_equity 
                damages_type[2] += row['loan balance'] - row['after'] + row['damage']
                new_NFIP_dam[counter,5] = total_equity 
                new_NFIP_dam[counter,6] = row['loan balance'] - row['after'] + row['damage']
    #if property value changes is greater than homeowner equity
    #the homeowner loses their equity and all damages accrue to mortgage owner
        elif total_equity + row['change'] < 0.0:
            depreciation_type[1] += max(total_equity, 0.0)
            depreciation_type[2] += max((total_equity + row['change']) * (-1.0), 0.0)
            new_NFIP_dam[counter,1] = max(total_equity, 0.0)
            new_NFIP_dam[counter,2] = max((total_equity + row['change']) * (-1.0), 0.0)
            if row['damage'] > row['after']:
                damages_type[3] += 20000.0
                damages_type[2] += row['loan balance'] - max((total_equity + row['change']) * (-1.0), 0.0)
                new_NFIP_dam[counter,7] = 20000.0
                new_NFIP_dam[counter,6] = row['loan balance'] - max((total_equity + row['change']) * (-1.0), 0.0)
            else:
                damages_type[2] += row['damage']
                new_NFIP_dam[counter,6] = row['damage']

    counter += 1

#add output in the numpy array to the dataframe
parcels_ltv['NFIP_dep'] = new_NFIP_dam[:,0]
parcels_ltv['home_dep'] = new_NFIP_dam[:,1]
parcels_ltv['bank_dep'] = new_NFIP_dam[:,2]
parcels_ltv['gov_dep'] = new_NFIP_dam[:,3]
parcels_ltv['NFIP_dam'] = new_NFIP_dam[:,4]
parcels_ltv['home_dam'] = new_NFIP_dam[:,5]
parcels_ltv['bank_dam'] = new_NFIP_dam[:,6]
parcels_ltv['gov_dam'] = new_NFIP_dam[:,7]

parcels_ltv.to_csv(project_folder+"/output_abdt_public"+datestr+".csv")


