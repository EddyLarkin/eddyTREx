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
#TREES_SYS = ( "all_syst", )
TREES_SYS = ()

def main(args):
  ROOT.gROOT.SetBatch(1)
  ROOT.gStyle.SetOptStat(0)

  if args.flattenTrees:
    flattenTrees(args)
  if args.makePlots:
    makePlots(args)
  if args.makeMCPlots:
    makeMCPlots(args)

def flattenTrees(args):
  fileSets = getFileSets(args)
  fileAlls = getFileAlls(args)

  for key, fileSet in fileSets.iteritems():
    for runName, runFiles in fileSet.iteritems():
      fileAll = fileAlls[key][runName]

      trees = TREES_DEF
      if key == NEUT or key == GENIE:
        trees = TREES_DEF + TREES_SYS

      print "\033[1mMaking new trees at {0}\033[0m".format(fileAll)
      firstEntry = True
      for tree in trees:
        print "  Merging {0} tree".format(tree)
        chain = ROOT.TChain(tree)
        for runFile in runFiles:
          chain.Add(runFile)
        newFile = None
        if firstEntry:
          newFile = ROOT.TFile.Open(fileAll, "RECREATE")
          firstEntry = False
        else:
          newFile = ROOT.TFile.Open(fileAll, "UPDATE")
        print "    {0} entries to merge".format(chain.GetEntries())
        print "    Starting merge".format(tree)
        chain.Merge(newFile, 0)
        print "    Done merge".format(tree)


def makePlots(args, var="", bins=()):
  draw = ROOT.DrawingTools(getAFile(args))
  experiment = getExperiment(args)

  subprocess.call(["mkdir", "-p", args.plotFolder])

  myCanv = ROOT.TCanvas("myCanv", "My Canvas", 1200, 800)
  myCanv.cd()

  #draw.DumpCategories(experiment)
  #for run in DIRS:
  #  draw.DumpPOT(experiment, run)
  #draw.Draw(experiment, "HMM_mom", 10,0,2000, "all", "accum_level>=0")
  draw.Draw(experiment, "HMM_mom", 10,0,2000, "all", "accum_level>=11")
  #draw.Draw(experiment, "HMM_mom", 10,0,2000, "reaction", "accum_level>=11")
  #draw.Draw(experiment, "HMM_mom", 10,0,2000, "target", "accum_level>=11")
  #draw.Draw(experiment, "HMM_mom", 10,0,2000, "oofv", "accum_level>=11")

  myCanv.SaveAs("{0}/accum_mom.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/accum_mom.pdf".format(args.plotFolder))

