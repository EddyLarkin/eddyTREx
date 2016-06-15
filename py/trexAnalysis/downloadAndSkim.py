# python
import os
import sys
import glob
import argparse
import subprocess

# ROOT
import ROOT

MAX_ACCUM = 12

LOCAL_DIR_TMP = "/storage/epp2/phrmav/tmp"
LOCAL_DIR_SKIM = "/storage/epp2/phrmav/tmp/skim"

GRID_LFC_STEM = "/grid/t2k.org"
GRID_LCG_STEM = "lfn:/grid/t2k.org"

NEUT_ROOT = "nd280/production006/H/mcp/neut"
RDP_ROOT = "nd280/production006/I/rdp/ND280"

NEUT_DIRS = (
              "{0}/2010-11-air/magnet/run2/reco".format(NEUT_ROOT),
              "{0}/2010-11-air/magnet/run3/reco".format(NEUT_ROOT),
              "{0}/2010-11-air/magnet/run4/reco".format(NEUT_ROOT),
              "{0}/2010-11-water/magnet/run2/reco".format(NEUT_ROOT),
              "{0}/2010-11-water/magnet/run4/reco".format(NEUT_ROOT)
                                                                               )
RDP_DIRS = (
              "{0}/00006000_00006999/reco".format(RDP_ROOT),
              "{0}/00007000_00007999/reco".format(RDP_ROOT),
              "{0}/00008000_00008999/reco".format(RDP_ROOT),
              "{0}/00009000_00009999/reco".format(RDP_ROOT),
              "{0}/00010000_00010999/reco".format(RDP_ROOT),
              "{0}/00011000_00011999/reco".format(RDP_ROOT)
                                                                         )

GRID_PRIORITY = (
                  "qmul.ac.uk",
                  "shef.ac.uk",
                  "nd280.org"
                                 )


def main(args):

  if(args.makeCSV):
    makeCSVFile(args)

  if(args.checkCSV):
    checkCSVFile(args)

  if(args.listData):
    listData(args)

  if(args.acquireData):
    acquireData(args)

def makeCSVFile(args):
  microTrees = []
  for microTreePattern in args.inTrees:
    microTrees += glob.glob(microTreePattern)
  microChain = ROOT.TChain("default")
  for microTree in microTrees:
    microChain.Add(microTree)

  outFile = open(args.csv, "w")

  for entry in microChain:
    if entry.accum_level[0] >= MAX_ACCUM:
      outFile.write("{0},{1},{2}\n".format(entry.run, entry.subrun, entry.evt))

  outFile.close()

def checkCSVFile(args):
  fileIDs = readCSVFile(args)

  for (run, subRun), events in fileIDs.iteritems():
    outMSG = "Files for \033[1m{0},{1}\033[0m :".format(run, subRun)
    outMSG += " "*(36-len(outMSG))
    outMSG += str(len(events))
    outMSG += " "*(48-len(outMSG))
    outMSG += "File status:  "
    if getIsSkimmed(args, run, subRun):
      outMSG += "\033[92mSKIMMED\033[0m"
    elif getIsDownloaded(args, run, subRun):
      outMSG += "\033[94mDOWNLOADED\033[0m"
    else:
      outMSG += "\033[93mUNPROCESSED\033[0m"

    print outMSG

def listData(args):
  fileIDs = readCSVFile(args)

  allDirsList = []
  if args.neut:
    for mcpDir in NEUT_DIRS:
      allDirsList.append("{0}/{1}".format(GRID_LFC_STEM, mcpDir))
  if args.rd:
    for rdpDir in RDP_DIRS:
      allDirsList.append("{0}/{1}".format(GRID_LFC_STEM, rdpDir))

  allFileList = []
  for curDir in allDirsList:
    procResult = subprocess.Popen(["lfc-ls", curDir], stdout=subprocess.PIPE)
    out, err = procResult.communicate()
    for line in out.split("\n"):
      allFileList.append("{0}/{1}".format(curDir, line))

  dlList = []
  for curFile in allFileList:
    found = False

    for run, subRun in fileIDs.iterkeys():
      runStr = str(run)
      subRunStr = str(subRun)
      if len(runStr)<8:
        runStr = "0"*(8-len(runStr)) + runStr
      if len(subRunStr)<4:
        subRunStr = "0"*(4-len(subRunStr)) + subRunStr

      if "_{0}-{1}_".format(runStr, subRunStr) in curFile:
        found = True

    if found:
      dlList.append(curFile)

  outFile = open(args.gridList, "w")

  for fileFull in dlList:
    fileLoc = fileFull.replace("{0}/".format(GRID_LFC_STEM), "")
    outFile.write("{0}\n".format(fileLoc))

  outFile.close()

