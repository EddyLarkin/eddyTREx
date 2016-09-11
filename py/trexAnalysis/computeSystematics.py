# python
import glob
import math
import array
import argparse
import subprocess

# ROOT
import ROOT

RD = "rd"
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
BINS_COSTHETA = (0., .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.001)
BINS_MULT = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

def main(args):
  ROOT.gROOT.SetBatch(1)
  ROOT.gStyle.SetOptStat(0)

  if args.singleBin:
    getSingleBinSyst(args)
  if args.momBin:
    getMomBinSyst(args)
  if args.costhetaBin:
    getCosThetaBinSyst(args)
  if args.hotPathBin:
    getHotPathBinSyst(args)
  if args.hotProtonBin:
    getHotProtonBinSyst(args)
  if args.maxProtonMomBin:
    getMaxProtonMomBinSyst(args)

def getSingleBinSyst(args):
  fileSets = getFileSets(args)

  for key, fileSet in fileSets.iteritems():
    print "--- Single bin systematics for {0} ---".format(key)
    print "  Using cut-off of {0}".format(args.cutOff)
    bigTree = ROOT.TChain(TREE_SYS)
    for runName, runFiles in fileSet.iteritems():
      for file in runFiles:
        bigTree.Add(file)

    print "  {0} events total".format(bigTree.GetEntries())

    allToyBinContents = []
    unweightedBinContents = 0.
    for i in range(1000):
      allToyBinContents.append(0.)

    for entry in bigTree:
      # ignore entries that haven't passed the selection
      if entry.accum_level[0] < 11:
        continue
      weightBuff = entry.weight_syst_total

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
      if buffVariance < args.cutOff**2:
        unweightedBinContents += 1
        i = 0
        for weight in weightBuff:
          allToyBinContents[i] += weight
          i += 1

    # get bin content variance across toys
    binContentSum = 0.
    for i in range(1000):
      binContentSum += allToyBinContents[i]
    mean = binContentSum / 1000.

    binContentDiff2Sum = 0.
    for i in range(1000):
      diff2 = (allToyBinContents[i] - mean)**2
      binContentDiff2Sum += diff2
    variance = binContentDiff2Sum / 1000.
    sigma = math.sqrt(variance)

    print "  Total fractional systematic is {0}".format(sigma/mean)
    print "  Final average bin content is {0} +- {1}".format(mean, sigma)
    print "    as fraction of total is {0} +- {1}".format(mean/float(unweightedBinContents), sigma/float(unweightedBinContents))

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
    print "  Using cut-off of {0}".format(args.cutOff)
    bigTree = ROOT.TChain(TREE_SYS)
    for runName, runFiles in fileSet.iteritems():
      for file in runFiles:
        bigTree.Add(file)

    print "  {0} events total".format(bigTree.GetEntries())

    allToyBinContents = {}
    unweightedBinContents = {}
    for key in keys:
      allToyBinContents[key] = []
      unweightedBinContents[key] = 0
      for i in range(1000):
        allToyBinContents[key].append(0.)

    for entry in bigTree:
      # ignore entries that haven't passed the selection
      if entry.accum_level[0] < 11:
        continue
      weightBuff = entry.weight_syst_total

      bin = None
      for key in keys:
        if entry.HMM_mom[0] >= key[0] and entry.HMM_mom[0] < key[1]:
          bin = key
          break

      if bin:
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
        if buffVariance < args.cutOff**2:
          unweightedBinContents[bin] += 1
          i = 0
          for weight in weightBuff:
            allToyBinContents[bin][i] += weight
            i += 1

    for key in keys:
      print "  Bin from {0} to {1}".format(key[0], key[1])
      # get bin content variance across toys
      binContentSum = 0.
      for i in range(1000):
        binContentSum += allToyBinContents[key][i]
      mean = binContentSum / 1000.

      binContentDiff2Sum = 0.
      for i in range(1000):
        diff2 = (allToyBinContents[key][i] - mean)**2
        binContentDiff2Sum += diff2
      variance = binContentDiff2Sum / 1000.
      sigma = math.sqrt(variance)

      if mean:
        print "  Total fractional systematic is {0}".format(sigma/mean)
      print "  Final average bin content is {0} +- {1}".format(mean, sigma)
      if unweightedBinContents[key]:
        print "    as fraction of total is {0} +- {1}".format(mean/float(unweightedBinContents[key]), sigma/float(unweightedBinContents[key]))

