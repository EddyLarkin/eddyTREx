# python
import glob
import argparse
import subprocess

# ROOT
import ROOT

DATA_ROOT = "/data/eddy/t2k/ND280"
FLAT_ROOT = "/data/eddy/t2k/flats"

DATA_RD = "{0}/production006/I/rdp/ND280/*/anal/*.root".format(DATA_ROOT)
DATA_NEUT = "{0}/production006/H/mcp/neut/*/*/*/anal/*.root".format(DATA_ROOT)
DATA_GENIE = "{0}/production006/H/mcp/genie/*/*/*/anal/*.root".format(DATA_ROOT)

def main(args):
  filePattern = ""
  if args.rd:
    filePattern = DATA_RD
  elif args.neut:
    filePattern = DATA_NEUT
  elif args.genie:
    filePattern = DATA_GENIE

  if args.list:
    listData(args, filePattern)
  elif args.process:
    processData(args, filePattern)

def listData(args, dataRoot):
  filesToProcess = glob.glob(dataRoot)

  for i in range(0, len(filesToProcess), args.chunkSize):
    firstFile = filesToProcess[i]
    chunkRoot = getFlatDir(firstFile)

    # count how many files to process
    nFiles = 0
    for j in range(args.chunkSize):
      ind = i+j
      if ind >= len(filesToProcess):
        break

      fileName = filesToProcess[ind]
      fileRoot = getFlatDir(fileName)
      if fileRoot != chunkRoot:
        break

      nFiles += 1

    if nFiles>0:
      listName = "{0}/list/flats_{1}-to-{2}.list".format(chunkRoot, i, nFiles+i)

      print "Chunk of index #{0} listed at {1}".format(i, listName)
      subprocess.call(["rm", "-rf", "{0}/list".format(chunkRoot)])
      subprocess.call(["mkdir", "-p", "{0}/list".format(chunkRoot)])
      listFile = open(listName, "w")

      for j in range(nFiles):
        ind = i+j
        fileName = filesToProcess[ind]
        listFile.write("{0}\n".format(fileName))

      listFile.close()

def processData(args, dataRoot):
  filesToProcess = glob.glob(dataRoot)

  fileRoots = []

  for fileName in filesToProcess:
    fileRoot = getFlatDir(fileName)
    fileRoots.append(fileRoot)

  fileRootSet = set(fileRoots)

  for stem in fileRootSet:
    if (args.pattern == "") or (args.pattern in stem):
      print "Processing files in {0}".format(stem)

      listDir = "{0}/list".format(stem)
      flatDir = "{0}/flat".format(stem)
      scriptDir = "{0}/script".format(stem)
      logDir = "{0}/log".format(stem)

      subprocess.call(["mkdir", "-p", flatDir])
      subprocess.call(["mkdir", "-p", scriptDir])
      subprocess.call(["mkdir", "-p", logDir])

      listFiles = glob.glob("{0}/*.list".format(listDir))
      for listFile in listFiles:
        flatFile = listFile.replace(listDir, flatDir).replace(".list", ".root")
        scriptFile = listFile.replace(listDir, scriptDir).replace(".list", ".sh")
        logFile = listFile.replace(listDir, logDir).replace(".list", ".log")

        scriptWriteable = open(scriptFile, "w")

        scriptWriteable.write("#!/bin/bash\n")
        scriptWriteable.write("\n")
        scriptWriteable.write("RunTRExAnalysis.exe -v -o {0} {1}".format(flatFile, listFile))

        scriptWriteable.close()

        subprocess.call(["chmod", "774", scriptFile])

        print "Submitting {0} to long queue".format(scriptFile)
        jobCommand = ["bsub", "-q", "long", "-oo", logFile, scriptFile]
        print jobCommand

def getFlatDir(fileName):
  return fileName.replace(DATA_ROOT, FLAT_ROOT).split("/anal/")[0]

def checkArguments():
  parser = argparse.ArgumentParser(description="Process TREx analysis data")

  parser.add_argument("--rd", action="store_true", help="Process neut files")
  parser.add_argument("--neut", action="store_true", help="Process neut files")
  parser.add_argument("--genie", action="store_true", help="Process neut files")

  parser.add_argument("--pattern", type=str, help="Pattern to restrict processing to", default="")

  parser.add_argument("--chunkSize", type=int, help="Number of files per chunk", default=100)
  parser.add_argument("--nFiles", type=int, help="Number of chunks to process at one time", default=800)

  parser.add_argument("--list", action="store_true", help="Make lists of files ready to process")
  parser.add_argument("--process", action="store_true", help="process files from lists")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)

