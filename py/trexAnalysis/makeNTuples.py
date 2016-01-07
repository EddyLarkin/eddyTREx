# python
import argparse
import subprocess

# eddy
import trexAnalysis.parameters

def main(args):
  beamList = ""
  gasList = ""
  beamOut = ""
  gasOut = ""

  if args.full:
    beamList = trexAnalysis.parameters.Lists.neutBeam
    gasList = trexAnalysis.parameters.Lists.neutGas
    beamOut = trexAnalysis.parameters.NTuples.neutBeam
    gasOut = trexAnalysis.parameters.NTuples.neutGas
  else:
    beamList = trexAnalysis.parameters.Lists.reducedNeutBeam
    gasList = trexAnalysis.parameters.Lists.reducedNeutGas
    beamOut = trexAnalysis.parameters.NTuples.reducedNeutBeam
    gasOut = trexAnalysis.parameters.NTuples.reducedNeutGas

  if len(args.filesID):
    beamList = "{0}/{1}Beam.list".format(trexAnalysis.parameters.Dirs.lists, args.filesID)
    gasList = "{0}/{1}Gas.list".format(trexAnalysis.parameters.Dirs.lists, args.filesID)

  if not args.gasOnly:
    subprocess.call(["rm", "-f", beamOut])
    subprocess.call(["RunTRExAnalysis.exe", "-v", "-o", beamOut, beamList])
  if not args.beamOnly:
    subprocess.call(["rm", "-f", gasOut])
    subprocess.call(["RunTRExAnalysis.exe", "-v", "-o", gasOut, gasList])

def checkArguments():
  parser = argparse.ArgumentParser(description="Produce ntuples for gas and beam")
  parser.add_argument("--full", action="store_true", help="Analyse full available data sets (default is reduced)")
  parser.add_argument("--gasOnly", action="store_true", help="Process only gas MC")
  parser.add_argument("--beamOnly", action="store_true", help="Process only beam MC")
  parser.add_argument("--oldTREx", action="store_true", help="Use older version of TREx software")

  parser.add_argument("--filesID", type=str, help="Identifier for files to run over", default="")

  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
