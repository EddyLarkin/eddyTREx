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

DET_ALL = { DET_TPC:0, DET_FGD:1, DET_P0D:2, DET_ECAL:3, DET_SMRD:4, DET_OTHER:5 }
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

def main(args):
  geomFile = ROOT.TFile.Open(args.geomFile)
  geomTree = geomFile.Get("HeaderDir/GeometrySummary")

  # fill limits for each detector
  detLimits = getLimits(args, geomTree)

  microTreeFile = ROOT.TFile.Open(args.microTreeFile)
  defTree = microTreeFile.Get("default")
  for entry in defTree:
    if entry.accum_level[0] > 12.5:
      vertexTruePos = (entry.Vertex_true_pos[0], entry.Vertex_true_pos[1], entry.Vertex_true_pos[2])
      print getDetector(detLimits, vertexTruePos)

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


def checkArguments():
  parser = argparse.ArgumentParser(description="Produce plots showing where OOFV background is coming from")
  parser.add_argument("--geomFile", type=str, help="Analysis file for extracting geometry information", default="/data/eddy/t2k/nd280/production006/B/mcp/neut/2010-11-air/magnet/run4/trexanal/oa_nt_beam_90400000-0000_jrvqsli66bf2_trexanal_000_prod6amagnet201011airc.root")
  parser.add_argument("--microTreeFile", type=str, help="Highland micro tree for reading OOFV background", default="/home/eddy/t2k/workspaces/highlandGasInteractions/highland2/eddyTREx/run/highStatsBeam.root")
  parser.add_argument("--oaAnalysisLibs", type=str, help="Libraries to use for reading oaAnalysis files", default="/home/eddy/t2k/workspaces/highlandGasInteractions/nd280AnalysisTools/v1r10/Linux-x86_64/AnalysisTools/libReadoaAnalysis/libReadoaAnalysis.so")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)

