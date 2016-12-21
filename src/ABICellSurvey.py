print "Starting script"

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
from collections import defaultdict

import mysql.connector
import traceback
import numpy as np
from numpyconversion import NumpyMySQLConverter

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
    # Features specific to cell level (typically average, or any)
    mycmd = ('''CREATE TABLE specimenFXs (''' + 
             '''id int(11) NOT NULL AUTO_INCREMENT, ''' + 
             '''specID int(11) NOT NULL, ''' + 
#              '''abiFXID int(11) NOT NULL, ''' + 
             '''hasSpikes bool, ''' +
#              '''adaptation double, ''' + 
#              '''avg_isi double, ''' + 
#              '''dendrite_type bool, ''' + 
#              '''electrode_0_pa double, ''' + 
#              '''f_i_curve_slope double, ''' + 
#              '''fast_trough_t_long_square double, ''' + 
#              '''fast_trough_t_ramp double, ''' + 
#              '''fast_trough_t_short_square double, ''' + 
#              '''fast_trough_v_long_square double, ''' + 
#              '''fast_trough_v_ramp double, ''' + 
#              '''fast_trough_v_short_square double, ''' + 
#              '''has_burst bool, ''' + 
#              '''has_delay bool, ''' + 
#              '''has_pause bool, ''' + 
#              '''hemisphere char(5), ''' +
             '''input_resistance_mohm double, ''' +                 # xcf ok
#              '''latency double, ''' + 
#              '''peak_t_long_square double, ''' + 
#              '''peak_t_ramp double, ''' + 
#              '''peak_t_short_square double, ''' + 
#              '''peak_v_long_square double, ''' + 
#              '''peak_v_ramp double, ''' + 
#              '''peak_v_short_square double, ''' +
#              '''reporter_status char(30), ''' + 
             '''rheobase_current double, ''' +                      # xcf ok 
             '''sag double, ''' +                                   # xcf ok
#              '''seal_gohm double, ''' + 
#              '''slow_trough_t_long_square double, ''' + 
#              '''slow_trough_t_ramp double, ''' + 
#              '''slow_trough_t_short_square double, ''' + 
#              '''slow_trough_v_long_square double, ''' + 
#              '''slow_trough_v_ramp double, ''' + 
#              '''slow_trough_v_short_square double, ''' +
#              '''structure_acronym char(20), ''' +
#              '''structure_name char(50), ''' + 
             '''tau double, ''' +                                    # xcf ok
#              '''threshold_i_long_square double, ''' + 
#              '''threshold_i_ramp double, ''' + 
#              '''threshold_i_short_square double, ''' + 
#              '''threshold_t_long_square double, ''' + 
#              '''threshold_t_ramp double, ''' + 
#              '''threshold_t_short_square double, ''' + 
#              '''threshold_v_long_square double, ''' + 
#              '''threshold_v_ramp double, ''' + 
#              '''threshold_v_short_square double, ''' +
#              '''transgenic_line char(30), ''' + 
#              '''trough_t_long_square double, ''' + 
#              '''trough_t_ramp double, ''' + 
#              '''trough_t_short_square double, ''' + 
#              '''trough_v_long_square double, ''' + 
#              '''trough_v_ramp double, ''' + 
#              '''trough_v_short_square double, ''' + 
#              '''upstroke_downstroke_ratio_long_square double, ''' + 
#              '''upstroke_downstroke_ratio_ramp double, ''' + 
#              '''upstroke_downstroke_ratio_short_square double, ''' + 
             '''v_baseline double, ''' +          # = vrest?         # xcf ok 
             '''vm_for_sag double, ''' +                             # xcf ok
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
             '''adaptation double, ''' +                            # xcf ok
#              '''avg_rate double, ''' +                              # xcf ok
             '''hasSpikes bool, ''' +                               # xcf ok
             '''numSpikes int(11), ''' +                            # xcf ok
             '''first_isi double, ''' +                             # xcf ok
             '''mean_isi double, ''' +                              # xcf ok
#              '''median_isi double, ''' +                            # xcf ok
             '''isi_cv double, ''' +                                # xcf ok
             '''f_peak double, ''' +  
             '''latency double, ''' +                               # xcf ok
             '''threshold double, ''' +
             '''FOREIGN KEY(expID) REFERENCES experiments(id) ON DELETE CASCADE, ''' +
             '''PRIMARY KEY (id)) ENGINE=InnoDB''')
#              '''hasBursts bool, ''' +                             # xcf    NO
#              '''numBursts int(11), ''' +                          # xcf    NO 
#              '''hasPauses bool, ''' +                             # xcf    NO
#              '''numPauses int(11), ''' +                          # xcf    NO

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
specimens = [484635029]
# specimens = [312883165,484635029]
# specimens with models only 
# specimens = [
#             484635029,
#             469801569,
#             469753383,
#             487667205,
#             468120757,
#             476104386,
#             484742372,
#             475622793,
#             464188580,
#             478058328,
#             476218657,
#             318808427,
#             479704527,
#             324493977,
#             483020137,
#             464212183,
#             476457450,
#             324266189,
#             478107198,
#             476686112,
#             478396248,
#             485058595,
#             475622680,
#             327962063,
#             474267418,
#             466664172,
#             474626527,
#             464198958]

