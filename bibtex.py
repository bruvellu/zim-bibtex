# Copyleft 2023 Bruno C. Vellutini <https://brunovellutini.com>
#
# Import BibTeX references to Zim Desktop Wiki
#
# This plugin converts the entries of a BibTeX file to pages in Zim. This allows one to link to these references directly from other pages.
#
# TODO:
# - Action does not work, probably need to be a PageViewExtension
# - Show statistics for library in new window
# - Get methods for making new pages and directories from Zim
# - Add options to sort by alphabetical or year
# - Save last modified date to replace updated only
# - Delete pages that disappeared

import logging

from zim.actions import action
from zim.plugins import PluginClass
from zim.notebook import Path, NotebookExtension

from pybtex.database import parse_file

logger = logging.getLogger('zim.plugins.bibtex')


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
		logger.debug(f'BibTeX namespace: {self.namespace}')
		logger.debug(f'BibTeX file: {self.bibfile}')

	@action(_('Update _References'), menuhints='tools') # T: Menu item
	def load_bibfile(self):
		logger.debug(f'Parsing... {self.bibfile}')
		self.bibdata = BibLibrary(self.bibfile)

class BibLibrary():

	def __init__(self, bibfile):
		self.data = parse_file(bibfile)

