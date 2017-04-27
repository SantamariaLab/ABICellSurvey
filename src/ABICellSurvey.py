def CreateDB(specimenList, databaseName, resetDB, manifestFile, 
             host, user, password, verbose):
    # TODO: Tidy up; eliminate memory leaks; add final features; begin working on processing
    # functions such as calculating statistics of each parameter
    
    # Handle connection problems
    # Handle bad inputs and specimen not found
    # Pull out stimulus delays as defaults
    
    # http://stackoverflow.com/questions/17053435/mysql-connector-python-insert-python-variable-to-mysql-table    

    if verbose:
        print "CreateDB importing..."
        
    import sys
    from allensdk.ephys.extract_cell_features import extract_cell_features
    from allensdk.core.cell_types_cache import CellTypesCache
    from collections import defaultdict
    
    import mysql.connector
    
    import numpy as np
    from numpyconversion import NumpyMySQLConverter
    #import math
    
    from CellSurveyTableOps import dropTable, createDonorsTable
    from CellSurveyTableOps import createSpecimensTable, createSpecimenFXsTable
    from CellSurveyTableOps import createExperimentsTable, createExperimentFXsTable
    from CellSurveyTableOps import addSpecimen, addExperiment, addDonor
    from CellSurveyTableOps import addExpFX,addSpecFX
    from ABISweepFX import getABIAnalysisPoints, ExtractSweepFeatures
    
    #### Create the database from scratch if required
    if verbose:
        print "Connecting to the database"; 
    
    try: 
        cnx = mysql.connector.connect(user=user, password=password,
                                      host=host, database=databaseName,
                                      converter_class=NumpyMySQLConverter)
        if verbose:
            print "Connection complete"
            
        cursobj = cnx.cursor()
    except:
        cnx = mysql.connector.connect(user=user, password=password, host=host,
                                      converter_class=NumpyMySQLConverter)
        if verbose:
            print cnx
        cursobj = cnx.cursor()
        mycmd = 'create database ' + databaseName
        cursobj.execute(mycmd)
        if verbose:
            print "Database created"
        mycmd = 'use ' + databaseName
        cursobj.execute(mycmd)
        if verbose:
            print "Using database " + databaseName
    
    if resetDB:
        if verbose:
            print "Dropping all tables"
            
        tablenames = ['specimenFXs', 'experimentFXs', 'experiments', 
                      'specimens', 'donors']
        for tablename in tablenames:
            result = dropTable(cnx, tablename)
            if verbose:
                if result:
                    print tablename + " table dropped"
                else:
                    print " There was a problem dropping table " + tablename
    
        # -----
        if verbose:
            print "Creating tables"
       
        result = createDonorsTable(cnx)
        if verbose:
            if result:
                print "Donors Table created"
            else:
                print "There was a problem creating the Donors Table"
    
        result = createSpecimensTable(cnx)
        if verbose:
            if result:
                print "Specimens Table created"
            else:
                print "There was a problem creating the Specimens Table"
    
        result = createExperimentsTable(cnx)
        if verbose:
            if result:
                print "Experiments Table created"
            else:
                print "There was a problem creating the Experiments Table"
    
        result = createSpecimenFXsTable(cnx)
        if verbose:
            if result:
                print "Specimens Table created"
            else:
                print "There was a problem creating the Specimens Table"
    
        result = createExperimentFXsTable(cnx)
        if verbose:
            if result:
                print "Experiments Table created"
            else:
                print "There was a problem creating the Experiments Table"
    
        
    # ====================================================================
    # Install the ABI Datasets
    if verbose:
        print "Installing the ABI Datasets into the database"; sys.stdout.flush()
        
    # Instantiate the CellTypesCache instance.  
    ctc = CellTypesCache(manifest_file=manifestFile)
    
    # Get metadata on all cells
    cells = ctc.get_cells()
    
    ####### ALL DONORS #######
    # Populate the donors table with all donors of all cells
    if verbose:
        print "Populating donors table"
    
    for cell in cells:
        addDonor(cnx, cell['donor_id'], cell['donor']['sex'], cell['donor']['name'])

        
    ####### ALL EPHYS FEATURES #######
    try:
        # for all cells
        allEphysFeatures = ctc.get_ephys_features()  
    except:
        # If no ephys features, we cannot do anything
        print "No ephys features available; aborting program."
        sys.exit()
            
            
    ####### SPECIMENS #######
    # Get relevant info for each specimen in input list
    if verbose:
        print "Processing each specimen in turn"; sys.stdout.flush()
        
    for specimen in specimenList:
