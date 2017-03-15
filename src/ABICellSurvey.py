print "Starting script"

# TODO: Tidy up; eliminate memory leaks; add final features; begin working on processing
# functions such as calculating statistics of each parameter

# http://stackoverflow.com/questions/17053435/mysql-connector-python-insert-python-variable-to-mysql-table    
    
redoTables = True # True/False
useTraceback = True     # True/False

installCells = True
runAnalyses = True

print "Importing..."
import sys
# from allensdk.api.queries.cell_types_api import CellTypesApi
from allensdk.ephys.extract_cell_features import extract_cell_features
from allensdk.core.cell_types_cache import CellTypesCache
from allensdk.ephys.feature_extractor import EphysFeatureExtractor
from allensdk.ephys.ephys_extractor import EphysSweepFeatureExtractor
from collections import defaultdict

import mysql.connector
import traceback
import numpy as np
from numpyconversion import NumpyMySQLConverter
import math

from pprint import pprint

#### Create the database from scratch
# [1]
print "\n[1]: Connect to the database or create the database from scratch"; 
sys.stdout.flush()
databaseName = 'ABICellSurvey'

try: 
    cnx = mysql.connector.connect(user='root', password='Uni53mad',
                                  host='localhost', database=databaseName,
                                  converter_class=NumpyMySQLConverter)
    print "Connection complete"
    cursobj = cnx.cursor()
except:
    cnx = mysql.connector.connect(user='root', password='Uni53mad',
                                  host='localhost',
                                  converter_class=NumpyMySQLConverter)
    print cnx
    cursobj = cnx.cursor()
    mycmd = 'create database ' + databaseName
    cursobj.execute(mycmd)
    print "Database created"
    mycmd = 'use ' + databaseName
    cursobj.execute(mycmd)
    print "Using database " + databaseName

