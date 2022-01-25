import os
import json
import arcpy

class DatabaseHelper:
    def __init__(self):
        return

    @staticmethod
    def loadConfig(config_file):
        with open(config_file, "r") as json_config:
            config_string = json_config.read()#.replace(r'\n', '')        
            data = json.loads(config_string)
            return data

    @staticmethod
    def folder_exists(folder):
        return os.path.isdir(folder)

    @staticmethod
    def disconnectUsers(sde_sa_connection):    
        print("\nTesting Environment: {}".format(sde_sa_connection))
        if sde_sa_connection.find('.sde') > -1:
            arcpy.env.workspace = sde_sa_connection 
            try:
                arcpy.DisconnectUser(arcpy.env.workspace, "ALL")
                for fd in arcpy.ListDatasets("*"):
                    print("Dataset found: {}".format(fd))
            except Exception as ex:
                print(ex)
            print("Environment Verified\n")
        else:
            print("Using file GDB environment verified\n")