def makeMCPlots(args, var="", bins=()):
  draw = ROOT.DrawingTools(getAFile(args))
  experiment = getExperiment(args)

  subprocess.call(["mkdir", "-p", args.plotFolder])

  myCanv = ROOT.TCanvas("myCanv", "My Canvas", 1200, 800)
  myCanv.cd()

  # efficiency and purity
  draw.SetTitle("Track efficiency and purity")
  #draw.DrawEffPurVSCut(experiment, 0, "(target==18) && (nu_pdg==14) && (nu_truereac>0) && (nu_truereac<30)", "", 0, 11, "")
  draw.DrawEffPurVSCut(experiment, 0, "reactionCC==1", "", 0, 11, "")

  myCanv.SaveAs("{0}/effPur.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/effPur.pdf".format(args.plotFolder))

  # surviving OOFV source
  draw.SetTitle("Surviving events source")
  draw.SetTitleX("Track momentum")
  draw.Draw(experiment, "HMM_mom", 40,0.,2000., "oofv", "accum_level>=11", "", "", 1.)

  myCanv.SaveAs("{0}/survOOFV.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/survOOFV.pdf".format(args.plotFolder))

  # surviving particle type
  draw.SetTitle("Surviving particle type")
  draw.SetTitleX("Track momentum")
  draw.Draw(experiment, "HMM_mom", 40,0.,2000., "particle", "accum_level>=11", "", "", 1.)

  myCanv.SaveAs("{0}/survParticle.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/survParticle.pdf".format(args.plotFolder))

  # muon PID
  #draw.SetTitleX("Track x angle")
  #draw.Draw(experiment, "HMM_lik_muon", 10,0.,1., "oofv", "accum_level>=3")
  #draw.DrawCutLineVertical(0.05, True, "r")

  # MIP PID
  #draw.SetTitleX("Track x angle")
  #draw.Draw(experiment, "HMM_lik_mip", 10,0.,1., "oofv", "accum_level>=3")
  #draw.DrawCutLineVertical(0,8, True, "r")

  # momentum values
  draw.SetTitle("Cut on momentum")
  draw.SetTitleX("Track momentum")
  draw.Draw(experiment, "HMM_mom", 40,0.,2000., "oofv", "accum_level>=5", "", "", 1.)
  draw.DrawCutLineVertical(100., True, "r")

  myCanv.SaveAs("{0}/cutMom.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/cutMom.pdf".format(args.plotFolder))
  myCanv.SaveAs("{0}/cutMom.svg".format(args.plotFolder))

  # costhetaX values
  draw.SetTitle("Cut on x angle")
  draw.SetTitleX("Track x angle")
  draw.Draw(experiment, "HMM_dir[0]", 40,0.,1., "oofv", "accum_level>=6", "", "NOLEG", 1.)
  draw.DrawCutLineVertical(0.9, True, "l")

  myCanv.SaveAs("{0}/cutCos.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/cutCos.pdf".format(args.plotFolder))
  myCanv.SaveAs("{0}/cutCos.svg".format(args.plotFolder))

  # likelihood (path)
  #draw.SetTitleX("Track x angle")
  #draw.Draw(experiment, "HMM_max_likdiff", 10,0.,1., "oofv", "accum_level>=9")
  #draw.DrawCutLineVertical(1000, True, "l")

  return

  # surviving reaction type
  draw.SetTitle("Surviving reaction type")
  draw.SetTitleX("Track momentum")
  draw.Draw(experiment, "HMM_mom", 40,0.,2000., "reacnofv", "accum_level>=11", "", "", 1.)
  draw.DrawCutLineVertical(100., True, "r")

  myCanv.SaveAs("{0}/survReac.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/survReac.pdf".format(args.plotFolder))

  # surviving topology
  draw.SetTitle("Surviving topology")
  draw.SetTitleX("Track momentum")
  draw.Draw(experiment, "HMM_mom", 40,0.,2000., "topology", "accum_level>=11", "", "", 1.)
  draw.DrawCutLineVertical(100., True, "r")

  myCanv.SaveAs("{0}/survTopo.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/survTopo.pdf".format(args.plotFolder))

  # surviving MEC topology
  draw.SetTitle("Surviving MEC topology")
  draw.SetTitleX("Track momentum")
  draw.Draw(experiment, "HMM_mom", 40,0.,2000., "mectopology", "accum_level>=11", "", "", 1.)
  draw.DrawCutLineVertical(100., True, "r")

  myCanv.SaveAs("{0}/survMECTopo.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/survMECTopo.pdf".format(args.plotFolder))

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
  parser.add_argument("--makeMCPlots", action="store_true", help="Plot selection performace and cuts on MC")

  parser.add_argument("--rd", action="store_true", help="Use real data files")
  parser.add_argument("--neut", action="store_true", help="Use neut files")
  parser.add_argument("--genie", action="store_true", help="Use genie files")

  parser.add_argument("--rdRoot", type=str, help="Folder for real data files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/I/rdp")
  parser.add_argument("--neutRoot", type=str, help="Folder for neut files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/H/mcp/neut")
  parser.add_argument("--genieRoot", type=str, help="Folder for genie files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/H/mcp/genie")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
