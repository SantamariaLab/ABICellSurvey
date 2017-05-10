# Sweep feature extraction module for CellSurvey database construction
import numpy as np
try:
	#	if isNMRemote:
	from feature_extractor import EphysFeatureExtractor
	from ephys_extractor import EphysSweepFeatureExtractor
except ImportError:
	#	else:
	from allensdk.ephys.feature_extractor import EphysFeatureExtractor
	from allensdk.ephys.ephys_extractor import EphysSweepFeatureExtractor

def getABIAnalysisPoints(stimType):
	# Get the analysis points used by ABI for the various stimuli.
	# Hardcoded stimulus delay and analysis duration in seconds, 
	# not recorded in the database that I could see; does show 
	# up hardcoded in the sdk.  
	# This function does not include ramps, noise, or tests
	# All times are in seconds.
	# stimulusStart = time of beginning of stimulus waveform from beginning of sweep (sweep, not experiment)
	# stimulusDuration = duration of stimulus waveform
	# analysisStart = time from beginning of sweep (sweep, not experiment)
	# analysisDuration = time from analysisStart to close of desired analysis window
	
	# stim_duration (as listed in the documentation for, say, process_instance)
	# is apparently effectively analysis_duration which 
	# is not ideal imho since there may be results that occur or persist
	# after the stimulus is complete. Easy example: using 3 msec duration on 
	# short square misses the cell's spike.  and in fact, it doesn't seem possible
	# to calculate the beginning of the pulse from anything but doing analysis 
	# of the stimulus data itself. 
	# So instead, we use hard-coded values that match those used by ABI in the
	# stimulus signal design; there are easily changed by the user.

	# See comments in ABICellSurvey: at this point we are really only using 
	#  Long Square
	analysisPoints = {}
	addlAnalysisDuration = 0.2  # i.e., 20% past
	# No switch statement in Python
	if stimType == 'Long Square':
		stimulusStart = 1.02
		stimulusDuration = 1.0
		analysisPoints['analysisStart'] = stimulusStart
		analysisPoints['stimulusStart'] = stimulusStart
		analysisPoints['analysisDuration'] = stimulusDuration * (1 + addlAnalysisDuration)
		return(analysisPoints)

	# These choices require revisiting
	if stimType == 'Square - 2s Suprathreshold':
		stimulusStart = 1.02
		stimulusDuration = 2.0
		analysisPoints['analysisStart'] = stimulusStart
		analysisPoints['stimulusStart'] = stimulusStart
		analysisPoints['analysisDuration'] = stimulusDuration * (1 + addlAnalysisDuration)
		return(analysisPoints)

	# These choices require revisiting
	if stimType == 'Square - 0.5ms Subthreshold':
		stimulusStart = 1.0 + 0.02 + 0.002
		stimulusDuration = 0.0005
		analysisPoints['analysisStart'] = stimulusStart
		analysisPoints['stimulusStart'] = stimulusStart
		analysisPoints['analysisDuration'] = 1.0
		return(analysisPoints)

	# Has issues with feature extraction
	if stimType == 'Short Square':
		stimulusStart = 1.02
		stimulusDuration = 0.003
		analysisPoints['analysisStart'] = stimulusStart
		analysisPoints['stimulusStart'] = stimulusStart
		analysisPoints['analysisDuration'] = 1.0 * (1 + addlAnalysisDuration)
		return(analysisPoints)
		
	# This stimType not supported here or on ABI webpage
# 	if stimType == 'Short Square - Triple':
# 		stimulusStart = 2.02
# 		stimulusDuration = 0.0170
# 		analysisPoints['analysisStart'] = stimulusStart
# 		analysisPoints['stimulusStart'] = stimulusStart
# 		analysisPoints['analysisDuration'] = 2.0 
# 		return(analysisPoints)

	analysisPoints['analysisStart'] = None
	analysisPoints['stimulusStart'] = None
	analysisPoints['analysisDuration'] = None
	return(analysisPoints)