# [3]
print "\n[3]: Get the cell data if not in cache"; sys.stdout.flush()
# Instantiate the CellTypesCache instance.  
ctc = (CellTypesCache(manifest_file='C:/Users/David/Dropbox/Documents/'
     + 'SantamariaLab/Projects/Fractional/ABI-FLIF/FeatExtractDev/'
     + 'cell_types/cell_types_manifest.json'))

# Get all cells with reconstructions
cells = ctc.get_cells(require_reconstruction=True)

# Populate the donors table
for cell in cells:
    queryStr = 'select * from donors where abiDonorID=' + str(cell['donor_id'])
#     print queryStr
    cursobj.execute(queryStr)
    row = cursobj.fetchone()
#     print type(row), row
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


# [4]
print "\n[4]: Process each specimen in turn"; sys.stdout.flush()
for specimen in specimens:
    # this saves the NWB file to '...FeatExtractDev/cell_types/specimen_XXXXXXXXX/ephys.nwb'
    print 'Processing:', specimen
    try:
        specEphysData = ctc.get_ephys_data(specimen)
    except:
        print "No ephys data for specimen ", specimen
        continue

#     print type(data_set)
#     pprint(data_set)
#     sys.exit("Error message")

#     dsspec = data_set['specimen_id']
#     print "Specimen:", specimen, "dsspec:", dsspec
#     sys.exit("Error message")

    if False:
        morphFeat = ctc.get_morphology_features()
    #     print "morphFeat:", morphFeat
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

    # Add the specimen feature extraction data to the database
    data_set = ctc.get_ephys_data(specCell['id'])
    sweeps = ctc.get_ephys_sweeps(specimen)
    sweep_numbers = defaultdict(list)
    for sweep in sweeps:
        sweep_numbers[sweep['stimulus_name']].append(sweep['sweep_number'])

    cell_features = (extract_cell_features(data_set, sweep_numbers['Ramp'], 
                sweep_numbers['Short Square'], sweep_numbers['Long Square']))
#     print "cell_features", cell_features

    hasSpikes = cell_features['long_squares']['spiking_sweeps'] != []
    input_resistance = cell_features['long_squares']['input_resistance']
    rheobase_current = cell_features['long_squares']['rheobase_i']
    sag = cell_features['long_squares']['sag']
    tau = cell_features['long_squares']['tau']
    v_baseline = cell_features['long_squares']['v_baseline']
    vm_for_sag = cell_features['long_squares']['vm_for_sag']
    
    insertStr = ('insert into specimenFXs (id, specID, hasSpikes, ' + 
                 'input_resistance_mohm, rheobase_current, sag, ' + 
                 'tau, v_baseline, vm_for_sag) values (' + 
                 '%s, %s, %s, %s, %s, %s, %s, %s, %s)')
    insertData = (int(0), specimenTableID, hasSpikes, 
                 input_resistance, rheobase_current, sag,  
                 tau, v_baseline, vm_for_sag)
    cursobj.execute(insertStr, insertData)
    specFXTableID = cursobj.lastrowid
    cnx.commit()

#     sys.exit("Not an error message")

    # Add the sweep/experiment to the database
    sweeps = ctc.get_ephys_sweeps(specimen)
    for sweep in sweeps:
        sweepNum = sweep['sweep_number']
        print ("sweep_number:", sweepNum, 
               "   stimulus:", sweep['stimulus_name'], 
               "   num_spikes", sweep['num_spikes'])
        print sweep
        if sweep['stimulus_name'] not in ['Long Square', 'Short Square']:
            continue

        sweep_data = specEphysData.get_sweep(sweepNum)
        print sweep_data
        print "Index Range: ", sweep_data["index_range"] 
        sweep_metadata = specEphysData.get_sweep_metadata(sweepNum)
        print sweep_metadata
        
        # Need to check if this sweep is actually an experiment
        # (not implemented yet)
        
        print (type(specimenTableID), type(sweepNum), type(None), 
               type(sweep_metadata['aibs_stimulus_name']), 
               type(sweep_metadata['aibs_stimulus_amplitude_pa']))
        insertStr = ('insert into experiments (id, specimenIDX, ' + 
                     'abiExperimentID, expFXID, stimulusType, stimCurrent) ' + 
                     'values (%s, %s, %s, %s, %s, %s)')
        insertData = (int(0), specimenTableID, sweepNum, None, 
                      sweep_metadata['aibs_stimulus_name'], 
                      float(sweep_metadata['aibs_stimulus_amplitude_pa']))
        cursobj.execute(insertStr, insertData)
        experimentIDX = cursobj.lastrowid
        print "experimentIDX:", experimentIDX


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
#     # index_range[0] is the "experiment" start index. 0 is the "sweep" start index
        index_range = sweep_data["index_range"]
