# python
import glob
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
#DIRS = ( RUN2WATER, )

TREES_DEF = ( "default", "truth", "config", "header" )
#TREES_SYS = ( "all_syst", )
TREES_SYS = ()

# note: doing POT stuff manually since I don't trust highland
POT_DATA = {  RUN2WATER:4.28,
              RUN2AIR:3.55,
              RUN3B:2.14,
              RUN3C:13.48,
              RUN4WATER:16.25,
              RUN4AIR:17.62     }

POT_MC =   {  RUN2WATER:42.8,
              RUN2AIR:35.5,
              RUN3B:21.4,
              RUN3C:134.8,
              RUN4WATER:162.5,
              RUN4AIR:176.2     }

POT_FILES_MC = { RUN2WATER:856,
                 RUN2AIR:710,
                 RUN3B:428,
                 RUN3C:2696,
                 RUN4WATER:3250,
                 RUN4AIR:3254     }

POT_FILES_SEEN_MC = {  RUN2WATER:2407,
                       RUN2AIR:1795,
                       RUN3B:894,
                       RUN3C:5256,
                       RUN4WATER:6989,
                       RUN4AIR:6993     }

# nominal values for single bin analysis
NOM_DATA_COL = 46
NOM_DATA_VAL_SINGLE = 310
NOM_DATA_ERR_SINGLE = 0.056796183
NOM_GENIE_COL = ROOT.kMagenta-6 #alt 30, ROOT.kMagenta-6
NOM_GENIE_VAL_SINGLE = 372.513
NOM_GENIE_ERR_SINGLE = 0.175713217
NOM_NEUT_COL = 38
NOM_NEUT_VAL_SINGLE = 10.
NOM_NEUT_ERR_SINGLE = 1.

# correction for whatever highland weirdness is causing too few GENIE events regardless of cut level
# TODO: fix this properly so the hack isn't needed
CORR_GENIE = 2.3353/3.958

FLUX_FILE = "/home/phrmav/t2k/newHighland/psyche/psycheUtils/v3r7/data/tuned13av1.1/run1-4/nd5_tuned13av1.1_13anom_run1-4_fine.root"
FLUX_HIST = "enu_nd5_13a_real_numu"
FLUX_NOM_AVG_SCL = 200. # nominal value to scale flux to (same ballpark as value of MC bin but probably less)

def main(args):
  ROOT.gROOT.SetBatch(1)
  ROOT.gStyle.SetOptStat(0)

  if args.flattenTrees:
    flattenTrees(args)
  if args.makeCSPlot:
    makeCSPlot(args)
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

