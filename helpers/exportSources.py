#!/usr/bin/env python2
import json, arcpy
import getopt, sys  # command line args
import os

sourceGdb = r"C:\sourcecode\PGLNSG.gdb"
targetGdb = r"C:\sourcecode\PGLNSG_NoCOM.gdb"

def exportAllTables(sourceGdb):
    arcpy.env.workspace = sourceGdb
    dataset_fcs = arcpy.ListFeatureClasses(feature_dataset='Integrys_Gas')
    standalone_fcs = arcpy.ListFeatureClasses()
    all_fcs = dataset_fcs + standalone_fcs
    
    for fc in all_fcs:
        try:
            print("fc: {}".format(fc))
            # Import feature class into target GDB
            # Process: Append the feature classes to the empty feature class
            arcpy.Append_management([fc], os.path.join(targetGdb, fc), 'TEST')
        
        except Exception as ex:
            arcpy.AddMessage("Exception Thrown:\n\t{}".format(ex))


if __name__ == "__main__":
    exportAllTables(sourceGdb)