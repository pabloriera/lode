(
s.quit;
s.waitForBoot{

	var scope_n = 6;
	var scope_i = 2;
	var scope_j = 3;
	var scope_widht = 240;
	var scope_height = 240;

	f = Array.fill(scope_n,{arg i; Buffer.alloc(s,4096*2,2)});
	// f.do({arg f_; f_.bufnum.postln});
	w=Window("Scope", Rect(10, Window.screenBounds.height-10,scope_widht*scope_j,scope_height*scope_i)).front;

	r = Array.fill(scope_n,{arg i;
		r = Rect((i%scope_j)*scope_widht,(i/scope_j).asInt*scope_height,scope_widht,scope_height);
		r;
	});
	c = Array.fill(scope_n,
		{arg i;
			c = ScopeView(w,r[i]);
			c.bufnum = f[i].bufnum;
			c.server_(s);
			c.style=2;
			c.xZoom = 0.5;
			c.yZoom = 0.5;
			c.start;
			c;
	});

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

	OSCFunc(
		{
			arg msg, time, addr, port;
			var fn;
			// Get local filename
			fn = msg[1].asString;
			fn.postln;
			fn.interpret;
		},
		'/lode/interpret'
	);

	SynthDef.new(\value,
		{| val=0, bus=10, lag=0.1, arg1=0|
			Out.ar(bus,DC.ar(1)*VarLag.kr(val+arg1,lag));
	}).add;

	SynthDef.new(\output,
		{|bus=10, amp=0, pan=0, lag=0.1|
			var amp_ = VarLag.kr(amp,lag)/2.0;
			Out.ar(0,Pan2.ar(LeakDC.ar(In.ar(bus,1)*(amp_**4)),pan));

	}).add;

	SynthDef.new(\scope,
		{|bufnum=0, busx=0, busy=0, maxFrames=8192, scopeFrames=4096|
			var x = [In.ar(busx), In.ar(busy)];
			ScopeOut2.ar( x, bufnum, maxFrames, scopeFrames);
	}).add;

	SynthDef.new(\connection,
		{| from=0, to=0, mul=1,add = 0, lag= 0.1, arg1=0|
			var mul_ = VarLag.kr(mul,lag);
			var add_ = VarLag.kr(add,lag);
			var arg1_ = VarLag.kr(arg1,lag);
			Out.ar(to,DelayC.ar(InFeedback.ar(from,1)*mul_+add_,1.0,arg1_));
	}).add;

	SynthDef.new(\noise,
		{|mul=1, add=0, bus=10, lag=0.1, arg1=6000|
			var freq_ = VarLag.kr(arg1,lag);
			var mul_ = VarLag.kr(mul,lag);
			var add_ = VarLag.kr(add,lag);
			var arg1_ = VarLag.kr(arg1,lag);
			Out.ar(bus,LPF.ar(WhiteNoise.ar,arg1_, mul_,add_));
	}).add;


	SynthDef.new(\sine,
		{| mul=1, add=0, bus=10, lag=0.1, arg1=0|
			var mul_ = VarLag.kr(mul,lag);
			var add_ = VarLag.kr(add,lag);
			var arg1_ = VarLag.kr(arg1,lag);
			Out.ar(bus,SinOsc.ar(freq:arg1_, mul:mul_, add:add_));
	}).add;

	SynthDef.new(\sine1,
		{| mul=1, add=0, bus=10, lag=0.1, arg1=0|
			var mul_ = VarLag.kr(mul,lag);
			var add_ = VarLag.kr(add,lag);
			var arg1_ = VarLag.kr(arg1,lag);
			Out.ar(bus,SinOsc.ar(freq:arg1_, mul:0.5, add:0.5)*mul_+add_);
	}).add;

};

// MIDIClient.init(1,1);
// MIDIIn.connectAll;
)
