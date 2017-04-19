# Sweep feature extraction module
import numpy as np
from pprint import pprint

# Extract the features of the sweep from the input data
# time in seconds, voltage in mV, current in pA
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
	
# 	from pprint import pprint # temporary
	
	# Following approach seen at 
	# http://alleninstitute.github.io/AllenSDK/_static/examples/nb/cell_types.html#Computing-Electrophysiology-Features
	fx = EphysFeatureExtractor()
	try:
		fx.process_instance("", voltage, stimulus, time, 
							analysisStart, analysisDuration, "")
	except:
		print "Problem processing instance."
		# If unsuccessful, return an empty dictionary
		return({})
	
	# feature_data holds adapt, base_v, 
	#   latency (first spike time - analysis window begin time), 
	#   n_spikes, rate, and spike info		
	feature_data = fx.feature_list[0].mean  # See ABI code

	print('FEATURE DATA vvv')
	pprint(feature_data)
	print('FEATURE DATA ^^^')
	print('FEATURE DATA SPIKES vvv')
	pprint(feature_data['spikes'])
	print('FEATURE DATA SPIKES ^^^')
	print "feature_data keys", feature_data.keys()

	# Pull out the specific features for entry into the database
	numSpikes = feature_data['n_spikes']
	hasSpikes = (numSpikes != 0)
	
	if not hasSpikes:
		if verbose: 
			print "no spikes found"
		latency 	= None
		ISIFirst 	= None
		ISIMean 	= None
		ISICV 		= None
		adaptation 	= None
		threshold 	= None
		averageSpikePeak = None  
	else:  # at least one spike
		if 'latency' in feature_data:
			latency = feature_data['latency']
		else:
			latency = None

		if 'f_peak' in feature_data: 
			averageSpikePeak = feature_data['f_peak']
		else:
			averageSpikePeak = None  
		
		if 'threshold' in feature_data:
			threshold = feature_data['threshold']
		else:
			threshold = None

		if numSpikes == 1:
			if verbose:
				print "one spike found"
			ISIFirst 	= None
			ISIMean 	= None
			ISICV 		= None
			adaptation 	= None
		else: # numSpikes > 1
			if verbose:
				print "Number of spikes found: ", numSpikes
			ISIMean = feature_data['isi_avg']
			ISIFirst = None # Replace below if appears in process_spikes
			ISICV = None # Replace below if appears in process_spikes
			adaptation = feature_data['adapt']
# 			print "\n[14]: Individual spike data from EphysFeatureExtractor"
# 			for i in range(0,numSpikes):
# 				print "Spike data for spike ", i 
# 				pprint(feature_data["spikes"][i])

	#print "Sweep processing now" 
	# Following approach seen in the code at 
	# https://alleninstitute.github.io/AllenSDK/_modules/allensdk/ephys/ephys_extractor.html#EphysSweepFeatureExtractor._process_spike_related_features
	analysisEnd = analysisStart + analysisDuration
	sfx = EphysSweepFeatureExtractor(t=time, v=voltage, i=stimulus, 
									 start=analysisStart, end=analysisEnd)
	# process_spikes() does not appear to work if fewer than 2
	# We use values obtained here to trump any obtained above.
#	if numSpikes >= 2:  
	try:
		if verbose:
			print "Processing spikes now"
		sfx.process_spikes()
		if verbose:
			print "Spikes processed"
		
		swFXDict = sfx.as_dict()
		print "SWEEP_FEATURE AS DICT vvv"
		pprint(swFXDict)
		print "SWEEP_FEATURE AS DICT ^^^"
		#print "sfx keys", sfx.keys()
		
		print "Length of spike list:", len(swFXDict['spikes'])

		
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

		try:
# 				print ("Burst data for this experiment (max_burstiness_index " + 
# 					   "- normalized max rate in burst vs out, num_bursts - " + 
# 					   "number of bursts detected):")
			burstMetrics = sfx.burst_metrics()
			maxBurstiness = burstMetrics[0]
			numBursts = burstMetrics[1]
			hasBursts = numBursts!=0
		except:
			maxBurstiness = None
			numBursts = 0
			hasBursts = False
			
		try:
