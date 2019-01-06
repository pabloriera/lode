(
s.quit;
s.waitForBoot{
	OSCFunc(
		{
			arg msg, time, addr, port;
			var fn;
			// Get local filename
			fn = msg[1].asString;
			// Print a message to the user
			("Loading SynthDef from" + fn).postln;
			// Add SynthDef to file
			fn = File(fn, "r");
			fn.readAllString.interpret;
			fn.close;
		},
		'/lode'
	);

	SynthDef.new(\connection,
		{| from=0, to=0, mul=1,add = 0 del=0|
			Out.ar(to,DelayL.ar(InFeedback.ar(from,1)*mul+add,1.0,del));
	}).add;

	SynthDef.new(\parameter,
		{| val=0, bus=10|
			Out.ar(bus,DC.ar(1)*VarLag.kr(val,0.5));
	}).add;

	SynthDef.new(\input,
		{| mul=1, add=0, bus=10|
			var mul_ = VarLag.kr(mul,0.5);
			var add_ = VarLag.kr(add,0.5);
			var input = Noise.ar(mul_,add_);
			Out.ar(bus,input);
	}).add;

	SynthDef.new(\output,
		{|bus=10, amp=0, pan=0|
			Out.ar(0,Pan2.ar(LeakDC.ar(In.ar(bus,1)*(VarLag.kr(amp/2.0,0.5)**4)),pan));
	}).add;

};

)

{SinOsc.ar}.play

~c2 = Synth(\connect,target: 1011);
~c2.set(\from,10,\to,41,\add,0,\mul,100.0,\del,0.01);
~c2.free
//
// ~c2 = Synth(\connect,target: 1011);
// ~c2.set(\from,12,\to,44,\add,0,\mul,5.0);
// ~c2.free

{Odemap.ar("Map",1)}.play
