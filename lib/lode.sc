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

	SynthDef.new(\connect,
		{| from=0, to=0, mul=1,add = 0|
			Out.ar(to,InFeedback.ar(from,1)*mul+add);
	}).add;

	SynthDef.new(\param,
		{| val=0, bus=10|
			Out.ar(bus,DC.ar(1)*VarLag.kr(val,0.5));
	}).add;

	SynthDef.new(\output,
		{|bus=10, amp=1, pan=0|
			Out.ar(0,Pan2.ar(LeakDC.ar(In.ar(bus,1)*(VarLag.kr(amp,0.5)**4)),pan));
	}).add;

};

)

~c2 = Synth(\connect,target: 1011);
~c2.set(\from,12,\to,44,\add,0,\mul,5.0);
~c2.free