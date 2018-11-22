SynthDef.new(\Hopf, 
	{| e=1.0, w=440, amp=1 |
    var osc;
    
    osc = Oderk4.ar("Hopf", DC.ar(1)*e, DC.ar(1)*w )*amp;
    OffsetOut.ar(3,osc[0]);
	OffsetOut.ar(4,osc[1]);
});
