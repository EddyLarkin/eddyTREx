# python
import math
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
TREES_SYS = ( "all_syst", )
#TREES_SYS = ()

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

# manually get flux systs since they don't seem to be applied as expected to weights
FLUX_WEIGHT_SYST = {
                      (0., 400.):.121,
                      (400., 500.):.130,
                      (500., 600.):.122,
                      (600., 700.):.115,
                      (700., 1000.):.129,
                      (1000., 1500.):.116,
                      (1500., 2500.):.100,
                      (2500., 3500.):.095,
                      (3500., 5000.):.112,
                      (5000., 7000.):.152,
                      (7000., 30000.):.187
                                            }

# correction for whatever highland weirdness is causing the wrong number of events regardless of cut level
# TODO: fix this properly so the hack isn't needed
CORR_GENIE = 2.34678/3.98058
CORR_NEUT = 1.65133/3.98058
CORR_ALL = 258./310.

GENIE_INT = 4783.48
NEUT_INT = 3279.92

# nominal values for single bin analysis
NOM_DATA_COL = 46
NOM_DATA_VAL_SINGLE = 310.
NOM_GENIE_COL = ROOT.kMagenta-6 #alt 30, ROOT.kMagenta-6
NOM_GENIE_VAL_SINGLE = 372.513
NOM_GENIE_ERR_SINGLE = 0.092236
NOM_NEUT_COL = 38
NOM_NEUT_VAL_SINGLE = 355.032
NOM_NEUT_ERR_SINGLE = 0.090080
NOM_FLUX_SYST = 0.109875

FLUX_FILE = "/home/phrmav/t2k/newHighland/psyche/psycheUtils/v3r7/data/tuned13av1.1/run1-4/nd5_tuned13av1.1_13anom_run1-4_fine.root"
FLUX_HIST = "enu_nd5_13a_real_numu"
FLUX_NOM_AVG_SCL = 120. # nominal value to scale flux to (same ballpark as value of MC bin but probably less)

# nominal values for muon momentum plots
NOM_BINNING_MOM = (10, 0.,2000.)

NOM_DATA_VAL_MOM = (44., 117., 42., 23., 18., 6., 4., 6., 9., 41.)
NOM_GENIE_VAL_MOM = (626.141, 1394.9, 877.146, 490.006, 264.938, 187.43, 135.05, 99.7307, 73.398, 634.735)
NOM_GENIE_ERR_MOM = (0.081270, 0.085126, 0.0921765, 0.110331, 0.111852, 0.114440, 0.128581, 0.106984, 0.131234, 0.122029)
NOM_NEUT_VAL_MOM = (429.543, 936.461, 629.628, 331.302, 174.714, 112.875, 87.2237, 59.8061, 61.487, 456.876)
NOM_NEUT_ERR_MOM = (0.0883060, 0.081537, 0.092485, 0.103761, 0.112368, 0.114474, 0.138796, 0.106348, 0.133936, 0.144392)

# nominal values for muon angle plots
NOM_BINNING_ANG = (10, -1.,1.)

NOM_DATA_VAL_ANG = (22., 13., 14., 12., 17., 19., 40., 34., 43., 96.)
NOM_GENIE_VAL_ANG = (338.202, 216.494, 229.826, 204.203, 204.957, 248.969, 357.592, 557.715, 739.112, 1686.51)
NOM_GENIE_ERR_ANG = (0.082626, 0.101407, 0.093476, 0.086628, 0.078598, 0.082144, 0.087098, 0.089970, 0.101364, 0.102221)
NOM_NEUT_VAL_ANG = (210.113, 159.422, 134.313, 139.135, 139.957, 174.669, 281.544, 429.857, 525.914, 1084.99)
NOM_NEUT_ERR_ANG = (0.090582, 0.080753, 0.088635, 0.080005, 0.081086, 0.084838, 0.084137, 0.087780, 0.105585, 0.104565)

# nominal values for path multiplicity plots
NOM_BINNING_PATH = (11, 0.5,10.5)

