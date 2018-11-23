//Basic example to play with faders
(
Ndef(\Lorenz_def, {

    var osc;
	var beta = \beta.ar(2.6666)+In.ar(10);
    var rho = \rho.ar(28);
    var sigma = \sigma.ar(10);
    var tau = \tau.ar(50.0);

    osc = Oderk4.ar("Lorenz", beta, rho, sigma, tau )*0.5;
	[osc[0],osc[1],osc[2]]
});
g = NdefGui(Ndef(\Lorenz_def));
g.edits.do({arg x; x.slider.controlSpec.warp = 'lin'});
)


(
Ndef(\Hopf_def, {

    var osc;
    var e = \e.ar(1.0);
    var w = \w.ar(440);
    osc = Oderk4.ar("Hopf", e, w );
	[osc[0],osc[1]]
});