def getCosThetaBinSyst(args):
  fileSets = getFileSets(args)

  keys = []
  allWeights = {}
  allDiff2s = {}
  allEvents = {}
  for i in range(len(BINS_COSTHETA)-1):
    low = BINS_COSTHETA[i]
    up = BINS_COSTHETA[i+1]
    keys.append((low, up))
    allWeights[(low, up)] = []
    allDiff2s[(low, up)] = []
    allEvents[(low, up)] = 0

  for key, fileSet in fileSets.iteritems():
    print "--- Cos theta bin systematics for {0} ---".format(key)
    print "  Using cut-off of {0}".format(args.cutOff)
    bigTree = ROOT.TChain(TREE_SYS)
    for runName, runFiles in fileSet.iteritems():
      for file in runFiles:
        bigTree.Add(file)

    print "  {0} events total".format(bigTree.GetEntries())

    allToyBinContents = {}
    unweightedBinContents = {}
    for key in keys:
      allToyBinContents[key] = []
      unweightedBinContents[key] = 0
      for i in range(1000):
        allToyBinContents[key].append(0.)

    for entry in bigTree:
      # ignore entries that haven't passed the selection
      if entry.accum_level[0] < 11:
        continue
      weightBuff = entry.weight_syst_total

      bin = None
      for key in keys:
        if entry.HMM_costheta >= key[0] and entry.HMM_costheta < key[1]:
          bin = key
          break

      if bin:
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
        if buffVariance < args.cutOff**2:
          unweightedBinContents[bin] += 1
          i = 0
          for weight in weightBuff:
            allToyBinContents[bin][i] += weight
            i += 1

    for key in keys:
      print "  Bin from {0} to {1}".format(key[0], key[1])
      # get bin content variance across toys
      binContentSum = 0.
      for i in range(1000):
        binContentSum += allToyBinContents[key][i]
      mean = binContentSum / 1000.

      binContentDiff2Sum = 0.
      for i in range(1000):
        diff2 = (allToyBinContents[key][i] - mean)**2
        binContentDiff2Sum += diff2
      variance = binContentDiff2Sum / 1000.
      sigma = math.sqrt(variance)

      if mean:
        print "  Total fractional systematic is {0}".format(sigma/mean)
      print "  Final average bin content is {0} +- {1}".format(mean, sigma)
      if unweightedBinContents[key]:
        print "    as fraction of total is {0} +- {1}".format(mean/float(unweightedBinContents[key]), sigma/float(unweightedBinContents[key]))

def getHotPathBinSyst(args):
  fileSets = getFileSets(args)

  keys = []
  allWeights = {}
  allDiff2s = {}
  allEvents = {}
  for i in BINS_MULT:
    allWeights[i] = []
    allDiff2s[i] = []
    allEvents[i] = 0
    keys.append(i)

  for key, fileSet in fileSets.iteritems():
    print "--- Hot path bin systematics for {0} ---".format(key)
    print "  Using cut-off of {0}".format(args.cutOff)
    bigTree = ROOT.TChain(TREE_SYS)
    for runName, runFiles in fileSet.iteritems():
      for file in runFiles:
        bigTree.Add(file)

    print "  {0} events total".format(bigTree.GetEntries())

    allToyBinContents = {}
    unweightedBinContents = {}
    for key in keys:
      allToyBinContents[key] = []
      unweightedBinContents[key] = 0
      for i in range(1000):
        allToyBinContents[key].append(0.)

    for entry in bigTree:
      # ignore entries that haven't passed the selection
      if entry.accum_level[0] < 11:
        continue
      weightBuff = entry.weight_syst_total

      bin = None
      for key in keys:
        if entry.Vertex_N_hot_paths == key:
          bin = key
          break

      if bin:
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
        if buffVariance < args.cutOff**2:
          unweightedBinContents[bin] += 1
          i = 0
          for weight in weightBuff:
            allToyBinContents[bin][i] += weight
            i += 1

    for key in keys:
      print "  Bin at {0}".format(key)
      # get bin content variance across toys
      binContentSum = 0.
      for i in range(1000):
        binContentSum += allToyBinContents[key][i]
      mean = binContentSum / 1000.

      binContentDiff2Sum = 0.
      for i in range(1000):
        diff2 = (allToyBinContents[key][i] - mean)**2
        binContentDiff2Sum += diff2
      variance = binContentDiff2Sum / 1000.
      sigma = math.sqrt(variance)

      if mean:
        print "  Total fractional systematic is {0}".format(sigma/mean)
      print "  Final average bin content is {0} +- {1}".format(mean, sigma)
      if unweightedBinContents[key]:
        print "    as fraction of total is {0} +- {1}".format(mean/float(unweightedBinContents[key]), sigma/float(unweightedBinContents[key]))

