// (
// {
// 	o = Oderk4(\Hopf);
// 	o.inputs[5] = DC.ar(1.0);
// 	o.inputs[6] = DC.ar(440.0);
// }.plot
// )

s.quit;
s.waitForBoot{
 {Oderk4(\Hopf,DC.ar(1.0),DC.ar(440.0))}.play
}