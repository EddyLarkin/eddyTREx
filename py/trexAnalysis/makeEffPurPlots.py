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

  if args.s1s:
    if args.full:
      beamOut = trexAnalysis.parameters.NTuples.s1sNeutBeam
      gasOut = trexAnalysis.parameters.NTuples.s1sNeutGas
      beamPot = trexAnalysis.parameters.Pots.listS1SNeutBeam
      gasPot = trexAnalysis.parameters.Pots.listS1SNeutGas
    else:
      beamOut = trexAnalysis.parameters.NTuples.s1sReducedNeutBeam
      gasOut = trexAnalysis.parameters.NTuples.s1sReducedNeutGas
      beamPot = trexAnalysis.parameters.Pots.listS1SReducedNeutBeam
      gasPot = trexAnalysis.parameters.Pots.listS1SReducedNeutGas
  else:
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

  if args.s1s:
    if args.drawingTools:
      makeEffPurPlots(args, beamOut, gasOut, beamPot, gasPot, "{0}_s1s".format(args.plotFolder))
    else:
      makeEffPurPlots2(args, beamOut, gasOut, beamPot, gasPot, "{0}_s1s".format(args.plotFolder))
  else:
    if args.drawingTools:
      makeEffPurPlots(args, beamOut, gasOut, beamPot, gasPot, "{0}_all".format(args.plotFolder))
    else:
      makeEffPurPlots2(args, beamOut, gasOut, beamPot, gasPot, "{0}_all".format(args.plotFolder))

def makeEffPurPlots(args, beamOut, gasOut, beamPot, gasPot, folder="plots"):
  '''Make efficiency and purity plots with the drawing tools'''

  subprocess.call(["mkdir", "-p", folder])
  ROOT.gROOT.SetBatch(True);

  # set up normalised beam and gas
  mcBeam = ROOT.DataSample(beamOut, beamPot)
  mcGas = ROOT.DataSample(gasOut, gasPot)

  # add combined MC to experiment
  exp = ROOT.Experiment("nd280")

  combinedMC = ROOT.SampleGroup("combined")
  combinedMC.AddMCSample("mcBeam", mcBeam)
  combinedMC.AddMCSample("mcGas", mcGas)

  exp.AddSampleGroup("combined", combinedMC)

  # draw plots
  myCanv = ROOT.TCanvas("myCanv","myCanv", 1000,800)
  myCanv.cd()

  drawer = ROOT.DrawingTools(beamOut)
  drawer.DrawEffPurVSCut(exp, "(target==18) && (nu_pdg==14) && (nu_truereac>0) && (nu_truereac<30)", "", -1,-1, "")

  myCanv.SaveAs("{0}/effPur.png".format(folder))

  # TODO: get hist to print purity information
  #graphEff = myCanv.GetPrimitive("eff_39")
  #graphPur = myCanv.GetPrimitive("eff_115")
  #histEff = graphEff.GetHistogram()
  #histPur = graphPur.GetHistogram()
  #finalEff = histEff.GetBinContent( histEff.GetNbinsX() )
  #finalPur = histPur.GetBinContent( histPur.GetNbinsX() )
  #print "Final efficiency: {0}%".format(finalEff*100.)
  #print "Final purity: {0}%".format(finalPur*100.)

