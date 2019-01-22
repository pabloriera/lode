(
s.quit;
s.waitForBoot{

	var scope_n = 6;
	var scope_i = 2;
	var scope_j = 3;
	var scope_widht = 380;
	var scope_height = 380;

	f = Array.fill(scope_n,{arg i; Buffer.alloc(s,2048,2)});
	// f.do({arg f_; f_.bufnum.postln});
	w=Window("Scope", Rect(10, Window.screenBounds.height-10,scope_widht*scope_j,scope_height*scope_i)).front;

	c = Array.fill(scope_n,
		{arg i;
			c = ScopeView(w,Rect((i%scope_j)*scope_widht,(i/scope_j).asInt*scope_height,scope_widht,scope_height));
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

	SynthDef.new(\connection,
		{| from=0, to=0, mul=1,add = 0 delay_time=0|
			Out.ar(to,DelayL.ar(InFeedback.ar(from,1)*mul+add,1.0,delay_time));
	}).add;

	SynthDef.new(\value,
		{| val=0, bus=10|
			Out.ar(bus,DC.ar(1)*VarLag.kr(val,0.5));
	}).add;

	SynthDef.new(\output,
		{|bus=10, amp=0, pan=0|
			Out.ar(0,Pan2.ar(LeakDC.ar(In.ar(bus,1)*(VarLag.kr(amp/2.0,0.5)**4)),pan));

	}).add;

	SynthDef.new(\scope,
		{|bus_x=10, bus_y=11, bufnum=0, channels=2|
			var x = [In.ar(bus_x,1), In.ar(bus_y,1)];
			ScopeOut2.ar( x, bufnum);
	}).add;
	SynthDef.new(\noise,
		{|mul=1, add=0, bus=10, arg1=6000|
			var freq_ = VarLag.kr(arg1,0.5);
			var mul_ = VarLag.kr(mul,0.5);
			var add_ = VarLag.kr(add,0.5);
			Out.ar(bus,LPF.ar(WhiteNoise.ar,freq_, mul_,add_));
	}).add;

	SynthDef.new(\sinosc,
		{| mul=1, add=0, bus=10, arg1=0|
			var mul_ = VarLag.kr(mul,0.5);
			var add_ = VarLag.kr(add,0.5);
			Out.ar(bus,SinOsc.ar(freq:arg1, mul:mul_, add:add_));
	}).add;

};

)

{SinOsc.ar(400)*0.2}.play



c[0].xZoom=1;
c[0].yZoom=0.2;
c[0]

c[1].xZoom=0.05;
c[1].yZoom=0.05;

c[2].style=2
c[0].xZoom=0.1;
c[0].yZoom=0.1;

(

)


(
AppClock.sched(0.1,{c[0].xZoom=0.2; nil;});
)

c[3].yZoom


// ~c2 = Synth(\connect,target: 1011);
// ~c2.set(\from,10,\to,41,\add,0,\mul,100.0,\del,0.01);
// ~c2.free
// {Odemap.ar("Map",1)}.play
