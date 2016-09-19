# python
import math
import glob
import array
import argparse
import subprocess

# ROOT
import ROOT

SAND_FILES = "/data/t2k/phrmav/gasAnalysisFlats/production006/B/mcp/sand/run3/flat/*.root"
SAND_TREE = "default"

FILES_PER_FLAT = 25
POT_PER_FILE = 2.5E17
POT_DATA = 5.73E20

BINS_MOM = (0., 200., 400., 600., 800., 1000., 1200., 1400., 1600., 1800., 2000.)
BINS_COSTHETA = (0., .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.001)

def main():
  sandFiles = glob.glob(SAND_FILES)
  print "Getting sand events from {0} flat files ({1} regular files)".format(len(sandFiles), len(sandFiles)*FILES_PER_FLAT)

  sandChain = ROOT.TChain(SAND_TREE)
  for sandFile in sandFiles:
    sandChain.Add(sandFile)

  print "Computing selected events from {0} entries".format(sandChain.GetEntries())

  potTotal = POT_PER_FILE * len(sandFiles) * FILES_PER_FLAT
  dataFrac = POT_DATA / potTotal

  allEventsByMom = {}
  keysMom = []
  for i in range(len(BINS_MOM)-1):
    low = BINS_MOM[i]
    up = BINS_MOM[i+1]
    allEventsByMom[(low, up)] = 0
    keysMom.append((low, up))

  allEventsByCosTheta = {}
  keysCosTheta = []
  for i in range(len(BINS_COSTHETA)-1):
    low = BINS_COSTHETA[i]
    up = BINS_COSTHETA[i+1]
    allEventsByCosTheta[(low, up)] = 0
    keysCosTheta.append((low, up))

  nEntries = 0
  nSelected = 0
  for entry in sandChain:
    nEntries += 1
    if entry.accum_level[0] >= 11:
      nSelected += 1

      for key in allEventsByMom.iterkeys():
        if entry.HMM_mom[0] >= key[0] and entry.HMM_mom[0] < key[1]:
          allEventsByMom[key] += 1
      for key in allEventsByCosTheta.iterkeys():
        if entry.HMM_costheta >= key[0] and entry.HMM_costheta < key[1]:
          allEventsByCosTheta[key] += 1

  nSelectedErr = math.sqrt(float(nSelected))

  print "{0} +- {1} sand events selected at {2} PoT".format(nSelected, nSelectedErr, potTotal)
  print "Corresponds to {0} +- {1} in data".format(nSelected*dataFrac, nSelectedErr*dataFrac)

  print "By momentum bin:"
  for key in keysMom:
    val = allEventsByMom[key]
    valErr = math.sqrt(float(val))
    print "  Bin from {0} to {1}".format(key[0], key[1])
    print "    Measured: {0} +- {1}".format(val, valErr)
    print "    Actual: {0} +- {1}".format(val*dataFrac, valErr*dataFrac)
  print "By cos theta bin:"
  for key in keysCosTheta:
    val = allEventsByCosTheta[key]
    valErr = math.sqrt(float(val))
    print "  Bin from {0} to {1}".format(key[0], key[1])
    print "    Measured: {0} +- {1}".format(val, valErr)
    print "    Actual: {0} +- {1}".format(val*dataFrac, valErr*dataFrac)

if __name__ == "__main__":
  main()
