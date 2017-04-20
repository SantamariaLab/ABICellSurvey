def dropTable(connection,tableName):
    try:
        mycmd = 'DROP TABLE ' + tableName
        cursor = connection.cursor()
        cursor.execute(mycmd)
        result = True
    except: 
        result = False
        
    cursor.close()                
    return(result)


def createDonorsTable(connection):
    mycmd = ('''CREATE TABLE donors (''' + 
             '''donorIDX int(11) NOT NULL AUTO_INCREMENT, ''' + 
             '''abiDonorID int(11), ''' + 
             '''sex char(4), ''' + 
             '''name char(100), ''' + 
             '''PRIMARY KEY (donorIDX)) ENGINE=InnoDB''')
    try:
        cursor = connection.cursor()
        cursor.execute(mycmd)
        result = True
    except:
        result = False
        
    cursor.close()                
    return(result)


def createSpecimensTable(connection):
    mycmd = ('''CREATE TABLE specimens (''' + 
             '''specIDX int(11) NOT NULL AUTO_INCREMENT, ''' + 
             '''donorIDX int(11), ''' + 
             '''abiSpecimenID int(11), ''' +
             '''FOREIGN KEY (donorIDX) REFERENCES donors (donorIDX) ON DELETE CASCADE, ''' +  
             '''PRIMARY KEY (specIDX)) ENGINE=InnoDB''')
    try:
        cursor = connection.cursor()
        cursor.execute(mycmd)
        result = True
    except:
        result = False
        
    cursor.close()                
    return(result)


def createExperimentsTable(connection):
    mycmd = ('''CREATE TABLE experiments (''' + 
             '''expIDX int(11) NOT NULL AUTO_INCREMENT, ''' + 
             '''specIDX int(11) NOT NULL, ''' +
             '''abiExpID int(11), ''' +
             '''expFXIDX int(11), ''' +          
             '''sampling_rate int(11), ''' +
             '''stimulusType char(100), ''' + 
             '''stimCurrent double, ''' +
             '''FOREIGN KEY(specIDX) REFERENCES specimens(specIDX) ON DELETE CASCADE, ''' + 
             '''PRIMARY KEY (expIDX)) ENGINE=InnoDB''')
    try:
        cursor = connection.cursor()
        cursor.execute(mycmd)
        result = True
    except:
        result = False
        
    cursor.close()                
    return(result)


def createSpecimenFXsTable(connection):
    mycmd = ('''CREATE TABLE specimenFXs (''' + 
             '''specFXIDX int(11) NOT NULL AUTO_INCREMENT, ''' + 
             '''specIDX int(11) NOT NULL, ''' + 
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
             '''FOREIGN KEY(specIDX) REFERENCES specimens(specIDX) ON DELETE CASCADE, ''' +
             '''PRIMARY KEY (specFXIDX)) ENGINE=InnoDB''')
    try:
        cursor = connection.cursor()
        cursor.execute(mycmd)
        result = True
    except:
        result = False
        
    cursor.close()                
    return(result)


def createExperimentFXsTable(connection):
    mycmd = ('''CREATE TABLE experimentFXs (''' + 
             '''expFXIDX int(11) NOT NULL AUTO_INCREMENT, ''' +
             '''expIDX int(11) NOT NULL, ''' +  
             '''analysisStart double, ''' +                         #           in seconds
             '''analysisDuration double, ''' +                      #           in seconds
             '''stimulusStart double, ''' +                         # in seconds
             '''adaptation double, ''' +                            # xcf ok    
             '''avgFiringRate double, ''' +                         # xcf ok    spikes per second
             '''avgHlfHgtWidth double, ''' +                        # units???
             '''baseV double, ''' +                                 # mV
             '''maxSpkV double, ''' +
             '''hasSpikes bool, ''' +                               # xcf ok    1=true;0=false
             '''numSpikes int(11), ''' +                            # xcf ok    
             '''hasBursts bool, ''' +                               #           1=true;0=false                                   
             '''numBursts int(11), ''' +                            #
             '''maxBurstiness double, ''' +                         #
             '''hasPauses bool, ''' +                               #           1=true;0=false
             '''numPauses int(11), ''' +                            #           
             '''pauseFraction double, ''' +                         #           %
             '''hasDelay bool, ''' +                                #           
             '''delayRatio double, ''' +                            #           
             '''delayTau double, ''' +                              #           
             '''ISIFirst double, ''' +                              # xcf ok    in seconds
             '''ISIMean double, ''' +                               # xcf ok    in seconds
             '''ISICV double, ''' +                                 # xcf ok    dimensionless
             '''latency double, ''' +                               # xcf ok    in seconds
             '''stimulusLatency double, ''' +                       # xcf ok    in seconds
             '''frstSpkThresholdV double, ''' +                     #           in milliVolts
             '''FOREIGN KEY(expIDX) REFERENCES experiments(expIDX) ON DELETE CASCADE, ''' +
             '''PRIMARY KEY (expFXIDX)) ENGINE=InnoDB''')
    try:
        cursor = connection.cursor()
        cursor.execute(mycmd)
        result = True
    except:
        result = False
        
    cursor.close()                
    return(result)


