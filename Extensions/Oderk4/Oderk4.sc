Oderk4 : MultiOutUGen {
	*ar { arg label ... in;
		("Oderk4:"++label).postln;
		^this.multiNewList([label] ++ in);		
	}
	*new { arg label ... in;
		^this;
	}
	*new1 { arg label ... in;
		var inputs_;
		label = label ?? { "default" };
		// label.postln;
		label = label.asString.collectAs(_.ascii, Array);
		inputs_ = [label.size] ++ label ++ in;
		// inputs_.postln;
		^super.new.rate_('audio').addToSynth.init(inputs_);
	}

	init { arg theInputs;
		inputs = theInputs;
		^this.initOutputs(8,rate)
	}
}