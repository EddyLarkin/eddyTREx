# python
import argparse
import subprocess
import array

# ROOT
import ROOT

WEIGHT_SYSTS = ( "t0 efficiency",
                 "Hairy muon efficiency" )
WEIGHT_TREES = ( "kTREx_tpct0eff_syst",
                 "kTREx_hairytrackmuoneff_syst" )

def main(args):
  ROOT.gStyle.SetOptStat(0)
  ROOT.gROOT.SetBatch(1)

  if args.allWeights:
    for systName, treeName in zip(WEIGHT_SYSTS, WEIGHT_TREES):
      makeWeightsPlot(args, systName, treeName)
  elif args.allVariations:
    None

def makeWeightsPlot(args, systName, treeName):
  systNameNW = systName.replace(" ", "-")

  inTFile = ROOT.TFile.Open(args.inFile)
  inTTree = inTFile.Get(treeName)

  weightHist = ROOT.TH1D(systNameNW, systName, 100,.4,1.6)

  for entry in inTTree:
    nToys = entry.NTOYS
    nWeights = entry.NWEIGHTS

    weightBuff = entry.weight_syst_total
    weightBuff.SetSize(nToys)
    for weight in list(weightBuff):
      weightHist.Fill(weight)

  myCanv = ROOT.TCanvas("{0}_canv".format(systNameNW), systName, 1200,800)
  myCanv.cd()

  weightHist.Draw("HIST")

  subprocess.call(["mkdir", "-p", args.plotFolder])
  myCanv.SaveAs( "{0}/weight_{1}.png".format(args.plotFolder, systNameNW) )


def checkArguments():
  parser = argparse.ArgumentParser(description="Produce plots for gas and beam")
  parser.add_argument("--plotFolder", type=str, help="Folder to put plots in", default="syst_diagnostics")
  parser.add_argument("--inFile", type=str, help="Input file to read", default="testTRExAnalysis.root")
  parser.add_argument("--allWeights", action="store_true", help="Analyse all available weight systematics")
  parser.add_argument("--allVariations", action="store_true", help="Analyse all available variation systematics")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
