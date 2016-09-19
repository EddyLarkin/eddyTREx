# python
import re
import os
import glob
import argparse
import subprocess

# ROOT
import ROOT

RD = "rd"
NEUT = "neut"
GENIE = "genie"
SAND = "sand"

DATA_ROOT = "/data/t2k/data"
EDDY_ROOT = "/data/t2k/phrmav/data"
FLAT_ROOT = "/data/t2k/phrmav/gasAnalysisFlats"

DATA_RD = "{0}/production006/I/rdp/ND280/*/anal/*.root".format(DATA_ROOT)
DATA_NEUT = "{0}/production006/H/mcp/neut/*/*/*/anal/*.root".format(DATA_ROOT)
DATA_GENIE = "{0}/production006/H/mcp/genie/*/*/*/anal/*.root".format(DATA_ROOT)
DATA_SAND = "{0}/production006/B/mcp/neut/2010-11-air/sand/*/trexanal/*.root".format(EDDY_ROOT)

DATA_FLUX = "{0}/fluxes/tuned13av1.1".format(DATA_ROOT)

FLAT_RD = "{0}/production006/I/rdp".format(FLAT_ROOT)
FLAT_NEUT = "{0}/production006/H/mcp/neut".format(FLAT_ROOT)
FLAT_GENIE = "{0}/production006/H/mcp/genie".format(FLAT_ROOT)
FLAT_SAND = "{0}/production006/B/mcp/sand".format(FLAT_ROOT)

# see $PSYCHEUTILSROOT/src/AnalysisUtils.cxx for run ranges for run ranges
RD_TYPES = (
                ("run2water", 6462, 7663),
                ("run2air", 7664, 7754),
                ("run3b", 8309, 8453),
                ("run3c", 8550, 8753),
                ("run4water", 8995, 9422),
                ("run4air", 9423, 9798)
                                            )
NEUT_TYPES = (
              ("run2water", 90210000, 90219999, "{0}/run2".format(DATA_FLUX)),
              ("run2air", 90200000, 90209999, "{0}/run2".format(DATA_FLUX)),
              ("run3b", 90300000, 90300015,  "{0}/run3b".format(DATA_FLUX)),
              ("run3c", 90300016, 90300110, "{0}/run3c".format(DATA_FLUX)),
              ("run4water", 90410000, 90419999, 3250, "{0}/run4water".format(DATA_FLUX)),
              ("run4air", 90400000, 90409999, "{0}/run4air".format(DATA_FLUX))
                                                                                        )
GENIE_TYPES = (
              ("run2water", 91210000, 91219999, "{0}/run2".format(DATA_FLUX)),
              ("run2air", 91200000, 91209999, "{0}/run2".format(DATA_FLUX)),
              ("run3b", 91300000, 91300015,  "{0}/run3b".format(DATA_FLUX)),
              ("run3c", 91300016, 91300110, "{0}/run3c".format(DATA_FLUX)),
              ("run4water", 91410000, 91419999, 3250, "{0}/run4water".format(DATA_FLUX)),
              ("run4air", 91400000, 91409999, "{0}/run4air".format(DATA_FLUX))
                                                                                        )

SAND_TYPES = (
              ("run3", 0, 99999999, "{0}/run3c".format(DATA_FLUX)),
                                                                                        )

def main(args):
  filePattern = ""
  dataType = ""
  if args.rd:
    dataType = RD
  elif args.neut:
    dataType = NEUT
  elif args.genie:
    dataType = GENIE
  elif args.sand:
    dataType = SAND

  if args.list:
    listData(args, dataType)
  elif args.process:
    processData(args, dataType)

