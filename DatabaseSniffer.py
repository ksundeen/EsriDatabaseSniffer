
import arcpy, os, sys
from datetime import datetime
import argparse
import xlwt
import pandas as pd
import codecs
sys.path.append('./helpers')
from MessageLogger import MessageLogger
from DatabaseHelper import DatabaseHelper

## ---- Set Globals ---- ##

class DatabaseSnifferDb:
    """
    Purpose
    Parameters
    ----------
    
    Author: Kim Sundeen, 1/25/2022
    Purpose: Exports out csv and Excel files of metadatafor Esri enterprise or file geodatabases. Outputs include excel domains,  
    feature class feature counts, feature class feature counts, subtype descriptions, and subtype counts by configured fields.    
    
    Returns
    -------
    class instance of DatabaseSniffer.
    """
    
    def __init__(self, config, dbParams): 
        globals = config["globals"]
        domainSchemaConfig = globals["domainSchemaConfig"]
        featureCountConfig = globals["featureCountConfig"]
        fieldCountConfig = globals["fieldCountConfig"]
        subtypeConfig = globals["subtypeConfig"]
        subtypeCountConfig = globals["subtypeCountConfig"]
        attributeRulesConfig = globals["attributeRulesConfig"]
        
        # Config global params
        self.outDir = globals["outDir"]
        self.csvLoggingFilepath = globals["csvLoggingFilepath"]
        self.mergeCsvsToExcel = globals["mergeCsvsToExcel"].upper()
        self.skipSystemFieldTypes = globals["skipSystemFieldTypes"]
                
        # Opens write files for read/write (w) of append (a) from config
        self.overWriteOption = "w" if globals["overWriteOption"] == "YES" else "a"
        
        # Config Feature Count file params
        self.featureCountRun = featureCountConfig["run"].upper()
        self.featureCountHeaders = featureCountConfig["featureCountHeaders"]
        
        # Config Field Count file params
        self.domainSchemaRun = domainSchemaConfig["run"].upper()           
        
        # Config for attribute rules
        self.attributeRulesRun = attributeRulesConfig["run"].upper()

        # Config Field Count file params
        self.fieldCountRun = fieldCountConfig["run"].upper()    
        self.fieldCountHeaders = fieldCountConfig["fieldCountHeaders"]
        self.fieldCountLimit = fieldCountConfig["fieldCountLimit"]
        self.includeFieldCountFields = fieldCountConfig["includeFieldCountFields"] if dbParams["includeFieldCountFields"] == "GLOBAL" else dbParams["includeFieldCountFields"]        
        self.excludeFieldCountFields = fieldCountConfig["excludeFieldCountFields"] if dbParams["excludeFieldCountFields"] == "GLOBAL" else dbParams["excludeFieldCountFields"]

        # Config Subtype file params
        self.subtypeRun = subtypeConfig["run"].upper()    
        self.subtypeHeaders = subtypeConfig["subtypeHeaders"]
        
        # Config Subtype Count file params    
        self.subtypeCountRun = subtypeCountConfig["run"].upper()        
        self.subtypeCountHeaders = subtypeCountConfig["subtypeCountHeaders"]
        self.includeSubtypeCountFields = subtypeCountConfig["includeSubtypeCountFields"] if dbParams["includeSubtypeCountFields"] == "GLOBAL" else dbParams["includeSubtypeCountFields"]        
        self.excludeSubtypeCountFields = subtypeCountConfig["excludeSubtypeCountFields"] if dbParams["excludeSubtypeCountFields"] == "GLOBAL" else dbParams["excludeSubtypeCountFields"]
        self.subtypeShowMarginCount = subtypeCountConfig["subtypeShowMarginCount"]
        self.subtypeCountCategoryLimit = subtypeCountConfig["subtypeCountCategoryLimit"]
                
        # Config database params
        self.sourceDir = dbParams["sourceDir"]
        self.dataSetsToCheck = dbParams["dataSetsToCheck"]
        self.keyword = dbParams["keyword"]
        self.fcList = [w.upper() for w in dbParams["fcList"]] if len(dbParams["fcList"]) > 0 else []
        self.skipFcList = [w.upper() for w in dbParams["skipFcList"]] if len(dbParams["skipFcList"]) > 0 else []
        
        # Dynamically-generated params
        #Pandas field count data frame object
        self.fieldCountdf = None
        
        self.outExcelFilepath = None

        self.featureCountCsvFilepath = None
        self.featureCountFileWriter = None # Output file object for CSV summaries (until converted to pandas df)       
        
        self.fieldCountCsvFilepath = None
        self.fieldCountFileWriter = None # Output file object for CSV summaries (until converted to pandas df)
        
        self.subtypeCsvFilepath = None
        self.subtypeFileWriter = None # Output file object for CSV subtype summaries (until converted to pandas df)
        
        self.subtypeCountCsvFilepath = None
        self.subtypeCountFileWriter = None # Output file object for CSV subtype summaries (until converted to pandas df)

        # Set environment
        arcpy.env.workspace = self.sourceDir

    def _exportDomainSchemaToExcel(self):
        workbook = xlwt.Workbook()

        # Applying multiple styles
        style = xlwt.easyxf('font: bold 1')  #, color red;')

        # Domain list in workspace
        domains = arcpy.da.ListDomains(arcpy.env.workspace)
        counter = 0

        try:
            for domain in domains:
                domainName = domain.name
                sheetName = domain.name
                # Shorten domain name to allowed 22 char length
                if len(domainName) > 22:
                    sheetName = '{0}_{1}'.format(domainName[:20], counter)
                    counter += 1
                    
                # Replace invalid XLSX sheet name chars
                sheetName = sheetName.replace("\\", "-").replace("/", "-")
                # Domain Sheet
                domainSheet = workbook.add_sheet(sheetName)

                # Add Sheet headers
                domainSheet.write(0, 0, 'DomainName', style)
                domainSheet.write(1, 0, 'DomainType', style)
                domainSheet.write(2, 0, 'FieldType', style)
                domainSheet.write(3, 0, 'MergePolicy', style)
                domainSheet.write(4, 0, 'SplitPolicy', style)
                domainSheet.write(5, 0, 'Range', style)
                domainSheet.write(6, 0, 'Description', style)
                domainSheet.write(7, 0, 'Owner', style)
                domainSheet.write(8, 0, '')

                domainSheet.write(0, 1, '{}'.format(domainName))
                domainSheet.write(1, 1, '{}'.format(domain.domainType))
                domainSheet.write(2, 1, '{}'.format(domain.type))
                domainSheet.write(3, 1, '{}'.format(domain.mergePolicy))
                domainSheet.write(4, 1, '{}'.format(domain.splitPolicy))
                domainSheet.write(5, 1, '{}'.format(domain.range))
                domainSheet.write(6, 1, '{}'.format(domain.description))
                domainSheet.write(7, 1, '{}'.format(domain.owner))

                # Format Coded Values with counter for rows
                rowCounter = 11
                if domain.domainType == 'CodedValue':
                    # Only label for coded values
                    domainSheet.write(9, 0, 'CodedValues', style)
                    domainSheet.write(10, 0, 'Code')
                    domainSheet.write(10, 1, 'Name')

                    codedValues = domain.codedValues

                    for code, val in codedValues.items():
                        # Write code
                        domainSheet.write(rowCounter, 0, '{}'.format(code))
                        # Write description/name
                        domainSheet.write(rowCounter, 1, '{}'.format(val))
                        rowCounter += 1

                elif domain.domainType == 'Range':
                    domainSheet.write(9, 0, 'RangeValues')
                    domainSheet.write(10, 1, 'Code')

                    rangeValues = domain.range

                    for val in rangeValues:
                        # Write code
                        domainSheet.write(rowCounter, 1, '{}'.format(val))
                        rowCounter += 1
                        
            domainOutExcelFilepath = os.path.join(self.outDir, '{0}_DomainsOnly.xls'.format(self.keyword))
            workbook.save(domainOutExcelFilepath)
            arcpy.AddMessage("Finished exporting domains\n")
            self.logger.info("Finished exporting domains\n")     
                   
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in exportDomainSchemaToExcel():\n\t{}".format(ex))

    def _getFieldDomains(self, field):
        try:
            domains = arcpy.da.ListDomains(arcpy.env.workspace)
            domainStr = ''
            # Run through domain values.
            for domain in domains:
                if '{0}'.format(field.domain) == '{0}'.format(
                        domain.name):
                    # IF THE DOMAIN IN THE FIELD MATCHES A DOMAIN IN THE SDE, IT PRINTS THE VALUES
                    domainStr += '{0}'.format(domain.name)
                    if domain.domainType == 'CodedValue':
                        coded_values = domain.codedValues
                        domainStr += ',IsCodedValueDomain,'
                        for val, desc in coded_values.items():
                            if "," in desc:
                                desc = desc.replace(",", "'")
                            domainStr += '{0} : {1}'.format(val, desc) +' | '
                    
                    elif domain.domainType == 'Range':
                        domainStr += ',IsRangeDomain,Min: {0} | Max: {1} |'.format(
                            domain.range[0], 
                            domain.range[1])
                    else:
                        print('No Domain')
                        self.logger.info('No Domain')
            return domainStr
                    
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _writeFieldDomains: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _writeFieldDomains: {0}\n\t".format(ex))
    
    def _calcUniqueCounts(self, fc, setDict, fieldName):
        # counts unique values in field
        data = [row[0] for row in arcpy.da.SearchCursor(fc, fieldName)]
        
        for val in set(data):
            valCount = data.count(val)
            setDict[val] = valCount

        # Clean up setDict for printing
        setDict = self._cleanAndLimitSetDict(setDict, fieldName)
        return setDict
    
    def _checkIfSystemField(self, fieldName, fieldType):
        
        if fieldName in self.skipSystemFieldTypes:
            return True           
        # Skip field if configured to skip
        elif fieldType in [u'Blob', u'OID', u'Geometry']:
            return True    
        return False     
    
    def _checkIfCalcSummary(self, fieldName, includeList, excludeList):
        #Skip any system-generated fields to remove from data sheet entirely
        # Limits unique values for configured fields (if present)
        if len(includeList) > 0:
            if any(f in fieldName for f in includeList):
                return True
            # Only calculate unique if include fields count fields is populated. 
            return False
          
        elif fieldName in excludeList: 
            return False  
        else: 
            for exField in excludeList:
                if exField.upper() in fieldName:
                    return False                     

        for includeField in includeList:
            if includeField.upper() in fieldName:
                return False
            
        return True
    
    def _writeFcFields(self, fc, featureCount, datasetValues):
        try:
            # Dictionary of unique value with their counts per field
            fields = arcpy.ListFields(fc)

            # For each field in fc, count unique values & describe of fields
            for field in fields:
                # Set defaults
                upperCaseField = str(field.name).upper()
                isSystemSkipField = False        
                # Skip field if configured to skip
                if field.type in self.skipSystemFieldTypes:
                    isSystemSkipField = True    
                
                calculateUnique = self._checkIfCalcSummary(upperCaseField, self.includeFieldCountFields, self.excludeFieldCountFields)

                # Set defaults
                setDict = {}  
                nullPercent = ''                
                domainStr = ''
                
                if isSystemSkipField is False: 
                    if calculateUnique:
                        setDict = self._calcUniqueCounts(fc, setDict, upperCaseField)
                        nullPercent = self._calcNullPercent(fc, field, featureCount, setDict, True)
                        setDict = str(setDict).replace(',', ';')               
                    else:
                        nullPercent = self._calcNullPercent(fc, field, featureCount, setDict, False)                                    
                        setDict = "SKIPPED COUNT"
                    
                    # Calculate domains for all fields for reference
                    domainStr = self._getFieldDomains(field)
                else:
                    setDict = "SYSTEM FIELD SKIPPED"
                    nullPercent = "NA"
                    domainStr = ""
                    
                # Appends to CSV file        
                self.fieldCountFileWriter.write('\n{0},{1},{2},{3},{4},{5},{6},{7},{8}'.format(
                    datasetValues,
                    str(field.name), 
                    str(field.aliasName), 
                    str(field.type), 
                    str(field.length), 
                    str(field.precision), 
                    setDict, 
                    nullPercent,
                    domainStr)
                )
                                
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _writeFcFields: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _writeFcFields: {0}\n\t".format(ex))
            
    def _cleanAndLimitSetDict(self, setDict, upperCaseField):
        '''Pair down the full list of unique values to the uniqueCountLimit'''
        try:
            setDictUpdate = {}
            
            # Skip if summaryField is configured to be skipped
            if upperCaseField in self.excludeFieldCountFields: 
                return "EXCLUDED"
            
            else: 
                for exField in self.excludeFieldCountFields:
                    if exField.upper() in upperCaseField:
                        return "EXCLUDED"
            
            # Limits unique values for configured fields (if present)
            if any(f in upperCaseField for f in self.includeFieldCountFields):
                return setDict
            else:
                for includeField in self.includeFieldCountFields:
                    if includeField.upper() in upperCaseField:
                        return setDict

            # limit count to the threshold
            for key in list(setDict)[0:self.fieldCountLimit]:
                setDictUpdate[key] = setDict[key]
            # return str(setDictUpdate).replace(",", ";")
            return setDictUpdate

        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _cleanAndLimitSetDict: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _cleanAndLimitSetDict: {0}\n\t".format(ex))
        
    def _calcNullPercent(self, fc, field, featureCount, setDict, calculateUnique):
        featureCountFloat = None
        nullPercent = 0
        
        try:
            featureCountFloat = float(featureCount[0])
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in calNullPercent: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _calcNullPercent: {0}\n\t".format(ex))          
        
        if calculateUnique is False:
            whereClause = '"{0}" IS NULL'.format(field.name)
            nullData = [row[0] for row in arcpy.da.SearchCursor(fc, field.name, where_clause=whereClause)]
            if float(featureCount[0]) == 0:
                return 100
            else:
                return (len(nullData) / float(featureCount[0])) * 100
        
        if isinstance(setDict, dict):
            if (len(setDict) == 0):
                    nullPercent = 100
            elif (len(setDict) > 0):
                totalNullTypes = 0.0
            
                for countKey in setDict.keys():
                    if (countKey in [None, u'None', 'None', '', ' ']):
                        totalNullTypes += setDict[countKey]
                        
                nullPercent = (totalNullTypes/featureCountFloat) * 100.0
                return nullPercent
            return nullPercent
        else: 
            return "NULL % COUNT SKIPPED"
            
    def _calcCrossTab(self, inTable, fieldDict, whereClause=None):       
        crosstab = ''
 
        try:            
            # Skip if summaryField is any datetime field
            if fieldDict['summaryField'].upper() in self.excludeSubtypeCountFields: 
                return 'FIELD EXCLUDED'
            
            else: 
                for exField in self.excludeSubtypeCountFields:
                    if exField.upper() in fieldDict['summaryField'].upper():
                        return 'FIELD EXCLUDED'
                        
            if crosstab == '':            
                # inFields = [fieldDict['subtypeField'], fieldDict['summaryField']]
                inFields = [fieldDict['subtypeField'], fieldDict['summaryField']]
                
                data = [row for row in arcpy.da.SearchCursor(inTable, inFields, where_clause=whereClause)]
                
                # if None in data value row[1]. Continues to throw 'No objects to concatenate'
                newData = []
                for i in data:
                    newVal = []
                    if i[1] is None:
                        newVal = [i[0], 'Null']
                    else:
                        newVal = i
                    newData.append(newVal)
                    data = newData
                                    
                df = pd.DataFrame(data, columns=inFields)
                                    
                crosstabObj = pd.crosstab(index=df[inFields[0]], columns=df[inFields[1]], dropna=False, margins=True, margins_name="Total")
                
                if isinstance(crosstabObj, pd.DataFrame):
                    # Converts to str type
                    numColumns = len(crosstabObj.columns.to_list())
                    if numColumns > self.subtypeCountCategoryLimit:
                        crosstab = "EXCEEDED {0} CATEGORY LIMIT. Found {1}".format(self.subtypeCountCategoryLimit, numColumns)
                    else:
                        crosstab = crosstabObj.to_csv(sep=",")
                
            return str(crosstab)  
                     
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _calcCrossTab: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _calcCrossTab: {0}\n\t".format(ex))

    def _formatCrossTab(self, fc, field, formattedHeaderVals, subtypeDict):       
        crosstabObj = ''
        # Only check fields that are not the subtype field
        if field != subtypeDict['SubtypeField']:
                
            # Summarize field by subtype field (if there is a subtype)
            if subtypeDict['SubtypeField'] not in [u'', None]:
                fieldDict = {'subtypeField': subtypeDict['SubtypeField'], 'summaryField': field}

                try:
                    # crosstab = self._formatCrossTab(fc, fieldDict, whereClause)
                    crosstabObj = self._calcCrossTab(fc, fieldDict)
                        
                except Exception as ex:
                    arcpy.AddMessage("Exception Thrown in crosstab: {0}\n\t".format(ex))
                    
            else:
                crosstabObj = 'NO SUBTYPE ASSIGNED'
             
        crosstabFrmt = ''                   
        if crosstabObj in [None, 'None', '', 'NO SUBTYPE ASSIGNED']:
            crosstabFrmt = 'NO SUBTYPE ASSIGNED'
        elif crosstabObj == 'FIELD EXCLUDED':
            crosstabFrmt = 'FIELD EXCLUDED IN CONFIG'            
        else:        
            # Remove line breaks
            crosstabFrmt = crosstabObj.rstrip('\r\n')
            # crosstabFrmt = crosstabObj.replace('\r\n', '\n')
            
            if self.subtypeShowMarginCount == 'YES':
                # Re-format 1st occurance of VERTICAL Total crosstab str
                crosstabFrmt = crosstabFrmt.replace('Total\r\n', 'Total\n{0},'.format(formattedHeaderVals), 1)
                                    
                # Re-format 1st occurance of HORIZONTAL Total crosstab str
                crosstabFrmt = crosstabFrmt.replace('\r\nTotal', '\n{0},Total'.format(formattedHeaderVals), 1)  
                
            # Replace double returns with single
            crosstabFrmt = crosstabFrmt.replace('\r\n', '\n' + formattedHeaderVals)
            
            # Replace all misaligned cells ,| to
        
        
        allData = '{0},{1}\n'.format(formattedHeaderVals, crosstabFrmt)   
        allData = allData.replace('|,,', '|,')
        return allData

    def _writeSubtypeCounts(self, fc, subtypes, datasetValues): 
        try: 
            # Write subtypes only if configured
            continueSubtypeCounts = True
            
            for subtypeCode, subtypeDict in subtypes.items():   
                if continueSubtypeCounts is False: break              
                fields = subtypeDict['FieldValues']
                
                
                # Iterate through each subtype dictionary & writes subtype name (field) & list of values (fieldvals)                
                for field, fieldvals in fields.items():   
                
                    subtypeField = subtypeDict['SubtypeField'] if subtypeDict['SubtypeField'] != '' else False
                                                        
                    formattedHeaderVals = '{0},{1},|,'.format(datasetValues,field)
                    
                    if subtypeField is False:
                        self.subtypeCountFileWriter.write(formattedHeaderVals + 'NO SUBTYPE ASSIGNED\n')
                        # continueSubtypeCounts = False # end writing for no subtypes
                        break
                    else:
                        # Only run subtype comparisons for configured fields
                        calcSubtypeCrossTab = self._checkIfCalcSummary(field.upper(), self.includeSubtypeCountFields, self.excludeSubtypeCountFields)
                        if calcSubtypeCrossTab:
                            data = self._formatCrossTab(fc, field, formattedHeaderVals, subtypeDict)
                            self.subtypeCountFileWriter.write(data)
                            continueSubtypeCounts = False
                            continue
                                            
                print('\nCompleted with SubtypeField: {0} - {1}'.format(str(subtypeCode), str(subtypeDict['Name'])))
                self.logger.info('Completed with SubtypeField: {0} - {1}'.format(str(subtypeCode), str(subtypeDict['Name']))) 
                
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _writeSubtypeCounts: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _writeSubtypeCounts: {0}\n\t".format(ex))

    def _writeSubtypes(self, subtypes, datasetValues): 
        try:   
            # Write subtypes only if configured
            continueSubtypeCounts = True   
                        
            for subtypeCode, subtypeDict in subtypes.items(): 
                subtypeDesc = subtypeDict['Name']
                if continueSubtypeCounts is False: break                                              
                fields = subtypeDict['FieldValues']
                               
                # Iterate through each subtype dictionary & writes subtype name (field) & list of values (fieldvals)                
                for field, fieldvals in fields.items():   
                    
                        subtypeField = subtypeDict['SubtypeField'] if subtypeDict['SubtypeField'] != '' else False
                    
                        ###--- Format DEFAULT FIELD VALUES if present ---##
                        defaultVals = fieldvals[0]
                        
                        ###--- Format DOMAIN NAME if present ---##
                        domainName = str(fieldvals[1].name) if fieldvals[1] is not None else 'NO FIELD DOMAIN'
                        
                        # Format pre freuquency header values
                        formattedSubtypeVals = '{0},{1},{2},{3},{4},{5},{6}\n'.format(
                            datasetValues,
                            str(subtypeCode), 
                            str(subtypeDesc),
                            subtypeField, 
                            field, 
                            defaultVals,
                            domainName
                        )
                        self.subtypeFileWriter.write(formattedSubtypeVals)                    
                        
                        if subtypeField is False:
                            break
                        
                # self.subtypeFileWriter.write(",\n")
                print('\nCompleted with SubtypeField: {0} - {1}'.format(str(subtypeCode), str(subtypeDict['Name'])))
                self.logger.info('Completed with SubtypeField: {0} - {1}'.format(str(subtypeCode), str(subtypeDict['Name']))) 
                
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _writeSubtypes: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _writeSubtypes: {0}\n\t".format(ex))
    
    def _writeData(self, datasetIndex, fc):
        '''
            Purpose: method creates output formatted file with headers just for the feature class feature count.
        '''
        try:
            featureCount = arcpy.GetCount_management(fc)
            if featureCount is not None:
                properties = arcpy.Describe(fc)
                
                datasetValues = '{0},{1},{2},{3},{4}'.format(
                    str(self.dataSetsToCheck[datasetIndex]), 
                    str(fc),
                    str(properties.featureType), 
                    str(properties.shapeType),
                    str(featureCount)
                )                
                
                if self.featureCountRun == "YES":
                    self.featureCountFileWriter.write('{0}\n'.format(datasetValues))
                
                if self.fieldCountRun == "YES":
                    # self.fieldCountFileWriter.write(datasetValues)
                    self._writeFcFields(fc, featureCount, datasetValues)
                    
                if self.subtypeRun == "YES" or self.subtypeCountRun == "YES":
                    subtypes = arcpy.da.ListSubtypes(fc)       

                    if self.subtypeRun == "YES":
                        self._writeSubtypes(subtypes, datasetValues)
                    
                    if self.subtypeCountRun == "YES":
                        self._writeSubtypeCounts(fc, subtypes, datasetValues)
                
                if self.attributeRulesRun == "YES":
                    # Create attribute rules folder
                    attributeRulesDir = os.path.join(self.outDir, "attributeRulesExport")
                    inTable = os.path.join(self.sourceDir, fc)
                    if os.path.isdir(attributeRulesDir) is False:
                        os.makedirs(attributeRulesDir)
                        
                    outFilepath = os.path.join(attributeRulesDir, fc + ".csv")
                    arcpy.ExportAttributeRules_management(inTable, outFilepath)
                    
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _writeData: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _writeData: {0}\n\t".format(ex))
                          
    def _loopThroughFeatureClasses(self, datasetIndex):
        featuresToCheck = []
        try:   
            if (self.dataSetsToCheck[datasetIndex] == 'STANDALONE'):
                featuresToCheck = arcpy.ListFeatureClasses()
                print('\nChecking standalone tables\n')
            
            elif self.dataSetsToCheck[datasetIndex] is not None and self.dataSetsToCheck[datasetIndex] != 'ALL':
                featuresToCheck = arcpy.ListFeatureClasses(feature_dataset=self.dataSetsToCheck[datasetIndex])
                print('\nStarting Dataset\n:', self.dataSetsToCheck[datasetIndex])

            # Run if no feature datasets in db
            else:
                featuresToCheck = arcpy.ListFeatureClasses()
                print('\nNo datasets found\n:')


            # Iterate through listed feature classes in dataset list, count # features, describe properties, & write properties in output file
            for fc in featuresToCheck:
                try:
                    # Only check fcList if provided.
                    if len(self.fcList) > 0:
                        if fc.upper() not in self.fcList: continue   
                                    
                    # Skip listed feature classes                                             
                    if fc.upper() in self.skipFcList: continue

                    print('\nStarting Feature Class:', fc)
                    self.logger.info('Feature Class:' + fc)
                    self._writeData(datasetIndex, fc)
                                                
                except Exception as ex:
                    arcpy.AddMessage("Exception Thrown in _loopThroughFeatureClasses method for fc loop: {0}\n\t".format(ex, fc))

        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _loopThroughFeatureClasses: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _loopThroughFeatureClasses: {0}\n\t".format(ex))

    def _loopThroughDatasets(self):            
        try:            
            # datasetIndex for # of feature classes in dataset
            datasetIndex = 0

            if (self.dataSetsToCheck[datasetIndex] == 'ALL'):
                self.dataSetsToCheck = arcpy.ListDatasets()
                print('\nChecking all feature datasets')          
                # self.logger.info('Checking all feature datasets')          

            while (datasetIndex < len(self.dataSetsToCheck)):
                self._loopThroughFeatureClasses(datasetIndex)
                datasetIndex += 1   

        
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _loopThroughDatasets: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _loopThroughDatasets: {0}\n\t".format(ex))
    
    def _formatFeatureCountHeaders(self):
        # Field header names for feature dataset & feature counts
        h = self.featureCountHeaders
        headers = '{0},{1},{2},{3},{4}'.format(
            h["featureDataset"],
            h["featureClass"],
            h["featureType"],
            h["shapeType"],
            h["featureCount"]
        )
        return headers    
        
    def _formatFieldCountHeaders(self):
        h = self.fieldCountHeaders
        headers = '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14}'.format(
            h["featureDataset"],
            h["featureClass"],
            h["featureType"],
            h["shapeType"],
            h["featureCount"],
            h["fieldName"], 
            h["fieldAlias"], 
            h["fieldType"], 
            h["fieldLength"], 
            h["fieldPrecision"], 
            h["fieldCounts"], 
            h["nullPercent"], 
            h["fieldDomain"], 
            h["domainType"], 
            h["domainValues"]
        )
        return headers
    
    def _formatFieldCountDfHeaders(self):
        h = self.fieldCountHeaders
        headers = [
            h["featureDataset"],
            h["featureClass"],
            h["featureType"],
            h["shapeType"],
            h["featureCount"],
            h["fieldName"], 
            h["fieldAlias"], 
            h["fieldType"], 
            h["fieldLength"], 
            h["fieldPrecision"], 
            h["fieldCounts"], 
            h["nullPercent"], 
            h["fieldDomain"], 
            h["domainType"], 
            h["domainValues"]
        ]
        return headers    

    def _formatSubtypeHeaders(self):
        s = self.subtypeHeaders
        headers = '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}'.format(
            s["featureDataset"],
            s["featureClass"],
            s["featureType"],
            s["shapeType"],
            s["featureCount"],
            s["subtypeCode"],
            s["subtypeDesc"], 
            s["subtypeName"], 
            s["fieldName"], 
            s["defaultValues"], 
            s["domain"],
        )
        return headers

    def _formatSubtypeCountHeaders(self):
        s = self.subtypeCountHeaders
        extraSpacers = ''
        for i in range(self.subtypeCountCategoryLimit + 5):
            extraSpacers += ',col{0}'.format(i)
        headers = '{0},{1},{2},{3},{4},{5},|,{6}{7}'.format(
            s["featureDataset"],
            s["featureClass"],
            s["featureType"],
            s["shapeType"],
            s["featureCount"],            
            s["fieldName"],
            s["subtypeCount"]
            ,extraSpacers
        )
        return headers
    
    def _formatDateTime(self):
        now = datetime.now()
        return now.strftime("\n\nData exported %m/%d/%Y %H:%M:%S\n\n")
    
    def _checkPy27(self):
        if sys.version_info[0] == 2:
            return True
        else:
            return False
    
    def _createFeatureCountFiles(self):
        try:
            # Field header names for output CSV file:
            headers = self._formatFeatureCountHeaders() 
            formattedDateTime = self._formatDateTime()
            
            # Output csv file to store exported data
            self.featureCountCsvFilepath = os.path.join(self.outDir, '{0}_FeatureCounts.csv'.format(self.keyword))
            if self._checkPy27():
                self.featureCountFileWriter = codecs.open(self.featureCountCsvFilepath, self.overWriteOption) # w = read/write or "a" = append
            else:
                self.featureCountFileWriter = open(self.featureCountCsvFilepath, self.overWriteOption, encoding='UTF-8') # w = read/write or "a" = append
            
            self.featureCountFileWriter.write(headers + formattedDateTime)

        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _createFeatureCountFiles: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _createFeatureCountFiles: {0}\n\t".format(ex))
    
    def _createFieldCountFiles(self):
        try:
            # Field header names for output CSV file:
            fieldCountHeaders = self._formatFieldCountHeaders()
            formattedDateTime = self._formatDateTime()

            # Output csv file to store exported data
            self.fieldCountCsvFilepath = os.path.join(self.outDir, '{0}_FieldCounts.csv'.format(self.keyword))
            if self._checkPy27():
                self.fieldCountFileWriter = codecs.open(self.fieldCountCsvFilepath, self.overWriteOption) # w = read/write or "a" = append
            else:            
                self.fieldCountFileWriter = open(self.fieldCountCsvFilepath, self.overWriteOption, encoding='UTF-8') # w = read/write or "a" = append
            self.fieldCountFileWriter.write(fieldCountHeaders + formattedDateTime)            
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _createFieldCountFiles: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _createFieldCountFiles: {0}\n\t".format(ex))

    def _createSubtypeFiles(self):
        try:            
            # Field header names for output CSV file:
            formattedSubtypeHeaders = self._formatSubtypeHeaders()
            formattedDateTime = self._formatDateTime()

            # Output csv file to store exported data
            self.subtypeCsvFilepath = os.path.join(self.outDir, '{0}_Subtypes.csv'.format(self.keyword))
            if self._checkPy27():
                self.subtypeFileWriter = codecs.open(self.subtypeCsvFilepath, self.overWriteOption) # w = read/write or "a" = append
            else:            
                self.subtypeFileWriter = open(self.subtypeCsvFilepath, self.overWriteOption, encoding='UTF-8') # w = read/write or "a" = append
            self.subtypeFileWriter.write(formattedSubtypeHeaders + formattedDateTime)

        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _createSubtypeFiles: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _createSubtypeFiles: {0}\n\t".format(ex))
    
    def _createSubtypeCountFiles(self):
        try:            
            # Field header names for output CSV file:
            formattedSubtypeCountHeaders = self._formatSubtypeCountHeaders()
            formattedDateTime = self._formatDateTime()

            # Output csv file to store exported data
            self.subtypeCountCsvFilepath = os.path.join(self.outDir, '{0}_SubtypeCounts.csv'.format(self.keyword))
            if self._checkPy27():
                self.subtypeCountFileWriter = codecs.open(self.subtypeCountCsvFilepath, self.overWriteOption) # w = read/write or "a" = append
            else:            
                self.subtypeCountFileWriter = open(self.subtypeCountCsvFilepath, self.overWriteOption, encoding='UTF-8') # w = read/write or "a" = append
            self.subtypeCountFileWriter.write(formattedSubtypeCountHeaders + formattedDateTime)

        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _createSubtypeCountFiles: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _createSubtypeCountFiles: {0}\n\t".format(ex))
    
    def _mergeCsvToExcel(self):
        try:            
            with pd.ExcelWriter(self.outExcelFilepath, mode="a", if_sheet_exists="replace", engine="openpyxl") as excelWriter:
                try:
                    if self.featureCountCsvFilepath and os.path.isfile(self.featureCountCsvFilepath):
                        featureCountDf = pd.read_csv(self.featureCountCsvFilepath, sep=",", skip_blank_lines=True, warn_bad_lines=True)   
                        featureCountDf.to_excel(excelWriter, sheet_name="FeatureCounts")
                        
                        arcpy.AddMessage("Finished Excel export of Feature Count File\n\t")
                        self.logger.info("Finished Excel export of Feature Count File\n\t")
                    
                except Exception as ex:
                    arcpy.AddMessage("Exception Thrown in _exportFilesToExcel/featureCountRun: {0}\n\t".format(ex))
                    self.logger.error("Exception Thrown in _exportFilesToExcel/featureCountRun: {0}\n\t".format(ex))                
        
                try:
                    if self.fieldCountCsvFilepath and os.path.isfile(self.fieldCountCsvFilepath):
                        featureCountDf = pd.read_csv(self.fieldCountCsvFilepath, sep=",", skip_blank_lines=True, warn_bad_lines=True)   
                        featureCountDf.to_excel(excelWriter, sheet_name="FieldCounts")
                        
                        arcpy.AddMessage("Finished Excel export of Field Count File\n\t")
                        self.logger.info("Finished Excel export of Field Count File\n\t")
                    
                except Exception as ex:
                    arcpy.AddMessage("Exception Thrown in _exportFilesToExcel/featureCountRun: {0}\n\t".format(ex))
                    self.logger.error("Exception Thrown in _exportFilesToExcel/featureCountRun: {0}\n\t".format(ex))   
                    
                try:
                    if self.subtypeCsvFilepath and os.path.isfile(self.subtypeCsvFilepath):
                        featureCountDf = pd.read_csv(self.subtypeCsvFilepath, sep=",", skip_blank_lines=True, warn_bad_lines=True)  
                        featureCountDf.to_excel(excelWriter, sheet_name="SubtypeCounts")
                        
                        arcpy.AddMessage("Finished Excel export of Subtypes File\n\t")
                        self.logger.info("Finished Excel export of Subtypes File\n\t")
                    
                except Exception as ex:
                    arcpy.AddMessage("Exception Thrown in _exportFilesToExcel/subtypeRun: {0}\n\t".format(ex))
                    self.logger.error("Exception Thrown in _exportFilesToExcel/subtypeRun: {0}\n\t".format(ex))   
                    
                try:
                    if self.subtypeCountCsvFilepath and os.path.isfile(self.subtypeCountCsvFilepath):
                        featureCountDf = pd.read_csv(self.subtypeCountCsvFilepath, sep=",", skip_blank_lines=True, warn_bad_lines=True)
                        featureCountDf.to_excel(excelWriter, sheet_name="SubtypeCounts")
                        arcpy.AddMessage("Finished Excel export of Subtype Count File\n\t")
                        self.logger.info("Finished Excel export of Subtype Count File\n\t")
                    
                except Exception as ex:
                    arcpy.AddMessage("Exception Thrown in _exportFilesToExcel/featureCountRun: {0}\n\t".format(ex))
                    self.logger.error("Exception Thrown in _exportFilesToExcel/featureCountRun: {0}\n\t".format(ex))                                                               

                excelWriter.save()
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in mergeCsvToExcel: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in mergeCsvToExcel: {0}\n\t".format(ex))
                                
    def _exportFilesToExcel(self):
        try:
            if self.featureCountRun == "YES":
                featureCountExcelFilepath = os.path.splitext(self.featureCountCsvFilepath)[0] + '.xlsx'
                featureCountDf = pd.read_csv(self.featureCountCsvFilepath, sep=",", skip_blank_lines=True, warn_bad_lines=True)  #header=None, prefix='Col', 
                featureCountDf.to_excel(featureCountExcelFilepath, sheet_name="FeatureCounts")
                                        
                arcpy.AddMessage("Finished Excel export of Feature Count File\n\t")
                self.logger.info("Finished Excel export of Feature Count File\n\t")
                
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _exportFilesToExcel/featureCountRun: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _exportFilesToExcel/featureCountRun: {0}\n\t".format(ex))                
            
        try:
            # Convert csv to excel file
            if self.fieldCountRun == "YES":
                fieldCountExcelFilepath = os.path.splitext(self.fieldCountCsvFilepath)[0] + '.xlsx'
                with pd.ExcelWriter(fieldCountExcelFilepath, mode="w", engine="openpyxl") as fieldCountExcelWriter:
                    fieldCountExcelDf = pd.read_csv(self.fieldCountCsvFilepath, sep=",", skip_blank_lines=True, warn_bad_lines=True) #header=None, prefix='Col', 
                    fieldCountExcelDf.to_excel(fieldCountExcelWriter, sheet_name="FieldCounts")
                    
                    arcpy.AddMessage("Finished Excel export of Field Count File\n\t")
                    self.logger.info("Finished Excel export of Field Count File\n\t")
                
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _exportFilesToExcel/fieldCountRun: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _exportFilesToExcel/fieldCountRun: {0}\n\t".format(ex))                
        
        try:
            if self.subtypeRun == "YES":                
                subtypeExcelFilepath = os.path.splitext(self.subtypeCsvFilepath)[0] + '.xlsx'
                with pd.ExcelWriter(subtypeExcelFilepath, mode="a", if_sheet_exists="replace", engine="openpyxl") as subtypeExcelWriter:                    
                    subtypeDf = pd.read_csv(self.subtypeCsvFilepath, sep=",", skip_blank_lines=True, warn_bad_lines=True) 
                    subtypeDf.to_excel(subtypeExcelWriter, sheet_name="Subtypes")  

                    arcpy.AddMessage("Finished Excel export of Subtype File\n\t")
                    self.logger.info("Finished Excel export of Subtype File\n\t")
                
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _exportFilesToExcel/subtypeRun: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _exportFilesToExcel/subtypeRun: {0}\n\t".format(ex))
    
        try:        
            if self.subtypeCountRun == "YES":
                subtypeCountExcelFilepath = os.path.splitext(self.subtypeCountCsvFilepath)[0] + '.xlsx'
                with pd.ExcelWriter(subtypeCountExcelFilepath, mode="w", if_sheet_exists="replace", engine="openpyxl") as subtypeCountExcelWriter:

                    # skip_blank_lines = set to False when errors should be thrown
                    subtypeCountDf = pd.read_csv(self.subtypeCountCsvFilepath, sep=",", skip_blank_lines=True, warn_bad_lines=True) # header=None, prefix='Col', 
                    subtypeCountDf.to_excel(subtypeCountExcelWriter, sheet_name="SubtypeCounts")

                    arcpy.AddMessage("Finished Excel export of Subtype Count File\n\t")
                    self.logger.info("Finished Excel export of Subtype Count File\n\t")
                                        
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in _exportFilesToExcel/subtypeCountRun: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in _exportFilesToExcel/subtypeCountRun: {0}\n\t".format(ex))                     

    def runDatabaseSnifferDb(self):
        try:           
            # Create/confirm output & logs folders.             
            self.logsDir = os.path.join(self.outDir, 'logs')
            
            # Confirm if output directory exists. If not, make it.
            if os.path.isdir(self.outDir) is False:
                os.makedirs(self.outDir)
            
            if os.path.isdir(self.logsDir) is False:
                os.makedirs(self.logsDir)  
            
            # Make logger
            self.logger = MessageLogger.configureLogger(self.csvLoggingFilepath, "FeatureCounter")
            
            arcpy.AddMessage("Created/confirmed output & logs folders created")
            self.logger.info("Created/confirmed output & logs folders created")
                        
            self.outExcelFilepath = os.path.join(self.outDir, '{0}_MergedDatabaseSnifferResults.xlsx'.format(self.keyword))

            if self.domainSchemaRun == "YES":
                self._exportDomainSchemaToExcel()
                
            if (self.featureCountRun == "YES" or self.fieldCountRun == "YES" or self.subtypeRun == "YES" or self.subtypeCountRun == "YES"):
                if self.featureCountRun == "YES":
                    self._createFeatureCountFiles()
                    
                if self.fieldCountRun == "YES":
                    self._createFieldCountFiles()
                
                if self.subtypeRun == "YES":
                    self._createSubtypeFiles()
                    
                if self.subtypeCountRun == "YES":
                    self._createSubtypeCountFiles()
                
                self._loopThroughDatasets()   
            
                # Release resources
                if self.featureCountFileWriter: 
                    self.featureCountFileWriter.close()
                    del self.featureCountFileWriter
                if self.fieldCountFileWriter: 
                    self.fieldCountFileWriter.close()
                    del self.fieldCountFileWriter 
                if self.subtypeFileWriter: 
                    self.subtypeFileWriter.close()
                    del self.subtypeFileWriter    

                if self._checkPy27() is False:
                    if self.mergeCsvsToExcel == "YES":
                        self._mergeCsvToExcel()
                    else:
                        self._exportFilesToExcel()

            print('\nScript Completed\n')
            self.logger.info('\n Script Completed\n')
                        
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown in runDatabaseSnifferDb: {0}\n\t".format(ex))
            self.logger.error("Exception Thrown in runDatabaseSnifferDb: {0}\n\t".format(ex))

def getParser():
    """ The argument parser of the command-line version """
    parser = argparse.ArgumentParser(description='Runs database sniffer.')
    parser.add_argument('--config_file', '-C', dest='configFile', required=True, 
            help="Config file path (use quotes around file path, separated by 1 '\\'")

    return parser.parse_args()

def main():
    args = None
    config = ''
    try:
        args = getParser()        
    except Exception as ex:
        print("Skipping running through command arguments" + ex)
        
    finally:
            
        if args:              
            configFilePath = args.configFile
        else:
            configFilePath = r".\DatabaseSniffer_config.json"     # Defaults to same directory
        
        # Load Config
        config = DatabaseHelper.loadConfig(configFilePath)
        
        sourceDbList = config["sourceDbDict"]
        now = datetime.now()
        print(now.strftime("\n\Started %m/%d/%Y %H:%M:%S\n\n"))

        # Load params        
        for dbParams in sourceDbList:
            print("\n Running job for item: " + dbParams["keyword"])  
            instance = DatabaseSnifferDb(config, dbParams)
            instance.runDatabaseSnifferDb()
        
        now = datetime.now()
        print(now.strftime("\n\Ended %m/%d/%Y %H:%M:%S\n\n"))
if __name__ == '__main__':  
    main()  