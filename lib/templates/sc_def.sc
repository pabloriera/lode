SynthDef.new(\${Ode_name}, 
	{| $def_arg_list, amp=1 |
    var osc;
    $inputs
    "SynthDef:${Ode_name}".postln;
    osc = Oderk4.ar("${Ode_name}", $ode_arg_list )*amp;
    $outputs
    // Out.ar(0,Splay.ar(osc));
}).add;