NOM_DATA_VAL_PATH = (188., 89., 25., 5., 2., 1., 0., 0., 0., 0.)
NOM_GENIE_VAL_PATH = (1939.1, 1925.26, 539.458, 198.339, 89.4029, 34.8228, 23.4256, 23.4256, 17.3325, 11.5105, 4.622)
NOM_GENIE_ERR_PATH = (0.10, 0.078684, 0.101126, 0.134108, 0.184121, 0.246387, 0.286670, 0.322656, 0.332453, 0.369137, 0.495789)
NOM_NEUT_VAL_PATH = (1222.49, 1370.08, 439.752, 171.89, 47.645, 16.1337, 5.8665, 4.5342, 0.9555, 0.9555)
NOM_NEUT_ERR_PATH = (0.082541, 0.099398, 0.138663, 0.175863, 0.227779, 0.341496, 0.303745, 0.333594, 0., 0.466606)

# nominal values for proton multiplicity plots
NOM_BINNING_PMULT = (11, -0.5,10.5)

NOM_DATA_VAL_PMULT = (275., 26., 7., 2., 0., 0., 0., 0., 0., 0., 0.,)
NOM_GENIE_VAL_PMULT = (3377.93, 1047.98, 232.437, 70.0422, 28.0008, 15.5793, 6.733, 1.911, 0.9555, 0.9555, 0.9555)
NOM_GENIE_ERR_PMULT = (0.1, 0.118047, 0.171935, 0.215410, 0.293535, 0.408842, 0.345821, 0.441971, 0.528134, 0.625992, 1.)
NOM_NEUT_VAL_PMULT = (2212.92, 825.574, 166.98, 58.3092, 13.2672, 1.911, 0., 0.9555, 0., 0., 0.)
NOM_NEUT_ERR_PMULT = (0.1, 0.114852, 0.153710, 0.174534, 0.264660, 0.347540, 1., 0.344017, 1., 1., 1.)

# nominal values for proton momentum plots
NOM_BINNING_PMOM = (10, 0.,2000.)

NOM_DATA_VAL_PMOM = (2., 10., 8., 6., 4., 2., 0., 0., 0., 3., 275.)
NOM_GENIE_VAL_PMOM = (171.133, 466.055, 372.464, 202.665, 96.002, 32.0696, 14.466, 10.2672, 4.7775, 35.6483, 3377.93)
NOM_GENIE_ERR_PMOM = (0.141544, 0.137173, 0.129134, 0.135540, 0.141629, 0.142948, 0.162471, 0.198255, 0.198050, 0.303866)
NOM_NEUT_VAL_PMOM = (49.1102, 367.117, 318.048, 164.785, 78.5325, 38.179, 11.6683, 14.3325, 1.9555, 23.2678, 2212.92)
NOM_NEUT_ERR_PMOM = (0.147423, 0.125103, 0.128505, 0.122324, 0.120329, 0.135282, 0.127794, 0.121635, 0., 0.162591)

def main(args):
  ROOT.gROOT.SetBatch(1)
  ROOT.gStyle.SetOptStat(0)

  if args.flattenTrees:
    if args.key and args.runName:
      flattenTree(args)
    else:
      flattenTrees(args)
  if args.makeCSPlot:
    makeCSPlot(args)
  if args.makeMomentumPlot:
    makeMomentumPlot(args)
  if args.makeCosThetaPlot:
    makeCosThetaPlot(args)
  if args.makePathMultPlot:
    makePathMultPlot(args)
  if args.makeProtonMultPlot:
    makeProtonMultPlot(args)
  if args.makeProtonMomPlot:
    makeProtonMomPlot(args)
  if args.makeMCPlots:
    makeMCPlots(args)

