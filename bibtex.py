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

import bibtexparser
import logging
import os

from bibtexparser.bparser import BibTexParser
from zim.actions import action
from zim.plugins import PluginClass
from zim.notebook import Path
from zim.gui.pageview import PageViewExtension
from zim.formats import get_format

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

            logger.debug(f"Loaded bibtexparser v{bibtexparser.__version__}")

            has_bibv1 = bibtexparser.__version__.startswith("1")
            if not has_bibv1:
                logger.debug(
                    f"You have v{bibtexparser.__version__} installed, but only v1 is supported"
                )
        except:
            logger.debug("bibtexparser is not installed")
            has_bibv1 = False

        return has_bibv1, [("python3-bibtexparser (v1)", has_bibv1, True)]


class BibTeXPageViewExtension(PageViewExtension):
    def __init__(self, plugin, pageview):
        PageViewExtension.__init__(self, plugin, pageview)

        # Define class variables
        self.namespace = ""
        self.bibfile = ""
        self.bibdata = ""

        # Fill variables
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
        self.navigation.open_page(self.namespace)
        self.bibdata = BibTeXLibrary(self.bibfile)
        self.update_stats()

    def update_stats(self):
        """Update statistics about the BibTeX library."""
        # Get page
        page = self.pageview.notebook.get_page(self.namespace)

        # Generate statistics
        total = len(self.bibdata.library.entries)
        stats_content = ["\n", f"**File:** {self.bibfile}\n", f"**Entries:** {total}\n"]

        # Append statistics to existing content
        if page.hascontent:
            page_format = get_format("wiki")
            page_content = page_format.Dumper().dump(page.get_parsetree())
            page_content.extend(stats_content)
        else:
            page_content = stats_content

        print(page_content)

        # Parse format and get content tree
        tree = page_format.Parser().parse("".join(page_content))

        # Save updated library page
        page.set_parsetree(tree)
        self.pageview.notebook.store_page(page)

        logger.debug(f"BibTeX: Updated statistics of {self.namespace}")


class BibTeXLibrary:
    def __init__(self, bibfile):
        self.bibtex = os.path.expanduser(bibfile)
        self.library = ""
        # Don't ignore non-standard BibTeX entry types
        self.parser = BibTexParser(ignore_nonstandard_types=False)

        with open(self.bibtex) as file:
            logger.debug(f"BibTeX: Importing {file.name}... (this might take a while)")
            self.library = bibtexparser.load(file, self.parser)
            n = len(self.library.entries)
            logger.debug(
                f"BibTeX: Loaded {n} entries from {os.path.basename(file.name)}"
            )
