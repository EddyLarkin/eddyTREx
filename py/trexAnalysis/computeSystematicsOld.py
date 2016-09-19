# python
import glob
import math
import array
import argparse
import subprocess

# ROOT
import ROOT

NEUT = "neut"
GENIE = "genie"

RUN2WATER = "run2water"
RUN2AIR = "run2air"
RUN3B = "run3b"
RUN3C = "run3c"
RUN4WATER = "run4water"
RUN4AIR = "run4air"

DIRS = (  RUN2WATER,
          RUN2AIR,
          RUN3B,
          RUN3C,
          RUN4WATER,
          RUN4AIR     )
DIRS = ( RUN2WATER, )

TREE_SYS = ( "all_syst" )

BINS_MOM = (0., 200., 400., 600., 800., 1000., 1200., 1400., 1600., 1800., 2000.)

def main(args):
  ROOT.gROOT.SetBatch(1)
  ROOT.gStyle.SetOptStat(0)

  if args.singleBin:
    getSingleBinSyst(args)
  if args.momBin:
    getMomBinSyst(args)

def getSingleBinSyst(args):
  fileSets = getFileSets(args)

  for key, fileSet in fileSets.iteritems():
    print "--- Single bin systematics for {0} ---".format(key)
    bigTree = ROOT.TChain(TREE_SYS)
    for runName, runFiles in fileSet.iteritems():
      for file in runFiles:
        bigTree.Add(file)
        break

    print "  {0} events total".format(bigTree.GetEntries())

    allWeights = []
    allDiff2s = []
    allEvents = 0

    for entry in bigTree:
      # ignore entries that haven't passed the selection
      if entry.accum_level[0] < 11:
        continue
      weightBuff = entry.weight_syst_total
      allEvents += 1

      buffSum = 0.
      buffEntries = 0
      for weight in weightBuff:
        buffSum += weight
        buffEntries += 1
      buffMean = buffSum/buffEntries
      buffDiff2Sum = 0.
      for weight in weightBuff:
        diff2 = (weight - buffMean)**2
        buffDiff2Sum += diff2
      buffVariance = buffDiff2Sum / buffEntries

      # some systematics can be artificially inflated by errors in computing them - ignore these
      if buffVariance < .4**2:
        for weight in weightBuff:
          diff2 = (weight - buffMean)**2
          allWeights.append(weight)
          allDiff2s.append(diff2)

    allWeightSum = 0.
    allWeightEntries = 0
    for weight in allWeights:
      allWeightSum += weight
      allWeightEntries += 1
    mean = allWeightSum / float(allWeightEntries)
    allDiff2Sum = 0.
    allDiff2Entries = 0
    for diff2 in allDiff2s:
      allDiff2Sum += diff2
      allDiff2Entries += 1
    variance = allDiff2Sum / float(allDiff2Entries)
    sigma = math.sqrt(variance)

    print "  Total fractional systematic is {0}".format(sigma)
    print "  Final average weight is {0} +- {1}".format(mean, mean*sigma)
    print "  Final events are {0} +- {1}".format(mean*float(allEvents), mean*sigma*float(allEvents))

def getMomBinSyst(args):
  fileSets = getFileSets(args)

  keys = []
  allWeights = {}
  allDiff2s = {}
  allEvents = {}
  for i in range(len(BINS_MOM)-1):
    low = BINS_MOM[i]
    up = BINS_MOM[i+1]
    keys.append((low, up))
    allWeights[(low, up)] = []
    allDiff2s[(low, up)] = []
    allEvents[(low, up)] = 0

  for key, fileSet in fileSets.iteritems():
    print "--- Momentum bin systematics for {0} ---".format(key)
    bigTree = ROOT.TChain(TREE_SYS)
    for runName, runFiles in fileSet.iteritems():
      for file in runFiles:
        bigTree.Add(file)

    print "  {0} events total".format(bigTree.GetEntries())

    for entry in bigTree:
      # ignore entries that haven't passed the selection
      if entry.accum_level[0] < 11:
        continue

      bin = None
      for key in keys:
        if entry.HMM_mom[0] >= key[0] and entry.HMM_mom[0] < key[1]:
          bin = key
          break

      if bin:
        weightBuff = entry.weight_syst_total
        allEvents[bin] += 1

        buffSum = 0.
        buffEntries = 0
        for weight in weightBuff:
          buffSum += weight
          buffEntries += 1
        buffMean = buffSum/buffEntries
        buffDiff2Sum = 0.
        for weight in weightBuff:
          diff2 = (weight - buffMean)**2
          buffDiff2Sum += diff2
        buffVariance = buffDiff2Sum / buffEntries

        # some systematics can be artificially inflated by errors in computing them - ignore these
        if buffVariance < .4**2:
          for weight in weightBuff:
            diff2 = (weight - buffMean)**2
            allWeights[key].append(weight)
            allDiff2s[key].append(diff2)

    for key in keys:
      print "  Bin from {0} to {1}".format(key[0], key[1])
      mean = 0.
      variance = 0.
      sigma = 0.

      allWeightSum = 0.
      allWeightEntries = 0
      for weight in allWeights[key]:
        allWeightSum += weight
        allWeightEntries += 1
      if(allWeightEntries):
        mean = allWeightSum / float(allWeightEntries)
      allDiff2Sum = 0.
      allDiff2Entries = 0
      for diff2 in allDiff2s[key]:
        allDiff2Sum += diff2
        allDiff2Entries += 1
      if(allDiff2Entries):
        variance = allDiff2Sum / float(allDiff2Entries)
        sigma = math.sqrt(variance)

      print "    Total fractional systematic is {0}".format(sigma)
      print "    Final average weight is {0} +- {1}".format(mean, mean*sigma)
      print "    Final events are {0} +- {1}".format(mean*float(allEvents[key]), mean*sigma*float(allEvents[key]))

def getFileSets(args):
  toProcess = getToProcess(args)
  fileSets = {}

  for key, rootDir in toProcess.iteritems():
    fileSets[key] = {}
    for runDir in DIRS:
      fileSets[key][runDir] = []

      fileNames = glob.glob("{0}/{1}/flat/flats_*.root".format(rootDir, runDir))
      for fileName in fileNames:
        fileSets[key][runDir].append(fileName)

  return fileSets

def getToProcess(args):
  toProcess = {}
  if args.neut:
    toProcess[NEUT] = args.neutRoot
  if args.genie:
    toProcess[GENIE] = args.genieRoot

  return toProcess

def getRoot(type):
  root = ""
  if type == NEUT:
    root = args.genieRoot
  elif type == GENIE:
    root = args.neutRoot

  return root

def checkArguments():
  parser = argparse.ArgumentParser(description="Produce plots for gas and beam")
  parser.add_argument("--singleBin", action="store_true", help="Compute systematics for single bin analysis")
  parser.add_argument("--momBin", action="store_true", help="Compute systematics for momentum bin analysis")

  parser.add_argument("--neut", action="store_true", help="Use neut files")
  parser.add_argument("--genie", action="store_true", help="Use genie files")

  parser.add_argument("--neutRoot", type=str, help="Folder for neut files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/H/mcp/neut")
  parser.add_argument("--genieRoot", type=str, help="Folder for genie files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/H/mcp/genie")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