def acquireData(args):
  filePaths = readPathFile(args)

  # create directories and construct paths for destination files
  destPaths = []
  for path in filePaths:
    fullPath = "{0}/{1}".format(LOCAL_DIR_TMP, path[:-1])
    pathFolder = os.path.dirname(fullPath)

    destPaths.append(fullPath)
    subprocess.call(["mkdir", "-p", pathFolder])

  # make list of file locations and destinations
  transferList = []
  for path, dest in zip(filePaths, destPaths):
    procResult = subprocess.Popen(["lcg-lr", "{0}/{1}".format(GRID_LCG_STEM, path[:-1])], stdout=subprocess.PIPE)
    out, err = procResult.communicate()

    # use whichever location comes first on our priority list
    for line in out.split("\n"):
      for loc in GRID_PRIORITY:
        if loc in line:
          transferList.append((line, dest))
          break

  # now the trixy bit - download each file, skim it and delete it
  for loc, dest in transferList:
    skimFile = "{0}/{1}".format(LOCAL_DIR_SKIM, os.path.basename(dest))
    # don't try re-skim
    if not os.path.isfile(skimFile):
      # don't try to re-download
      if not os.path.isfile(dest):
        subprocess.call(["lcg-cp", "-v", "--vo", "t2k.org", loc, dest], stdout=subprocess.PIPE)

      if os.path.isfile(dest):
        subprocess.call(["rm", "-f", skimFile])
        subprocess.call(["skimFromCSV.exe", "-O", "file={0}".format(args.csv), "-o", skimFile, dest])
        subprocess.call(["rm", "-f", dest])

def readCSVFile(args):
  outDict = {}

  inFile = open(args.csv, "r")

  for line in inFile:
    run, subRun, event = line[:-1].split(",")
    idTuple = ( int(run), int(subRun) )
    eventID = int(event)
    if( idTuple in outDict.keys()):
      outDict[idTuple].append(eventID)
    else:
      outDict[idTuple] = [eventID]

  return outDict

def readPathFile(args):
  outPaths = []

  inFile = open(args.gridList, "r")

  for line in inFile:
    outPaths.append(line)

  return outPaths

def setupGRID(args):
  subprocess.call(["/storage/epp2/phrmav/scripts/grid-env.sh"], shell=True)
  os.environ["LFC_HOST"] = "lfc.gridpp.rl.ac.uk"
  subprocess.call(["voms-proxy-init", "-voms", "t2k.org", "-valid", "24:00"])

def getIsSkimmed(args, run, subRun):
  return False

def getIsDownloaded(args, run, subRun):
  return False


def checkArguments():
  parser = argparse.ArgumentParser(description="Download files from the grid, skim them and return them")

  parser.add_argument("--inTrees", type=str, nargs="+", help="Pattern of trees to base the skim on",
                      default=["/data/eddy/t2k/microtrees/PreNeutBeamMC_nuar_tree.root"])
  parser.add_argument("--csv", type=str, help="CSV file where to store and access run,subrun,event", default="eventIDs.csv")
  parser.add_argument("--gridList", type=str, help="List of files to download from the grid", default="eventFileList.list")

  parser.add_argument("--makeCSV", action="store_true", help="Make CSV file where to store and access run,subrun,event")
  parser.add_argument("--checkCSV", action="store_true", help="Check the status of events from the specified CSV file")
  parser.add_argument("--listData", action="store_true", help="Record the locations of all files to download")
  parser.add_argument("--acquireData", action="store_true", help="Download and skim files")

  parser.add_argument("--neut", action="store_true", help="Get NEUT MC")
  parser.add_argument("--rd", action="store_true", help="Get real data")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
