# python
import os
import glob
import argparse
import subprocess

# ROOT
import ROOT

MAX_ACCUM = 12

LOCAL_DIR_TMP = "/data/t2k/phrmav/tmp"
LOCAL_DIR_SKIM = "/data/t2k/phrmav/skim"

def main(args):
  if(args.makeCSV):
    makeCSVFile(args)
  if(args.checkCSV):
    checkCSVFile(args)
  if(args.probeData):
    probeData(args)

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

def probeData(args):
  fileIDs = readCSVFile(args)
  setupGRID(args)

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

def setupGRID(args):
  subprocess.call(["/data/t2k/phrmav/script/setup-emi3-ui-example.sh"], shell=True)
  os.environ["LFC_HOST"] = "lfc.gridpp.rl.ac.uk"
  subprocess.call(["voms-proxy-init", "-voms", "t2k.org", "-valid", "72:00"])

def getIsSkimmed(args, run, subRun):
  return False

def getIsDownloaded(args, run, subRun):
  return False


def checkArguments():
  parser = argparse.ArgumentParser(description="Download files from the grid, skim them and return them")

  parser.add_argument("--inTrees", type=str, nargs="+", help="Pattern of trees to base the skim on",
                      default=["/data/eddy/t2k/microtrees/PreNeutBeamMC_nuar_tree.root"])
  parser.add_argument("--csv", type=str, help="CSV file where to store and access run,subrun,event", default="eventIDs.csv")

  parser.add_argument("--makeCSV", action="store_true", help="Make CSV file where to store and access run,subrun,event")
  parser.add_argument("--checkCSV", action="store_true", help="Check the status of events from the specified CSV file")
  parser.add_argument("--probeData", action="store_true", help="Make sure we can find the data we're trying to download")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
