SynthDef.new(\Lorenz, 
	{| beta=2.6666, rho=28, sigma=10, tau=50.0, amp=1 |
    var osc;
    
    osc = Oderk4.ar("Lorenz", DC.ar(1)*beta, DC.ar(1)*rho, DC.ar(1)*sigma, DC.ar(1)*tau )*amp;
    OffsetOut.ar(0,osc[0]);
	OffsetOut.ar(1,osc[1]);
	OffsetOut.ar(2,osc[2]);
});