#        if verbose:
        print '@@@@@ Processing specimen:', specimen
        
        try:
            specEphysData = ctc.get_ephys_data(specimen)
        except:
            # If no ephys data, we do not want to bother with it
            print "No ephys data for specimen ", specimen, "; ignoring it."
            continue
    
        ###### SPECIMEN >>> METADATA ######
        # Paw through the cells to find the metadata for the current specimen
        # The cell is a dictionary that has most of the "other" non-sweep stuff
        # we need such as cell averages, rheobase info, transgenic line, hemisphere, 
        # age, sex, graph order, dendrite type, area, has_burst,...
        # May be able to improve this search Pythonically 
        for cell in cells:
            datasets = cell['data_sets']
            for dataset in datasets:
                dsspec = dataset['specimen_id']
                if dsspec == specimen:
                    specCell = cell
                    break
                
        # Add the specimen to the database
        donorID = specCell['donor_id']
        specimenTableIDX = addSpecimen(cnx, donorID, specimen)
    
        ####### SPECIMEN >>> SWEEPS/EXPERIMENTS #######
        # Change these to true if show in any sweep 
        cellHasBursts = False
        cellHasDelays = False
        cellHasPauses = False
        
        # Process each sweep in turn
        sweeps = ctc.get_ephys_sweeps(specimen)
        for sweep in sweeps:
            sweepNum = sweep['sweep_number']
            
#             if verbose:
            msg = ("  Processing sweep_number: " + str(sweepNum) + 
                   "  stimulus: " + str(sweep['stimulus_name']) + 
                   "  num_spikes = " + str(sweep['num_spikes']))
            print msg
    
            # Screen out some sweep types because they are not suitable for our 
            #      simulations or because the stimulus type is not successful 
            #      in use of process_spikes() (which we use for simulations)
            databaseList = ['Long Square', 'Short Square', 'Noise 1', 'Noise 2', 
                            'Square - 2s Suprathreshold', 'Square - 0.5ms Subthreshold',
                            'Short Square - Triple', 'Ramp', 'Ramp to Rheobase']
            if sweep['stimulus_name'] not in databaseList:
                print "    Stimulus type", sweep['stimulus_name'], "not supported."
                continue
    
            # sweepData holds index range, response data vector, sampling_rate, and stimulus vector 
            sweepData = specEphysData.get_sweep(sweepNum)
    
            # sweep_metadata holds aibs_stimulus_amplitude_pa, aibs_stimulus_name,
            #  gain, initial_access_resistance, and seal
            sweep_metadata = specEphysData.get_sweep_metadata(sweepNum)
            samplingRate = sweepData["sampling_rate"] # in Hz
            
            # Need to check if this sweep is actually an experiment
            # [not implemented]
            
            # Add the experiment to the database
            experimentIDX = (#
                addExperiment(cnx, specimenTableIDX, 
                              sweepNum, samplingRate,
                              sweep_metadata['aibs_stimulus_name'],
                              float(sweep_metadata['aibs_stimulus_amplitude_pa'])))

            # Only Long Square is suitable for our simulations
            fxOKList = ['Long Square']
            if sweep['stimulus_name'] not in fxOKList:
                print "    Stimulus type", sweep['stimulus_name'], "entered into database but not supported for feature extractions."
                continue

            ## Create the experiment feature extraction data ## 
            # This approach seen at   
            # http://alleninstitute.github.io/AllenSDK/_static/examples/nb/
            #      cell_types.html#Computing-Electrophysiology-Features
            # index_range[0] is the "experiment" start index. 0 is the "sweep" start index
            indexRange = sweepData["index_range"]
            # For our purposes, we grab the data from the beginning of the sweep 
            #  instead of the beginning of the experiment
            # i = sweepData["stimulus"][indexRange[0]:indexRange[1]+1] # in A
            # v = sweepData["response"][indexRange[0]:indexRange[1]+1] # in V
            i = sweepData["stimulus"][0:indexRange[1]+1] # in A
            v = sweepData["response"][0:indexRange[1]+1] # in V
            i *= 1e12 # to pA
            v *= 1e3 # to mV
            t = np.arange(0, len(v)) * (1.0 / samplingRate) # in seconds
         
            ###### Do the sweep's feature extraction #######
            # Determine the position and length of the analysis window with respect
            # to the beginning of the sweep 
            stimType = sweep_metadata['aibs_stimulus_name']
            analysisPoints = getABIAnalysisPoints(stimType)
            analysis_start = analysisPoints['analysisStart']
            stimulus_start = analysisPoints['stimulusStart']
            analysis_duration = analysisPoints['analysisDuration']
    
            if verbose:
                print ('analysis_start', analysis_start, 'stimulus_start ', 
                       stimulus_start, 'analysis_duration', analysis_duration)
    
            # Trim the analysis to end of experiment if necessary
            if (analysis_start + analysis_duration) * samplingRate >= indexRange[1]:
                end_time = (indexRange[1]-1)/samplingRate
                analysis_duration = end_time - analysis_start
    
            if verbose:
                print ('analysis_start', analysis_start, 'stimulus_start ', 
                       stimulus_start, 'analysis_duration', analysis_duration)
    
            # Now we extract the sweep features from that analysis window
            swFXs = ExtractSweepFeatures(t, v, i, analysis_start, 
                            analysis_duration, stimulus_start, verbose)
            if len(swFXs) == 0:
                print "Skipping experiment: ", specimen, '/', sweepNum, " and continuing..."
                continue
            
            if swFXs['hasBursts']: cellHasBursts = True

            if swFXs['hasPauses']: cellHasPauses = True

            if swFXs['hasDelay']: cellHasDelays = True