def flattenTrees(args):
  fileSets = getFileSets(args)
  fileAlls = getFileAlls(args)

  for key, fileSet in fileSets.iteritems():
    for runName, runFiles in fileSet.iteritems():
      fileAll = fileAlls[key][runName]

      command = ["python", "../py/trexAnalysis/plotAnalysedFiles.py"]
      command += ["--key", key]
      command += ["--runName", runName]
      command += ["--flattenTrees"]
      if args.rd:
        command += ["--rd"]
      if args.neut:
        command += ["--neut"]
      if args.genie:
        command += ["--genie"]
      subcommand = ["bsub", "-q", "long", "-G", "finalyeargrp"]
      subprocess.call(subcommand + command)

def flattenTree(args):
  fileSets = getFileSets(args)
  fileAlls = getFileAlls(args)

  key = args.key
  runName= args.runName
  fileSet = fileSets[key]
  fileAll = fileAlls[key][runName]
  runFiles = fileSet[runName]

  print "Flattening to {0}".format(fileAll)
  trees = TREES_DEF
  if key == NEUT or key == GENIE:
    trees = TREES_DEF + TREES_SYS

  fileAll = fileAll.replace("all", "newAll")
  print "\033[1mMaking new trees at {0}\033[0m".format(fileAll)
  newFile = ROOT.TFile.Open(fileAll, "RECREATE")
  for tree in trees:
    print "  Merging {0} tree over {1} files".format(tree, len(runFiles))
    list = ROOT.TList()

    for runFile in runFiles:
      runFileObj = ROOT.TFile.Open(runFile)
      runTree = runFileObj.Get(tree)
      list.Add(runTree)

    print "    Starting merge".format(tree)
    newFile.cd()
    newTree = ROOT.TTree.MergeTrees(list)
    print "    Done merge".format(tree)
    newTree.SetName(tree)
    newTree.Write()
  newFile.Close()
  print "Done all merges".format(tree)


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

  sumFluxSyst = 0.
  nFluxSyst = 0
  for i in range(1, nBins+1):
    content = fluxHist.GetBinContent(i)
    min = fluxHist.GetBinLowEdge(i) * 1000. # MeV
    max = min + fluxHist.GetBinWidth(i) * 1000. # MeV
    mid= min+max/2.
    for limits, syst in FLUX_WEIGHT_SYST.iteritems():
      if mid >= limits[0] and mid < limits[1]:
        nFluxSyst += 1
        sumFluxSyst += syst
        break


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

    genieHist.SetBinContent(1, NOM_GENIE_VAL_SINGLE*CORR_ALL)
    genieHist.SetBinError(1, NOM_GENIE_VAL_SINGLE*math.sqrt(NOM_GENIE_ERR_SINGLE**2 + NOM_FLUX_SYST**2)*CORR_ALL)
    genieHist.SetLineWidth(2)
    genieHist.SetLineColor(NOM_GENIE_COL)
    neutHist.SetBinContent(1, NOM_NEUT_VAL_SINGLE*CORR_ALL)
    neutHist.SetBinError(1, NOM_NEUT_VAL_SINGLE*math.sqrt(NOM_NEUT_ERR_SINGLE**2 + NOM_FLUX_SYST**2)*CORR_ALL)
    neutHist.SetLineWidth(2)
    neutHist.SetLineColor(NOM_NEUT_COL)
    rdHist.SetBinContent(1, NOM_DATA_VAL_SINGLE*CORR_ALL)
    rdHist.SetBinError(1, math.sqrt(NOM_DATA_VAL_SINGLE**CORR_ALL))
    rdHist.SetLineWidth(2)
    rdHist.SetLineColor(NOM_DATA_COL)

    leg = ROOT.TLegend(0.65,0.75, 0.9,0.9)
    leg.AddEntry(rdHist, "Real data", "l")
    leg.AddEntry(neutHist, "Neut MC", "l")
    leg.AddEntry(genieHist, "Genie MC", "l")

    print "Data:   {0} +- {1}".format(rdHist.GetBinContent(1), rdHist.GetBinError(1))
    print "GENIE:  {0} +- {1}".format(genieHist.GetBinContent(1), genieHist.GetBinError(1))
    print "NEUT :  {0} +- {1}".format(neutHist.GetBinContent(1), neutHist.GetBinError(1))

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
    draw.Draw(experiment, "HMM_mom", 1,0,2000, "all", "accum_level>=11", "", "OVER NOVARBIN")
    #draw.Draw(experiment, "HMM_mom", 10,0,2000, "reaction", "accum_level>=11")
    #draw.Draw(experiment, "HMM_mom", 10,0,2000, "target", "accum_level>=11")
    #draw.Draw(experiment, "HMM_mom", 10,0,2000, "oofv", "accum_level>=11")

  myCanv.SaveAs("{0}/accum_mom.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/accum_mom.pdf".format(args.plotFolder))

