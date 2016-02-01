# python
import argparse
import subprocess

# ROOT
import ROOT

# eddy
import trexAnalysis.parameters

def main(args):
  beamOut = ""
  gasOut = ""
  beamPot = 1.
  gasPot = 1.

  if args.full:
    beamOut = trexAnalysis.parameters.NTuples.neutBeam
    gasOut = trexAnalysis.parameters.NTuples.neutGas
    beamPot = trexAnalysis.parameters.Pots.listNeutBeam
    gasPot = trexAnalysis.parameters.Pots.listNeutGas
  else:
    beamOut = trexAnalysis.parameters.NTuples.reducedNeutBeam
    gasOut = trexAnalysis.parameters.NTuples.reducedNeutGas
    beamPot = trexAnalysis.parameters.Pots.listReducedNeutBeam
    gasPot = trexAnalysis.parameters.Pots.listReducedNeutGas

  makeStatisticsPlots(args, beamOut, gasOut, beamPot, gasPot, "{0}_all".format(args.plotFolder))

def makeStatisticsPlots(args, beamOut, gasOut, beamPot, gasPot, folder="plots"):
  '''Manual creation of efficiency and purity plots for cross checking'''

  subprocess.call(["mkdir", "-p", folder])
  ROOT.gROOT.SetBatch(True);
  ROOT.gStyle.SetOptStat(0);

  cutBins = [ "Uncut",
              "Event quality",
              "Tracks exist",
              "Candidate paths",
              "Muon PID",
              "TPC FV",
              "Strict TPC FV",
              "Delta ray cut",
              "Broken track cut",
              "Candidate global path",
              "Global muon PID",
              "Global track match     " ]

  if len(args.extraVars) > 0:
    pos = args.extraVarsPos
    if pos == -1:
      cutBins = cutBins + args.extraVars
    elif pos < 0:
      cutBins = cutBins[:pos+1] + args.extraVars + cutBins[pos+1:]
    else:
      cutBins = cutBins[:pos] + args.extraVars + cutBins[pos:]

  # get ntuples
  beamFile = ROOT.TFile.Open(beamOut)
  gasFile = ROOT.TFile.Open(gasOut)
  beamDefaultTree = beamFile.Get("default")
  gasDefaultTree = gasFile.Get("default")
  beamTrueTree = beamFile.Get("truth")
  gasTrueTree = gasFile.Get("truth")

  # fill accum levels for beam and gas
  histProjTotal = ROOT.TH1D("projTotal", "Projected number of data events;Energy/MeV;Events", int(args.energyBins[0]+.5),args.energyBins[1],args.energyBins[2])

  # normalise by current pot
  gasNorm = trexAnalysis.parameters.Pots.potCurrent / gasPot
  beamNorm = trexAnalysis.parameters.Pots.potCurrent / beamPot

  # save total and passing events
  totalEvents = 0
  passingEvents = 0

  # ignore gas events in beam
  for entry in gasDefaultTree:
    if getIsGas(entry):
      totalEvents += 1
      if(entry.accum_level[0] >= len(cutBins)):
        passingEvents += 1
        histProjTotal.Fill(entry.HMM_true_mom)

  print gasNorm
  gasNorm = 0.04335
  totalNormEvents = float(totalEvents) * gasNorm
  passingNormEvents = float(passingEvents) * gasNorm
  # expect about 733 events
  print "{0} total events ({1} in MC)".format(totalNormEvents, totalEvents)
  print "{0} passing events ({1} in MC)".format(passingNormEvents, passingEvents)

  for i in range(histProjTotal.GetNbinsX()+2):
    trueContent = histProjTotal.GetBinContent(i) * gasNorm
    trueError = ROOT.TMath.Sqrt(trueContent)

    histProjTotal.SetBinContent(i, trueContent)
    histProjTotal.SetBinError(i, trueError)

  # draw statistics plots
  myCanv = ROOT.TCanvas("myCanv","myCanv", 1000,800)
  myCanv.cd()

  histProjTotal.SetMinimum(0.)
  histProjTotal.SetMaximum(60.)
  histProjTotal.SetLineColor(ROOT.kBlue)
  histProjTotal.SetMarkerColor(ROOT.kBlack)
  histProjTotal.SetMarkerStyle(7)

  histProjTotal.Draw("HIST")
  histProjTotal.Draw("E1 P0 SAME")

  myCanv.SaveAs("{0}/gasStatistics.png".format(folder))

def getIsGas(entry):
  # NOTE definition here discards 5% of gas events not on argon
  return (entry.target == 18)

def getIsTrue(entry):
  isTrue = True

  # in fiducial volume
  #isTrue &= (entry.Vertex_true_in_fiducial == 1)
  # on argon
  isTrue &= (entry.target == 18)
  # numu CC
  isTrue &= (entry.nu_pdg == 14)
  isTrue &= (entry.nu_truereac > 0 and entry.nu_truereac < 30)

  return isTrue

def checkArguments():
  parser = argparse.ArgumentParser(description="Produce plots for gas and beam")
  parser.add_argument("--full", action="store_true", help="Analyse full available data sets (default is reduced)")
  parser.add_argument("--plotFolder", type=str, help="Folder to put plots in", default="plots_stat")

  parser.add_argument("--extraVars", type=str, nargs="+", help="Extra variables to plot", default=[])
  parser.add_argument("--extraVarsPos", type=int, help="Place to slot extra variables", default=-1)

  parser.add_argument("--energyBins", type=float, nargs=3, help="Energy nBins,min,max to plot", default=[5.,0.,1000.])

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
