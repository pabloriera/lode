// (
// {
// 	o = Oderk4(\Hopf);
// 	o.inputs[5] = DC.ar(1.0);
// 	o.inputs[6] = DC.ar(440.0);
// }.plot
// )


Oderk4("Hopf",DC.ar(1.0),DC.ar(440.0)).channels

{Oderk4("Hopf",DC.ar(1.0),DC.ar(440.0))}.scope

{Oderk4("Lorenz",DC.ar(2.66),DC.ar(28),DC.ar(10),DC.ar(50))*0.1}.play

(
Ndef(\Lorenz_def, {

    var osc;
    var amp = \amp.kr(0);
    var beta = \beta.ar(2.6666);
    var rho = \rho.ar(28);
    var sigma = \sigma.ar(10);
    var tau = \tau.ar(50.0);

    osc = Oderk4("Lorenz", beta, rho, sigma, tau )*amp;
	[osc[0],osc[1],osc[2]]
});
Ndef(\Lorenz_def).gui

)


(
Ndef(\Hopf_def, {

    var osc;
    var amp = \amp.kr(0);
    var e = \e.ar(1.0);
    var w = \w.ar(440);

    osc = Oderk4("Hopf", e, w )*amp;
    osc
});

Ndef(\Hopf_def).gui;
)

p = ProxySpace.push(s.boot);
~out = {Oderk4("Hopf",DC.ar(1.0), ~freq.ar)};
~freq = {DC.ar(180.0)}


l = "hopf"
l.asString.collectAs(_.ascii, Array)