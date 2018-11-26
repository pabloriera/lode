(
SynthDef.new(\hopf, {
  Out.ar(\out.ar(0), Oderk4.ar(\Hopf, \w.ar(0.3), \e.ar(300)));
}).add;
)

f = { |key=\default| SynthDescLib.global.at(key).def.func };


p = ProxySpace.push(s);


~hopf.play;
~hopf[0] = f.(\hopf);

~pe = { LFNoise2.kr(30, 300, 500) };
~hopf.set(\e, ~pe);

~hopf2 = f.(\hopf);

~hopf2.set(\out, 10)

~hopf2.set(\e, 10)
~hopf.set(\w, ~pw+0.5)

~hopf[10] = \filter -> { |sig| FreeVerb.ar(RLPF.ar(sig, SinOsc.kr(0.25).range(5000,10000))) * SinOsc.kr(8).range(0.25,0.75) };

p