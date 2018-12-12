SynthDef.new(\${Ode_name}, 
	{|amp=1 |
    var osc;
    var inputs;
    "SynthDef:${Ode_name}".postln;
    $inputs
    osc = Oderk4.ar("${Ode_name}", *inputs )*amp;
    $outputs
}).add;
