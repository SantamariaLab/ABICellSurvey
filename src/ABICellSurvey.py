print "Starting script"

# http://stackoverflow.com/questions/17053435/mysql-connector-python-insert-python-variable-to-mysql-table    
    
redoTables = True # True/False
useTraceback = True     # True/False

installCells = True
runAnalyses = True

print "Importing..."
import sys
from allensdk.core.cell_types_cache import CellTypesCache
from allensdk.ephys.feature_extractor import EphysFeatureExtractor
import mysql.connector
import traceback
import numpy as np
from numpyconversion import NumpyMySQLConverter

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
#     cnx.set_converter_class(NumpyMySQLConverter)
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
        mycmd = 'DROP TABLE featureExtractions'
        cursobj.execute(mycmd)
        print "featureExtractions table dropped"
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

    # -----
    print "Creating tables"
   
    # Table specimens
    mycmd = ('''CREATE TABLE specimens (''' + 
             '''id int(11) NOT NULL AUTO_INCREMENT, ''' + 
             '''abiSpecimenID int(11), ''' + 
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
    # Temporary subset of all features for easier development
    mycmd = ('''CREATE TABLE experiments (''' + 
             '''id int(11) NOT NULL AUTO_INCREMENT, ''' + 
             '''specimenIDX int(11) NOT NULL, ''' +
             '''abiExperimentID int(11), ''' +
             '''fxID int(11), ''' +
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


    # Table featureExtractions
    # Temporary subset of all features for easier development
    mycmd = ('''CREATE TABLE featureExtractions (''' + 
             '''fxID int(11) NOT NULL AUTO_INCREMENT, ''' + 
             '''expID int(11) NOT NULL, ''' + 
             '''hasSpikes bool, ''' + 
             '''numSpikes int(11), ''' +
             '''latency double, ''' + 
             '''ISIMean double, ''' + 
             '''ISIFirst double, ''' + 
             '''ISICV double, ''' + 
#              '''hasBursts bool, ''' + 
#              '''numBursts int(11), ''' + 
#              '''hasPauses bool, ''' + 
#              '''numPauses int(11), ''' + 
             '''adaptation double, ''' + 
             '''threshold double, ''' +
             '''FOREIGN KEY(expID) REFERENCES experiments(id) ON DELETE CASCADE, ''' +
             '''PRIMARY KEY (fxID)) ENGINE=InnoDB''')

    try:
        cursobj.execute(mycmd)
        print "Table featureExtractions created"
    except:
        if useTraceback:
            traceback.print_exc()
            
        pass
        print "Table featureExtractions not created"

        
# ====================================================================
# Install the ABI Datasets
# Choose specimens and experiments; these are just for testing
# [2]
print "\n[2]: Install the ABI Datasets into the database"; sys.stdout.flush()
# specimens with models only 
specimens = [484635029]
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

# [4]
print "\n[4]: Process each specimen in turn"; sys.stdout.flush()
for specimen in specimens:
    # this saves the NWB file to '...FeatExtractDev/cell_types/specimen_XXXXXXXXX/ephys.nwb'
    print 'Processing:', specimen
    data_set = ctc.get_ephys_data(specimen)
    print data_set

    # Add the specimen to the database
    insertStr = 'insert into specimens (id, abiSpecimenID) values (%s, %s)'
    insertData = (0, specimen)
    cursobj.execute(insertStr, insertData)
    datasetid = cursobj.lastrowid
    print "datasetid:", datasetid

    sweeps = ctc.get_ephys_sweeps(specimen)
    for sweep in sweeps:
        sweepNum = sweep['sweep_number']
        print "\nsweep_number:", sweepNum, "   stimulus:", sweep['stimulus_name'], "   num_spikes", sweep['num_spikes']
        print sweep
        if sweep['stimulus_name'] not in ['Long Square', 'Short Square']:
            continue

        sweep_data = data_set.get_sweep(sweepNum)
        print sweep_data
        print "Index Range: ", sweep_data["index_range"] 
        sweep_metadata = data_set.get_sweep_metadata(sweepNum)
        print sweep_metadata
        
        # Add the sweep/experiment to the database
        print type(datasetid), type(sweepNum), type(None), type(sweep_metadata['aibs_stimulus_name']), type(sweep_metadata['aibs_stimulus_amplitude_pa'])
        insertStr = 'insert into experiments (id, specimenIDX, abiExperimentID, fxID, stimulusType, stimCurrent) values (%s, %s, %s, %s, %s, %s)'
        insertData = (int(0), datasetid, sweepNum, None, sweep_metadata['aibs_stimulus_name'], 
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
        insertStr = ('insert into featureExtractions (' + 
                        'fxID, expID, hasSpikes, numSpikes, latency, ' + 
                        'ISIMean, ISIFirst, ISICV, ' + 
#                         'hasBursts, numBursts, hasPauses, numPauses, ' + 
                        'adaptation, threshold) ' + 
                        'values(%s, %s, %s, %s, %s, %s, %s, ' + 
#                         '%s, %s, %s, %s, ' + 
                        '%s, %s, %s)')
        insertData = (0, experimentIDX, hasSpikes, int(numSpikes), 
                      latency, ISIMean, ISIFirst, ISICV, 
#                   hasBursts, numBursts, hasPauses, numPauses, 
                      adaptation, threshold) 
        print 'insertStr:', insertStr
        print type(latency), type(ISIMean), type(ISIFirst), type(ISICV)
        print "Inserting into featureExtractions table now"
        cursobj.execute(insertStr, insertData)
        fxID = cursobj.lastrowid
        cnx.commit()
        print fxID, experimentIDX
         
        # Add the fx to the experiment
        updateStr = 'update experiments set fxID=%s where id=%s'
        updateData = (fxID, experimentIDX)
        cursobj.execute(updateStr, updateData)
        cnx.commit()

cnx.close()
print "Script complete."
