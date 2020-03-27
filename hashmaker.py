#!/usr/bin/env python
#hashmaker.py


#######################################################################################################################
###REQUIRED LIBRARIES####

#######################################################################################################################

import hashlib
import os
import time
import re
import sys
import argparse
import config
from datetime import datetime

def makeFileList(sourceList,hashalg,mode):
    '''
returns a list of file(s) to hashmaker. list is a set of tuples with (filepath,hash). for now the hash is empty
    '''
    flist = []
    for s in sourceList:
        if os.path.isdir(s) is False: #if first argument is a file it's p easy
            sourceBasename = os.path.basename(s)
            if (mode == "verify"):
                if (sourceBasename.endswith(hashalg)): #ignore any sidecar files. We needn't be makeing sidecars of sidecars
                    flist.append(s)
                else:
                    print("WARNING: Input file " + sourceBasename + " ignored because it's not a hash file")
            elif (mode == "make"):
                if not sourceBasename.endswith(hashalg): #ignore any sidecar files. We needn't be makeing sidecars of sidecars
                    flist.append(s)
                else:
                    print("WARNING: Input file " + sourceBasename + " ignored because it is a hash file")
            else:
                print("CRITICAL ERROR: Something is wrong with the mode selection")
        #if the start object is a directory things get tricky
        elif os.path.isdir(s) is True:
            if not s.endswith("/"):
                s = s + "/" #later, when we do some string subs, this keeps os.path.join() from breaking on a leading / I HATE HAVING TO DO THIS
            for dirs, subdirs, files in os.walk(s): #walk recursively through the dirtree
                for x in files: #ok, for all files rooted at start object
                    sourceFile = os.path.join(dirs, x) #grab the start file full path
                    sourceBasename = os.path.basename(x)
                    if (mode == "verify"):
                        if not sourceBasename.startswith(".") and sourceBasename.endswith(hashalg): #ignore any sidecar files. We needn't be makeing sidecars of sidecars
                            flist.append(sourceFile)
                    elif (mode == "make"):
                        if not sourceBasename.startswith(".") and not sourceBasename.endswith(hashalg): #ignore any sidecar files. We needn't be makeing sidecars of sidecars
                            flist.append(sourceFile)
                    else:
                        print("CRITICAL ERROR: Something is wrong with the mode selection")
        else:
            print("Critical Error. Could not determine if the input is a file or directory. Something is very wrong.")
            sys.exit()
    return flist

def processList(flist,hashalg,hashlength,mode,resultsList):
    for f in flist:
        if mode == "make":
            fHashFile = f + "." + hashalg
            if os.path.exists(fHashFile):
                if not compare_modtime(f, fHashFile):
                    print("WARNING: Checksum for file: " + os.path.basename(f) + " is out of date. Creating new checksum")
                    resultsList = writeHash(f,hashalg,resultsList)
            else:
                print("Writing Checksum for file: " + os.path.basename(f))
                resultsList = writeHash(f,hashalg,resultsList)
        elif mode == "verify":
            resultsList = verifyHash(f, hashalg, hashlength, resultsList)
        else:
            print("CRITICAL ERROR: Something is wrong with the mode selection")
    return resultsList



#compares two files. If olderFile was created before newerFile then return true. else return false
def compare_modtime(olderFile, newerFile):
    olderFileMod = os.path.getmtime(olderFile)
    newerFileMod = os.path.getmtime(newerFile)
    if newerFileMod > olderFileMod:
        return True
    else:
        return False

#reads a hash from a sidecar checksum file
def readHash(hashFile, hashlength):
    with open(hashFile,'r') as f: #open it
        storedHash = re.search('\w{'+hashlength+'}',f.read()).group() #get the hash
    return storedHash

#generate checksums for both source and dest
def generateHash(inputFile, hashalg, blocksize=65536):
    '''
    using a buffer, hash the file
    '''
    with open(inputFile, 'rb') as f:
        hasher = hashlib.new(hashalg) #grab the hashing algorithm decalred by user
        buf = f.read(blocksize) # read the file into a buffer cause it's more efficient for big files
        while len(buf) > 0: # little loop to keep reading
            hasher.update(buf) # here's where the hash is actually generated
            buf = f.read(blocksize) # keep reading
    return hasher.hexdigest()

#write hash to a file
def writeHash(inputFile, hashalg, resultsList):
    #logNewLine("Writing New Sidecar Hash For " + os.path.basename(inputFile) + "........",logDir)
    #try:
    hash = generateHash(inputFile, hashalg)
    hashFile = inputFile + "." + hashalg
    txt = open(hashFile, "w") #old school
    txt.write(hash + " *" + os.path.basename(inputFile))
    txt.close()
    #logSameLine("Complete!",logDir)
    resultsList[0] += 1
    return resultsList
    #except:
        #logSameLine("ERROR!",logDir)
    #    resultsList[3] += 1
    #    return resultsList