if redoTables:
    print "Dropping all tables"
    
    try:
        mycmd = 'DROP TABLE specimenFXs'
        cursobj.execute(mycmd)
        print "specimenFXs table dropped"
    except: 
        if useTraceback:
            traceback.print_exc()
        
        pass
    
    try:
        mycmd = 'DROP TABLE experimentFXs'
        cursobj.execute(mycmd)
        print "experimentFXs table dropped"
    except: 
        if useTraceback:
            traceback.print_exc()
        
        pass
    
    try:
        mycmd = 'DROP TABLE experiments'
        cursobj.execute(mycmd)
        print "experiments table dropped"
    except: 
        if useTraceback:
            traceback.print_exc()
            
        pass

    try:
        mycmd = 'DROP TABLE specimens'
        cursobj.execute(mycmd)
        print "specimens table dropped"
    except: 
        if useTraceback:
            traceback.print_exc()
            
        pass

    try:
        mycmd = 'DROP TABLE donors'
        cursobj.execute(mycmd)
        print "donors table dropped"
    except: 
        if useTraceback:
            traceback.print_exc()
            
        pass

    # -----
    print "Creating tables"
   
    # Table donors
    mycmd = ('''CREATE TABLE donors (''' + 
             '''id int(11) NOT NULL AUTO_INCREMENT, ''' + 
             '''abiDonorID int(11), ''' + 
             '''sex char(4), ''' + 
             '''name char(100), ''' + 
             '''PRIMARY KEY (id)) ENGINE=InnoDB''')
    try:
        cursobj.execute(mycmd)
        print "Table donors created"
    except:
        if useTraceback:
            traceback.print_exc()
            
        pass
        print "Table donors not created"


    # Table specimens
    mycmd = ('''CREATE TABLE specimens (''' + 
             '''id int(11) NOT NULL AUTO_INCREMENT, ''' + 
             '''donorID int(11), ''' + 
             '''abiSpecimenID int(11), ''' +
             '''FOREIGN KEY (donorID) REFERENCES donors (id) ON DELETE CASCADE, ''' +  
             '''PRIMARY KEY (id)) ENGINE=InnoDB''')
    try:
        cursobj.execute(mycmd)
        print "Table specimens created"
    except:
        if useTraceback:
            traceback.print_exc()
            
        pass
        print "Table specimens not created"

    # Table experiments
    mycmd = ('''CREATE TABLE experiments (''' + 
             '''id int(11) NOT NULL AUTO_INCREMENT, ''' + 
             '''specimenIDX int(11) NOT NULL, ''' +
             '''abiExperimentID int(11), ''' +
             '''expFXID int(11), ''' +          # probably not necessary
             '''sampling_rate int(11), ''' +
             '''stimulusType char(100), ''' + 
             '''stimCurrent double, ''' +
             '''FOREIGN KEY(specimenIDX) REFERENCES specimens(id) ON DELETE CASCADE, ''' + 
             '''PRIMARY KEY (id)) ENGINE=InnoDB''')
    try:
        cursobj.execute(mycmd)
        print "Table experiments created"
    except:
        if useTraceback:
            traceback.print_exc()
            
        pass
        print "Table experiments not created"


    # Table specimenFXs
    # This table designed primarily from ephys_features output
    # See https://alleninstitute.github.io/AllenSDK/_static/examples/nb/cell_types.html#Computing-Electrophysiology-Features
    # See also extractCellFeaturesAnalysis.txt
    # How is hero sweep chosen?
    # Features specific to cell level (typically average, or any)
    mycmd = ('''CREATE TABLE specimenFXs (''' + 
             '''id int(11) NOT NULL AUTO_INCREMENT, ''' + 
             '''specID int(11) NOT NULL, ''' + 
#              '''abiFXID int(11) NOT NULL, ''' + 
             '''hasSpikes bool, ''' +                       # xcf-based
             '''hero_sweep_id int(11), ''' +                # ephys_features hero sweep 
             '''hero_sweep_avg_firing_rate double, ''' +    # ephys_features hero sweep 
             '''hero_sweep_adaptation double, ''' +         # ephys_features hero sweep 
             '''hero_sweep_first_isi double, ''' +          # ephys_features hero sweep
             '''hero_sweep_mean_isi double, ''' +           # ephys_features hero sweep
             '''hero_sweep_median_isi double, ''' +         # ephys_features hero sweep
             '''hero_sweep_isi_cv double, ''' +             # ephys_features hero sweep
             '''hero_sweep_latency double, ''' +            # ephys_features hero sweep
             '''hero_sweep_stim_amp double, ''' +           # ephys_features hero sweep
             '''hero_sweep_v_baseline double, ''' +         # ephys_features hero sweep
             '''dendrite_type char(15), ''' +               #   ***  
             '''electrode_0_pa double, ''' +                # ephys_features 
             '''f_i_curve_slope double, ''' +               # ephys_features
             '''fast_trough_t_long_square double, ''' +     # ephys_features 
             '''fast_trough_t_ramp double, ''' +            # ephys_features
             '''fast_trough_t_short_square double, ''' +    # ephys_features
             '''fast_trough_v_long_square double, ''' +     # ephys_features
             '''fast_trough_v_ramp double, ''' +            # ephys_features
             '''fast_trough_v_short_square double, ''' +    # ephys_features
             '''has_bursts bool, ''' +                      # custom 
             '''has_delays bool, ''' +                      # custom
             '''has_pauses bool, ''' +                      # custom
             '''hemisphere char(10), ''' +                  #   ***    
             '''input_resistance_mohm double, ''' +                 # xcf ok 
             '''peak_t_long_square double, ''' +            # ephys_features
             '''peak_t_ramp double, ''' +                   # ephys_features
             '''peak_t_short_square double, ''' +           # ephys_features
             '''peak_v_long_square double, ''' +            # ephys_features
             '''peak_v_ramp double, ''' +                   # ephys_features
             '''peak_v_short_square double, ''' +           # ephys_features
             '''reporter_status char(30), ''' +             #   ***
             '''rheobase_current double, ''' +                      # xcf ok 
             '''ri double, ''' +                            # ephys_features input_resistance
             '''sagFraction double, ''' +                   # xcf ok
             '''seal_gohm double, ''' +                     # ephys_features
             '''slow_trough_t_long_square double, ''' +     # ephys_features
             '''slow_trough_t_ramp double, ''' +            # ephys_features
             '''slow_trough_t_short_square double, ''' +    # ephys_features
             '''slow_trough_v_long_square double, ''' +     # ephys_features
             '''slow_trough_v_ramp double, ''' +            # ephys_features
             '''slow_trough_v_short_square double, ''' +    # ephys_features
             '''structure_acronym char(20), ''' +           #   ***
             '''structure_name char(50), ''' +              #   ***
             '''tau double, ''' +                                    # xcf ok or ephys_features??
             '''threshold_i_long_square double, ''' +       # ephys_features
             '''threshold_i_ramp double, ''' +              # ephys_features
             '''threshold_i_short_square double, ''' +      # ephys_features
             '''threshold_t_long_square double, ''' +       # ephys_features
             '''threshold_t_ramp double, ''' +              # ephys_features
             '''threshold_t_short_square double, ''' +      # ephys_features
             '''threshold_v_long_square double, ''' +       # ephys_features
             '''threshold_v_ramp double, ''' +              # ephys_features
             '''threshold_v_short_square double, ''' +      # ephys_features
             '''transgenic_line char(30), ''' +             #   ***
             '''trough_t_long_square double, ''' +          # ephys_features
             '''trough_t_ramp double, ''' +                 # ephys_features
             '''trough_t_short_square double, ''' +         # ephys_features
             '''trough_v_long_square double, ''' +          # ephys_features
             '''trough_v_ramp double, ''' +                 # ephys_features
             '''trough_v_short_square double, ''' +         # ephys_features
             '''upstroke_downstroke_ratio_long_square double, ''' +  # ephys_features
             '''upstroke_downstroke_ratio_ramp double, ''' +         # ephys_features
             '''upstroke_downstroke_ratio_short_square double, ''' + # ephys_features
             '''v_rest double, ''' +                        # xcf ok or ephys_features?? 
             '''vm_for_sag double, ''' +                    # xcf ok
             '''FOREIGN KEY(specID) REFERENCES specimens(id) ON DELETE CASCADE, ''' +
             '''PRIMARY KEY (id)) ENGINE=InnoDB''')

    try:
        cursobj.execute(mycmd)
        print "Table specimenFXs created"
    except:
        if useTraceback:
            traceback.print_exc()
            
        pass
        print "Table specimenFXs not created"

    # Table experimentFXs
    # Features specific to sweep/experiment level
    mycmd = ('''CREATE TABLE experimentFXs (''' + 
             '''id int(11) NOT NULL AUTO_INCREMENT, ''' +
             '''expID int(11) NOT NULL, ''' +  
             '''abiFXID int(11) NOT NULL, ''' +
             '''analysisStart double, ''' +                         #           in seconds
             '''analysisDuration double, ''' +                      #           in seconds
             '''adaptation double, ''' +                            # xcf ok    
             '''avgFiringRate double, ''' +                         # xcf ok    spikes per second
             '''hasSpikes bool, ''' +                               # xcf ok    1=true;0=false
             '''numSpikes int(11), ''' +                            # xcf ok    
             '''hasBursts bool, ''' +                               #           1=true;0=false                                   
             '''numBursts int(11), ''' +                            #
             '''maxBurstiness double, ''' +                         #
             '''hasPauses bool, ''' +                               #           1=true;0=false
             '''numPauses int(11), ''' +                            #           
             '''pauseFraction double, ''' +                         #           %
             '''hasDelays bool, ''' +                               #           REMOVE THIS
             '''delayRatio double, ''' +                            #           
             '''delayTau double, ''' +                              #           
             '''first_isi double, ''' +                             # xcf ok    in seconds
             '''mean_isi double, ''' +                              # xcf ok    in seconds
#              '''median_isi double, ''' +                          # xcf ok    in seconds
             '''isi_cv double, ''' +                                # xcf ok    dimensionless
             '''f_peak double, ''' +                                #           in milliVolts
             '''latency double, ''' +                               # xcf ok    in seconds
             '''threshold double, ''' +                             #           in milliVolts
             '''FOREIGN KEY(expID) REFERENCES experiments(id) ON DELETE CASCADE, ''' +
             '''PRIMARY KEY (id)) ENGINE=InnoDB''')

    try:
        cursobj.execute(mycmd)
        print "Table experimentFXs created"
    except:
        if useTraceback:
            traceback.print_exc()
            
        pass
        print "Table experimentFXs not created"

        