#             swFXs['abiFXID'] = abiFXID

            ## Add the feature extraction to the database ##
            expFXs = dict(swFXs)
            # individual spike data not going into the database directly
            del expFXs['spikeData']   
            addExpFX(cnx, experimentIDX, expFXs)
        # end of:  for sweep in sweeps:
    
        ## Assemble the specimen feature extraction data ##
        specimenEphysFeaturesList = [f for f in allEphysFeatures if f['specimen_id'] == specimen]
        specimenEphysFeatures = specimenEphysFeaturesList[0]
         
        data_set = ctc.get_ephys_data(specCell['id'])
        sweeps = ctc.get_ephys_sweeps(specimen)
        sweep_numbers = defaultdict(list)
        for sweep in sweeps:
            sweep_numbers[sweep['stimulus_name']].append(sweep['sweep_number'])
    
        cell_features = (extract_cell_features(data_set, sweep_numbers['Ramp'], 
                    sweep_numbers['Short Square'], sweep_numbers['Long Square']))
        spFXs = {}
        spFXs['hasSpikes']                   = cell_features['long_squares']['spiking_sweeps'] != []
        spFXs['hero_sweep_id']               = cell_features['long_squares']['hero_sweep']['id']
        spFXs['hero_sweep_avg_firing_rate']  = cell_features['long_squares']['hero_sweep']['avg_rate']
        spFXs['hero_sweep_adaptation']       = cell_features['long_squares']['hero_sweep']['adapt']
        spFXs['hero_sweep_first_isi']        = cell_features['long_squares']['hero_sweep']['first_isi']
        spFXs['hero_sweep_mean_isi']         = cell_features['long_squares']['hero_sweep']['mean_isi']
        spFXs['hero_sweep_median_isi']       = cell_features['long_squares']['hero_sweep']['median_isi']
        spFXs['hero_sweep_isi_cv']           = cell_features['long_squares']['hero_sweep']['isi_cv']
        spFXs['hero_sweep_latency']          = cell_features['long_squares']['hero_sweep']['latency']
        spFXs['hero_sweep_stim_amp']         = cell_features['long_squares']['hero_sweep']['stim_amp']
        spFXs['hero_sweep_v_baseline']       = cell_features['long_squares']['hero_sweep']['v_baseline']
        spFXs['dendrite_type']               = specCell['dendrite_type']
        spFXs['electrode_0_pa']              = specimenEphysFeatures['electrode_0_pa']
        spFXs['f_i_curve_slope']             = specimenEphysFeatures['f_i_curve_slope']
        spFXs['fast_trough_t_long_square']   = specimenEphysFeatures['fast_trough_t_long_square']     
        spFXs['fast_trough_t_ramp']          = specimenEphysFeatures['fast_trough_t_ramp']    
        spFXs['fast_trough_t_short_square']  = specimenEphysFeatures['fast_trough_t_short_square']  
        spFXs['fast_trough_v_long_square']   = specimenEphysFeatures['fast_trough_v_long_square']
        spFXs['fast_trough_v_ramp']          = specimenEphysFeatures['fast_trough_v_ramp']    
        spFXs['fast_trough_v_short_square']  = specimenEphysFeatures['fast_trough_v_short_square']
        spFXs['has_bursts']                  = cellHasBursts
        spFXs['has_delays']                  = cellHasDelays    
        spFXs['has_pauses']                  = cellHasPauses
        spFXs['hemisphere']                  = specCell['hemisphere'] 
        spFXs['input_resistance_mohm']       = specimenEphysFeatures['input_resistance_mohm']
        spFXs['peak_t_long_square']          = specimenEphysFeatures['peak_t_long_square']
        spFXs['peak_t_ramp']                 = specimenEphysFeatures['peak_t_ramp']    
        spFXs['peak_t_short_square']         = specimenEphysFeatures['peak_t_short_square']
        spFXs['peak_v_long_square']          = specimenEphysFeatures['peak_v_long_square'] 
        spFXs['peak_v_ramp']                 = specimenEphysFeatures['peak_v_ramp']    
        spFXs['peak_v_short_square']         = specimenEphysFeatures['peak_v_short_square']
        spFXs['reporter_status']             = specCell['reporter_status']
        spFXs['rheobase_current']            = cell_features['long_squares']['rheobase_i'] 
        spFXs['ri']                          = specimenEphysFeatures['ri']
        spFXs['sagFraction']                 = specimenEphysFeatures['sag']
        spFXs['seal_gohm']                   = specimenEphysFeatures['seal_gohm']
        spFXs['slow_trough_t_long_square']   = specimenEphysFeatures['slow_trough_t_long_square']
        spFXs['slow_trough_t_ramp']          = specimenEphysFeatures['slow_trough_t_ramp']           
        spFXs['slow_trough_t_short_square']  = specimenEphysFeatures['slow_trough_t_short_square']
        spFXs['slow_trough_v_long_square']   = specimenEphysFeatures['slow_trough_v_long_square']  
        spFXs['slow_trough_v_ramp']          = specimenEphysFeatures['slow_trough_v_ramp']                
        spFXs['slow_trough_v_short_square']  = specimenEphysFeatures['slow_trough_v_short_square']
        spFXs['structure_acronym']           = specCell['structure']['acronym']  
        spFXs['structure_name']              = specCell['structure']['name']
        spFXs['tau']                         = specimenEphysFeatures['tau']
        spFXs['threshold_i_long_square']     = specimenEphysFeatures['threshold_i_long_square']
        spFXs['threshold_i_ramp']            = specimenEphysFeatures['threshold_i_ramp']              
        spFXs['threshold_i_short_square']    = specimenEphysFeatures['threshold_i_short_square']
        spFXs['threshold_t_long_square']     = specimenEphysFeatures['threshold_t_long_square']  
        spFXs['threshold_t_ramp']            = specimenEphysFeatures['threshold_t_ramp']              
        spFXs['threshold_t_short_square']    = specimenEphysFeatures['threshold_t_short_square']
        spFXs['threshold_v_long_square']     = specimenEphysFeatures['threshold_v_long_square']  
        spFXs['threshold_v_ramp']            = specimenEphysFeatures['threshold_v_ramp']              
        spFXs['threshold_v_short_square']    = specimenEphysFeatures['threshold_v_short_square']
        spFXs['transgenic_line']             = specCell['transgenic_line']
        spFXs['trough_t_long_square']        = specimenEphysFeatures['trough_t_long_square']        
        spFXs['trough_t_ramp']               = specimenEphysFeatures['trough_t_ramp']                 
        spFXs['trough_t_short_square']       = specimenEphysFeatures['trough_t_short_square'] 
        spFXs['trough_v_long_square']        = specimenEphysFeatures['trough_v_long_square']   
        spFXs['trough_v_ramp']               = specimenEphysFeatures['trough_v_ramp']                 
        spFXs['trough_v_short_square']       = specimenEphysFeatures['trough_v_short_square'] 
        spFXs['upstroke_downstroke_ratio_long_square'] \
                                = specimenEphysFeatures['upstroke_downstroke_ratio_long_square']  
        spFXs['upstroke_downstroke_ratio_ramp'] \
                                = specimenEphysFeatures['upstroke_downstroke_ratio_ramp']        
        spFXs['upstroke_downstroke_ratio_short_square'] \
                                = specimenEphysFeatures['upstroke_downstroke_ratio_short_square'] 
        spFXs['v_rest']                      = specimenEphysFeatures['vrest']
        spFXs['vm_for_sag']                  = specimenEphysFeatures['vm_for_sag']

        ## Add the specimen feature extraction data to the database ##
        addSpecFX(cnx, specimenTableIDX, spFXs)
    # end of:  for specimen in specimenList
    
    cnx.close()
