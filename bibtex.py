# Copyleft 2023 Bruno C. Vellutini <https://brunovellutini.com>
#
# Import BibTeX references to Zim Desktop Wiki
#
# This plugin converts the entries of a BibTeX file to pages in Zim. This
# allows one to link to these references directly from other pages.

# TODO:
# - Migrate to bibtexparser
# - Updating namespace and bib file does not update immediately
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
from zim.gui.pageview import PageViewExtension

logger = logging.getLogger("zim.plugins.bibtex")


class BibtexPlugin(PluginClass):
    plugin_info = {
        "name": _("BibTeX"),  # T: plugin name
        "description": _(
            "Import references from a BibTeX file as pages in Zim."
        ),  # T: plugin description
        "author": "Bruno C. Vellutini",
        "help": "Plugins:BibTeX",
    }

    plugin_preferences = ()

    plugin_notebook_properties = (
        (
            "namespace",
            "namespace",
            _("Namespace"),
            Path(":References"),
        ),  # T: preference option
        ("bibfile", "file", _("Path to file"), ""),  # T: preference option
    )

    @classmethod
    def check_dependencies(klass):
        try:
            import bibtexparser
            has_bibv1 = bibtexparser.__version__.startswith('1')
        except:
            has_bibv1 = False

        return has_bibv1, [("python3-bibtexparser v1", has_bibv1, True)]


# class BibTexNotebookExtension(NotebookExtension):

# def __init__(self, plugin, notebook):
# NotebookExtension.__init__(self, plugin, notebook)
# self.properties = self.plugin.notebook_properties(notebook)


class BibTexPageViewExtension(PageViewExtension):
    def __init__(self, plugin, pageview):
        PageViewExtension.__init__(self, plugin, pageview)
        self.properties = self.plugin.notebook_properties(self.pageview.notebook)
        self.namespace = self.properties["namespace"]
        self.bibfile = self.properties["bibfile"]
        logger.debug(f"BibTeX namespace: {self.namespace}")
        logger.debug(f"BibTeX file: {self.bibfile}")

    @action(_("Import _BibTeX"), menuhints="tools")  # T: Menu item
    def load_bibfile(self):
        logger.debug(f"Parsing... {self.bibfile}")
        self.bibdata = BibLibrary(self.bibfile)


class BibLibrary:
    def __init__(self, bibfile):
        self.data = parse_file(bibfile)


