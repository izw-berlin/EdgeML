# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.

import os
import subprocess

import seedot.common as Common
import seedot.util as Util

# Program to build and run the predictor project using msbuild
# The accuracy and other statistics are written to the output file specified


class Predictor:

    def __init__(self, algo, version, datasetType, outputDir):
        self.algo, self.version, self.datasetType = algo, version, datasetType

        self.outputDir = outputDir
        os.makedirs(self.outputDir, exist_ok=True)

    def buildForWindows(self):
        '''
        Builds using the Predictor.vcxproj project file and creates the executable
        The target platform is currently set to x64
        '''
        print("Build...", end='')

        projFile = "Predictor.vcxproj"
        args = [Common.msbuildPath, projFile, r"/t:Build",
                r"/p:Configuration=Release", r"/p:Platform=x64"]

        logFile = os.path.join(self.outputDir, "msbuild.txt")
        with open(logFile, 'w') as file:
            process = subprocess.call(args, stdout=file)

        if process == 1:
            print("FAILED!!\n")
            return False
        else:
            print("success")
            return True   

    def buildForLinux(self):
        print("Build...", end='')

        args = ["make"]

        logFile = os.path.join(self.outputDir, "msbuild.txt")
        with open(logFile, 'w') as file:
            process = subprocess.call(args, stdout=file)

        if process == 1:
            print("FAILED!!\n")
            return False
        else:
            print("success")
            return True

    def buildForMingw(self):
        '''
        Build using makefile with mingw-compiler
        if Common.gccPath is not None, add it to front of path for execution
        '''
        
        my_env = os.environ.copy()
        if (Common.gccPath is not None) and (Common.gccPath):
            my_env['PATH'] = gccPath+';'+os.environ['PATH']
            
        args = ["mimg32-make.exe"]
            
        logFile = os.path.join(self.outputDir, "gccbuild.txt")
        with open(logFile, 'w') as file:
            process = subprocess.call(args, stdout=file, env=my_env)

        if process == 1:
            print("FAILED!!\n")
            return False
        else:
            print("success")
            return True   
            
    def build(self):
        if Util.windows():
            if Common.mingw:
                return self.buildForMingw()
            else:
                return self.buildForWindows()
        else:
            return self.buildForLinux()

    def executeForWindows(self):
        '''
        Invokes the executable with arguments
        '''
        print("Execution...", end='')

        exeFile = os.path.join("x64", "Release", "Predictor.exe")
        args = [exeFile, self.algo, self.version, self.datasetType]

        logFile = os.path.join(self.outputDir, "exec.txt")
        with open(logFile, 'w') as file:
            process = subprocess.call(args, stdout=file)

        if process == 1:
            print("FAILED!!\n")
            return None
        else:
            print("success")
            acc = self.readStatsFile()
            return acc

    def executeForLinux(self):
        print("Execution...", end='')

        exeFile = os.path.join("./Predictor")
        args = [exeFile, self.algo, self.version, self.datasetType]

        logFile = os.path.join(self.outputDir, "exec.txt")
        with open(logFile, 'w') as file:
            process = subprocess.call(args, stdout=file)

        if process == 1:
            print("FAILED!!\n")
            return None
        else:
            print("success")
            acc = self.readStatsFile()
            return acc

    def executeForMingw(self):
        print("Execution...", end='')

        exeFile = os.path.join("./Predictor.exe")
        args = [exeFile, self.algo, self.version, self.datasetType]

        logFile = os.path.join(self.outputDir, "exec.txt")
        with open(logFile, 'w') as file:
            process = subprocess.call(args, stdout=file)

        if process == 1:
            print("FAILED!!\n")
            return None
        else:
            print("success")
            acc = self.readStatsFile()
            return acc

    def execute(self):
        if Util.windows():
            if Common.mingw:
                return self.executeForMingw()
            else:
                return self.executeForWindows()
        else:
            return self.executeForLinux()

    # Read statistics of execution (currently only accuracy)
    def readStatsFile(self):
        statsFile = os.path.join(
            "output", self.algo + "-" + self.version, "stats-" + self.datasetType + ".txt")

        with open(statsFile, 'r') as file:
            content = file.readlines()

        stats = [x.strip() for x in content]

        return float(stats[0])

    def run(self):
        res = self.build()
        if res == False:
            return None

        acc = self.execute()

        return acc
