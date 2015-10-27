{
  gROOT.SetBatch(true);

  // reduced lists
  DataSample mcBeam("reducedOutBeam.root", (5.*2.));    // 5.0E17 POT / file over 2 files
  DataSample mcGas("reducedOutGas.root", (500.*60.));   //5.0E19 POT / file over 60 files

  // add the different sample groups
  Experiment exp("nd280");
  SampleGroup combinedMC("combined");

  combinedMC.AddMCSample("mcBeam", &mcBeam);
  combinedMC.AddMCSample("mcGas", &mcGas);

  exp.AddSampleGroup("combined", combinedMC);

  // draw
  DrawingTools drawer("reducedOutBeam.root");

  drawer.DrawEffPurVSCut(exp, "target==18", "", -1,-1, "");
  c1->SaveAs("effVsPurCombined.png");

  drawer.DrawEffPurVSCut(mcBeam, "target==18");
  c1->SaveAs("effVsPurBeam.png");

  drawer.DrawEffPurVSCut(mcGas, "target==18");
  c1->SaveAs("effVsPurGas.png");
}
