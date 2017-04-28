% ABIFeatExtrData
% A MATLAB class that provides access to the feature extraction data in the
% ABICellSurvey MySQL database.
classdef ABIFeatExtrData < handle
    properties
        dbConn;
        specData;
        expData;
    end
    
    methods
        function obj = ABIFeatExtrData(dbConn)
            obj.dbConn = dbConn;
            % Test the connection here (not implemented yet)
        end
        
        function data = getExpFXData(obj, specNum, expNum)
            setdbprefs('DataReturnFormat', 'structure');
            dbCmd = ['SELECT experimentfxs.* FROM ' ...
                     '((experimentfxs INNER JOIN experiments on ' ...
                       'experimentfxs.expIDX=experiments.expIDX) ' ...
                      'INNER JOIN specimens ON specimens.specIDX=experiments.specIDX) ' ...
                     'WHERE specimens.abiSpecimenID=' num2str(specNum) ...
                     ' AND experiments.abiExpID=' num2str(expNum)];
            curs = exec(obj.dbConn, dbCmd);
            curs = fetch(curs);
            data = curs.Data;
            close(curs);
        end
        
        function data = getSpecFXData(obj, specNum)
            setdbprefs('DataReturnFormat', 'structure');
            dbCmd = ['SELECT specimenfxs.* FROM ' ...
                     '(specimenfxs INNER JOIN specimens on ' ...
                       'specimenfxs.specIDX=specimens.specIDX) ' ...
                     'WHERE specimens.abiSpecimenID=' num2str(specNum)];
            curs = exec(obj.dbConn, dbCmd);
            curs = fetch(curs);
            data = curs.Data;
            close(curs);
        end
        
        function info = getExpInfo(obj, specNum, expNum)
            setdbprefs('DataReturnFormat', 'structure');
            dbCmd = ['SELECT experiments.* FROM ' ...
                     '(experiments INNER JOIN specimens on ' ...
                       'experiments.specIDX=specimens.specIDX) ' ...
                     'WHERE specimens.abiSpecimenID=' num2str(specNum) ...
                     ' AND experiments.abiExpID=' num2str(expNum)];
            curs = exec(obj.dbConn, dbCmd);
            curs = fetch(curs);
            info = curs.Data;
            close(curs);
        end
    end
end