# ====================================================================
# Install the ABI Datasets
# Choose specimens and experiments; these are just for testing
# [2]
print "\n[2]: Install the ABI Datasets into the database"; sys.stdout.flush()
# specimens = [484635029]
# specimens = [318808427]
# specimens = [321707905] # Hopefully has bursts (no, but has delays/pauses)
# specimens = [
#             321707905,
#             484635029,
#             469801569,
#             469753383]
# specimens = [312883165,484635029]
# specimens with models only 
specimens = [
            484635029,
            469801569,
            469753383,
            487667205,
            468120757,
            476104386,
            484742372,
            475622793,
            464188580,
            478058328,
            476218657,
            318808427,
            479704527,
            324493977,
            483020137,
            464212183,
            476457450,
            324266189,
            478107198,
            476686112,
            478396248,
            485058595,
            475622680,
            327962063,
            474267418,
            466664172,
            474626527,
            464198958]

# [3]
print "\n[3]: Get the cell data if not in cache"; sys.stdout.flush()
# Instantiate the CellTypesCache instance.  
ctc = (CellTypesCache(manifest_file='C:/Users/David/Dropbox/Documents/'
     + 'SantamariaLab/Projects/Fractional/ABI-FLIF/FeatExtractDev/'
     + 'cell_types/cell_types_manifest.json'))

# Get all cells with reconstructions
cells = ctc.get_cells(require_reconstruction=True)

####### ALL DONORS #######
# Populate the donors table
print "\n[4]: Populating donors table"
for cell in cells:
    queryStr = 'select * from donors where abiDonorID=' + str(cell['donor_id'])
#     print queryStr
    cursobj.execute(queryStr)
    row = cursobj.fetchone()
#     print type(row), row
#     print "donor:"
#     pprint(cell['donor'])
    if row is None:
        insertStr = ('insert into donors (id, abiDonorID, sex, name) ' +
                     ' values(%s, %s, %s, %s)')
        insertData = (0, cell['donor_id'], cell['donor']['sex'], 
                      cell['donor']['name'])
#         print insertStr
#         pprint(insertData)
        cursobj.execute(insertStr, insertData)
        donorid = cursobj.lastrowid
#         print "donorid:", donorid
        cnx.commit()

####### SPECIMENS #######
print "\n[5]: Process each specimen in turn"; sys.stdout.flush()
for specimen in specimens:
    # this saves the NWB file to '...FeatExtractDev/cell_types/specimen_XXXXXXXXX/ephys.nwb'
    print 'Processing:', specimen
    try:
        specEphysData = ctc.get_ephys_data(specimen)
#         print "specEphysData"
#         pprint(specEphysData)
    except:
        print "No ephys data for specimen ", specimen
        continue

    try:
        ephys_features = ctc.get_ephys_features()
#         print "ephys_features"
#         pprint(ephys_features)
    except:
        print "No ephys features for specimen ", specimen
        continue

#     print type(data_set)
#     pprint(data_set)
#     sys.exit("Error message")
#     dsspec = data_set['specimen_id']
#     print "Specimen:", specimen, "dsspec:", dsspec
#     sys.exit("Error message")

    if False:
