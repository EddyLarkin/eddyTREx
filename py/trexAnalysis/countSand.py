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
POT_PER_FILE = 2.5E17
POT_DATA = 5.73E20

TREES_DEF = ( "default", "truth", "config", "header" )
TREES_SYS = ( "all_syst", )

def main(args):
  sandFiles = glob.glob(SAND_FILES)

  sandChain = ROOT.TChain(SAND_TREE)
  for sandFile in sandFiles:
    sandChain.Add(sandFile)

  potTotal = POT_PER_FILE * len(sandFiles)
  dataFrac = POT_DATA / potTotal

  nEntries = 0
  nSelected = 0
  for entry in sandChain:
    nEntries += 1
    if entry.accum_level[0] >= 11:
      nSelected += 1

  nSelectedErr = math.sqrt(float(nSelected))

  print "{0} +- {1} sand events selected at {2} PoT".format(nSelected, nSelectedErr, potTotal)
  print "Corresponds to {0} +- {1} in data".format(nSelected*dataFrac, nSelectedErr*dataFrac)

if __name__ == "__main__":
  main()