def makeCSPlot(args, binMin=0.,binMax=2000.):
  subprocess.call(["mkdir", "-p", args.plotFolder])

  myCanv = ROOT.TCanvas("myCanv", "My Canvas", 1200,800)
  myCanv.cd()

  fluxFile = ROOT.TFile.Open(FLUX_FILE)
  fluxHist = fluxFile.Get(FLUX_HIST)

  bins = array.array("d")
  contents = array.array("d")

  nBins = fluxHist.GetNbinsX()
  width = fluxHist.GetBinWidth(1)

  for i in range(1, nBins+1):
    content = fluxHist.GetBinContent(i)
    min = fluxHist.GetBinLowEdge(i) * 1000. # MeV
    max = min + fluxHist.GetBinWidth(i) * 1000. # MeV

    bins.append(min)
    if max < binMax:
      contents.append(content)
    else:
      norm = (binMax - min) / (max - min)
      contents.append(content*norm)
      bins.append(max)
      break

  # get a pseudo average for pretty plots (doesn't really matter since we have separate axes for this)
  integral = fluxHist.Integral()
  scale = (FLUX_NOM_AVG_SCL / integral) * float(len(bins)-1)

  newHist = ROOT.TH1D("myCSHist", "Events passing selection;Energy / MeV;Events scaled to data PoT", len(bins)-1, bins)

  for i in range(len(contents)):
    newHist.SetBinContent(i+1, contents[i]*scale)

  minVal = 0.
  maxVal = newHist.GetMaximum()*1.1

  newHist.GetYaxis().SetRangeUser(minVal, maxVal)
  newHist.SetFillColor(ROOT.kGray)
  newHist.SetLineColor(ROOT.kGray)
  newHist.Draw()

  oldAxis = newHist.GetYaxis()

  newAxis = ROOT.TGaxis(bins[-1],0, bins[-1],maxVal, 0,maxVal/scale, 510, "+L")
  newAxis.SetTitle("Flux / cm^{2} / 50 MeV / 10^{21} PoT")
  newAxis.SetTitleColor(ROOT.kGray+2)
  newAxis.SetLineColor(ROOT.kGray+2)
  newAxis.SetLabelColor(ROOT.kGray+2)

  newAxis.Draw()

  # this is one large ugly function because of PyROOT memory issues if it's broken up >.<
  if args.manual:
    genieHist = ROOT.TH1D("genie", "Genie", 1,0,2000)
    neutHist = ROOT.TH1D("neut", "Neut", 1,0,2000)
    rdHist = ROOT.TH1D("data", "Data", 1,0,2000)

    genieHist.SetBinContent(1, NOM_GENIE_VAL_SINGLE)
    genieHist.SetBinError(1, NOM_GENIE_VAL_SINGLE*NOM_GENIE_ERR_SINGLE)
    genieHist.SetLineWidth(2)
    genieHist.SetLineColor(NOM_GENIE_COL)
    neutHist.SetBinContent(1, NOM_NEUT_VAL_SINGLE)
    neutHist.SetBinError(1, NOM_NEUT_VAL_SINGLE*NOM_NEUT_ERR_SINGLE)
    neutHist.SetLineWidth(2)
    neutHist.SetLineColor(NOM_NEUT_COL)
    rdHist.SetBinContent(1, NOM_DATA_VAL_SINGLE)
    rdHist.SetBinError(1, NOM_DATA_VAL_SINGLE*NOM_DATA_ERR_SINGLE)
    rdHist.SetLineWidth(2)
    rdHist.SetLineColor(NOM_DATA_COL)

    leg = ROOT.TLegend(0.65,0.75, 0.9,0.9)
    leg.AddEntry(rdHist, "Real data", "l")
    leg.AddEntry(neutHist, "Neut MC", "l")
    leg.AddEntry(genieHist, "Genie MC", "l")

    genieHist.Draw("E1 SAME")
    neutHist.Draw("E1 SAME")
    rdHist.Draw("E1 SAME")
    leg.Draw()

  else:
    draw = ROOT.DrawingTools(getAFile(args))
    experiment = getExperiment(args)

    #draw.DumpCategories(experiment)
    #for run in DIRS:
    #  draw.DumpPOT(experiment, run)
    draw.Draw(experiment, "HMM_mom", 1,0,2000, "all", "accum_level>=11", "SAME", "OVER NOVARBIN")
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

  ## efficiency and purity
  #draw.SetTitle("Track efficiency and purity")
  ##draw.DrawEffPurVSCut(experiment, 0, "(target==18) && (nu_pdg==14) && (nu_truereac>0) && (nu_truereac<30)", "", 0, 11, "")
  #draw.DrawEffPurVSCut(experiment, 0, "reactionCC==1", "", 0, 11, "")

  #myCanv.SaveAs("{0}/effPur.png".format(args.plotFolder))
  #myCanv.SaveAs("{0}/effPur.pdf".format(args.plotFolder))

  ## surviving OOFV source
  #draw.SetTitle("Surviving events source")
  #draw.SetTitleX("Track momentum")
  #draw.Draw(experiment, "HMM_mom", 40,0.,2000., "oofv", "accum_level>=11", "", "", 1.)

  #myCanv.SaveAs("{0}/survOOFV.png".format(args.plotFolder))
  #myCanv.SaveAs("{0}/survOOFV.pdf".format(args.plotFolder))

  ## surviving particle type
  #draw.SetTitle("Surviving particle type")
  #draw.SetTitleX("Track momentum")
  #draw.Draw(experiment, "HMM_mom", 40,0.,2000., "particle", "accum_level>=11", "", "", 1.)

  #myCanv.SaveAs("{0}/survParticle.png".format(args.plotFolder))
  #myCanv.SaveAs("{0}/survParticle.pdf".format(args.plotFolder))

  ## surviving topology
  #draw.SetTitle("Surviving topology")
  #draw.SetTitleX("Track momentum")
  #draw.Draw(experiment, "HMM_mom", 40,0.,2000., "topology", "accum_level>=11", "", "", 1.)
  #draw.DrawCutLineVertical(100., True, "r")

  #myCanv.SaveAs("{0}/survTopo.png".format(args.plotFolder))
  #myCanv.SaveAs("{0}/survTopo.pdf".format(args.plotFolder))
  #myCanv.SaveAs("{0}/survTopo.svg".format(args.plotFolder))

  ## surviving MEC topology
  #draw.SetTitle("Surviving MEC topology")
  #draw.SetTitleX("Track momentum")
  #draw.Draw(experiment, "HMM_mom", 40,0.,2000., "mectopology", "accum_level>=11", "", "", 1.)
  #draw.DrawCutLineVertical(100., True, "r")

  #myCanv.SaveAs("{0}/survMECTopo.png".format(args.plotFolder))
  #myCanv.SaveAs("{0}/survMECTopo.pdf".format(args.plotFolder))
  #myCanv.SaveAs("{0}/survMECTopo.svg".format(args.plotFolder))

  ## muon PID
  varBins = array.array("d", [-0.001, 0.05, 1.001])
  draw.SetTitle("Cut on muon PID")
  draw.SetTitleX("Track muon likelihood")
  draw.Draw(experiment, "HMM_likmu", len(varBins)-1, varBins, "oofv", "accum_level>=3", "", "OVER NOLEG NOVARBIN")
  draw.DrawCutLineVertical(0.05, True, "r")

  myCanv.SaveAs("{0}/cutLikMu.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/cutLikMu.pdf".format(args.plotFolder))
  myCanv.SaveAs("{0}/cutLikMu.svg".format(args.plotFolder))

  ## MIP PID
  varBins = array.array("d", [-0.001, 0.8, 1.001])
  draw.SetTitle("Cut on MIP PID over proton PID")
  draw.SetTitleX("Track (MIP likelihood)/(1 - proton likelihood)")
  draw.Draw(experiment, "HMM_likmip", len(varBins)-1, varBins, "oofv", "accum_level>=3", "", "OVER NOLEG NOVARBIN")
  draw.DrawCutLineVertical(0.8, True, "r")

  myCanv.SaveAs("{0}/cutLikMIP.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/cutLikMIP.pdf".format(args.plotFolder))
  myCanv.SaveAs("{0}/cutLikMIP.svg".format(args.plotFolder))

  ## momentum values
  #draw.SetTitle("Cut on momentum")
  #draw.SetTitleX("Track momentum")
  #draw.Draw(experiment, "HMM_mom", 40,0.,2000., "oofv", "accum_level>=5", "", "")
  #draw.DrawCutLineVertical(100., True, "r")

  #myCanv.SaveAs("{0}/cutMom.png".format(args.plotFolder))
  #myCanv.SaveAs("{0}/cutMom.pdf".format(args.plotFolder))
  #myCanv.SaveAs("{0}/cutMom.svg".format(args.plotFolder))

  ## costhetaX values
  #draw.SetTitle("Cut on x angle")
  #draw.SetTitleX("Track x angle")
  #draw.Draw(experiment, "HMM_dir[0]", 40,0.,1., "oofv", "accum_level>=6", "", "NOLEG OVER")
  #draw.DrawCutLineVertical(0.9, True, "l")

  #myCanv.SaveAs("{0}/cutCos.png".format(args.plotFolder))
  #myCanv.SaveAs("{0}/cutCos.pdf".format(args.plotFolder))
  #myCanv.SaveAs("{0}/cutCos.svg".format(args.plotFolder))

  ## likelihood (path)
  #draw.SetTitle("Cut on track matching likelihood")
  #draw.SetTitleX("Track minimum matching likelihood")
  #draw.Draw(experiment, "Vertex_min_likdiff", 41,0.,1025, "oofv", "accum_level>=9", "", "NOLEG OVER", 1.)
  #draw.DrawCutLineVertical(1000, True, "r")

  #myCanv.SaveAs("{0}/cutLik.png".format(args.plotFolder))
  #myCanv.SaveAs("{0}/cutLik.pdf".format(args.plotFolder))
  #myCanv.SaveAs("{0}/cutLik.svg".format(args.plotFolder))

  return

  # surviving reaction type
  draw.SetTitle("Surviving reaction type")
  draw.SetTitleX("Track momentum")
  draw.Draw(experiment, "HMM_mom", 40,0.,2000., "reacnofv", "accum_level>=11", "", "", 1.)
  draw.DrawCutLineVertical(100., True, "r")

  myCanv.SaveAs("{0}/survReac.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/survReac.pdf".format(args.plotFolder))
  myCanv.SaveAs("{0}/survReac.svg".format(args.plotFolder))