#     if True:
        morphFeat = ctc.get_morphology_features()
#         print "morphFeat:"
#         pprint(morphFeat)
        for spec in morphFeat:
            intspec = int(spec['specimen_id']) 
            if intspec==specimen:
                print "specimen:", intspec, "  soma_surface:", spec['soma_surface']
                pprint(spec)
                break

#     sys.exit("Not an error message")


    # START HERE ---- this cell is a dictionary that has most of the "other" non-sweep stuff
    # we need such as cell averages, rheobase info, transgenic line, hemisphere, 
    # age, sex, graph order, dendrite type, area, has_burst,...
    for cell in cells:
#         print "cell:"
#         pprint(cell)
        datasets = cell['data_sets']
        for dataset in datasets:
            dsspec = dataset['specimen_id']
            if dsspec == specimen:
                specCell = cell
                break
            
    # handle specimen id not found 
    
    # Add the specimen to the database
    donorID = specCell['donor_id']
#     print "specCell donor:", donorID
    queryStr = 'select id from donors where abiDonorID=' + str(donorID)
#     print queryStr
    temp = cursobj.execute(queryStr)
    row = cursobj.fetchone()
#     print row
    donorID = row[0]
#     print "fetched donor:", donorID

    insertStr = ('insert into specimens (id, donorID, abiSpecimenID) ' + 
                 'values (%s, %s, %s)')
    insertData = (0, donorID, specimen)
    cursobj.execute(insertStr, insertData)
    specimenTableID = cursobj.lastrowid
#     print "specimenTableID:", specimenTableID
    cnx.commit()

    # Update these if sweeps show them
    cellHasBursts = False
    cellHasDelays = False
    cellHasPauses = False
    
    ####### SWEEPS/EXPERIMENTS #######
    # Add the sweep/experiment to the database
    sweeps = ctc.get_ephys_sweeps(specimen)
    for sweep in sweeps:
        sweepNum = sweep['sweep_number']
        print "Processing experiment ", sweepNum

        print ("sweep_number:", sweepNum, 
               "   stimulus:", sweep['stimulus_name'], 
               "   num_spikes", sweep['num_spikes'])
#         print sweep
        if sweep['stimulus_name'] not in ['Long Square', 'Short Square']:
            continue

        sweep_data = specEphysData.get_sweep(sweepNum)
#         print "sweep_data", sweep_data
        print "Index Range: ", sweep_data["index_range"] 
        sweep_metadata = specEphysData.get_sweep_metadata(sweepNum)
#         print "sweep_metadata", sweep_metadata
        
        sampling_rate = sweep_data["sampling_rate"] # in Hz
#         print "Sampling Rate: ", sampling_rate        
        
        # Need to check if this sweep is actually an experiment
        # (not implemented yet)
        
#         print (type(specimenTableID), type(sweepNum), type(None), 
#                type(sweep_metadata['aibs_stimulus_name']), 
#                type(sweep_metadata['aibs_stimulus_amplitude_pa']))
        insertStr = ('insert into experiments (id, specimenIDX, ' + 
                     'abiExperimentID, expFXID, sampling_rate, ' + 
                     'stimulusType, stimCurrent) ' + 
                     'values (%s, %s, %s, %s, %s, %s, %s)')
        insertData = (int(0), specimenTableID, sweepNum, None, sampling_rate, 
                      sweep_metadata['aibs_stimulus_name'], 
                      float(sweep_metadata['aibs_stimulus_amplitude_pa']))
        cursobj.execute(insertStr, insertData)
        experimentIDX = cursobj.lastrowid
#         print "experimentIDX:", experimentIDX


#     # Create the data plot
#     print "\n    -- getting sweep data"
#     print "Sweep Number: ", spex.expNum
#     sweep_data = data_set.get_sweep(spex.expNum)
#     print sweep_data
#     print "Index Range: ", sweep_data["index_range"] 
# #     print "Stimulus Name:", sweep_data["aibs_stimulus_name"]
#     sweep_metadata = data_set.get_sweep_metadata(spex.expNum)
#     print sweep_metadata
#     
        
    # Create the experiment feature extraction data    
    # http://alleninstitute.github.io/AllenSDK/_static/examples/nb/cell_types.html#Computing-Electrophysiology-Features
#     # index_range[0] is the "experiment" start index. 0 is the "sweep" start index
        index_range = sweep_data["index_range"]
#     # i = sweep_data["stimulus"][index_range[0]:index_range[1]+1] # in A
#     # v = sweep_data["response"][index_range[0]:index_range[1]+1] # in V
        i = sweep_data["stimulus"][0:index_range[1]+1] # in A
        v = sweep_data["response"][0:index_range[1]+1] # in V
        print "++++ index_range[0], index_range[1]", index_range[0], index_range[1]
        i *= 1e12 # to pA
        v *= 1e3 # to mV
        t = np.arange(0, len(v)) * (1.0 / sampling_rate)
