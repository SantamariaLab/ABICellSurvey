# Provides a MySQL database interface for CellSurvey operations 

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
             '''specFXIDX int(11), ''' +
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
             '''hasSpikes bool, ''' +                       
             '''hero_sweep_id int(11), ''' +                 
             '''hero_sweep_avg_firing_rate double, ''' +     
             '''hero_sweep_adaptation double, ''' +          
             '''hero_sweep_first_isi double, ''' +          
             '''hero_sweep_mean_isi double, ''' +           
             '''hero_sweep_median_isi double, ''' +         
             '''hero_sweep_isi_cv double, ''' +             
             '''hero_sweep_latency double, ''' +            
             '''hero_sweep_stim_amp double, ''' +           
             '''hero_sweep_v_baseline double, ''' +         
             '''dendrite_type char(15), ''' +                 
             '''electrode_0_pa double, ''' +                 
             '''f_i_curve_slope double, ''' +               
             '''fast_trough_t_long_square double, ''' +      
             '''fast_trough_t_ramp double, ''' +            
             '''fast_trough_t_short_square double, ''' +    
             '''fast_trough_v_long_square double, ''' +     
             '''fast_trough_v_ramp double, ''' +            
             '''fast_trough_v_short_square double, ''' +    
             '''has_bursts bool, ''' +                       
             '''has_delays bool, ''' +                      
             '''has_pauses bool, ''' +                      
             '''hemisphere char(10), ''' +                      
             '''input_resistance_mohm double, ''' +          
             '''peak_t_long_square double, ''' +            
             '''peak_t_ramp double, ''' +                   
             '''peak_t_short_square double, ''' +           
             '''peak_v_long_square double, ''' +            
             '''peak_v_ramp double, ''' +                   
             '''peak_v_short_square double, ''' +           
             '''reporter_status char(30), ''' +             
             '''rheobase_current double, ''' +               
             '''ri double, ''' +                            
             '''sagFraction double, ''' +                   
             '''seal_gohm double, ''' +                     
             '''slow_trough_t_long_square double, ''' +     
             '''slow_trough_t_ramp double, ''' +            
             '''slow_trough_t_short_square double, ''' +    
             '''slow_trough_v_long_square double, ''' +     
             '''slow_trough_v_ramp double, ''' +            
             '''slow_trough_v_short_square double, ''' +    
             '''structure_acronym char(20), ''' +           
             '''structure_name char(50), ''' +              
             '''tau double, ''' +                           
             '''threshold_i_long_square double, ''' +       
             '''threshold_i_ramp double, ''' +              
             '''threshold_i_short_square double, ''' +      
             '''threshold_t_long_square double, ''' +       
             '''threshold_t_ramp double, ''' +              
             '''threshold_t_short_square double, ''' +      
             '''threshold_v_long_square double, ''' +       
             '''threshold_v_ramp double, ''' +              
             '''threshold_v_short_square double, ''' +      
             '''transgenic_line char(30), ''' +             
             '''trough_t_long_square double, ''' +          
             '''trough_t_ramp double, ''' +                 
             '''trough_t_short_square double, ''' +         
             '''trough_v_long_square double, ''' +          
             '''trough_v_ramp double, ''' +                 
             '''trough_v_short_square double, ''' +         
             '''upstroke_downstroke_ratio_long_square double, ''' +  
             '''upstroke_downstroke_ratio_ramp double, ''' +         
             '''upstroke_downstroke_ratio_short_square double, ''' + 
             '''v_rest double, ''' +                         
             '''vm_for_sag double, ''' +                    
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
             '''analysisStart double, ''' +                         
             '''analysisDuration double, ''' +                      
             '''stimulusStart double, ''' +                         
             '''adaptation double, ''' +                                
             '''avgFiringRate double, ''' +                         
             '''avgHlfHgtWidth double, ''' +                        
             '''baseV double, ''' +                                 
             '''maxSpkV double, ''' +
             '''hasSpikes bool, ''' +                               
             '''numSpikes int(11), ''' +                                
             '''hasBursts bool, ''' +                                                                  
             '''numBursts int(11), ''' +                            
             '''maxBurstiness double, ''' +                         
             '''hasPauses bool, ''' +                               
             '''numPauses int(11), ''' +                                       
             '''pauseFraction double, ''' +                         
             '''hasDelay bool, ''' +                                           
             '''delayRatio double, ''' +                                       
             '''delayTau double, ''' +                                         
             '''ISIFirst double, ''' +                              
             '''ISIMean double, ''' +                               
             '''ISICV double, ''' +                                 
             '''latency double, ''' +                               
             '''stimulusLatency double, ''' +                       
             '''frstSpkThresholdV double, ''' +                     
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

    insertStr = ('insert into specimens (specIDX, donorIDX, abiSpecimenID, specFXIDX) ' + 
                 'values (%s, %s, %s, %s)')
    insertData = (0, donorIDX, specimen, None)
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

import mysql.connector    
def addSpecFX(connection, specIDX, spFXs):
    for k,v in spFXs.items():
        if not isinstance(v, basestring):
            if math.isnan(v):
                spFXs[k] = None
                
    keys = spFXs.keys()
    numKeys = len(keys)
    
    paramStrList = []
    insertData = [int(0), specIDX]
    for k,v in spFXs.items():
        paramStrList.append(k)
        insertData.append(v)
    s = ", "
    paramStr = s.join(paramStrList)
    insertStr = ('insert into specimenFXs (specFXIDX, specIDX, ' + paramStr + 
                 ') values (' + '%s, '*(numKeys-1+2) + '%s)')

    try:
        cursor = connection.cursor()
        cursor.execute(insertStr, insertData)
        specFXIDX = cursor.lastrowid
        connection.commit()
    except:
        print "Failure adding specFX to specimenFXs table"
        cursor.close()
        return(-1)

    try:
        # Add the fx to the specimen
        updateStr = 'update specimens set specFXIDX=%s where specIDX=%s'
        updateData = (specFXIDX, specIDX)
        cursor.execute(updateStr, updateData)
        cursor.close()
        connection.commit()
        return(specFXIDX)
    except mysql.connector.Error as err:
        print "Failure adding specFX to specimens table"
        print "err", err
        cursor.close()
        return(-1)

