# python
import argparse

# ROOT
import ROOT

# big lists of detector branches to check
DET_TPC = "TPC"
DET_FGD = "FGD"
DET_P0D = "P0D"
DET_ECAL = "ECal"
DET_SMRD = "SMRD"
DET_OTHER = "other"

DET_BRANCHES = {
                 DET_TPC:(
                               "TPC1Extent",
                               "TPC2Extent",
                               "TPC3Extent"
                                             ),
                 DET_FGD:(
                               "FGD1Extent",
                               "FGD2Extent"
                                             ),
                 DET_P0D:(
                               "P0DExtent",
                                            ),
                 DET_ECAL:(
                               "TECAL1Extent",
                               "TECAL2Extent",
                               "TECAL3Extent",
                               "TECAL4Extent",
                               "TECAL5Extent",
                               "TECAL6Extent",
                               "DSECALExtent",
                               "PECAL1Extent",
                               "PECAL2Extent",
                               "PECAL3Extent",
                               "PECAL4Extent",
                               "PECAL5Extent",
                               "PECAL6Extent"
                                               ),
                 DET_SMRD:(
                               "SMRD1Extent",
                               "SMRD2Extent",
                               "SMRD3Extent",
                               "SMRD4Extent"
                                              ),
                 DET_OTHER:()
                                                  }

DET_TPC_FV = "TPC FV"
DET_TPC_FV_RANGE =  (
                      (
                        (    20., 1150.),
                        ( -1170., 1170.),
                        (  -885.,   89.)
                                          ),
                      (
                        (    20., 1150.),
                        ( -1170., 1170.),
                        (   474., 1448.)
                                          ),
                      (
                        (    20., 1150.),
                        ( -1170., 1170.),
                        (  1833., 2807.)
                                          )
                                            )


def main(args):
  # change ROOT plotting options
  ROOT.gROOT.SetBatch(1)
  ROOT.gStyle.SetOptStat(0)

  # get geometry
  geomFile = ROOT.TFile.Open(args.geomFile)
  geomTree = geomFile.Get("HeaderDir/GeometrySummary")

  # fill limits for each detector
  detLimits = getLimits(args, geomTree)

  microTreeFile = ROOT.TFile.Open(args.microTreeFile)
  defTree = microTreeFile.Get("default")

  # set up plot for all OOFV sources
  histCanv = ROOT.TCanvas("histCanv", "oofvSources", 1200,800)
  histOOFV = ROOT.TH1F("histOOFV", "oofvSources", 6,-.5,5.5)
  histOOFV.GetXaxis().SetBinLabel(1, "FGD")
  histOOFV.GetXaxis().SetBinLabel(2, "P0D")
  histOOFV.GetXaxis().SetBinLabel(3, "ECal")
  histOOFV.GetXaxis().SetBinLabel(4, "TPC OOFV")
  histOOFV.GetXaxis().SetBinLabel(5, "Other")
  histOOFV.GetXaxis().SetBinLabel(6, "TPC FV")
  histOOFV.SetLineWidth(2)

  for entry in defTree:
    if entry.accum_level[0] > 12.5:
      vertexTruePos = (entry.Vertex_true_pos[0], entry.Vertex_true_pos[1], entry.Vertex_true_pos[2])

      detName = getDetector(detLimits, vertexTruePos)
      inTPCFV = getInTPCFV(vertexTruePos)

      if detName == DET_FGD:
        histOOFV.Fill(0.)
      elif detName == DET_P0D:
        histOOFV.Fill(1.)
      elif detName == DET_ECAL:
        histOOFV.Fill(2.)
      elif detName == DET_TPC:
        if inTPCFV:
          histOOFV.Fill(5.)
        else:
          histOOFV.Fill(3.)
      else:
        histOOFV.Fill(4.)

  histCanv.cd()
  histOOFV.Draw("HIST E0")

  histCanv.SaveAs("{0}.png".format(args.outName))
  histCanv.SaveAs("{0}.eps".format(args.outName))

def getLimits(args, inTree):
  # load ROOT libraries
  ROOT.gSystem.Load("libCint.so")
  ROOT.gSystem.Load(args.oaAnalysisLibs)

  # build dictionary of detector extents
  detExtents = {
                 DET_TPC:[],
                 DET_FGD:[],
                 DET_P0D:[],
                 DET_ECAL:[],
                 DET_SMRD:[],
                 DET_OTHER:[]
                              }

  for entry in inTree:
    for det, branchNames in DET_BRANCHES.iteritems():
      for branchName in branchNames:
        extentObj = getattr(entry, branchName)
        extentVals = (
                       (extentObj.Minimum.X(), extentObj.Maximum.X()),
                       (extentObj.Minimum.Y(), extentObj.Maximum.Y()),
                       (extentObj.Minimum.Z(), extentObj.Maximum.Z())
                                                                          )
        detExtents[det].append(extentVals)
    break

  return detExtents

def getDetector(limits, pos):
  detector = DET_OTHER

  for det, extentValss in limits.iteritems():
    for extentVals in extentValss:
      inRange = True

      inRange &= (pos[0] >= extentVals[0][0])
      inRange &= (pos[0] <= extentVals[0][1])
      inRange &= (pos[1] >= extentVals[1][0])
      inRange &= (pos[1] <= extentVals[1][1])
      inRange &= (pos[2] >= extentVals[2][0])
      inRange &= (pos[2] <= extentVals[2][1])

      if inRange:
        detector = det
        break

    if detector != DET_OTHER:
      break

  return detector

def getInTPCFV(pos):
  inFV = False

  for tpcRange in DET_TPC_FV_RANGE:
    inRange = True

    inRange &= (abs(pos[0]) >= tpcRange[0][0])
    inRange &= (abs(pos[0]) <= tpcRange[0][1])
    inRange &= (pos[1] >= tpcRange[1][0])
    inRange &= (pos[1] <= tpcRange[1][1])
    inRange &= (pos[2] >= tpcRange[2][0])
    inRange &= (pos[2] <= tpcRange[2][1])

    if(inRange):
      inFV = True
      break

  return inFV


def checkArguments():
  parser = argparse.ArgumentParser(description="Produce plots showing where OOFV background is coming from")
  parser.add_argument("--geomFile", type=str, help="Analysis file for extracting geometry information", default="/data/eddy/t2k/nd280/production006/B/mcp/neut/2010-11-air/magnet/run4/trexanal/oa_nt_beam_90400000-0000_jrvqsli66bf2_trexanal_000_prod6amagnet201011airc.root")
  parser.add_argument("--microTreeFile", type=str, help="Highland micro tree for reading OOFV background", default="/home/eddy/t2k/workspaces/highlandGasInteractions/highland2/eddyTREx/run/highStatsBeam.root")
  parser.add_argument("--oaAnalysisLibs", type=str, help="Libraries to use for reading oaAnalysis files", default="/home/eddy/t2k/workspaces/highlandGasInteractions/nd280AnalysisTools/v1r10/Linux-x86_64/AnalysisTools/libReadoaAnalysis/libReadoaAnalysis.so")
  parser.add_argument("--outName", type=str, help="Name to save for output histograms", default="oofvSources")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)

