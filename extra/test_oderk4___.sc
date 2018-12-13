(
~busses = ~busses ?? {
	~matrix_in_count = 8;
	~matrix_out_count = 8;
	~matrix_ins = ~matrix_in_count.collect({ arg idx;
		var bus = Bus.audio(s,1);
		Ndef(\matrix).set(( \in++idx ).asSymbol, bus);
		bus;
	});
	~matrix_outs = ~matrix_out_count.collect({ arg idx;
		var bus = Bus.audio(s,1);
		Ndef(\matrix).set(( \out++idx ).asSymbol, bus);
		bus;
	});
};
)

(
SynthDef.new(\mod,
	{|depth=100, freq=1,offset=0|
		var osc = SinOsc.ar(freq,0,depth,offset);
		Out.ar(~matrix_outs[0].index, osc);
}).add
)

(
SynthDef.new(\Hopf,
	{|e=1, freq=440|
		var osc;
		var input1 = In.ar(~matrix_outs[0]);
		osc = Oderk4.ar("Hopf",DC.ar(1)*e,freq+input1);

		Out.ar(~matrix_outs[1].index, osc[0]);
		Out.ar(~matrix_outs[2].index, osc[1]);
}).add
)

s.sendMsg("/s_new", "Hopf", 123);
s.sendMsg("/s_new", "mod", 124);
s.sendMsg("/n_set", n, "freq", 500);
s.sendMsg("/n_free", 123);
s.sendMsg("/n_free", 124);

Out.ar(0,~matrix_outs[1])

~matrix_outs[0].ar()

{~matrix_outs[1].ar()}.play

~matrix_outs[1]

a = ~matrix_outs[0]

{SinOsc.ar(440)}.play

