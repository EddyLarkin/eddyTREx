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
  laptopRoot = "/home/eddy/t2k/workspaces/highlandGasInteractions/eddyTREx"
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
  s1sNeutBeam = "{0}/s1sNeutBeam.list".format(Dirs.lists)
  s1sNeutGas = "{0}/s1sNeutGas.list".format(Dirs.lists)
  s1sReducedNeutBeam = "{0}/s1sReducedNeutBeam.list".format(Dirs.lists)
  s1sReducedNeutGas = "{0}/s1sReducedNeutGas.list".format(Dirs.lists)

# relative weighting of files
class Pots:
  potPerFileBeam = 5.   # x10^17
  potPerFileGas = 500.  # x10^17
  listNeutBeam = potFromListFile(Lists.neutBeam, potPerFileBeam)
  listNeutGas = potFromListFile(Lists.neutGas, potPerFileGas)
  listReducedNeutBeam = potFromListFile(Lists.reducedNeutBeam, potPerFileBeam)
  listReducedNeutGas = potFromListFile(Lists.reducedNeutGas, potPerFileGas)
  listS1SNeutBeam = potFromListFile(Lists.s1sNeutBeam, potPerFileBeam)
  listS1SNeutGas = potFromListFile(Lists.s1sNeutGas, potPerFileGas)
  listS1SReducedNeutBeam = potFromListFile(Lists.s1sReducedNeutBeam, potPerFileBeam)
  listS1SReducedNeutGas = potFromListFile(Lists.s1sReducedNeutGas, potPerFileGas)

# sample ntuples
class NTuples:
  neutBeam = "{0}/neutBeam.root".format(Dirs.data)
  neutGas = "{0}/neutGas.root".format(Dirs.data)
  reducedNeutBeam = "{0}/reducedNeutBeam.root".format(Dirs.data)
  reducedNeutGas = "{0}/reducedNeutGas.root".format(Dirs.data)
  s1sNeutBeam = "{0}/s1sNeutBeam.root".format(Dirs.data)
  s1sNeutGas = "{0}/s1sNeutGas.root".format(Dirs.data)
  s1sReducedNeutBeam = "{0}/s1sReducedNeutBeam.root".format(Dirs.data)
  s1sReducedNeutGas = "{0}/s1sReducedNeutGas.root".format(Dirs.data)
