SynthDef.new(\example,
{|beat_dur=1, rel=0.01, level=0.8, pan=0, sus=1, bus=0, amp=1, fmod=0, blur=1, vib=0, freq=0, atk=0.01, peak=1, rate=0, decay=0.01|
var osc, env;
sus = sus * blur;
freq = In.kr(bus, 1);
freq = [freq, freq+fmod];
osc=SinOsc.ar(440.0);
osc = Mix(osc) * 0.5;
osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)}).add;