def makeMomentumPlot(args):
  subprocess.call(["mkdir", "-p", args.plotFolder])

  myCanv = ROOT.TCanvas("myCanv", "My Canvas", 1200,800)
  myCanv.cd()

  if args.manual:
    genieHist = ROOT.TH1D("genie", "Events passing selection by momentum;Muon momentum / MeV;Events", *NOM_BINNING_MOM)
    neutHist = ROOT.TH1D("neut", "Neut", *NOM_BINNING_MOM)
    rdHist = ROOT.TH1D("data", "Data", *NOM_BINNING_MOM)

    genieSum = 0.
    for bin in NOM_GENIE_VAL_MOM:
      genieSum += bin
    genieNorm = NOM_GENIE_VAL_SINGLE / genieSum
    neutSum = 0.
    for bin in NOM_NEUT_VAL_MOM:
      neutSum += bin
    neutNorm = NOM_NEUT_VAL_SINGLE / neutSum
    for i in range(10):
      genieHist.SetBinContent(i+1, NOM_GENIE_VAL_MOM[i]*CORR_ALL*genieNorm)
      genieHist.SetBinError(i+1, NOM_GENIE_VAL_MOM[i]*math.sqrt(NOM_GENIE_ERR_MOM[i]**2 + NOM_FLUX_SYST**2)*CORR_ALL*genieNorm)
      genieHist.SetLineWidth(2)
      genieHist.SetLineColor(NOM_GENIE_COL)
      neutHist.SetBinContent(i+1, NOM_NEUT_VAL_MOM[i]*neutNorm*CORR_ALL)
      neutHist.SetBinError(i+1, NOM_NEUT_VAL_MOM[i]*math.sqrt(NOM_NEUT_ERR_MOM[i]**2 + NOM_FLUX_SYST**2)*neutNorm*CORR_ALL)
      neutHist.SetLineWidth(2)
      neutHist.SetLineColor(NOM_NEUT_COL)
      rdHist.SetBinContent(i+1, round(NOM_DATA_VAL_MOM[i]*CORR_ALL))
      rdHist.SetBinError(i+1, math.sqrt(NOM_DATA_VAL_MOM[i]*CORR_ALL))
      rdHist.SetLineWidth(2)
      rdHist.SetLineColor(NOM_DATA_COL)

    leg = ROOT.TLegend(0.65,0.75, 0.9,0.9)
    leg.AddEntry(rdHist, "Real data", "l")
    leg.AddEntry(neutHist, "Neut MC", "l")
    leg.AddEntry(genieHist, "Genie MC", "l")

    genieHist.Draw("E1")
    neutHist.Draw("E1 SAME")
    rdHist.Draw("E1 SAME")
    leg.Draw()

  else:
    draw = ROOT.DrawingTools(getAFile(args))
    experiment = getExperiment(args)

    #draw.DumpCategories(experiment)
    #for run in DIRS:
    #  draw.DumpPOT(experiment, run)
    draw.Draw(experiment, "HMM_mom", 10,0,2000, "all", "accum_level>=11", "TEXT", "OVER NOVARBIN")
    #draw.Draw(experiment, "HMM_mom", 10,0,2000, "reaction", "accum_level>=11")
    #draw.Draw(experiment, "HMM_mom", 10,0,2000, "target", "accum_level>=11")
    #draw.Draw(experiment, "HMM_mom", 10,0,2000, "oofv", "accum_level>=11")

  myCanv.SaveAs("{0}/selMom.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/selMom.pdf".format(args.plotFolder))

