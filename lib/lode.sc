(
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

	SynthDef.new(\param,
		{| val=0, out=10|
			val.postln;
			Out.ar(out,DC.ar(1)*Lag.kr(val));
	}).add;

	SynthDef.new(\output,
		{|bus=10, amp=1, pan=0|
			Out.ar(0,Pan2.ar(In.ar(bus,1)*(amp**4),pan));
	}).add;

};


)

