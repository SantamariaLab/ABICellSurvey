print "Starting script CreateCSdb"

import CSdbconfig as cfg
from ABICellSurvey import CreateDB

databaseName = 'ABICellSurvey'

manifestFile = ('C:/Users/David/Dropbox/Documents/SantamariaLab/Projects/Fractional/ABI-FLIF/Cache/' +
                'cell_types/cell_types_manifest.json')
# manifestFile = ('C:/Users/David/Dropbox/Documents/'
#                 + 'SantamariaLab/Projects/Fractional/ABI-FLIF/FeatExtractDev/'
#                 + 'cell_types/cell_types_manifest.json')
resetDB = True  # True/False; redo all tables or add to them?
verbose = True  # Lots of status printing

#isNMRemote = False

# Choose specimens and experiments; these are just for testing
#specimens = [321707905, 469753383]
specimens = [484635029]
# specimens = [318808427]
# specimens = [321707905] # Hopefully has bursts (no, but has delays/pauses)
# specimens = [
#             321707905,
#             312883165,
#             484635029,
#             469801569,
#             469753383]
# specimens = [312883165, 484635029]
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

CreateDB(specimens, databaseName, resetDB, manifestFile, 
         cfg.mysql['host'], cfg.mysql['user'], cfg.mysql['password'], verbose)

print "Script complete."
