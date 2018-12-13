(
~global_input_offset = 20;
~global_output_offset = 10;
~global_n_inputs = 4;

SynthDef.new(\Hopf,
	{|input_offset=0, output_offset=0|
		var osc;
		var inputs;
		inputs = ~global_n_inputs.collect({|in| InFeedback.ar(in+input_offset+~global_input_offset );});
		inputs.do({arg item,i; item.source.inputs.postln});
		osc = Oderk4.ar("Hopf",*inputs);
		OffsetOut.ar(output_offset+~global_output_offset , osc[0]);
		OffsetOut.ar(output_offset+1+~global_output_offset , osc[1]);
}).add;

SynthDef.new(\param,
	{| val=0, out=10|
		val.postln;
		Out.ar(out+~global_input_offset,DC.ar(1)*val);
}).add;


SynthDef.new(\connect,
	{| from=0, to=0, mul=1,add = 0|
		Out.ar(to+~global_input_offset,InFeedback.ar(from+~global_output_offset,1)*mul+add);
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
~px1.set(\val,0.5,\out,~ode1_input_offset+0);
~px2.set(\val,330,\out,~ode1_input_offset+1);
~out = Synth(\output,~global_output_offset,1,1);


~c2 = Synth.before(~x,\connect);
~c2.set(\from,~ode1_output_offset,\to,~ode2_input_offset+1,\add,50);


~ode2_input_offset = ~ode1_input_offset+~global_n_inputs;
~ode2_output_offset = 2;
~y = Synth.after(~x,\Hopf,[\input_offset,~ode2_input_offset,\output_offset,~ode2_output_offset  ]);
~py1 = Synth(\param);
~py2 = Synth(\param);
~py1.set(\val,1.0,\out,~ode2_input_offset);
~py2.set(\val,1,\out,~ode2_input_offset + 1);

~c1 = Synth.before(~y,\connect);
// ~c1.set(\from,~ode2_output_offset,\to,~ode1_input_offset);
~c1.set(\from,~ode2_output_offset,\to,~ode1_input_offset+1,\mul,50);

)