#     
#     print "    -- plotting sweep data"
#     plt.style.use('ggplot')
#     fig, axes = plt.subplots(2, 1, sharex=True)
#     axes[0].plot(t, v, color='black')
#     axes[1].plot(t, i, color='gray')
#     axes[0].set_ylabel("Response (mV)")
#     axes[1].set_ylabel("Stimulus (pA)")
#     axes[1].set_xlabel("time (seconds)")
#     fig.suptitle('Specimen ID: ' + str(spex.specNum) + 
#                  ', Sweep: '  + str(spex.expNum) + 
#                  ', Stimulus: ' + sweep_metadata['aibs_stimulus_name'],
#                  fontsize=12)
#     voltageFigurePath = figuresDir + '/' + str(spex.specNum) + '-' + str(spex.expNum) + '.png' 
#     plt.savefig(voltageFigurePath)
#     plt.close
# 
#     # Do the feature extraction
#     # (not completed yet)
        fx = EphysFeatureExtractor()  # +++++++++++++++++++++++++++++++++++++++++++
# 
#     # NEED TO MAKE THESE INDIVIDUALLY DATA-DEPENDENT?
        stim_start = index_range[0]/sampling_rate
        stim_duration = index_range[1]/sampling_rate - 0.1
#     
    # Determining the stim_start and stim_duration automatically is unclear. 
    # Also, stim_duration (as listed in the documentation for, say, process_instance)
    #  is apparently effectively analysis_duration which 
    #  is a bad assumption imho since there may be results that occur or persist
    # after the stimulus is complete. Easy example: using 3 msec duration on 
    # short square misses the cell's spike.  and in fact, it doesn't seem possible
    # to calculate the beginning of the pulse from anything but doing analysis 
    # of the stimulus data itself. 
    # So instead, we use hard-coded values that match those used by ABI in the
    # stimulus signal design.
    # Note that analysis_start refers to
    
        # Hardcoded stimulus delay
        # assume for now is the same for all experiments and stimulus types
        # See https://github.com/AllenInstitute/AllenSDK/issues/37
        stimulus_delay = 0.02  # how to get this from the database?
        stimType = sweep_metadata['aibs_stimulus_name']
        if stimType == 'Long Square':
            analysis_start = 1.0 + stimulus_delay
            analysis_duration = 2.0
        else:
            if stimType == 'Short Square':
                analysis_start = 1.0 + stimulus_delay
                analysis_duration = 1.0
            else:
                # Ramp; not sure what to do yet; haven't found a combo that doesn't
                # result in error inside the process_instance routine
                analysis_start = 1.0 + stimulus_delay
                analysis_duration = 2.0
                
        # Trim the analysis to end of response if necessary
        if (analysis_start + analysis_duration) * sampling_rate >= index_range[1]:
            end_time = (index_range[1]-1)/sampling_rate
            analysis_duration = end_time - analysis_start
            print "Adjusting analysis_duration to fit response length..."

        # temp for debugging
        # Processing is super (improperly) sensitive to this setting.
#         analysis_start = stim_start
#         analysis_duration = stim_duration
#         analysis_start = 1.0
#         analysis_duration = 2.0
        print 'analysis_start', analysis_start, 'analysis_duration', analysis_duration

        # ?????
        # Following is approach seen at 
        # http://alleninstitute.github.io/AllenSDK/_static/examples/nb/cell_types.html#Computing-Electrophysiology-Features
        # THIS EXAMPLE MAY BE INCORRECT, BECAUSE THE START OF THE STIMULUS IS AFTER 1.0 SECONDS
#         fx.process_instance("", v, i, t, analysis_start, analysis_duration, stimType)

        try:
            fx.process_instance("", v, i, t, analysis_start, analysis_duration, "")
        except:
            if useTraceback:
                traceback.print_exc()
            print "Skipping experiment: ", sweepNum, " and continuing..."
            continue
            
        feature_data = fx.feature_list[0].mean
#         print "" 
#         print "feature_list: ", fx.feature_list
#         print "" 
#         print "feature_data: ", feature_data 
         
        pulseCurrent = sweep_metadata['aibs_stimulus_amplitude_pa']
         
        # pull out the desired individual features here
        numSpikes = feature_data['n_spikes']
        hasSpikes = numSpikes != 0
#         if numSpikes == 1:
#             print 'first spike time: ', feature_data['spikes'][0]['t']
     
        if numSpikes >= 2:
#             print 'second spike time: ', feature_data['spikes'][1]['t']
            ISIFirst = feature_data['spikes'][1]['t'] - feature_data['spikes'][0]['t']
        else:
            ISIFirst = None
               
        if 'adapt' in feature_data:
            f_dadaptation = feature_data['adapt']
            print "f_dadaptation", f_dadaptation
        else:
            f_dadaptation = None
            
        if 'latency' in feature_data:
            f_dlatency = feature_data['latency']
            print "f_dlatency", f_dlatency
        else:
            f_dlatency = None
              
        if 'ISICV' in feature_data:
            f_dISICV = feature_data['ISICV']
            print "f_dISICV", f_dISICV
        else:
            f_dISICV = None
         
        if 'isi_avg' in feature_data:
            f_dISIMean = feature_data['isi_avg']
            print "f_dISIMean", f_dISIMean
        else:
            f_dISIMean = None
             
        if 'rate' in feature_data:
            f_drate = feature_data['rate']
            print "f_drate", f_drate
        else:
            f_drate = None

        if 'threshold' in feature_data:
            threshold = feature_data['threshold']  # Not really sure if this is correct
        else: 
            threshold = None
            
        baseV = feature_data['base_v']
        if 'f_peak' in feature_data: 
            averageSpikePeak = feature_data['f_peak']
        else:
            averageSpikePeak = None  

        if 'id' in sweep:
            abiFXID = sweep['id']
        else:
            abiFXID = None
     
