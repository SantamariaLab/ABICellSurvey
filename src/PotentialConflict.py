print "Importing..."
# import sys
# from allensdk.ephys.extract_cell_features import extract_cell_features
from allensdk.core.cell_types_cache import CellTypesCache
from allensdk.ephys.feature_extractor import EphysFeatureExtractor
from allensdk.ephys.ephys_extractor import EphysSweepFeatureExtractor

import numpy as np

#from pprint import pprint
def getABIAnalysisPoints(stimType):
    # Get the analysis points used by ABI for the various stimuli.
    # Hardcoded stimulus delay and analysis duration in seconds, 
    # not recorded in the database that I could see; does show 
    # up hardcoded in the sdk.  
    # This function does not include ramps, noise, or tests
    # All times in seconds
    # stimulusStart = time of beginning of stimulus waveform from beginning of sweep (sweep, not experiment)
    # stimulusDuration = duration of stimulus waveform
    # analysisStart = time from beginning of sweep (sweep, not experiment)
    # analysisDuration = time from analysisStart to close of desired analysis window
    
    # stim_duration (as listed in the documentation for, say, process_instance)
    # is apparently effectively analysis_duration which 
    # is a bad assumption imho since there may be results that occur or persist
    # after the stimulus is complete. Easy example: using 3 msec duration on 
    # short square misses the cell's spike.  and in fact, it doesn't seem possible
    # to calculate the beginning of the pulse from anything but doing analysis 
    # of the stimulus data itself. 
    # So instead, we use hard-coded values that match those used by ABI in the
    # stimulus signal design; there are easily changed by the user.

    analysisPoints = {}
    addlAnalysisDuration = 0.2  # i.e., 20% past
    # No switch statement in Python
    if stimType == 'Long Square':
        stimulusStart = 1.02
        stimulusDuration = 1.0
        analysisPoints['analysisStart'] = stimulusStart
        analysisPoints['stimulusStart'] = stimulusStart
        analysisPoints['analysisDuration'] = stimulusDuration * (1 + addlAnalysisDuration) + 3.0
        return(analysisPoints)

    if stimType == 'Square - 2s Suprathreshold':
        stimulusStart = 1.02
        stimulusDuration = 2.0
        analysisPoints['analysisStart'] = stimulusStart
        analysisPoints['stimulusStart'] = stimulusStart
        analysisPoints['analysisDuration'] = stimulusDuration * (1 + addlAnalysisDuration)
        return(analysisPoints)

    if stimType == 'Square - 0.5ms Subthreshold':
        stimulusStart = 1.0 + 0.02 + 0.002
        stimulusDuration = 0.0005
        analysisPoints['analysisStart'] = stimulusStart
        analysisPoints['stimulusStart'] = stimulusStart
        analysisPoints['analysisDuration'] = 1.0
        return(analysisPoints)

    if stimType == 'Short Square':
        stimulusStart = 1.02
        stimulusDuration = 0.003
        analysisPoints['analysisStart'] = stimulusStart
        analysisPoints['stimulusStart'] = stimulusStart
        analysisPoints['analysisDuration'] = 1.0 * (1 + addlAnalysisDuration)
        return(analysisPoints)
        
    # This stimType not supported here or on ABI webpage
    #     if stimType == 'Short Square - Triple':
    #         stimulusStart = 2.02
    #         stimulusDuration = 0.0170
    #         analysisPoints['analysisStart'] = stimulusStart
    #         analysisPoints['stimulusStart'] = stimulusStart
    #         analysisPoints['analysisDuration'] = 2.0 
    #         return(analysisPoints)

    analysisPoints['analysisStart'] = None
    analysisPoints['stimulusStart'] = None
    analysisPoints['analysisDuration'] = None
    return(analysisPoints)



manifestFile = ('C:/Users/David/Dropbox/Documents/SantamariaLab/Projects/Fractional/ABI-FLIF/Cache/' +
                'cell_types/cell_types_manifest.json')

# specimenList = [484635029]
# specimenList = [321707905, 469753383]
specimenList = [
            321707905,
            312883165,
            484635029,
            469801569,
            469753383]

ctc = CellTypesCache(manifest_file=manifestFile)


