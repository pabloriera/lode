(
// init busses (change ?? to !? to init again)
~busses = ~busses ?? {
	~matrix_in_count = 8;
	~matrix_out_count = 4;
	~matrix_ins = ~matrix_in_count.collect({ arg idx;
		var bus = Bus.audio(s,2);
		Ndef(\matrix).set(( \in++idx ).asSymbol, bus);
		bus;
	});
	~matrix_outs = ~matrix_out_count.collect({ arg idx;
		var bus = Bus.audio(s,2);
		Ndef(\matrix).set(( \out++idx ).asSymbol, bus);
		bus;
	});
};

// the matrix synth!
Ndef(\matrix, {
	var ins;

	// Collects inputs in a list
	// Inside a Synthdef, instead of "arg freq=440", you can use \freq.kr(440)
	// here we use this system to generate argument names in a loop
	ins = ~matrix_in_count.collect { arg in_idx;
		InFeedback.ar(( \in++in_idx ).asSymbol.kr(100), 2);
	};

	// for each output, sum the inputs with a different gain for each
	~matrix_out_count.do { arg out_idx;
		out_idx.postln;
		Out.ar(( \out++out_idx ).asSymbol.kr(0),
			ins.collect({ arg in, in_idx;
				in * (\gain++in_idx++"_"++out_idx).asSymbol.kr(0)
			}).sum
		);
	};

}).play;
);

(
	~matrix_gui = {
		var win;
		var layout;
		win = Window.new;

		// generate an array of array representing the knob grid
		layout = GridLayout.rows(*


			// top label header
			[
				[ StaticText.new.string_("") ] ++
				~matrix_out_count.collect { arg out_idx;
					StaticText.new.string_("Out " ++ out_idx)
				}
			] ++

			// knobs
			~matrix_in_count.collect { arg in_idx;
				[ StaticText.new.string_("In " ++ in_idx) ] ++ // left label header
				~matrix_out_count.collect { arg out_idx;
					var knob;
					var key = ( \gain++in_idx++"_"++out_idx ).asSymbol;
					knob = Knob.new.action_({ arg my;
						Ndef(\matrix).set(key, my.value)
					});
					knob.value = Ndef(\matrix).get(key);
					knob;
				}
			}
		);
		win.layout = layout;
		win.front;
	};
	~matrix_gui.value; // show the gui!
)