def ExtractSweepFeatures(time, voltage, stimulus, analysisStart, 
						 analysisDuration, stimulusStart, verbose):
	usePP = False
	if usePP:
		from pprint import pprint # temporary

	# This can be customized
	featureList = ['analysisStart', 'analysisDuration', 'stimulusStart', 
                   'adaptation', 'avgFiringRate', 'avgHlfHgtWidth', 'baseV',
                   'maxSpkV', 'ISIFirst', 'ISIMean', 'ISICV', 'latency',
                   'stimulusLatency', 'frstSpkThresholdV', 
                   'hasSpikes', 'numSpikes', 'hasBursts', 'numBursts', 
                   'maxBurstiness', 'hasPauses', 'numPauses', 'pauseFraction',
                   'hasDelay', 'delayRatio', 'delayTau']

	# Following approach seen at 
	# http://alleninstitute.github.io/AllenSDK/_static/examples/nb/cell_types.html#Computing-Electrophysiology-Features
	fx = EphysFeatureExtractor()
	try:
		fx.process_instance("", voltage, stimulus, time, 
							analysisStart, analysisDuration, "")
	except:
		print "Problem processing instance - FX Failure."
		# If unsuccessful, impose mostly NULLs (see User Guide)
		features = dict()
		for feature in featureList:
			features[feature] = None
		features['analysisStart']       = analysisStart
		features['analysisDuration']    = analysisDuration
		features['stimulusStart']		= stimulusStart
		return(features)

	# feature_data holds adapt, base_v, 
	#   latency (first spike time - analysis window begin time), 
	#   n_spikes, rate, and spike info		
	feature_data = fx.feature_list[0].mean  # See ABI code

	if usePP:
		print('FEATURE DATA vvv')
		pprint(feature_data)
		print('FEATURE DATA ^^^')
		print('FEATURE DATA SPIKES vvv')
		pprint(feature_data['spikes'])
		print('FEATURE DATA SPIKES ^^^')

	# Pull out the specific features for entry into the database
	baseV = feature_data['base_v']
	numSpikes = feature_data['n_spikes']
	hasSpikes = (numSpikes != 0)

	# Dependent on number of spikes
	if not hasSpikes:
		if verbose: 
			print "No spikes found"

		# Impose No Spikes NULLS    
		avgFiringRate		= 0.0
		features = dict()
		for feature in featureList:
			features[feature] = None

		features['analysisStart']       = analysisStart
		features['analysisDuration']    = analysisDuration
		features['stimulusStart']		= stimulusStart
		features['baseV'] = baseV
		features['numSpikes'] = numSpikes
		features['hasSpikes'] = hasSpikes
		return(features)

	else:  # at least one spike
		if 'half_height_width' in feature_data:
			avgHlfHgtWidth = feature_data['half_height_width']
		elif 'half_height_width' in feature_data['spikes'][0]:
			avgHlfHgtWidth = feature_data['spikes'][0]['half_height_width']
		else:
			avgHlfHgtWidth = None
		
		if 'f_peak' in feature_data: 
			maxSpkV = feature_data['f_peak']
		else:
			maxSpkV = None  
		
		if 'threshold' in feature_data:
			frstSpkThresholdV = feature_data['threshold']
		else:
			frstSpkThresholdV = None
		
		# Following approach seen in the code at 
		# https://alleninstitute.github.io/AllenSDK/_modules/
		# allensdk/ephys/ephys_extractor.html#EphysSweepFea
		# tureExtractor._process_spike_related_features
		analysisEnd = analysisStart + analysisDuration
		sfx = EphysSweepFeatureExtractor(t=time, v=voltage, i=stimulus, 
										 start=analysisStart, end=analysisEnd)
		try:
			if verbose:
				print "Processing spikes now"
			sfx.process_spikes()
			if verbose:
				print "Spikes processed"

		except:  # process_spikes failed
			print "process_spikes() failed"
			# Impose PrSpk Failure NULLS (see User Guide)
			features = dict()
			for feature in featureList:
				features[feature] = None

			features['analysisStart']       = analysisStart
			features['analysisDuration']    = analysisDuration
			features['stimulusStart']		= stimulusStart
			features['baseV'] = baseV
			features['numSpikes'] = numSpikes
			features['hasSpikes'] = hasSpikes
			return(features)

		# process_spikes didn't fail, so continue    
		swFXDict = sfx.as_dict()
		if usePP:
			print "SWEEP_FEATURE AS DICT vvv"
			pprint(swFXDict)
			print "SWEEP_FEATURE AS DICT ^^^"

		if verbose:
			print "Length of spike list:", len(swFXDict['spikes'])

		if 'adapt' in swFXDict:
			adaptation = swFXDict['adapt']
		else:
			print "adapt not found"
			adaptation = None

		if 'avg_rate' in swFXDict:
			avgFiringRate = swFXDict['avg_rate']
		else:
			print "avg_rate not found"
			avgFiringRate = None

		if 'first_isi' in swFXDict:
			# isi stuff from feature extractor is in msecs, whereas 
			# isi stuff from sweep feature extractor is in seconds, so we 
			# ensure both are in msec.
			ISIFirst = swFXDict['first_isi']*1000
			print "ISIFirst: ", ISIFirst
		else:
			print "first_isi not found in swFXDict."
			ISIFirst = None

		if 'mean_isi' in swFXDict:
			# isi stuff from feature extractor is in msecs, whereas 
			# isi stuff from sweep feature extractor is in seconds, so we 
			# ensure both are in msec.
			ISIMean = swFXDict['mean_isi']*1000
			print "ISIMean: ", ISIMean
		else:
			print "mean_isi not found in swFXDict."
			ISIMean = None

		if 'isi_cv' in swFXDict:
			ISICV = swFXDict['isi_cv']
		else:
			print "isi_cv not found in swFXDict."
			ISICV = None

		if 'latency' in swFXDict:
			latency = swFXDict['latency']
			# stimulusLatency is from stimulus start to the first spike threshold
			stimulusLatency = latency - (stimulusStart - analysisStart)*1000
		else:
			print "latency not found in swFXDict."
			latency = None
			stimulusLatency = None

		try:
			#   print ("Burst data for this experiment (max_burstiness_index " + 
			# 		   "- normalized max rate in burst vs out, num_bursts - " + 
			# 		   "number of bursts detected):")
			burstMetrics = sfx.burst_metrics()
			numBursts = burstMetrics[1]
			hasBursts = numBursts!=0
			if hasBursts:
				maxBurstiness = burstMetrics[0]
			else:
				maxBurstiness = None
		except:
			maxBurstiness = None
			numBursts = None
			hasBursts = None

		try:
			# 	print ("Pause data for this experiment (num_pauses - " + 
			# 		   "number of pauses detected, pause_fraction - fraction " + 
			# 		   "of interval [between start and end] spent in a pause):")
			pauseMetrics = sfx.pause_metrics()
			numPauses = pauseMetrics[0]
			hasPauses = numPauses!=0
			if hasPauses:
				pauseFraction = pauseMetrics[1]
			else:
				pauseFraction = None
		except:
			numPauses = None
			hasPauses = None
			pauseFraction = None

		try: 
			if (latency and ISIMean):
				# See white paper definition of delay (pp 10)
				hasDelay = bool(latency > ISIMean)  
			else:
				hasDelay = False
				
			# 	print ("Delay data for this experiment (delay_ratio - ratio of " + 
			# 		   "latency to tau [higher means more delay], tau - dominant " + 
			# 		   "time constant of rise before spike):")
			if hasDelay:
				delayMetrics = sfx.delay_metrics()
				delayRatio = delayMetrics[0]
				# Test necessary because ABI SDK not consistent
				if delayRatio.dtype == 'numpy.float64' and np.isnan(delayRatio):
					delayRatio = None
					
				delayTau = delayMetrics[1]
				# Test necessary because ABI SDK not consistent
				if delayTau.dtype == 'numpy.float64' and np.isnan(delayTau):
					delayTau = None
			else:
				delayRatio = None
				delayTau = None
		except:
			hasDelay = None
			delayRatio = None
			delayTau = None
			
	# Additional criteria for imposing NULL (see User Guide)
	if numSpikes < 2:
		ISIFirst = None
		ISIMean = None
		ISICV = None
	if numSpikes < 3:
		adaptation = None

	# Fill a dictionary with the results and then save to file
	features = dict()
	features['analysisStart']       = analysisStart								
	features['analysisDuration']    = analysisDuration							
	features['stimulusStart']		= stimulusStart								
	features['adaptation']          = adaptation								 
	features['avgFiringRate']       = avgFiringRate								
	features['avgHlfHgtWidth']      = avgHlfHgtWidth							
	features['baseV']				= baseV										
	features['maxSpkV']      		= maxSpkV									
	features['ISIFirst']            = ISIFirst									
	features['ISIMean']             = ISIMean									
	features['ISICV']               = ISICV										
	features['latency']             = latency									
	features['stimulusLatency'] = stimulusLatency

	features['frstSpkThresholdV']	= frstSpkThresholdV							
	features['hasSpikes']           = hasSpikes                                 
	features['numSpikes']           = numSpikes                                  
	features['hasBursts']           = hasBursts                                 
	features['numBursts']           = numBursts                                 
	features['maxBurstiness']       = maxBurstiness                             
	features['hasPauses']           = hasPauses                                 
	features['numPauses']           = numPauses                                 
	features['pauseFraction']       = pauseFraction                             
	features['hasDelay']            = hasDelay   								 
	features['delayRatio']          = delayRatio                                
	features['delayTau']            = delayTau                                  

	features['spikeData'] = []
	if numSpikes > 0:
		for i in range(0,numSpikes):
			swFXDict["spikes"][i]['spikeNumber'] = i
			features['spikeData'].append(swFXDict["spikes"][i])
		
	if usePP:
		print "FEATURES DICTIONARY vvv"
		pprint(features)
		print "FEATURES DICTIONARY ^^^"

	return features
