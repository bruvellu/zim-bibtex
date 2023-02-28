# Copyleft 2023 Bruno C. Vellutini https://brunovellutini.com


from zim.plugins import PluginClass
from zim.notebook import Path, NotebookExtension


class BibtexPlugin(PluginClass):

	plugin_info = {
	    'name': _('BibTeX'), # T: plugin name
		'description': _('Import BibTeX references to Zim.'), # T: plugin description
		'author': 'Bruno C. Vellutini',
		'help': 'Plugins:BibTeX'
	}
		

	plugin_preferences = ()
	
	plugin_notebook_properties = (
	    ('namespace', 'namespace', _('Namespace'), Path(':References')), # T: preference option
	    ('bibfile', 'file', _('Path to file'), ''), # T: preference option
	)


class BibTexNotebookExtension(NotebookExtension):

    def __init__(self, plugin, notebook):
        NotebookExtension.__init__(self, plugin, notebook)
        self.properties = self.plugin.notebook_properties(notebook)
        self.namespace = self.properties['namespace']
        self.bibfile = self.properties['bibfile']
