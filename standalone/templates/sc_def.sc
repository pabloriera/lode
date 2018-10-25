Ndef(\${Ode_name}_def, {

    var osc;
    var amp = \amp.kr(0);
    $vars

    osc = ${Ode_name}.ar( $ode_arg_list )*amp;
    Splay.ar(osc);
});
