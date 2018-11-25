(
SynthDef.new(\Hopf,
	{|input_offset=10, output_offset=10|
		var osc;
		var inputs;
		inputs = 10.collect({|in| In.ar(in+input_offset+64);});
		inputs.do({arg item,i; item.source.inputs.postln});
		osc = Oderk4.ar("Hopf",*inputs);
		OffsetOut.ar(output_offset, osc[0]);
		OffsetOut.ar(output_offset+1, osc[1]);
}).add;

SynthDef.new(\param,
	{| val=0, out=10|
		val.postln;
		Out.ar(out,DC.ar(1)*val);
}).add;


SynthDef.new(\connect,
	{| in=0, out=10|
		Out.ar(out,In.ar(in));
}).add;


SynthDef.new(\output,
	{|bus=10, amp=1|
		Out.ar(0,Splay.ar(In.ar(bus,1),1,amp));
}).add;
)

(
~x = Synth(\Hopf);
~px1 = Synth(\param);
~px2 = Synth(\param);
~px1.set(\val,0.1,\out,10+64);
~px2.set(\val,330,\out,11+64);
~out = Synth(\output,10,1,1);
)

(
~y = Synth(\Hopf,[\input_offset,12,\output_offset,12]);
~py1 = Synth(\param);
~py2 = Synth(\param);
~c1 = Synth(\connect);
~py1.set(\val,0.1,\out,12+64);
~py2.set(\val,10,\out,13+64);
~c1.set(12+64,11)
)