#         print 'hasSpikes:',  hasSpikes 
#         print 'numSpikes:',  numSpikes 
#         print 'latency:',    latency 
#         print 'ISIMean:',    ISIMean 
#         print 'ISIFirst:',   ISIFirst 
#         print 'ISICV:',      ISICV 
#         print 'adaptation:', adaptation 
#         print 'threshold:', threshold
#         print 'averageSpikePeak', averageSpikePeak

        # ?????
        # This approach seen in code at 
        # https://alleninstitute.github.io/AllenSDK/_modules/allensdk/ephys/ephys_extractor.html#EphysSweepFeatureExtractor._process_spike_related_features
        sfx = EphysSweepFeatureExtractor(t, v, i, 
                                         analysis_start, analysis_duration)
#             sfx = EphysSweepFeatureExtractor(id=abiFXID)
#             sfxDict = sfx.as_dict()
#             pprint(sfxDict)
        if numSpikes >= 2:  # process_spikes() does not work if fewer than 2
            print "numSpikes: ", numSpikes
#             print 'analysis_start', analysis_start, 'analysis_duration', analysis_duration
            try:
                sfx.process_spikes()
#                 print "Spikes processed"

                try:
                    adaptation = sfx.sweep_feature('adapt')
                except:
                    adaptation = None

                try:
                    latency = sfx.sweep_feature('latency')
                except:
                    latency = None

                try:
                    ISICV = sfx.sweep_feature('isi_cv')
                except:
                    ISICV = None

                try:
                    ISIMean = sfx.sweep_feature('mean_isi')
                except:
                    ISIMean = None

                try:
                    ISIMedian = sfx.sweep_feature('median_isi')
                except:
                    ISIMedian = None

                try:
                    ISIFirst = sfx.sweep_feature('first_isi')
                except:
                    ISIFirst = None

                try:
                    avgFiringRate = sfx.sweep_feature('avg_rate')
                except:
                    avgFiringRate = None

                print "adaptation", adaptation
                print "latency", latency
                print "ISICV", ISICV
                print "ISIMean", ISIMean
                print "ISIMedian", ISIMedian
                print "ISIFirst", ISIFirst
                print "avgFiringRate", avgFiringRate
                        
                try:
                    print "Burst data for this experiment (max_burstiness_index - normalized max rate in burst vs out, num_bursts - number of bursts detected):"
                    burstMetrics = sfx.burst_metrics()
                    pprint(burstMetrics)
                    maxBurstiness = burstMetrics[0]
                    numBursts = burstMetrics[1]
                    hasBursts = numBursts!=0
                except:
                    if useTraceback:
                        traceback.print_exc()
                    print "No burst in this experiment"
                    
                try:
                    print "Pause data for this experiment (num_pauses - number of pauses detected, pause_fraction - fraction of interval [between start and end] spent in a pause):"
                    pauseMetrics = sfx.pause_metrics()
                    pprint(pauseMetrics)
                    numPauses = pauseMetrics[0]
                    hasPauses = numPauses!=0
                    pauseFraction = pauseMetrics[1]
                except:
                    if useTraceback:
                        traceback.print_exc()
                    print "No pause in this experiment"
                    
                try: 
                    print "Delay data for this experiment (delay_ratio - ratio of latency to tau [higher means more delay], tau - dominant time constant of rise before spike):"
                    delayMetrics = sfx.delay_metrics()
                    pprint(delayMetrics)
                    delayRatio = delayMetrics[0]
                    delayTau = delayMetrics[1]
                    if delayTau!=0.0:
                        hasDelays = True
                    else:
                        hasDelays = False
                        delayTau = None
                except:
                    if useTraceback:
                        traceback.print_exc()
                    print "No delay in this experiment"
            except:
                if useTraceback:
                    traceback.print_exc()
                print "process_spikes() failed"
        else:
            adaptation = None
            latency = None
            ISICV = None
            ISIMean = None
            ISIMedian = None
            ISIFirst = None
            avgFiringRate = None
            hasBursts = False
            numBursts = 0
            maxBurstiness = None
            hasPauses = False
            numPauses = 0
            pauseFraction = None
            hasDelays = False
            delayRatio = None
            delayTau = None
            
#         print "hasBursts:", hasBursts, ", numBursts:", numBursts, ", maxBurstiness:", maxBurstiness
#         print "hasPauses:", hasPauses, ", numPauses:", numPauses, ", pauseFraction:", pauseFraction
#         print "hasDelays:", hasDelays, ", delayRatio:", delayRatio, ", delayTau:", delayTau
        if hasBursts:
            cellHasBursts = True
            
        if hasPauses:
            cellHasPauses = True
            
        if hasDelays:
            cellHasDelays = True
             
