# python
import os
import subprocess

# useful misc commands
def potFromListFile(inFile, perFile=1.):
  catOut = subprocess.Popen(["cat", inFile], stdout=subprocess.PIPE)
  wcOut = subprocess.check_output(["wc", "-l"], stdin=catOut.stdout)

  return perFile * float(wcOut)

class Dirs:
  # root path to files
  laptopRoot = "/home/eddy/t2k/workspaces/highlandGasInteractions/highland2/eddyTREx"
  laptopID = "eddyLaptop"

  #TODO set up to work on other machines
  root = laptopRoot
  defID = laptopID

  if(os.path.isdir(laptopRoot)):
    root = laptopRoot
  else:
    root = ""

  # default directories
  lists = "{0}/lists/{1}".format(root, defID)
  data = "{0}/data".format(root)
  run = "{0}/run".format(root)

# lists of files
class Lists:
  neutBeam = "{0}/neutBeam.list".format(Dirs.lists)
  neutGas = "{0}/neutGas.list".format(Dirs.lists)
  reducedNeutBeam = "{0}/reducedNeutBeam.list".format(Dirs.lists)
  reducedNeutGas = "{0}/reducedNeutGas.list".format(Dirs.lists)

# relative weighting of files
class Pots:
  potCurrentFHC = 6914 # x10^17 all data so far
  potCurrentRHC = 4011 # x10^17 all data so far
  potCurrent = potCurrentFHC
  potPerFileBeam = 5.   # x10^17
  potPerFileGas = 500.  # x10^17
  listNeutBeam = potFromListFile(Lists.neutBeam, potPerFileBeam)
  listNeutGas = potFromListFile(Lists.neutGas, potPerFileGas)
  listReducedNeutBeam = potFromListFile(Lists.reducedNeutBeam, potPerFileBeam)
  listReducedNeutGas = potFromListFile(Lists.reducedNeutGas, potPerFileGas)

# sample ntuples
class NTuples:
  neutBeam = "{0}/neutBeam.root".format(Dirs.data)
  neutGas = "{0}/neutGas.root".format(Dirs.data)
  reducedNeutBeam = "{0}/reducedNeutBeam.root".format(Dirs.data)
  reducedNeutGas = "{0}/reducedNeutGas.root".format(Dirs.data)
