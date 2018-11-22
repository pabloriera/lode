// Ndef(\${Ode_name}_def, {
	
//     var osc;
//     var amp = \amp.kr(0);
//     $vars

//     osc = Oderk4("${Ode_name}", $ode_arg_list )*amp;
//     [${output}]
// });


// (
// Ndef(\synth, {

// 	var osc;
// 	var freq = \freq.ar(500);
// 	var amp     = \amp.kr(0);
// 	var fb = \fb.ar(0)*10.0;
// 	var deltime = \delay.kr(0.2);
// 	var noiseamp = \noiseamp.kr(0.0)*10.0;
// 	var mod_depth = \mod_depth.kr(0.0);
// 	var mod_freq = \mod_freq.kr(10.0);
// 	var input;

// 	input = DelayL.ar(LocalIn.ar(1),1.0,deltime,1)*fb+BrownNoise.ar(noiseamp);
// 	freq = SinOsc.ar(mod_freq,0.0,mod_depth*10.0,freq);
// 	// osc = Hopf.ar(DC.ar(1.0), input, DC.ar(0.0), freq)*amp;
// 	osc = Hopf.ar(DC.ar(1.0), input, DC.ar(0.0), freq)*amp;

// 	LocalOut.ar(osc[0]);
// 	Splay.ar(osc);
// });