def getHotProtonBinSyst(args):
  fileSets = getFileSets(args)

  keys = []
  allWeights = {}
  allDiff2s = {}
  allEvents = {}
  for i in BINS_MULT:
    allWeights[i] = []
    allDiff2s[i] = []
    allEvents[i] = 0
    keys.append(i)

  for key, fileSet in fileSets.iteritems():
    print "--- Hot proton bin systematics for {0} ---".format(key)
    print "  Using cut-off of {0}".format(args.cutOff)
    bigTree = ROOT.TChain(TREE_SYS)
    for runName, runFiles in fileSet.iteritems():
      for file in runFiles:
        bigTree.Add(file)

    print "  {0} events total".format(bigTree.GetEntries())

    allToyBinContents = {}
    unweightedBinContents = {}
    for key in keys:
      allToyBinContents[key] = []
      unweightedBinContents[key] = 0
      for i in range(1000):
        allToyBinContents[key].append(0.)

    for entry in bigTree:
      # ignore entries that haven't passed the selection
      if entry.accum_level[0] < 11:
        continue
      weightBuff = entry.weight_syst_total

      bin = None
      for key in keys:
        if entry.Vertex_N_protons == key:
          bin = key
          break

      if bin:
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
        if buffVariance < args.cutOff**2:
          unweightedBinContents[bin] += 1
          i = 0
          for weight in weightBuff:
            allToyBinContents[bin][i] += weight
            i += 1

    for key in keys:
      print "  Bin at {0}".format(key)
      # get bin content variance across toys
      binContentSum = 0.
      for i in range(1000):
        binContentSum += allToyBinContents[key][i]
      mean = binContentSum / 1000.

      binContentDiff2Sum = 0.
      for i in range(1000):
        diff2 = (allToyBinContents[key][i] - mean)**2
        binContentDiff2Sum += diff2
      variance = binContentDiff2Sum / 1000.
      sigma = math.sqrt(variance)

      if mean:
        print "  Total fractional systematic is {0}".format(sigma/mean)
      print "  Final average bin content is {0} +- {1}".format(mean, sigma)
      if unweightedBinContents[key]:
        print "    as fraction of total is {0} +- {1}".format(mean/float(unweightedBinContents[key]), sigma/float(unweightedBinContents[key]))

def getMaxProtonMomBinSyst(args):
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
    print "--- Highest proton momentum bin systematics for {0} ---".format(key)
    print "  Using cut-off of {0}".format(args.cutOff)
    bigTree = ROOT.TChain(TREE_SYS)
    for runName, runFiles in fileSet.iteritems():
      for file in runFiles:
        bigTree.Add(file)

    print "  {0} events total".format(bigTree.GetEntries())

    allToyBinContents = {}
    unweightedBinContents = {}
    for key in keys:
      allToyBinContents[key] = []
      unweightedBinContents[key] = 0
      for i in range(1000):
        allToyBinContents[key].append(0.)

    for entry in bigTree:
      # ignore entries that haven't passed the selection
      if entry.accum_level[0] < 11:
        continue
      weightBuff = entry.weight_syst_total

      bin = None
      for key in keys:
        if entry.Vertex_max_proton_mom >= key[0] and entry.Vertex_max_proton_mom < key[1]:
          bin = key
          break

      if bin:
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
        if buffVariance < args.cutOff**2:
          unweightedBinContents[bin] += 1
          i = 0
          for weight in weightBuff:
            allToyBinContents[bin][i] += weight
            i += 1

    for key in keys:
      print "  Bin from {0} to {1}".format(key[0], key[1])
      # get bin content variance across toys
      binContentSum = 0.
      for i in range(1000):
        binContentSum += allToyBinContents[key][i]
      mean = binContentSum / 1000.

      binContentDiff2Sum = 0.
      for i in range(1000):
        diff2 = (allToyBinContents[key][i] - mean)**2
        binContentDiff2Sum += diff2
      variance = binContentDiff2Sum / 1000.
      sigma = math.sqrt(variance)

      if mean:
        print "  Total fractional systematic is {0}".format(sigma/mean)
      print "  Final average bin content is {0} +- {1}".format(mean, sigma)
      if unweightedBinContents[key]:
        print "    as fraction of total is {0} +- {1}".format(mean/float(unweightedBinContents[key]), sigma/float(unweightedBinContents[key]))

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
  if args.rd:
    toProcess[RD] = args.rdRoot
  if args.neut:
    toProcess[NEUT] = args.neutRoot
  if args.genie:
    toProcess[GENIE] = args.genieRoot

  return toProcess

def getRoot(type):
  root = ""
  if type == RD:
    root = args.rdRoot
  elif type == NEUT:
    root = args.genieRoot
  elif type == GENIE:
    root = args.neutRoot

  return root

def checkArguments():
  parser = argparse.ArgumentParser(description="Produce plots for gas and beam")
  parser.add_argument("--singleBin", action="store_true", help="Compute systematics for single bin analysis")
  parser.add_argument("--momBin", action="store_true", help="Compute systematics for momentum bin analysis")
  parser.add_argument("--costhetaBin", action="store_true", help="Compute systematics for cos theta bin analysis")
  parser.add_argument("--hotPathBin", action="store_true", help="Compute systematics for high momentum path bin analysis")
  parser.add_argument("--hotProtonBin", action="store_true", help="Compute systematics for high momentum proton bin analysis")
  parser.add_argument("--maxProtonMomBin", action="store_true", help="Compute systematics for max proton momentum proton bin analysis")

  parser.add_argument("--rd", action="store_true", help="Use real data files")
  parser.add_argument("--neut", action="store_true", help="Use neut files")
  parser.add_argument("--genie", action="store_true", help="Use genie files")

  parser.add_argument("--cutOff", type=float, help="Cut off for event sigma to avoid distortion from badly propagated events", default=2.)

  parser.add_argument("--rdRoot", type=str, help="Folder for real data files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/I/rdp")
  parser.add_argument("--neutRoot", type=str, help="Folder for neut files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/H/mcp/neut")
  parser.add_argument("--genieRoot", type=str, help="Folder for genie files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/H/mcp/genie")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