def getAFile(args):
  fileSets = getFileSets(args)

  # search for first valid file
  for key, fileSet in fileSets.iteritems():
    for runName, runFiles in fileSet.iteritems():
      for runFile in runFiles:
        return runFile

def getExperiment(args):
  fileAlls = getFileAlls(args)
  fileSets = getFileSets(args)

  samples = {}

  dataPOTs = {}
  mcPOTs = {}

  for runName in DIRS:
    dataPOT = POT_DATA[runName]
    mcPOT = POT_MC[runName] * float(POT_FILES_SEEN_MC[runName])/float(POT_FILES_MC[runName])

    samples[runName] = ROOT.SampleGroup(runName)
    dataPOTs[runName] = dataPOT
    mcPOTs[runName] = mcPOT

  for key, runList in fileAlls.iteritems():
    for runName, runFile in runList.iteritems():
      pot = 1.
      if key == RD:
        pot = dataPOTs[runName]
      else:
        pot = mcPOTs[runName]
        if key == GENIE:
          pot *= CORR_GENIE


      if key == RD:
        print "Adding {0} to {1} data".format(runFile, runName)
        dataSample = ROOT.DataSample(runFile, pot)
        samples[runName].AddDataSample(dataSample)
      elif key == NEUT or key == GENIE:
        if args.systs:
          i = 0
          potNorm = pot/float(len(fileSets[key][runName]))
          for file in fileSets[key][runName]:
            i += 1
            print "Adding {0} to {1} MC".format(file, runName)
            dataSample = ROOT.DataSample(file, potNorm)
            samples[runName].AddMCSample("MC_{0}".format(i), dataSample)
        else:
          dataSample = ROOT.DataSample(runFile, pot)
          samples[runName].AddMCSample("MC", dataSample)

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
  parser.add_argument("--makeCSPlot", action="store_true", help="Plot selection for selected samples")
  parser.add_argument("--makeMCPlots", action="store_true", help="Plot selection performace and cuts on MC")

  parser.add_argument("--systs", action="store_true", help="Use systematic uncertainties (takes longer)")
  parser.add_argument("--manual", action="store_true", help="Draw MC manually since highland is a piece of crap")

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