def makeEffPurPlots2(args, beamOut, gasOut, beamPot, gasPot, folder="plots", cuts=7):
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
  binN = len(cutBins)
  binLow = 0.5
  binUp = binLow + float(binN)

  histTrueTotal = ROOT.TH1D("trueTotal", "Efficiency and purity", binN,binLow,binUp)
  histTrueSelected = ROOT.TH1D("trueSelected", "Efficiency and purity", binN,binLow,binUp)
  histBgTotal = ROOT.TH1D("beamTotal", "Efficiency and purity", binN,binLow,binUp)
  histBgSelected = ROOT.TH1D("beamSelected", "Efficiency and purity", binN,binLow,binUp)
  histTotalSelected = ROOT.TH1D("totalSelected", "Efficiency and purity", binN,binLow,binUp)

  histTrueTotal.Sumw2()
  histTrueSelected.Sumw2()
  histBgTotal.Sumw2()
  histBgSelected.Sumw2()
  histTotalSelected.Sumw2()

  # fill histograms with weights

  # beam
  beamNorm = 1./beamPot

  # ignore gas events in beam
  for entry in beamDefaultTree:
    if not getIsGas(entry):
      for i in range(binN):
        histBgTotal.Fill(i+1, beamNorm)
        if(i <= entry.accum_level[0]):
          histBgSelected.Fill(i+1, beamNorm)
          histTotalSelected.Fill(i+1, beamNorm)

  gasNorm = 1./gasPot

  # count non-signal events in gas
  for entry in gasDefaultTree:
    if getIsTrue(entry):
      for i in range(binN):
        histTrueTotal.Fill(i+1, gasNorm)
        if(i <= entry.accum_level[0]):
          histTrueSelected.Fill(i+1, gasNorm)
          histTotalSelected.Fill(i+1, gasNorm)
    else:
      for i in range(binN):
        histBgTotal.Fill(i+1, gasNorm)
        if(i <= entry.accum_level[0]):
          histBgSelected.Fill(i+1, gasNorm)
          histTotalSelected.Fill(i+1, gasNorm)

  # calculate efficiency and purity and signal selection and background rejection from histograms
  histEff = ROOT.TH1D("eff", "Efficiency and purity", binN,binLow,binUp)
  histPur = ROOT.TH1D("pur", "Efficiency and purity", binN,binLow,binUp)
  histSel = ROOT.TH1D("sel", "Signal selection", binN,binLow,binUp)
  histRej = ROOT.TH1D("rej", "Background rejection", binN,binLow,binUp)

  histEff.Add(histTrueSelected)
  histEff.Divide(histTrueTotal)

  histPur.Add(histTrueSelected)
  histPur.Divide(histTotalSelected)

  histSel.Add(histTrueSelected)
  histSel.Divide(histTrueTotal)

  histRej.Add(histBgTotal)
  histRej.Add(histBgSelected, -1.)
  histRej.Divide(histBgTotal)

  # set bin cutBins and errors vanishingly close to zero for now
  for i in range(len(cutBins)):
    #histEff.SetBinError(i+1, .000001)
    #histPur.SetBinError(i+1, .000001)
    #histSel.SetBinError(i+1, .000001)
    #histRej.SetBinError(i+1, .000001)

    histEff.GetXaxis().SetBinLabel(i+1, cutBins[i])
    histPur.GetXaxis().SetBinLabel(i+1, cutBins[i])
    histSel.GetXaxis().SetBinLabel(i+1, cutBins[i])
    histRej.GetXaxis().SetBinLabel(i+1, cutBins[i])

  # draw efficiency/purity plots
  myCanv = ROOT.TCanvas("myCanv","myCanv", 1000,800)
  myCanv.cd()

  histEff.SetMinimum(0.)
  histEff.SetMaximum(1.)
  histEff.SetLineColor(ROOT.kRed)
  histEff.SetMarkerColor(ROOT.kBlack)
  histEff.SetMarkerStyle(7)

  histPur.SetLineColor(ROOT.kBlue)
  histPur.SetMarkerColor(ROOT.kBlack)
  histPur.SetMarkerStyle(7)

  myLegend = ROOT.TLegend(0.15,0.75, 0.35,0.85)
  myLegend.AddEntry(histEff, "Efficiency", "LPE")
  myLegend.AddEntry(histPur, "Purity", "LPE")

  histEff.Draw("HIST L")
  histEff.Draw("E1 P0 SAME")
  histPur.Draw("HIST L SAME")
  histPur.Draw("E1 P0 SAME")

  myLegend.Draw()

  myCanv.SaveAs("{0}/effPur2.png".format(folder))

  # draw signal selection
  histSel.SetMinimum(0.)
  histSel.SetMaximum(1.)
  histSel.SetLineColor(ROOT.kBlue)
  histSel.SetMarkerColor(ROOT.kBlack)
  histSel.SetMarkerStyle(7)

  histSel.Draw("HIST L")
  histSel.Draw("E1 P0 SAME")

  myCanv.SaveAs("{0}/signalSelection.png".format(folder))

  # draw background rejection
  histRej.SetMinimum(0.)
  histRej.SetMaximum(1.)
  histRej.SetLineColor(ROOT.kBlue)
  histRej.SetMarkerColor(ROOT.kBlack)
  histRej.SetMarkerStyle(7)

  histRej.Draw("HIST L")
  histRej.Draw("E1 P0 SAME")

  myCanv.SaveAs("{0}/backgroundRejection.png".format(folder))

  # TODO: work out why efficiency goes up with s1s in place
  effFinal = histEff.GetBinContent( histEff.GetNbinsX() )
  print "Final signal efficiency: {0}%".format(effFinal*100.)
  rejFinal = histRej.GetBinContent( histRej.GetNbinsX() )
  print "Final background rejection: {0}%".format(rejFinal*100.)

  if args.checkVar:
    i = args.checkVarID
    if i < 0:
      i = len(cutBins) + i

      effBefore = histEff.GetBinContent(i)
      rejBefore = histRej.GetBinContent(i)
      effAfter = histEff.GetBinContent(i+1)
      rejAfter = histRej.GetBinContent(i+1)

      print "Signal efficiency before and after cut \"{0}\"".format(cutBins[i])
      print "   before: {0}%".format(effBefore*100.)
      print "   after : {0}%  ({1}% less signal)".format(effAfter*100., (effAfter/effBefore)*100.)
      print "Background rejection before and after cut \"{0}\"".format(cutBins[i])
      print "   before: {0}%".format(rejBefore*100.)
      print "   after : {0}%  ({1}% less background)".format(rejAfter*100., ((1.-rejAfter)/(1.-rejBefore))*100.)

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
  parser.add_argument("--s1s", action="store_true", help="Analyse stage one selection passed data sets")
  parser.add_argument("--drawingTools", action="store_true", help="Use default drawing tools methods for making plots")
  parser.add_argument("--plotFolder", type=str, help="Folder to put plots in", default="plots")

  parser.add_argument("--extraVars", type=str, nargs="+", help="Extra variables to plot", default=[])
  parser.add_argument("--extraVarsPos", type=int, help="Place to slot extra variables", default=-1)

  parser.add_argument("--checkVar", action="store_true", help="Check performance before and after specific var")
  parser.add_argument("--checkVarID", type=int, help="Position of variable to check performance at", default=-1)

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
