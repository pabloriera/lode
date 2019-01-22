SynthDef.new(\${Ode_name}, 
	{|amp=1, $initial_conditions_args |
    var osc;
    var inputs;
    "SynthDef:${Ode_name}".postln;
    $inputs
    osc = ${rk4_or_discrete}.ar("${Ode_name}", $initial_conditions, *inputs )*amp;
    $outputs
}).add;
