(
s.quit;
// configure the sound server: here you could add hardware specific options
// see http://doc.sccode.org/Classes/ServerOptions.html
s.options.numBuffers = 1024 * 16; // increase this if you need to load more samples
s.options.memSize = 8192 * 16; // increase this if you get "alloc failed" messages
s.options.maxNodes = 1024 * 32; // increase this if you are getting drop outs and the message "too many nodes"
s.options.numOutputBusChannels = 2; // set this to your hardware output channel size, if necessary
s.options.numInputBusChannels = 2; // set this to your hardware output channel size, if

s.waitForBoot {


	var scope_n = 6;
	var scope_i = 2;
	var scope_j = 3;
	var scope_widht = 1920/scope_j;
	var scope_height = 1220/scope_i;

	f = Array.fill(scope_n,{arg i; Buffer.alloc(s,4096*8,2)});
	w = Window("Scope", Rect(10, Window.screenBounds.height-10,scope_widht*scope_j,scope_height*scope_i)).front;

	c = Array.fill(scope_n,
		{arg i;
			r = Rect((i%scope_j)*scope_widht,(i/scope_j).asInt*scope_height,scope_widht,scope_height);
			c = ScopeView(w,r);
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
			var fn = msg[1].asString;
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
			var amp_ = VarLag.kr(amp,lag);
			var z = In.ar(bus,1);
			var s = Compander.ar(z, z,
				thresh: 0.9,
				slopeBelow: 1,
				slopeAbove: 0.5,
				clampTime:  0.01,
				relaxTime:  0.01
			);
			Out.ar(0,Pan2.ar(HPF.ar(s*(amp_**2),10),pan));

	}).add;

	SynthDef.new(\scope,
		{|bufnum=0, busx=0, busy=0, offx=0, offy=0, maxFrames=8192, scopeFrames=4096|
			var x = [In.ar(busx)-offx, In.ar(busy)-offy];
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

	SynthDef.new(\asr,
		{| mul=1, add=0, bus=10, lag=0.1, arg1=0, arg2=0.1, arg3=0.1,arg4=0.1|
			var mul_ = VarLag.kr(mul,lag);
			var add_ = VarLag.kr(add,lag);
			Out.ar(bus,EnvGen.ar(Env.asr(arg2, arg3, arg4),gate:arg1, doneAction: 0)*mul_+add_);
	}).add;

	SynthDef.new(\sine1,
		{| mul=1, add=0, bus=10, lag=0.1, arg1=0|
			var mul_ = VarLag.kr(mul,lag);
			var add_ = VarLag.kr(add,lag);
			var arg1_ = VarLag.kr(arg1,lag);
			Out.ar(bus,SinOsc.ar(freq:arg1_, mul:0.5, add:0.5)*mul_+add_);
	}).add;

	SynthDef.new(\input,
		{| mul=1, add=0, bus=10, lag=0.1, arg1=0|
			var mul_ = VarLag.kr(mul,lag);
			var add_ = VarLag.kr(add,lag);
			var arg1_ = VarLag.kr(arg1,lag);
			Out.ar(bus,SoundIn.ar([0,1], mul:mul_, add:add_));
	}).add;

	MIDIClient.init(1,1);
	// MIDIIn.connectAll;


	};

s.latency = 0.3; // increase this if you get "late" messages

);


(
s.waitForBoot {
    ~dirt = SuperDirt(2, s); // two output channels, increase if you want to pan across more channels
	~dirt.loadSoundFiles;   // load samples (path containing a wildcard can be passed in)
	// for example: ~dirt.loadSoundFiles("/Users/myUserName/Dirt/samples/*");
	s.sync; // wait for samples to be read
	~dirt.start(57120, [0, 0, 0, 0, 0, 0, 0]);   // start listening on port 57120, create two busses each sending audio to channel 0

	"Loading synths.".underlined.postln;
	(thisProcess.nowExecutingPath.dirname +/+ "/synths/*.scd").loadPaths(warn:false);

	~midiOut = MIDIOut.newByName("Midi Through", "Midi Through Port-0"); // substitute your own device here

	~dirt.soundLibrary.addMIDI(\mydevice, ~midiOut);

}


)

MIDIdef.all.keys()