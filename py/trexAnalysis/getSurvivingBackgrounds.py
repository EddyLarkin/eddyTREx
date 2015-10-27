# python
import argparse
import subprocess
import glob
import re

# ROOT
import ROOT

PROCESSING = ("list", "analyse", "csv", "skim")

def main(args):
  stages = []
  for stage in PROCESSING:
    if stage == args.first:
      stages.append(stage)
    elif len(stages) > 0:
      stages.append(stage)
    if stage == args.last:
      break

  for stage in stages:
    if stage == PROCESSING[0]:
      doList(args)
    elif stage == PROCESSING[1]:
      doAnalyse(args)
    elif stage == PROCESSING[2]:
      doCSV(args)
    elif stage == PROCESSING[3]:
      doSkim(args)

def doList(args):
  print "# getting list of files to run analysis over, {0}".format(args.listFile)

  with open(args.listFile, "w") as listFile:
    print "  # looking in {0}/{1}".format(args.path, args.folderAnal)
    fileNames = glob.glob("{0}/{1}/oa_*.root".format(args.path, args.folderAnal))

    print "  # {0} analysis files found; searching for recon matches".format(len(fileNames))
    # use only files with an associated recon file
    matchedFileNames = []
    for fileName in fileNames:
      match = re.search("(\d{8,8}-\d{4,4}_\w{12,12})", fileName)
      uniqueID = match.group(0)

      inFiles = glob.glob("{0}/{1}/*{2}*.root".format(args.path, args.folderReco, uniqueID))
      if len(inFiles) > 0:
        matchedFileNames.append(fileName)

    print "  # {0} matching files found (saving {1})".format(len(matchedFileNames), min(len(matchedFileNames), args.nFiles))
    matchedFileNames = sorted(matchedFileNames)

    nFile = 0
    for matchedFileName in matchedFileNames:
      nFile += 1
      if nFile > args.nFiles:
        break
      listFile.write("{0}\n".format(matchedFileName))
    print "  # {0} saved".format(args.listFile)

def doAnalyse(args):
  print "# running analysis over {0}, giving {1}".format(args.listFile, args.analysisFile)

  subprocess.call(["rm", "-f", args.analysisFile])
  subprocess.call(["RunTRExAnalysis.exe", "-v", "-n", str(args.nEvents), "-o", args.analysisFile, args.listFile])

  print "  # produced {0}".format(args.analysisFile)

def doCSV(args):
  print "# getting CSV of surviving events in {0}, giving {1}".format(args.analysisFile, args.csvFile)

  drawingTools = ROOT.DrawingTools(args.analysisFile)
  analysisSample = ROOT.DataSample(args.analysisFile)
  drawingTools.PrintEventNumbers(analysisSample, "accum_level>={0}".format(args.accumLevel), args.csvFile)

  print "  # produced {0}".format(args.csvFile)

def doSkim(args):
  print "# skimming surviving backgrounds from reco files using CSV {0}, giving {1}".format(args.csvFile, args.skimFile)

  # keep sorted to make sure we're using the right file
  matchedFileNames = []
  with open(args.listFile, "r") as listFile:
    for line in listFile:
      matchedFileNames.append(line)
  matchedFileNames = sorted(matchedFileNames)

  inFileList = []
  nFile = 0
  for matchedFileName in matchedFileNames:
    nFile += 1
    if nFile > args.nFiles:
      break

    match = re.search("(\d{8,8}-\d{4,4}_\w{12,12})", matchedFileName)
    uniqueID = match.group(0)

    inFiles = glob.glob("{0}/{1}/*{2}*.root".format(args.path, args.folderReco, uniqueID))
    inFileList += inFiles

  subprocess.call(["rm", "-f", args.skimFile])
  subprocess.call(["skimFromCSV.exe", "-O", "file={0}".format(args.csvFile), "-o", args.skimFile] + inFileList)
  print "  # produced skim file {0}".format(args.skimFile)


def checkArguments():
  parser = argparse.ArgumentParser(description="Get surviving backgrounds from analysis")
  parser.add_argument("--first", type=str, help="First step of process to run", choices=PROCESSING, default=PROCESSING[0])
  parser.add_argument("--last", type=str, help="Last step to process to run", choices=PROCESSING, default=PROCESSING[-1])

  parser.add_argument("--path", type=str, help="Path to folders containing analysis and recon files", default="/data/eddy/t2k/nd280/production006/B/mcp/neut/2010-11-air/magnet/run4")
  parser.add_argument("--folderAnal", type=str, help="Name of folder containing analysis files", default="trexanal")
  parser.add_argument("--folderReco", type=str, help="Name of folder containing reco files", default="trexreco")

  parser.add_argument("--listFile", type=str, help="Name of file containing events to pass to RunTRExAnalysis.exe", default="trexFiles.list")
  parser.add_argument("--analysisFile", type=str, help="Name of ntuple from RunTRExAnalysis.exe", default="trexEvents.root")
  parser.add_argument("--csvFile", type=str, help="Name of csv file containing events passing selection", default="survivingBackgrounds.csv")
  parser.add_argument("--skimFile", type=str, help="Name of reco file containing surviving backgrounds", default="survivingBackgrounds.root")

  parser.add_argument("-n", "--nEvents", type=int, help="Number of events to process", default=10000)
  parser.add_argument("--nFiles", type=int, help="Number of files to process", default=1)
  parser.add_argument("--accumLevel", type=int, help="Accum level to count as passing", default=7)

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