#             sys.exit("Not an error message")
#AttributeError: EphysSweepFeatureExtractor instance has no attribute '_spikes_df'

        # Add the feature extraction to the database
        insertStr = ('insert into experimentFXs (' + 
                     'id, expID, abiFXID, analysisStart, analysisDuration, ' + 
                     'adaptation, avgFiringRate, ' + 
                     'hasSpikes, numSpikes, ' + 
                     'hasBursts, numBursts, maxBurstiness, ' + 
                     'hasPauses, numPauses, pauseFraction, ' +
                     'hasDelays, delayRatio, delayTau, ' +
                     'first_isi, mean_isi, isi_cv, f_peak, latency, threshold) ' + 
                     'values(%s, %s, %s, %s, %s, %s, ' + 
                     '%s, %s, ' +
                     '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ' + 
                     '%s, %s, %s, %s, %s, %s)')
        insertData = (0, experimentIDX, abiFXID,
                      analysis_start, analysis_duration,  
                      adaptation, avgFiringRate, 
                      hasSpikes, int(numSpikes), 
                      hasBursts, int(numBursts), maxBurstiness,
                      hasPauses, int(numPauses), pauseFraction, 
                      hasDelays, delayRatio, delayTau,
                      ISIFirst, ISIMean, ISICV, averageSpikePeak, 
                      latency, threshold)
         
        fixedInsertData = []
        for v in insertData:
            if not isinstance(v, basestring):
                if isinstance(v, float):
                    if math.isnan(v):
                        v = None
            fixedInsertData.append(v)
                    
        print 'insertStr:', insertStr
        print 'fixedInsertData:', fixedInsertData
        print "Inserting into featureExtractions table now"
        cursobj.execute(insertStr, fixedInsertData)
        fxID = cursobj.lastrowid
        cnx.commit()
#         print fxID, experimentIDX
         
        # Add the fx to the experiment
        updateStr = 'update experiments set expFXID=%s where id=%s'
        updateData = (fxID, experimentIDX)
        cursobj.execute(updateStr, updateData)
        cnx.commit()


#v--------------------
    # Add the specimen feature extraction data to the database
    # Source 1: ephys_features
    cell_ephys_features_list = [f for f in ephys_features if f['specimen_id'] == specimen]
    cell_ephys_features = cell_ephys_features_list[0]
     
    # Source 2: ephys_data
    data_set = ctc.get_ephys_data(specCell['id'])
    sweeps = ctc.get_ephys_sweeps(specimen)
    sweep_numbers = defaultdict(list)
    for sweep in sweeps:
        sweep_numbers[sweep['stimulus_name']].append(sweep['sweep_number'])

    cell_features = (extract_cell_features(data_set, sweep_numbers['Ramp'], 
                sweep_numbers['Short Square'], sweep_numbers['Long Square']))
#     print "cell_features", cell_features
#     print "hero sweep"
#     pprint(cell_features['long_squares']['hero_sweep'])
    sFXs = {}
    sFXs['hasSpikes']                   = cell_features['long_squares']['spiking_sweeps'] != []
    sFXs['hero_sweep_id']               = cell_features['long_squares']['hero_sweep']['id']
    sFXs['hero_sweep_avg_firing_rate']  = cell_features['long_squares']['hero_sweep']['avg_rate']
    sFXs['hero_sweep_adaptation']       = cell_features['long_squares']['hero_sweep']['adapt']
    sFXs['hero_sweep_first_isi']        = cell_features['long_squares']['hero_sweep']['first_isi']
    sFXs['hero_sweep_mean_isi']         = cell_features['long_squares']['hero_sweep']['mean_isi']
    sFXs['hero_sweep_median_isi']       = cell_features['long_squares']['hero_sweep']['median_isi']
    sFXs['hero_sweep_isi_cv']           = cell_features['long_squares']['hero_sweep']['isi_cv']
    sFXs['hero_sweep_latency']          = cell_features['long_squares']['hero_sweep']['latency']
    sFXs['hero_sweep_stim_amp']         = cell_features['long_squares']['hero_sweep']['stim_amp']
    sFXs['hero_sweep_v_baseline']       = cell_features['long_squares']['hero_sweep']['v_baseline']
    sFXs['dendrite_type']               = specCell['dendrite_type']
    sFXs['electrode_0_pa']              = cell_ephys_features['electrode_0_pa']
    sFXs['f_i_curve_slope']             = cell_ephys_features['f_i_curve_slope']
    sFXs['fast_trough_t_long_square']   = cell_ephys_features['fast_trough_t_long_square']     
    sFXs['fast_trough_t_ramp']          = cell_ephys_features['fast_trough_t_ramp']    
    sFXs['fast_trough_t_short_square']  = cell_ephys_features['fast_trough_t_short_square']  
    sFXs['fast_trough_v_long_square']   = cell_ephys_features['fast_trough_v_long_square']
    sFXs['fast_trough_v_ramp']          = cell_ephys_features['fast_trough_v_ramp']    
    sFXs['fast_trough_v_short_square']  = cell_ephys_features['fast_trough_v_short_square']