allEphysFeatures = ctc.get_ephys_features()
    

for specimen in specimenList:
    print '================================='
    print 'Processing specimen:', specimen
    try:
        specEphysData = ctc.get_ephys_data(specimen)
    except:
        # If no ephys features, we do not want to bother with it
        print "No ephys data for specimen ", specimen, "; ignoring it."
        continue
    
    sweeps = ctc.get_ephys_sweeps(specimen)
    for sweep in sweeps:
        sweepNum = sweep['sweep_number']
        if sweep['stimulus_name'] not in ['Long Square',]:
#         if sweep['stimulus_name'] not in ['Short Square',
#                                           'Square - 2s Suprathreshold']:
#         if sweep['stimulus_name'] not in ['Long Square', 'Short Square',
#                                           'Square - 0.5ms Subthreshold',
#                                           'Square - 2s Suprathreshold']:
            continue
#         if sweep['sweep_number'] not in [91,92,93]:
#             continue
        
        print "@@@@@ sweepNum: ", sweepNum, '   stimulus type: ', sweep['stimulus_name']
        sweepData = specEphysData.get_sweep(sweepNum)
        samplingRate = sweepData["sampling_rate"] # in Hz
    
        indexRange = sweepData["index_range"]
        # For our purposes, we grab the data from the beginning of the sweep 
        #  instead of the beginning of the experiment
        # i = sweepData["stimulus"][indexRange[0]:indexRange[1]+1] # in A
        # v = sweepData["response"][indexRange[0]:indexRange[1]+1] # in V
        i = sweepData["stimulus"][0:indexRange[1]+1] # in A
        v = sweepData["response"][0:indexRange[1]+1] # in V
        i *= 1e12 # to pA
        v *= 1e3 # to mV
        t = np.arange(0, len(v)) * (1.0 / samplingRate)
     
        # Determine the position and length of the analysis window with respect
        # to the beginning of the sweep 
        stimType = sweep['stimulus_name']
        analysisPoints = getABIAnalysisPoints(stimType)
        analysis_start = analysisPoints['analysisStart']
        stimulus_start = analysisPoints['stimulusStart']
        analysis_duration = analysisPoints['analysisDuration']        
#         analysis_start = 1.02   
#         stimulus_start = 1.02   
#         analysis_duration = 2.4 #0.001 #2.4 
    
        print ('Pretrim:  analysis_start', analysis_start, 'stimulus_start ', 
               stimulus_start, 'analysis_duration', analysis_duration)
    
        # Trim the analysis to end of experiment if necessary
        if (analysis_start + analysis_duration) * samplingRate >= indexRange[1]:
            end_time = (indexRange[1]-1)/samplingRate
            analysis_duration = end_time - analysis_start
    
        print ('Posttrim: analysis_start', analysis_start, 'stimulus_start ', 
               stimulus_start, 'analysis_duration', analysis_duration)
    
        fx = EphysFeatureExtractor()
        fx.process_instance("", v, i, t, analysis_start, analysis_duration, "")
        feature_data = fx.feature_list[0].mean
    
        fdNumSpikes = feature_data['n_spikes']
        print "FEATURE DATA NUM SPIKES: ", fdNumSpikes
#         print('FEATURE DATA SPIKES vvv')
#         pprint(feature_data['spikes'])
#         print('FEATURE DATA SPIKES ^^^')

        analysis_end = analysis_start + analysis_duration
        sfx = EphysSweepFeatureExtractor(t=t, v=v, i=i, 
                                     start=analysis_start, end=analysis_end)
        try:
            sfx.process_spikes()
        except:
            print "process_spikes failed."
            swNumSpikes = None
            continue

        swFXDict = sfx.as_dict()
        #         print "SWEEP_FEATURE AS DICT vvv"
        #         pprint(swFXDict)
        #         print "SWEEP_FEATURE AS DICT ^^^"
        swNumSpikes = len(swFXDict['spikes'])
        print "SWEEP FEATURE NUM SPIKES:", swNumSpikes
            
        if fdNumSpikes!=swNumSpikes:
            print "  DISAGREEMENT! *****************************"


print "Script complete."


