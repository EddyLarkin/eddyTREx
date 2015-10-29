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

  if args.oldTREx:
    beamList = trexAnalysis.parameters.Lists.oldReducedNeutBeam
    gasList = trexAnalysis.parameters.Lists.oldReducedNeutGas
    beamOut = trexAnalysis.parameters.NTuples.reducedNeutBeam
    gasOut = trexAnalysis.parameters.NTuples.reducedNeutGas
  elif args.s1s:
    if args.full:
      beamList = trexAnalysis.parameters.Lists.s1sNeutBeam
      gasList = trexAnalysis.parameters.Lists.s1sNeutGas
      beamOut = trexAnalysis.parameters.NTuples.s1sNeutBeam
      gasOut = trexAnalysis.parameters.NTuples.s1sNeutGas
    else:
      beamList = trexAnalysis.parameters.Lists.s1sReducedNeutBeam
      gasList = trexAnalysis.parameters.Lists.s1sReducedNeutGas
      beamOut = trexAnalysis.parameters.NTuples.s1sReducedNeutBeam
      gasOut = trexAnalysis.parameters.NTuples.s1sReducedNeutGas
  else:
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
  parser.add_argument("--s1s", action="store_true", help="Use files produced with stage 1 selection")
  parser.add_argument("--oldTREx", action="store_true", help="Use older version of TREx software")
  return parser.parse_args()

if __name__ == "__main__":
  args = checkArguments()
  main(args)