#     sFXs['has_bursts']             = cell_ephys_features['has_burst']    # could not trace source of this at cell level; need to create custom function
#     sFXs['has_delays']             = cell_ephys_features['has_delay']    # could not trace source of this at cell level; need to create custom function    
#     sFXs['has_pauses']             = cell_ephys_features['has_pause']    # could not trace source of this at cell level; need to create custom function
    sFXs['has_bursts']                  = cellHasBursts
    sFXs['has_delays']                  = cellHasDelays    
    sFXs['has_pauses']                  = cellHasPauses
    sFXs['hemisphere']                  = specCell['hemisphere'] 
    sFXs['input_resistance_mohm']       = cell_ephys_features['input_resistance_mohm']
    sFXs['peak_t_long_square']          = cell_ephys_features['peak_t_long_square']
    sFXs['peak_t_ramp']                 = cell_ephys_features['peak_t_ramp']    
    sFXs['peak_t_short_square']         = cell_ephys_features['peak_t_short_square']
    sFXs['peak_v_long_square']          = cell_ephys_features['peak_v_long_square'] 
    sFXs['peak_v_ramp']                 = cell_ephys_features['peak_v_ramp']    
    sFXs['peak_v_short_square']         = cell_ephys_features['peak_v_short_square']
    sFXs['reporter_status']             = specCell['reporter_status']
    sFXs['rheobase_current']            = cell_features['long_squares']['rheobase_i'] 
    sFXs['ri']                          = cell_ephys_features['ri']
    sFXs['sagFraction']                 = cell_ephys_features['sag']
    sFXs['seal_gohm']                   = cell_ephys_features['seal_gohm']
    sFXs['slow_trough_t_long_square']   = cell_ephys_features['slow_trough_t_long_square']
    sFXs['slow_trough_t_ramp']          = cell_ephys_features['slow_trough_t_ramp']           
    sFXs['slow_trough_t_short_square']  = cell_ephys_features['slow_trough_t_short_square']
    sFXs['slow_trough_v_long_square']   = cell_ephys_features['slow_trough_v_long_square']  
    sFXs['slow_trough_v_ramp']          = cell_ephys_features['slow_trough_v_ramp']                
    sFXs['slow_trough_v_short_square']  = cell_ephys_features['slow_trough_v_short_square']
    sFXs['structure_acronym']           = specCell['structure']['acronym']  
    sFXs['structure_name']              = specCell['structure']['name']
    sFXs['tau']                         = cell_ephys_features['tau']
    sFXs['threshold_i_long_square']     = cell_ephys_features['threshold_i_long_square']
    sFXs['threshold_i_ramp']            = cell_ephys_features['threshold_i_ramp']              
    sFXs['threshold_i_short_square']    = cell_ephys_features['threshold_i_short_square']
    sFXs['threshold_t_long_square']     = cell_ephys_features['threshold_t_long_square']  
    sFXs['threshold_t_ramp']            = cell_ephys_features['threshold_t_ramp']              
    sFXs['threshold_t_short_square']    = cell_ephys_features['threshold_t_short_square']
    sFXs['threshold_v_long_square']     = cell_ephys_features['threshold_v_long_square']  
    sFXs['threshold_v_ramp']            = cell_ephys_features['threshold_v_ramp']              
    sFXs['threshold_v_short_square']    = cell_ephys_features['threshold_v_short_square']
    sFXs['transgenic_line']             = specCell['transgenic_line']
    sFXs['trough_t_long_square']        = cell_ephys_features['trough_t_long_square']        
    sFXs['trough_t_ramp']               = cell_ephys_features['trough_t_ramp']                 
    sFXs['trough_t_short_square']       = cell_ephys_features['trough_t_short_square'] 
    sFXs['trough_v_long_square']        = cell_ephys_features['trough_v_long_square']   
    sFXs['trough_v_ramp']               = cell_ephys_features['trough_v_ramp']                 
    sFXs['trough_v_short_square']       = cell_ephys_features['trough_v_short_square'] 
    sFXs['upstroke_downstroke_ratio_long_square'] \
                            = cell_ephys_features['upstroke_downstroke_ratio_long_square']  
    sFXs['upstroke_downstroke_ratio_ramp'] \
                            = cell_ephys_features['upstroke_downstroke_ratio_ramp']        
    sFXs['upstroke_downstroke_ratio_short_square'] \
                            = cell_ephys_features['upstroke_downstroke_ratio_short_square'] 
    sFXs['v_rest']                      = cell_ephys_features['vrest']
    sFXs['vm_for_sag']                  = cell_ephys_features['vm_for_sag']
    
    for k,v in sFXs.items():
        if not isinstance(v, basestring):
            if math.isnan(v):
                sFXs[k] = None
            
    keys = sFXs.keys()
    numKeys = len(keys)
    print "Number of sFXs keys:", numKeys
    
    paramStrList = []
    insertData = [int(0), specimenTableID]
    for k,v in sFXs.items():
        paramStrList.append(k)
        insertData.append(v)
    s = ", "
    paramStr = s.join(paramStrList)
    insertStr = ('insert into specimenFXs (id, specID, ' + paramStr + 
                 ') values (' + '%s, '*(numKeys-1+2) + '%s)')
#     print insertStr
#     print insertData
    cursobj.execute(insertStr, insertData)
    specFXTableID = cursobj.lastrowid
    cnx.commit()
#^--------------------        
#     sys.exit("Not an error message")

queryStr = 'select * from specimenFXs inner join'

cnx.close()
print "Script complete."
