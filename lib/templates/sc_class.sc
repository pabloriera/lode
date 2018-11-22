$Ode_name : MultiOutUGen {
        *ar { arg $ode_class_args;
        ^this.multiNew('audio', $ode_arg_list)
    }
        *kr {arg $ode_class_args;
        ^this.multiNew('control',$ode_arg_list)
    }

    init {| ... args |
    	inputs = args;
    	^this.initOutputs($ode_n_equations,rate)
	}
}