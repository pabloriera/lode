// (
// {
// 	o = Oderk4(\Hopf);
// 	o.inputs[5] = DC.ar(1.0);
// 	o.inputs[6] = DC.ar(440.0);
// }.plot
// )

(
SynthDef.new(\mod,
	{|e=1, freq=440|
		var osc = SinOsc.ar(10,0,100,440);
		OffsetOut.ar(20, osc);
}).add
)

(
SynthDef.new(\Hopf,
	{| e=1.0, w=440.0, amp=1 |
		var osc;

		osc = Oderk4.ar("Hopf", DC.ar(1)*e, DC.ar(1)*w )*amp;
		// [osc[0],osc[1]]
		OffsetOut.ar(0,osc[0]);
		OffsetOut.ar(1,osc[1]);
}).add;
)

(
SynthDef.new(\Hopf,
	{|e=1, freq=440|
		var osc;
		var inputs;
		inputs = 10.collect({|in| In.ar(in+10);});
		osc = Oderk4.ar("Hopf",*inputs);
		OffsetOut.ar(0, osc[0]);
		OffsetOut.ar(1, osc[1]);
}).add
)

{Out.ar(0,In.ar(10))}.play

{Out.ar(10,DC.ar(1))}.play
{Out.ar(11,DC.ar(440))}.play


n = s.nextNodeID;
s.sendMsg("/s_new", "Hopf", n);

s.sendMsg("/n_set", n, "amp", 0.2);
s.sendMsg("/n_free", 1000);

(
Ndef(\Hopf_def, {

	var osc;
	var x;
	var e = \e.kr(1);
	x = SinOsc.ar(10,0,100,440);
	osc = Oderk4.ar("Hopf",DC.ar(1)*e,x);
	[osc[0],osc[1]];
});
)

n = s.nextNodeID;
s.sendMsg("/s_new", "Hopf_def", n);



{Oderk4.ar("Hopf",DC.ar(1.0),DC.ar(440.0))}.play


{Oderk4("Lorenz",DC.ar(2.66),DC.ar(28),DC.ar(10),DC.ar(50))*0.1}.play

(
Ndef(\Lorenz_def, {

    var osc;
    var beta = \beta.ar(2.6666);
    var rho = \rho.ar(28);
    var sigma = \sigma.ar(10);
    var tau = \tau.ar(50.0);

    osc = Oderk4.ar("Lorenz", beta, rho, sigma, tau );
	[osc[0],osc[1],osc[2]]
});
g = NdefGui(Ndef(\Lorenz_def));
g.edits.do({arg x; x.slider.controlSpec.warp = 'lin'});
)




(
Ndef(\Hopf_def, {

    var osc;
    var amp = \amp.kr(0);
    var e = \e.ar(1.0);
    var w = \w.ar(440);

    osc = Oderk4.ar("Hopf", e, w )*amp;
    osc
});

Ndef(\Hopf_def).gui;
)

p = ProxySpace.push(s.boot);
~out = {Oderk4("Hopf",DC.ar(1.0), ~freq.ar)};
~freq = {DC.ar(180.0)}


l = "hopf"
l.asString.collectAs(_.ascii, Array)