def makeCosThetaPlot(args):
  subprocess.call(["mkdir", "-p", args.plotFolder])

  myCanv = ROOT.TCanvas("myCanv", "My Canvas", 1200,800)
  myCanv.cd()

  if args.manual:
    genieHist = ROOT.TH1D("genie", "Events passing selection by muon angle relative to beam axis;cos#theta;Events", *NOM_BINNING_ANG)
    neutHist = ROOT.TH1D("neut", "Neut", *NOM_BINNING_ANG)
    rdHist = ROOT.TH1D("data", "Data", *NOM_BINNING_ANG)

    genieSum = 0.
    for bin in NOM_GENIE_VAL_ANG:
      genieSum += bin
    genieNorm = NOM_GENIE_VAL_SINGLE / genieSum
    neutSum = 0.
    for bin in NOM_NEUT_VAL_ANG:
      neutSum += bin
    neutNorm = NOM_NEUT_VAL_SINGLE / neutSum
    for i in range(10):
      genieHist.SetBinContent(i+1, NOM_GENIE_VAL_ANG[i]*genieNorm*CORR_ALL)
      genieHist.SetBinError(i+1, NOM_GENIE_VAL_ANG[i]*math.sqrt(NOM_GENIE_ERR_ANG[i]**2 + NOM_FLUX_SYST**2)*genieNorm*CORR_ALL)
      genieHist.SetLineWidth(2)
      genieHist.SetLineColor(NOM_GENIE_COL)
      neutHist.SetBinContent(i+1, NOM_NEUT_VAL_ANG[i]*neutNorm*CORR_ALL)
      neutHist.SetBinError(i+1, NOM_NEUT_VAL_ANG[i]*math.sqrt(NOM_NEUT_ERR_ANG[i]**2 + NOM_FLUX_SYST**2)*neutNorm*CORR_ALL)
      neutHist.SetLineWidth(2)
      neutHist.SetLineColor(NOM_NEUT_COL)
      rdHist.SetBinContent(i+1, round(NOM_DATA_VAL_ANG[i]*CORR_ALL))
      rdHist.SetBinError(i+1, math.sqrt(NOM_DATA_VAL_ANG[i]*CORR_ALL))
      rdHist.SetLineWidth(2)
      rdHist.SetLineColor(NOM_DATA_COL)

    leg = ROOT.TLegend(0.1,0.75, 0.35,0.9)
    leg.AddEntry(rdHist, "Real data", "l")
    leg.AddEntry(neutHist, "Neut MC", "l")
    leg.AddEntry(genieHist, "Genie MC", "l")

    genieHist.Draw("E1")
    neutHist.Draw("E1 SAME")
    rdHist.Draw("E1 SAME")
    leg.Draw()

  else:
    draw = ROOT.DrawingTools(getAFile(args))
    experiment = getExperiment(args)

    draw.Draw(experiment, "HMM_costheta", 10,-1.,1., "all", "accum_level>=11", "TEXT", "NOVARBIN")

  myCanv.SaveAs("{0}/selCosTheta.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/selCosTheta.pdf".format(args.plotFolder))