def listData(args, dataType):
  # get directories to use
  filePattern = ""
  flatRoot = ""
  types = ()
  if dataType == RD:
    filePattern = DATA_RD
    flatRoot = FLAT_RD
    types = RD_TYPES
  elif dataType == NEUT:
    filePattern = DATA_NEUT
    flatRoot = FLAT_NEUT
    types = NEUT_TYPES
  elif dataType == GENIE:
    filePattern = DATA_GENIE
    flatRoot = FLAT_GENIE
    types = GENIE_TYPES
  elif dataType == SAND:
    filePattern = DATA_SAND
    flatRoot = FLAT_SAND
    types = SAND_TYPES
  else:
    return

  # get files
  filesToProcess = glob.glob(filePattern)

  # list by run
  fileLists = {}
  for info in types:
    fileLists[info[0]] = [[], ""]

  for fileToProcess in filesToProcess:
    runInfo = ()
    runs = re.search("(\d{8})-(\d{4})", fileToProcess)
    run = int(runs.group(1))
    subRun = int(runs.group(2))

    for info in types:
      if (run >= info[1]) and (run <= info[2]):
        runInfo = info
        break

    if len(runInfo):
      fileLists[runInfo[0]][0].append(fileToProcess)
      if (len(runInfo) > 3):
        fileLists[runInfo[0]][1] = runInfo[3]

  # build lists
  for run, (fileList, flux) in fileLists.iteritems():
    if len(fileList):
      flatTreeRoot = "{0}/{1}".format(flatRoot, run)
      listRoot = "{0}/lists".format(flatTreeRoot)

      print "Rebuilding {0}".format(listRoot)
      subprocess.call(["rm", "-rf", listRoot])
      subprocess.call(["mkdir", "-p", listRoot])

      # build dirs
      subprocess.call(["mkdir", "-p", flatTreeRoot])

      # build parameter override files for fluxes
      # note: I don't think this is necessary in the current highland version
      if flux:
        paramOverride = "{0}/paramsOverride.dat".format(flatTreeRoot)
        paramOverrideFile = open(paramOverride, "w")
        paramOverrideFile.write("< trexAnalysis.FluxWeighting.File = {0} >".format(flux))
        paramOverrideFile.close()

    for i in range(0, len(fileList), args.chunkSize):
      # count how many files to process
      nFiles = 0
      for j in range(args.chunkSize):
        ind = i+j
        if ind >= len(fileList):
          break
        nFiles += 1

      if nFiles>0:
        listName = "{0}/flats_{1}-to-{2}.list".format(listRoot, i, i+nFiles)

        print "Chunk of index #{0} listed at {1}".format(i, listName)
        listFile = open(listName, "w")
        for j in range(nFiles):
          ind = i+j
          fileName = fileList[ind]
          listFile.write("{0}\n".format(fileName))
        listFile.close()

def processData(args, dataType):
  # get directories to use
  flatRoot = ""
  types = ()
  if dataType == RD:
    flatRoot = FLAT_RD
    types = RD_TYPES
  elif dataType == NEUT:
    flatRoot = FLAT_NEUT
    types = NEUT_TYPES
  elif dataType == GENIE:
    flatRoot = FLAT_GENIE
    types = GENIE_TYPES
  elif dataType == SAND:
    flatRoot = FLAT_SAND
    types = SAND_TYPES
  else:
    return

  for info in types:
    flatTreeRoot = "{0}/{1}".format(flatRoot, info[0])
    if (args.pattern == "") or (args.pattern in flatTreeRoot):
      listRoot = "{0}/lists".format(flatTreeRoot)
      flatsRoot = "{0}/flat".format(flatTreeRoot)
      scriptRoot = "{0}/script".format(flatTreeRoot)
      logRoot = "{0}/log".format(flatTreeRoot)

      subprocess.call(["mkdir", "-p", flatsRoot])
      subprocess.call(["mkdir", "-p", scriptRoot])
      subprocess.call(["mkdir", "-p", logRoot])

      listFiles = glob.glob("{0}/*.list".format(listRoot))
      print "\033[33;1mProcessing {0} lists in {1}\033[0m".format(len(listFiles), flatTreeRoot)
      for listFile in listFiles:
        flatFile = listFile.replace(listRoot, flatsRoot).replace(".list", ".root")
        scriptFile = listFile.replace(listRoot, scriptRoot).replace(".list", ".sh")
        logFile = listFile.replace(listRoot, logRoot).replace(".list", ".log")

        print flatFile
        if os.path.exists(flatFile) and not args.redo:
          print "\033[35;1mAlready processed\033[0m {0}".format(flatFile)
        else:
          scriptWriteable = open(scriptFile, "w")

          scriptWriteable.write("#!/bin/bash\n")
          scriptWriteable.write("\n")
          scriptWriteable.write("rm -f {0}\n".format(flatFile))
          scriptWriteable.write("RunTRExAnalysis.exe -v -o {0} {1}".format(flatFile, listFile))

          scriptWriteable.close()

          subprocess.call(["chmod", "774", scriptFile])

          print "Submitting {0} to long queue".format(scriptFile)
          jobCommand = ["bsub", "-q", "long", "-oo", logFile, "-G", "finalyeargrp", scriptFile]
          subprocess.call(jobCommand)

def checkArguments():
  parser = argparse.ArgumentParser(description="Process TREx analysis data")

  parser.add_argument("--rd", action="store_true", help="Process real data files")
  parser.add_argument("--neut", action="store_true", help="Process NEUT files")
  parser.add_argument("--genie", action="store_true", help="Process GENIE files")
  parser.add_argument("--sand", action="store_true", help="Process sand files")

  parser.add_argument("--pattern", type=str, help="Pattern to restrict processing to", default="")

  parser.add_argument("--chunkSize", type=int, help="Number of files per chunk", default=40)
  parser.add_argument("--nFiles", type=int, help="Number of chunks to process at one time", default=800)

  parser.add_argument("--list", action="store_true", help="Make lists of files ready to process")
  parser.add_argument("--process", action="store_true", help="Process files from lists")

  parser.add_argument("--redo", action="store_true", help="Redo files which have been processed")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)