def addSpecimen(connection, donorID, specimen):
    queryStr = 'select donorIDX from donors where abiDonorID=' + str(donorID)
    try:
        cursor = connection.cursor()
        cursor.execute(queryStr)
        row = cursor.fetchone()
        donorIDX = row[0]
    except:
        cursor.close()
        return(-1)

    insertStr = ('insert into specimens (specIDX, donorIDX, abiSpecimenID) ' + 
                 'values (%s, %s, %s)')
    insertData = (0, donorIDX, specimen)
    try:
        cursor.execute(insertStr, insertData)
        specimenTableID = cursor.lastrowid
        cursor.close()                
        connection.commit()
        return(specimenTableID)
    except:
        print "Failure adding to specimens table"
        cursor.close()
        return(-1)


def addExperiment(connection, specimenTableIDX, sweepNum, samplingRate,
                  stimulusType, stimulusCurrent):
    insertStr = ('insert into experiments (expIDX, specIDX, ' + 
                 'abiExpID, expFXIDX, sampling_rate, ' + 
                 'stimulusType, stimCurrent) ' + 
                 'values (' +
                 '%s, '*6 + '%s' + 
                 ')')
    insertData = (int(0), specimenTableIDX, sweepNum, None, samplingRate, 
                  stimulusType, stimulusCurrent)
    try:
        cursor = connection.cursor()
        cursor.execute(insertStr, insertData)
        experimentIDX = cursor.lastrowid
        cursor.close()
        connection.commit()
        return(experimentIDX)
    except:
        print "Failure adding to experiments table"
        cursor.close()
        return(-1)


def addDonor(connection, abiDonorID, sex, name):
    queryStr = 'select * from donors where abiDonorID=' + str(abiDonorID)
    try:
        cursor = connection.cursor()
        cursor.execute(queryStr)
        row = cursor.fetchone()
        if row is None:
            insertStr = ('insert into donors (donorIDX, abiDonorID, sex, name) ' +
                         ' values(%s, %s, %s, %s)')
            insertData = (0, abiDonorID, sex, name)
            cursor.execute(insertStr, insertData)
            donorIDX = cursor.lastrowid
            connection.commit()
            return(donorIDX)
        else:
            donorIDX = row[0]
            cursor.close()
            return(donorIDX)
    except:
        print "Failure adding to donors table"
        cursor.close()
        return(-1)

import math
def addExpFX(connection, experimentIDX, swFXs):
    for k,v in swFXs.items():
        if not isinstance(v, basestring):
            if isinstance(v, float):
                if math.isnan(v):
                    swFXs[k] = None
                
    keys = swFXs.keys()
    numKeys = len(keys)

    paramStrList = []
    insertData = [int(0), experimentIDX]
    for k,v in swFXs.items():
        paramStrList.append(k)
        insertData.append(v)
    s = ", "
    paramStr = s.join(paramStrList)
    insertStr = ('insert into experimentFXs (expFXIDX, expIDX, ' + paramStr + 
                 ') values (' + '%s, '*(numKeys-1+2) + '%s)')
    
    try:
        cursor = connection.cursor()
        cursor.execute(insertStr, insertData)
        fxIDX = cursor.lastrowid
        connection.commit()
    except:
        print "Failure adding to experimentFXs table"
        cursor.close()
        return(-1)

    try:
        # Add the fx to the experiment
        updateStr = 'update experiments set expFXIDX=%s where expIDX=%s'
        updateData = (fxIDX, experimentIDX)
        cursor.execute(updateStr, updateData)
        cursor.close()
        connection.commit()
        return(fxIDX)
    except:
        print "Failure adding expFX to experiments table"
        cursor.close()
        return(-1)
    

def addSpecFX(connection, specimenTableID, spFXs):
    for k,v in spFXs.items():
        if not isinstance(v, basestring):
            if math.isnan(v):
                spFXs[k] = None
                
    keys = spFXs.keys()
    numKeys = len(keys)
    
    paramStrList = []
    insertData = [int(0), specimenTableID]
    for k,v in spFXs.items():
        paramStrList.append(k)
        insertData.append(v)
    s = ", "
    paramStr = s.join(paramStrList)
    insertStr = ('insert into specimenFXs (specFXIDX, specIDX, ' + paramStr + 
                 ') values (' + '%s, '*(numKeys-1+2) + '%s)')
    print "insertStr", insertStr
    print "insertData", insertData

    try:
        cursor = connection.cursor()
        cursor.execute(insertStr, insertData)
        specFXTableIDX = cursor.lastrowid
        cursor.close()
        connection.commit()
        return(specFXTableIDX)
    except:
        print "Failure adding specFX to specimenFXs table"
        cursor.close()
        return(-1)


