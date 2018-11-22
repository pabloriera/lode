import pathlib
sc_extensions_path = '.local/share/SuperCollider/Extensions'
home_path = pathlib.Path.home()
module_directory = pathlib.Path(__file__).parent
sources_path = '{}/odes'.format(module_directory)
ode_template_filename = '{}/templates/ode_equation_template.cpp'.format(module_directory)
sc_class_template_filename = '{}/templates/sc_class.sc'.format(module_directory)
sc_def_template_filename = '{}/templates/sc_def.sc'.format(module_directory)