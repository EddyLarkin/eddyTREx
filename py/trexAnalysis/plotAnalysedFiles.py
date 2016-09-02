# python
import glob
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
#DIRS = ( RUN2WATER, )

TREES_DEF = ( "default", "truth", "config", "header" )
TREES_SYS = ( "all_sys", )

def main(args):
  ROOT.gROOT.SetBatch(1)
  ROOT.gStyle.SetOptStat(0)

  if args.flattenTrees:
    flattenTrees(args)
  if args.makePlots:
    makePlot(args)

def flattenTrees(args):
  fileSets = getFileSets(args)
  fileAlls = getFileAlls(args)

  for key, fileSet in fileSets.iteritems():
    for runName, runFiles in fileSet.iteritems():
      fileAll = fileAlls[key][runName]

      trees = TREES_DEF
      if key == NEUT or key == GENIE:
        trees = TREES_DEF + TREES_SYS

      for tree in trees:
        chain = ROOT.TChain(tree)
        for runFile in runFiles:
          chain.Add(runFile)
        newFile = ROOT.TFile.Open(fileAll, "UPDATE")
        chain.Merge(newFile, 0)

      print "Made new trees at {0}".format(fileAll)

def makePlot(args, var="", bins=()):
  draw = ROOT.DrawingTools(getAFile(args))
  experiment = getExperiment(args)

  subprocess.call(["mkdir", "-p", args.plotFolder])

  myCanv = ROOT.TCanvas("myCanv", "My Canvas", 1200, 800)
  myCanv.cd()

  draw.Draw(experiment, "HMM_mom", 10,0,2000, "all", "accum_level>12")

  myCanv.SaveAs("{0}/accum_mom.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/accum_mom.pdf".format(args.plotFolder))

def getAFile(args):
  fileSets = getFileSets(args)

  # search for first valid file
  for key, fileSet in fileSets.iteritems():
    for runName, runFiles in fileSet.iteritems():
      for runFile in runFiles:
        return runFile

def getExperiment(args):
  fileAlls = getFileAlls(args)

  samples = {}

  for runName in DIRS:
    samples[runName] = ROOT.SampleGroup(runName)

  for key, runList in fileAlls.iteritems():
    for runName, runFile in runList.iteritems():
      if key == RD:
        samples[runName].AddDataSample(runFile)
      elif key == NEUT or key == GENIE:
        samples[runName].AddMCSample("MC", runFile)

  experiment = ROOT.Experiment("GasInteractionAnalysis")
  for key, sample in samples.iteritems():
    experiment.AddSampleGroup(key, sample)

  return experiment

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

def getFileAlls(args):
  toProcess = getToProcess(args)
  fileAlls = {}

  for key, rootDir in toProcess.iteritems():
    fileAlls[key] = {}
    for runDir in DIRS:
      fileName = "{0}/{1}/flat/all_in_folder.root".format(rootDir, runDir)
      fileAlls[key][runDir] = fileName

  return fileAlls

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
  parser.add_argument("--plotFolder", type=str, help="Folder to put plots in", default="plots")

  parser.add_argument("--flattenTrees", action="store_true", help="Compress large numbers of flat trees into a single one")
  parser.add_argument("--makePlots", action="store_true", help="Plot selection for selected samples")

  parser.add_argument("--rd", action="store_true", help="Use real data files")
  parser.add_argument("--neut", action="store_true", help="Use neut files")
  parser.add_argument("--genie", action="store_true", help="Use genie files")

  parser.add_argument("--rdRoot", type=str, help="Folder for real data files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/I/rdp")
  parser.add_argument("--neutRoot", type=str, help="Folder for neut files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/H/neut")
  parser.add_argument("--genieRoot", type=str, help="Folder for genie files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/H/genie")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
