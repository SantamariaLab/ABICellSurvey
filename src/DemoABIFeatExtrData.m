% DemoABIFeatExtrData
% Illustrates use of ABIFeatExtrData MATLAB utility.
% Utilities are simple, which provides flexibility.

clc
clear classes;

%% Connect with the experimental data (ABI) database
config = ini2struct('config.ini');
username = config.CellSurvey.mySQLUsername;
password = config.CellSurvey.mySQLPassword;

% database exists and is populated
abiDatabaseName = 'ABICellSurvey';
disp(['Connecting to ABI database ' abiDatabaseName '.']);
abiDBConn = database.ODBCConnection(abiDatabaseName, username, password);

afed = ABIFeatExtrData(abiDBConn);

specNum = 469753383;
expNum = 48;

expData = afed.getExpFXData(specNum, expNum);

specData = afed.getSpecFXData(specNum);

expInfo = afed.getExpInfo(specNum, expNum);