def makePathMultPlot(args):
  subprocess.call(["mkdir", "-p", args.plotFolder])

  myCanv = ROOT.TCanvas("myCanv", "My Canvas", 1200,800)
  myCanv.cd()

  if args.manual:
    genieHist = ROOT.TH1D("genie", "Events passing selection by path multiplicity;Path multiplicity;Events", *NOM_BINNING_PATH)
    neutHist = ROOT.TH1D("neut", "Neut", *NOM_BINNING_PATH)
    rdHist = ROOT.TH1D("data", "Events passing selection by path multiplicity;Path multiplicity;Events", *NOM_BINNING_PATH)

    genieNorm = NOM_GENIE_VAL_SINGLE / GENIE_INT
    neutNorm = NOM_NEUT_VAL_SINGLE / NEUT_INT
    for i in range(10):
      genieHist.SetBinContent(i+1, NOM_GENIE_VAL_PATH[i]*CORR_ALL*genieNorm)
      genieHist.SetBinError(i+1, NOM_GENIE_VAL_PATH[i]*math.sqrt(NOM_GENIE_ERR_PATH[i]**2 + NOM_FLUX_SYST**2)*CORR_ALL*genieNorm)
      genieHist.SetLineWidth(2)
      genieHist.SetLineColor(NOM_GENIE_COL)
      neutHist.SetBinContent(i+1, NOM_NEUT_VAL_PATH[i]*neutNorm*CORR_ALL)
      neutHist.SetBinError(i+1, NOM_NEUT_VAL_PATH[i]*math.sqrt(NOM_NEUT_ERR_PATH[i]**2 + NOM_FLUX_SYST**2)*neutNorm*CORR_ALL)
      neutHist.SetLineWidth(2)
      neutHist.SetLineColor(NOM_NEUT_COL)
      rdHist.SetBinContent(i+1, round(NOM_DATA_VAL_PATH[i]*CORR_ALL))
      rdHist.SetBinError(i+1, math.sqrt(NOM_DATA_VAL_PATH[i]*CORR_ALL))
      rdHist.SetLineWidth(2)
      rdHist.SetLineColor(NOM_DATA_COL)

    leg = ROOT.TLegend(0.65,0.75, 0.9,0.9)
    leg.AddEntry(rdHist, "Real data", "l")
    leg.AddEntry(neutHist, "Neut MC", "l")
    leg.AddEntry(genieHist, "Genie MC", "l")

    rdHist.Draw("E1")
    genieHist.Draw("E1 SAME")
    neutHist.Draw("E1 SAME")
    rdHist.Draw("E1 SAME")
    leg.Draw()

  else:
    draw = ROOT.DrawingTools(getAFile(args))
    experiment = getExperiment(args)

    draw.Draw(experiment, "Vertex_N_hot_paths", 10,0.5,10.5, "all", "accum_level>=11", "TEXT", "UNDER OVER NOVARBIN")

  myCanv.SaveAs("{0}/selPathMult.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/selPathMult.pdf".format(args.plotFolder))

def makeProtonMultPlot(args):
  subprocess.call(["mkdir", "-p", args.plotFolder])

  myCanv = ROOT.TCanvas("myCanv", "My Canvas", 1200,800)
  myCanv.cd()

  if args.manual:
    genieHist = ROOT.TH1D("genie", "Events passing selection by proton multiplicity;Proton multiplicity;Events", *NOM_BINNING_PMULT)
    neutHist = ROOT.TH1D("neut", "Neut", *NOM_BINNING_PMULT)
    rdHist = ROOT.TH1D("data", "Data", *NOM_BINNING_PMULT)

    genieNorm = NOM_GENIE_VAL_SINGLE / GENIE_INT
    neutNorm = NOM_NEUT_VAL_SINGLE / NEUT_INT
    for i in range(10):
      genieHist.SetBinContent(i+1, NOM_GENIE_VAL_PMULT[i]*CORR_ALL*genieNorm)
      genieHist.SetBinError(i+1, NOM_GENIE_VAL_PMULT[i]*math.sqrt(NOM_GENIE_ERR_PMULT[i]**2 + NOM_FLUX_SYST**2)*CORR_ALL*genieNorm)
      genieHist.SetLineWidth(2)
      genieHist.SetLineColor(NOM_GENIE_COL)
      neutHist.SetBinContent(i+1, NOM_NEUT_VAL_PMULT[i]*neutNorm*CORR_ALL)
      neutHist.SetBinError(i+1, NOM_NEUT_VAL_PMULT[i]*math.sqrt(NOM_NEUT_ERR_PMULT[i]**2 + NOM_FLUX_SYST**2)*neutNorm*CORR_ALL)
      neutHist.SetLineWidth(2)
      neutHist.SetLineColor(NOM_NEUT_COL)
      rdHist.SetBinContent(i+1, round(NOM_DATA_VAL_PMULT[i]*CORR_ALL))
      rdHist.SetBinError(i+1, math.sqrt(NOM_DATA_VAL_PMULT[i]*CORR_ALL))
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
    draw.Draw(experiment, "Vertex_N_protons", 11,-0.5,10.5, "all", "accum_level>=11", "TEXT", "UNDER OVER NOVARBIN")

  myCanv.SaveAs("{0}/selProtMult.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/selProtMult.pdf".format(args.plotFolder))