#     # i = sweep_data["stimulus"][index_range[0]:index_range[1]+1] # in A
#     # v = sweep_data["response"][index_range[0]:index_range[1]+1] # in V
        i = sweep_data["stimulus"][0:index_range[1]+1] # in A
        v = sweep_data["response"][0:index_range[1]+1] # in V
        i *= 1e12 # to pA
        v *= 1e3 # to mV
#     
        sampling_rate = sweep_data["sampling_rate"] # in Hz
        print "Sampling Rate: ", sampling_rate
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
#     # NEED TO MAKE THESE INDIVIDUALLY DATA-DEPENDENT
        stim_start = index_range[0]/sampling_rate
        stim_duration = index_range[1]/sampling_rate - 0.1
#     
#     # Determining the stim_start and stim_duration automatically is unclear. 
#     # Also, stim_duration is apparently effectively analysis_duration which 
#     # is a bad assumption imho since there may be results that occur or persist
#     # after the stimulus is complete. Easy example: using 3 msec duration on 
#     # short square misses the cell's spike.  and in fact, it doesn't seem possible
#     # to calculate the beginning of the pulse from anything but doing analysis 
#     # of the stimulus data itself. 
        stimType = sweep_metadata['aibs_stimulus_name']
        if stimType == 'Long Square':
            analysis_start = 1.0
            analysis_duration = 2.0
        else:
            if stimType == 'Short Square':
    #             stim_start = 204000/sampling_rate
    #             stim_duration = 600/sampling_rate
                analysis_start = 1.0
                analysis_duration = 1.0
            else:
                # Ramp; not sure what to do yet; haven't found a combo that doesn't
                # result in error inside the process_instance routine
                analysis_start = 1.0
                analysis_duration = 2.0
                 
        print 'analysis_start', analysis_start, 'analysis_duration', analysis_duration
        fx.process_instance("", v, i, t, analysis_start, analysis_duration, "")
        feature_data = fx.feature_list[0].mean
        print "feature_data: ", feature_data 
         
        pulseCurrent = sweep_metadata['aibs_stimulus_amplitude_pa']
         
        # pull out the desired individual features here
        numSpikes = feature_data['n_spikes']
        hasSpikes = numSpikes != 0
        if 'latency' in feature_data:
            latency = feature_data['latency']
        else:
            latency = None
              
        if 'isi_avg' in feature_data:
            ISIMean = feature_data['isi_avg']
        else:
            ISIMean = None
             
        if numSpikes == 1:
            print 'first spike time: ', feature_data['spikes'][0]['t']
     
        if numSpikes >= 2:
            print 'second spike time: ', feature_data['spikes'][1]['t']
            ISIFirst = feature_data['spikes'][1]['t'] - feature_data['spikes'][0]['t']
        else:
            ISIFirst = None
               
        if 'ISICV' in feature_data:
            ISICV = feature_data['ISICV']
        else:
            ISICV = None
         
    #     numBursts =  
    #     hasBursts 
    #     hasPauses bool, ''' + 
    #     numPauses int(11), ''' + 
        if 'adapt' in feature_data:
            adaptation = feature_data['adapt']
        else:
            adaptation = None
        
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
     
        print 'hasSpikes:',  hasSpikes 
        print 'numSpikes:',  numSpikes 
        print 'latency:',    latency 
        print 'ISIMean:',    ISIMean 
        print 'ISIFirst:',   ISIFirst 
        print 'ISICV:',      ISICV 
        print 'adaptation:', adaptation 
        print 'threshold:', threshold
        print 'averageSpikePeak', averageSpikePeak 
         
        # Add the feature extraction to the database
        insertStr = ('insert into experimentFXs (' + 
                     'id, expID, abiFXID, adaptation, ' + 
                     'hasSpikes, numSpikes, ' + 
                     'first_isi, mean_isi, isi_cv, f_peak, latency, threshold) ' + 
                     'values(%s, %s, %s, %s, ' + 
                     '%s, %s, ' + 
                     '%s, %s, %s, %s, %s, %s)')
        insertData = (0, experimentIDX, abiFXID, adaptation, 
                      hasSpikes, int(numSpikes), 
                      ISIFirst, ISIMean, ISICV, averageSpikePeak, 
                      latency, threshold) 
        print 'insertStr:', insertStr
        print "Inserting into featureExtractions table now"
        cursobj.execute(insertStr, insertData)
        fxID = cursobj.lastrowid
        cnx.commit()
        print fxID, experimentIDX
         
        # Add the fx to the experiment
        updateStr = 'update experiments set expFXID=%s where id=%s'
        updateData = (fxID, experimentIDX)
        cursobj.execute(updateStr, updateData)
        cnx.commit()
        


cnx.close()
print "Script complete."