# 				print ("Pause data for this experiment (num_pauses - " + 
# 					   "number of pauses detected, pause_fraction - fraction " + 
# 					   "of interval [between start and end] spent in a pause):")
			pauseMetrics = sfx.pause_metrics()
			numPauses = pauseMetrics[0]
			hasPauses = numPauses!=0
			pauseFraction = pauseMetrics[1]
		except:
			numPauses = 0
			hasPauses = False
			pauseFraction = None
# 				print "No pause in this experiment"
			
		try: 
			if (latency and ISIMean):
				# See white paper definition of delay (pp 10)
				hasDelay = (latency > ISIMean)  
			else:
				hasDelay = False
				
# 				print ("Delay data for this experiment (delay_ratio - ratio of " + 
# 					   "latency to tau [higher means more delay], tau - dominant " + 
# 					   "time constant of rise before spike):")
			delayMetrics = sfx.delay_metrics()
			delayRatio = delayMetrics[0]
			# Test necessary because ABI SDK not consistent
			if delayRatio.dtype == 'numpy.float64' and np.isnan(delayRatio):
				delayRatio = None
				
			delayTau = delayMetrics[1]
			# Test necessary because ABI SDK not consistent
			if delayTau.dtype == 'numpy.float64' and np.isnan(delayTau):
				delayTau = None
		except:
			hasDelay = False
			delayRatio = None
			delayTau = None
# 				print "No delay in this experiment"
	except:  # process_spikes failed
		print "process_spikes() failed"
		adaptation = None
		latency = None
		ISICV = None
		ISIMean = None
		ISIFirst = None
		avgFiringRate = None
		hasBursts = False
		numBursts = 0
		maxBurstiness = None
		hasPauses = False
		numPauses = 0
		pauseFraction = None
		hasDelay = False
		delayRatio = None
		delayTau = None
# 	else:  # (if numSpikes >= 2)
# 		avgFiringRate = None
# 		ISIFirst = None
# 		hasBursts = False
# 		numBursts = 0
# 		maxBurstiness = None
# 		hasPauses = False
# 		numPauses = 0
# 		pauseFraction = None
# 		hasDelay = False
# 		delayRatio = None
# 		delayTau = None

	# Fill a dictionary with the results and then save to file
	features = dict()
	# features['abiFXID']				= abiFXID
	features['analysisStart']       = analysisStart     # in seconds
	features['analysisDuration']    = analysisDuration  # in seconds
	features['latency']             = latency
	# stimulusLatency is from stimulus start to the first spike threshold
	# latencies are in msec
	if latency is not None:
		features['stimulusLatency'] = latency - (stimulusStart - analysisStart)*1000
	else:
		features['stimulusLatency'] = None
		
	features['adaptation']          = adaptation                                  # 
	features['avgFiringRate']       = avgFiringRate                               # spikes per second
	features['hasSpikes']           = hasSpikes                                   # 1=true;0=false
	features['numSpikes']           = numSpikes                                   # 
	features['hasBursts']           = hasBursts                                   # 1=true;0=false
	features['numBursts']           = numBursts                                   #
	features['maxBurstiness']       = maxBurstiness                               #
	features['hasPauses']           = hasPauses                                   # 1=true;0=false
	features['numPauses']           = numPauses                                   #
	features['pauseFraction']       = pauseFraction                               #
	features['hasDelay']            = hasDelay   								  # 
	features['delayRatio']          = delayRatio                                  #
	features['delayTau']            = delayTau                                    #
	features['ISIFirst']            = ISIFirst                                    # in milliseconds
	features['ISIMean']             = ISIMean                                     # in milliseconds
	features['ISICV']               = ISICV                                       # dimensionless
	features['averageSpikePeak']    = averageSpikePeak                            # millivolts
	features['threshold']           = threshold

	features['spikeData'] = []
	for i in range(0,numSpikes):
		feature_data["spikes"][i]['spikeNumber'] = i
		features['spikeData'].append(feature_data["spikes"][i])
		
# 	print "FEATURES DICTIONARY vvv"
# 	pprint(features)
# 	print "FEATURES DICTIONARY ^^^"
	return features

	