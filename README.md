# Introduction 
This Schema Advisor tool is a simple and configurable tool for producing formatted, detailed schema documentation and database summary reports. This tool runs in either python 2.7 or 3 to output excel spreadsheets or csv files to help describe the schema.

The schema documentation can be used for a number of purposes, including:
- Review of source data schema pre-data migration (i.e. identify fields with all <null> values for removal)
- Export target schema details for quality checks, development, and/or a customer deliverable
- Identify schema gaps quickly, and outside of cumbersome ESRI tools (i.e. Design -> Subtypes)
- Quick data quality checks, including feature counts and invalid domain values

The database summary report mimics the new ArcGIS Pro Subtype view to show summaries by subtype, domain, or other combinations of fields.


# Getting Started
1.	Installation process:
    - Beyond arcpy and licensing with ArcGIS programs (ArcMap or ArcGIS Pro), there are not additional installs. 
2.	Software dependencies:
- Python 2.7 or 3 alongside ArcMap (for 2.7) or ArcGIS Pro (for 3). NOTE: UTF-8 formatting is limiting the use of Python 2.7. Use Python 3 instead.

# Build and Test
1. Execute the python file SchemaAdvisor.py either through a terminal or IDE with python 3.

# Contribute
1. Make a PR and we'll review!

# Configuration Parameters
{
"globals-DEFINITION": {
    "outDir-DEFINITION": "Output directory where all exported files will be created. Subdirectories are automatically created.", 
    "outDir": "C:\\repos\\SchemaAdvisor\\outputSchemaAdvisor_BHC_TestAllCount",
    "overWriteOption-DEFINITION": "Enter YES if the output csv file will be overwritten, otherwise use NO and you'll get an error message on overwrite.",
    "overWriteOption": "YES",
    "csvLoggingFilepath-DEFINITION": "This is the output logging file to record all messages, including errors and completed output.",
    "csvLoggingFilepath": "C:\\repos\\SchemaAdvisor\\outputSchemaAdvisor_BHC_TestAllCount\\logs\\SchemaAdvisor_log.csv",
    "mergeCsvsToExcel_DEFINITION": "Enter YES if merging all csv outputs to one. Otherwise enter NO to export separate xlsx spreadsheets",
    "mergeCsvsToExcel": "NO",
    "skipSystemFieldTypes-DEFINITION": "Enter Esri field types to skip. Options are 'OID', 'GlobalID', 'Guid', 'Date', 'Blob', 'Geometry'. Additional non-system field types are also 'SmallInteger', 'String', 'Integer', 'Double', 'Float'.",
    "domainSchemaConfig-DEFINITION": {
        "run-DEFINITION": "Enter YES to run this output.",
        "run": "NO"
    },
    "featureCountConfig-DEFINITION": {
        "run-DEFINITION": "Enter YES to run this output.",
        "run": "NO",
        "featureCountHeaders-DEFINITION": "Enter headers to the output file.",
        "featureCountHeaders": {
            "featureDataset": "Feature Dataset",
            "featureClass": "Feature Class",
            "featureType": "Feature Type",
            "shapeType": "Shape Type",                  
            "featureCount": "Feature Count"
        }
    },
    "fieldCountConfig-DEFINITION": {
        "run-DEFINITION": "Enter YES to run this output. Output shows all unique descriptions of the fields and optional unique value counts per field. Feature counts are also included in each row for the field.",
        "run": "YES",
        "skipSystemFields-DEFINITION": "All fields in this will are considered system-generated fields and skipped for the unique count calculations. IMPORTANT! - This is only used if the includeFieldCountFields is an emtpy array [].",
        "skipSystemFields":[
            "OBJECTID",
            "SHAPE",
            "OID",
            "GLOBALID",
            "DATE",
            "CREATED_DATE",
            "LAST_EDIT_DATE",
            "CREATED_USER",
            "LAST_EDIT_USER"
        ],
        "fieldCountHeaders-DEFINITION": "Enter headers to the output file.",
        "fieldCountHeaders": {
            "featureDataset": "Feature Dataset",
            "featureClass": "Feature Class",
            "featureType": "Feature Type",
            "shapeType": "Shape Type", 
            "featureCount": "Feature Count",               
            "fieldName": "Field Name",
            "fieldAlias": "Field Alias",
            "fieldType": "Field Type",
            "fieldLength": "Field Lenth",
            "fieldPrecision": "Field Precision",
            "fieldCounts": "Field Value Counts",
            "nullPercent": "Null Percent", 
            "fieldDomain": "Field Domain",
            "domainType": "Domain Type",
            "domainValues": "Domain Values"
        },
        "excludeFieldCountFields-DEFINITION": "All fields in this list will be excluded from counting unique values. Each field in this list is also checked to see if the field is contained within the field to include it. So if you enter 'ID', the program will look for any occurances of ID in the field and include that for the unique counts. IMPORTANT! - This is only used if the includeFieldCountFields is an emtpy array [].",
        "excludeFieldCountFields": [
            "ENABLED",
            "ROUTE",
            "GPS",
            "CREATOR",
            "CREATE",
            "EDITOR",
            "EDIT",
            "DATE",
            "LAT",
            "LONG",
            "ID",
            "USER",
            "NODE"
        ],
        "includeFieldCountFields-DEFINITION": "If this list is populated, then only these fields are used to calculate unique value counts. Each field in this list is also checked to see if the field is contained within the field to include it. So if you enter 'ID', the program will look for any occurances of ID in the field and include that for the unique counts. IMPORTANT! - This is only used if the includeFieldCountFields is an emtpy array [].",
        "includeFieldCountFields": [
            "SYSTEM",
            "SUBTYPE",
            "SUBTEYPCD",
            "TYPE",
            "CLASS",
            "REMARKS",
            "COMMENTS",
            "NOTES",
            "INDICATOR",
        ],
        "fieldCountLimit-DEFINITION": "This number is used to limit the recorded unique values. If there are 5,000 unique values for example, then only the first 20 unqiue values are printed into the file.",
        "fieldCountLimit": 20
    },
    "subtypeConfig-DEFINITION": {
        "run-DEFINITION": "Enter YES to run this output.",
        "run": "NO",
        "subtypeHeaders-DEFINITION": "Enter headers to the output file.",
        "subtypeHeaders":{
            "featureDataset": "Feature Dataset",
            "featureClass": "Feature Class",
            "featureType": "Feature Type",
            "shapeType": "Shape Type",
            "featureCount": "Feature Count",               
            "subtypeCode": "Subtype Code",
            "subtypeName": "Subtype Field (if assigned)",
            "fieldName": "Field Name",
            "defaultValues": "Default Value",
            "domain": "Domain Name"
        }
    },
    "subtypeCountConfig-DEFINITION": {
        "run-DEFINITION": "Enter YES to run this output.",
        "run": "NO",
        "subtypeCountHeaders-DEFINITION": "Enter headers to the output file.",
        "subtypeCountHeaders":{
            "featureDataset": "Feature Dataset",
            "featureClass": "Feature Class",
            "featureType": "Feature Type",
            "shapeType": "Shape Type",
            "featureCount": "Feature Count",
            "fieldName": "Field Name",
            "subtypeCount": "Frequency Count"
        }, 
        "subtypeCountCategoryLimit-DEFINITION": "This number is used to limit how many subtype count categories are recorded in the output file. For example, if the subtype field is cross-referenced with the material field and there are 50 unique combinations of SUBTYPE x MATERIAL, then the data will not be recorded in the output file because it's more unique combincations that the limit of 40. IMPORTANT! - This is only used if the includeFieldCountFields is an emtpy array [].",
        "subtypeCountCategoryLimit":40,
        "excludeSubtypeCountFields-DEFINITION": "Enter fields to be excluded from counts of subtypes.",
        "excludeSubtypeCountFields": [
            "ENABLED",
            "OBJECTID",
            "GLOBALID",
            "GUID",
            "DATE",
            "SHAPE",
            "SUBTYPECD"
        ],
        "includeSubtypeCountFields-DEFINITION": "Enter fields to be included in counts of subtypes. This overrides any fields entered in the exclude fields.",
        "includeSubtypeCountFields":[
            "SYSTEM",
            "SUBTYPE",
            "SUBTEYPCD",
            "TYPE",
            "CLASS",
            "INDICATOR"
        ],
        "subtypeShowMarginCount-DEFINITION": "Enter YES if you want to see the total of cross-tabulated counts.",
        "subtypeShowMarginCount": "YES"
    }
},
"sourceDbDict-DEFINITION": [
    {
        "sourceDir-DEFINITION": "Source file gdb or SDE database.",
        "sourceDir": "C:\\sourcecode\\MyFileDatabase.gdb",
        "dataSetsToCheck-DEFINITION": "Enter ['ALL'] if you want to check all feature datasets. Enter ['STANDALONE'] to check all tables. Otherwise enter specific names of feature classes. If an SDE connection, then enter the database and schema owner like ['MyDatabase.MySchema.TransmissionDataset']",
        "dataSetsToCheck": ["TransmissionDataset", "OtherDataset"],
        "keyword-DEFINITION": "Used to name the output file.",
        "keyword": "_DPL_electric_transmission_datasets_",
        "fcList-DEFINITION": "Enter feature class names that you want to get a description for. If you want to get all feature classes in the configuired feature datasets, enter []",
        "fcList": ["P_NoncontrollableFitting", "P_Pipes"],
        "skipFcList-DEFINITION": "List of feature datasets to skip looping through. Always include the name of the geometric network or utility network object to skip through.",
        "skipFcList": ["TransmissionNetwork", "ElectricDataset_GeometricNet"],
        "excludeSubtypeCountFields": "GLOBAL",
        "excludeFieldCountFields-DEFINITION": "Add database-specific exclude fields. These will only be used for this database and not applied for all other databases if others are configured. Enter GLOBAL if all included fields should are listed in the global config",            
        "excludeFieldCountFields": "GLOBAL",
        "includeFieldCountFields-DEFINITION": "Enter 'GLOBAL' if all included fields are listed in the global config",
        "includeFieldCountFields": [
            "CASINGDIAMETER",
            "DESIGNPRESSURE",
            "INSIDEDIAMETER",
            "MAOP",
            "MATERIAL",
            "NOMINALDIAMETER",
            "OPERATINGSTATUS",
            "OUTSIDEDIAMETER",
            "TESTPRESSURE",
            "PRESSURE",
            "TYPE",
            "DIAMETER",
            "SUBTYPE",
            "FITTING",
            "SIZE"
        ],
        "includeSubtypeCountFields-DEFINITION": "Enter 'GLOBAL' if all included fields are listed in the global config for subtype count fields. Otherwise, enter all fields to be included for unique subtype counts here. Only those configured fields will show in the output file if configured.",
        "includeSubtypeCountFields": "GLOBAL"
    },    
    {
        "sourceDir": "C:\\_myEnterpriseSDE.sde",
        "dataSetsToCheck-DEFINITION": "", 
        "dataSetsToCheck": ["STANDALONE"],
        "keyword": "_distribution__standalone_",
        "fcList": ["MySchema.PipeJoinMethod"],
        "skipFcList": [],
        "includeFieldCountFields": [
            "MAOP",
            "MATERIAL"
        ],
        "excludeFieldCountFields": "GLOBAL"
    },
    {
        "sourceDir": "C:\\_myOtherEnterpriseSDE.sde",
        "dataSetsToCheck": ["ALL"],
        "keyword": "__datasets_",
        "fcList": [],
        "skipFcList": ["MySchema.GasNetwork"],
        "includeFieldCountFields": "GLOBAL" 
    },
    {
        "sourceDir": "C:\\_myOtherEnterpriseSDE.gdb",
        "dataSetsToCheck": ["STANDALONE"],
        "keyword": "__standalone_",
        "fcList": [],
        "skipFcList": ["StructureOutline", "SkipThisPolygonFeatureClass_Name"], 
        "includeFieldCountFields": "GLOBAL"      
    },
    {
        "sourceDir": "C:\\example\\connections\\_transmissionFileGDB.gdb",
        "dataSetsToCheck": ["ALL"],
        "keyword": "_transmission__datasets_",
        "fcList": [],
        "skipFcList": ["GasTransmissionNetwork"],
        "includeFieldCountFields": "GLOBAL" 
    }
]
}