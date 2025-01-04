# Copyleft 2023 Bruno C. Vellutini <https://brunovellutini.com>
#
# Import BibTeX references to Zim Desktop Wiki
#
# This plugin converts the entries in a BibTeX file to pages in Zim. This
# allows one to link to these references directly from other pages.

# TODO:
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


class BibTeXPlugin(PluginClass):
    plugin_info = {
        "name": _("BibTeX"),  # T: plugin name
        "description": _(
            "Import bibliographic references from a BibTeX file as Zim pages."
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

            has_bibv1 = bibtexparser.__version__.startswith("1")
        except:
            has_bibv1 = False

        return has_bibv1, [("python3-bibtexparser (v1)", has_bibv1, True)]


class BibTeXPageViewExtension(PageViewExtension):
    def __init__(self, plugin, pageview):
        PageViewExtension.__init__(self, plugin, pageview)
        self.get_notebook_properties()

    def get_notebook_properties(self):
        self.properties = self.plugin.notebook_properties(self.pageview.notebook)
        self.namespace = self.properties["namespace"]
        self.bibfile = self.properties["bibfile"]
        logger.debug(f'BibTeX: Namespace is "{self.namespace}"')
        logger.debug(f'BibTeX: Filename is "{self.bibfile}"')

    @action(_("Import _BibTeX"), menuhints="tools")  # T: Menu item
    def load_bibfile(self):
        self.get_notebook_properties()
        self.library = BibTeXLibrary(self.bibfile)


class BibTeXLibrary:
    def __init__(self, bibfile):
        self.data = parse_file(bibfile)
