from allensdk.api.queries.cell_types_api import CellTypesApi
from allensdk.ephys.extract_cell_features import extract_cell_features
from collections import defaultdict
from allensdk.core.nwb_data_set import NwbDataSet
from pprint import pprint

# pick a cell to analyze
print "1"
# specimen_id = 484635029
# nwb_file = '../../ABIFeatureExtraction/cell_types/specimen_484635029.nwb'
specimen_id = 464212183
nwb_file = '../../FeatExtractDev/cell_types/specimen_464212183/ephys.nwb'

# download the ephys data and sweep metadata
print "2"
cta = CellTypesApi()
print "3"
sweeps = cta.get_ephys_sweeps(specimen_id)
print "4"
# cta.save_ephys_data(specimen_id, nwb_file)

# group the sweeps by stimulus 
print "5"
sweep_numbers = defaultdict(list)
print "sweep_numbers", sweep_numbers

print "6"
for sweep in sweeps:
    sweep_numbers[sweep['stimulus_name']].append(sweep['sweep_number'])

print "sweep_numbers", sweep_numbers

# calculate features
print "7"
print sweep_numbers['Ramp']
print sweep_numbers['Short Square']
print sweep_numbers['Long Square']

cell_features = extract_cell_features(NwbDataSet(nwb_file),
                                    sweep_numbers['Ramp'],
                                    sweep_numbers['Short Square'],
                                    sweep_numbers['Long Square'])
pprint(cell_features)
print "8"
print cell_features.keys()
print "9"