def makeProtonMomPlot(args):
  subprocess.call(["mkdir", "-p", args.plotFolder])

  myCanv = ROOT.TCanvas("myCanv", "My Canvas", 1200,800)
  myCanv.cd()

  if args.manual:
    genieHist = ROOT.TH1D("genie", "Events passing selection by highest proton;Highest proton momentum / MeV;Events", *NOM_BINNING_PMOM)
    neutHist = ROOT.TH1D("neut", "Neut", *NOM_BINNING_PMOM)
    rdHist = ROOT.TH1D("data", "Data", *NOM_BINNING_PMOM)

    genieNorm = NOM_GENIE_VAL_SINGLE / GENIE_INT
    neutNorm = NOM_NEUT_VAL_SINGLE / NEUT_INT
    for i in range(10):
      genieHist.SetBinContent(i+1, NOM_GENIE_VAL_PMOM[i]*CORR_ALL*genieNorm)
      genieHist.SetBinError(i+1, NOM_GENIE_VAL_PMOM[i]*math.sqrt(NOM_GENIE_ERR_PMOM[i]**2 + NOM_FLUX_SYST**2)*CORR_ALL*genieNorm)
      genieHist.SetLineWidth(2)
      genieHist.SetLineColor(NOM_GENIE_COL)
      neutHist.SetBinContent(i+1, NOM_NEUT_VAL_PMOM[i]*neutNorm*CORR_ALL)
      neutHist.SetBinError(i+1, NOM_NEUT_VAL_PMOM[i]*math.sqrt(NOM_NEUT_ERR_PMOM[i]**2 + NOM_FLUX_SYST**2)*neutNorm*CORR_ALL)
      neutHist.SetLineWidth(2)
      neutHist.SetLineColor(NOM_NEUT_COL)
      rdHist.SetBinContent(i+1, round(NOM_DATA_VAL_PMOM[i]*CORR_ALL))
      rdHist.SetBinError(i+1, math.sqrt(NOM_DATA_VAL_PMOM[i]*CORR_ALL))
      rdHist.SetLineWidth(2)
      rdHist.SetLineColor(NOM_DATA_COL)

    leg = ROOT.TLegend(0.65,0.75, 0.9,0.9)
    leg.AddEntry(rdHist, "Real data", "l")
    leg.AddEntry(neutHist, "Neut MC", "l")
    leg.AddEntry(genieHist, "Genie MC", "l")

    genieHist.Draw("E1")
    neutHist.Draw("E1 SAME")
    rdHist.Draw("E1 SAME")
    leg.Draw()

  else:
    draw = ROOT.DrawingTools(getAFile(args))
    experiment = getExperiment(args)

    #draw.DumpCategories(experiment)
    #for run in DIRS:
    #  draw.DumpPOT(experiment, run)
    draw.Draw(experiment, "Vertex_max_proton_mom", 10,0.,2000., "all", "accum_level>=11", "TEXT", "UNDER OVER NOVARBIN")
    #draw.Draw(experiment, "HMM_mom", 10,0,2000, "reaction", "accum_level>=11")
    #draw.Draw(experiment, "HMM_mom", 10,0,2000, "target", "accum_level>=11")
    #draw.Draw(experiment, "HMM_mom", 10,0,2000, "oofv", "accum_level>=11")

  myCanv.SaveAs("{0}/selProtMom.png".format(args.plotFolder))
  myCanv.SaveAs("{0}/selProtMom.pdf".format(args.plotFolder))

