(
~global_input_offset = 20;
~global_output_offset = 10;
~global_n_inputs = 4;

SynthDef.new(\Hopf,
	{|input_offset=0, output_offset=0|
		var osc;
		var inputs;
		inputs = ~global_n_inputs.collect({|in| In.ar(in+input_offset+~global_input_offset );});
		inputs.do({arg item,i; item.source.inputs.postln});
		osc = Oderk4.ar("Hopf",*inputs);
		OffsetOut.ar(output_offset+~global_output_offset , osc[0]);
		OffsetOut.ar(output_offset+1+~global_output_offset , osc[1]);
}).add;

SynthDef.new(\param,
	{| val=0, out=10|
		val.postln;
		Out.ar(out,DC.ar(1)*val);
}).add;


SynthDef.new(\connect,
	{| in=0, out=10|
		Out.ar(out,In.ar(in,1));
}).add;


SynthDef.new(\output,
	{|bus=10, amp=1|
		Out.ar(0,Splay.ar(In.ar(bus,1),1,amp));
}).add;
)

(
~ode1_input_offset = 0;
~x = Synth(\Hopf);
~px1 = Synth(\param);
~px2 = Synth(\param);
~px1.set(\val,0.5,\out,0+~global_input_offset );
~px2.set(\val,330,\out,1+~global_input_offset );
~out = Synth(\output,~global_output_offset,1,1);
)


(
~ode2_input_offset = ~ode1_input_offset+~global_n_inputs;
~ode2_output_offset = ~global_output_offset + 2;
~y = Synth(\Hopf,[\input_offset,~ode2_input_offset,\output_offset,~ode2_output_offset ]);
~py1 = Synth(\param);
~py2 = Synth(\param);
~c1 = Synth.after(~y,\connect);
~py1.set(\val,1.0,\out,~ode2_input_offset + ~global_input_offset );
~py2.set(\val,10,\out,~ode2_input_offset + 1 +~global_input_offset );
~c1.set(\in,~ode2_output_offset,\out,~ode1_input_offset+~global_input_offset )
)