#verify's a hash from the sidecar file
def verifyHash(sidecarFile, hashalg, hashlength, resultsList):
    #logNewLine("Verifying Hash For " + os.path.basename(sidecarFile) + "........",logDir)
    #try:
    writtenHash = readHash(sidecarFile, hashlength) #read the hash written in the sidecar
    generatedHash = generateHash(sidecarFile.replace("." + hashalg, ""), hashalg) #generate the hash of the associated file
    if writtenHash == generatedHash: #then verify the checksums
        pass
        #logSameLine("Complete! Checksum Verified",logDir)
        print("Checksum for file " + os.path.basename(sidecarFile) + " Verified!")
        resultsList[1] += 1
        return resultsList
    else:
        pass
        #logSameLine("ERROR: Checksum Verification Failed!",logDir)
        print("ERROR: Checksum for file " + os.path.basename(sidecarFile) + " Failed!")
        resultsList[3] += 1
        return resultsList
    #except:
        #logSameLine("ERROR!",logDir)


def processResults(dictList):
    count = 0
    success = 0
    fail = 0
    failList = []

    for dict in dictList:
        if dict["Result"]:
            success += 1
        else:
            failList.append(dict["Filename"])
            fail += 1
        count += 1
    print("\n")
    print("Number of Checksums Processed: " + str(count))
    print("Number of Successes: " + str(success))
    print("Number of Failures: " + str(fail))
    if fail > 0:
        print("\n")
        print("List of Failed Files:")
        for f in failList:
            print(f)
    print("\n")

def initLog(sourceList,destination,hashalg):
    '''
    initializes log file
    '''
    txtFile = open(destination + "/LoadingScript.log", "a+")
    txtFile.write("Load and Verify Script Started at: " + time.strftime("%Y-%m-%d_%H:%M:%S") + "\n")
    for f in sourceList:
        txtFile.write("From: " + f + "\n")
    txtFile.write("To: " + destination + "\n")
    txtFile.write("Hash algorithm: " + hashalg + "\n")
    txtFile.write("\n\n")
    txtFile.close()

def logNewLine(text,destination):
    txtFile = open(destination + "/LoadingScript.log", "a+")
    txtFile.write("\n" + time.strftime("%Y-%m-%d_%H:%M:%S") + ": " + text)

def logSameLine(text,destination):
    txtFile = open(destination + "/LoadingScript.log", "a+")
    txtFile.write(text)

def make_args():
    '''
    initialize arguments from the cli
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-a','--algorithm',action='store',dest='a',default='md5',choices=['md5','sha1','sha256','sha512'],help="the hashing algorithm to use")
    parser.add_argument('-m','--make',action='store_true',dest='m',default=False,help="Make mode. The script creates checksum files in this mode")
    parser.add_argument('-v','--verify',action='store_true',dest='v',default=False,help="Verify mode. The script verifies checksum files in this mode")
    parser.add_argument('sourceObj',nargs='+',help="As many files are directories you would like processed. Only sidecar checksum files are processed.")
    return parser.parse_args()

def main():
    '''
    do the thing
    '''
    #init args from cli
    args = make_args()

    #Initialize log
    #initLog(sourceList,destinationDir,args.a)

    #init variables
    dictList = []
    successWriteHashCount = 0
    successVerifyHashCount = 0
    warningCount = 0
    errorCount = 0
    mode = False
    resultsList = [successWriteHashCount,successVerifyHashCount,warningCount,errorCount]
    hashAlgorithm = hashlib.new(args.a) #creates a hashlib object that is the algorithm we're using
    hashlengths = {'md5':'32','sha1':'40','sha256':'64','sha512':'128'}
    hashlength = hashlengths[args.a] #set value for comparison later

    #Check that input conforms
    if len(args.sourceObj) < 1: #if less than two input arguments we have to exit
        print("CRITICAL ERROR: You must give this script at least one argument")
        sys.exit()

    if args.v and args.m: #if make and create mode are both selected
        print("CRITICAL ERROR: You cannot run this script in Make mode and Verify mode simultaneously")
        sys.exit()
    elif args.v and not args.m: #if verify mode selected
        mode = "verify"
        print("Running script in Verify Mode\n")
    elif not args.v and args.m: #if make mode selected
        mode = "make"
        print("Running script in Make Mode\n")
    else:                        #if neither mode selected, error out
        print("CRITICAL ERROR: You must chose to run this script in Make mode or Verify")
        sys.exit()

    #create list of dictionarie (which represent hash files) to be processed
    flist = makeFileList(args.sourceObj,args.a,mode)

    #process the list
    resultsList = processList(flist,args.a,hashlength,mode,resultsList)

    if mode == "make":
        if resultsList[0] != 0:
            print("\n")
        print("Script Completed! Here are the results.")
        print("Checksums Written: " + str(resultsList[0]))
        print("Warnings: " + str(resultsList[2]))
        print("Errors: " + str(resultsList[3]))
        print("\n")
    elif mode == "verify":
        if resultsList[1] != 0:
            print("\n")
        print("Script Completed! Here are the results.")
        print("Checksums Verified: " + str(resultsList[1]))
        print("Warnings: " + str(resultsList[2]))
        print("Errors: " + str(resultsList[3]))
        print("\n")

    #tally up the success and failures, print the failed files.
    #processResults(dictList)

main()