def makeMCPlots(args, var="", bins=()):
  draw = ROOT.DrawingTools(getAFile(args))
  experiment = getExperiment(args)

  subprocess.call(["mkdir", "-p", args.plotFolder])

  myCanv = ROOT.TCanvas("myCanv", "My Canvas", 1200, 800)
  myCanv.cd()

  ## efficiency and purity
  draw.SetTitle("Track efficiency and purity")
  ##draw.DrawEffPurVSCut(experiment, 0, "(target==18) && (nu_pdg==14) && (nu_truereac>0) && (nu_truereac<30)", "", 0, 11, "")
  draw.DrawEffPurVSCut(experiment, 0, "(reactionCC==1)", "", 0, 11, "")

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
  #varBins = array.array("d", [-0.001, 0.05, 1.001])
  #draw.SetTitle("Cut on muon PID")
  #draw.SetTitleX("Track muon likelihood")
  #draw.Draw(experiment, "HMM_likmu", len(varBins)-1, varBins, "oofv", "accum_level>=3", "", "OVER NOLEG NOVARBIN")
  #draw.DrawCutLineVertical(0.05, True, "r")

  #myCanv.SaveAs("{0}/cutLikMu.png".format(args.plotFolder))
  #myCanv.SaveAs("{0}/cutLikMu.pdf".format(args.plotFolder))
  #myCanv.SaveAs("{0}/cutLikMu.svg".format(args.plotFolder))

  ## MIP PID
  #varBins = array.array("d", [-0.001, 0.8, 1.001])
  #draw.SetTitle("Cut on MIP PID over proton PID")
  #draw.SetTitleX("Track (MIP likelihood)/(1 - proton likelihood)")
  #draw.Draw(experiment, "HMM_likmip", len(varBins)-1, varBins, "oofv", "accum_level>=3", "", "OVER NOLEG NOVARBIN")
  #draw.DrawCutLineVertical(0.8, True, "r")

  #myCanv.SaveAs("{0}/cutLikMIP.png".format(args.plotFolder))
  #myCanv.SaveAs("{0}/cutLikMIP.pdf".format(args.plotFolder))
  #myCanv.SaveAs("{0}/cutLikMIP.svg".format(args.plotFolder))

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
        if key == NEUT:
          pot *= CORR_NEUT

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
  parser.add_argument("--makeMomentumPlot", action="store_true", help="Plot muon momentum for selected samples")
  parser.add_argument("--makeCosThetaPlot", action="store_true", help="Plot muon anglefor selected samples")
  parser.add_argument("--makePathMultPlot", action="store_true", help="Plot path multiplicity momentum for selected samples")
  parser.add_argument("--makeProtonMultPlot", action="store_true", help="Plot proton multiplicity for selected samples")
  parser.add_argument("--makeProtonMomPlot", action="store_true", help="Plot proton momentum for selected samples")
  parser.add_argument("--makeMCPlots", action="store_true", help="Plot selection performace and cuts on MC")

  parser.add_argument("--systs", action="store_true", help="Use systematic uncertainties (takes longer)")
  parser.add_argument("--manual", action="store_true", help="Draw MC manually since highland is a piece of crap")

  parser.add_argument("--rd", action="store_true", help="Use real data files")
  parser.add_argument("--neut", action="store_true", help="Use neut files")
  parser.add_argument("--genie", action="store_true", help="Use genie files")

  parser.add_argument("--rdRoot", type=str, help="Folder for real data files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/I/rdp")
  parser.add_argument("--neutRoot", type=str, help="Folder for neut files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/H/mcp/neut")
  parser.add_argument("--genieRoot", type=str, help="Folder for genie files", default="/data/t2k/phrmav/gasAnalysisFlats/production006/H/mcp/genie")

  parser.add_argument("--key", type=str, help="Key for processing individual files", default="")
  parser.add_argument("--runName", type=str, help="Run name for processing individual files", default="")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
