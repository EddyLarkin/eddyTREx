# python
import os
import sys
import glob
import argparse
import subprocess

# ROOT
import ROOT

MAX_ACCUM = 11
FLATS_PATTERN = "/data/t2k/phrmav/gasAnalysisFlats/production006/I/rdp/*/flat/flats_*.root"

def main(args):
  makeCSVFile(args)

def makeCSVFile(args):
  microTrees = glob.glob(FLATS_PATTERN)

  microChain = ROOT.TChain("default")
  for microTree in microTrees:
    microChain.Add(microTree)

  outFile = open(args.csv, "w")

  for entry in microChain:
    if entry.accum_level[0] >= MAX_ACCUM:
      outFile.write("{0},{1},{2}\n".format(entry.run, entry.subrun, entry.evt))

  outFile.close()

def checkArguments():
  parser = argparse.ArgumentParser(description="Download files from the grid, skim them and return them")

  parser.add_argument("--csv", type=str, help="CSV file where to store and access run,subrun,event", default="survivingDataEventIDs.csv")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
