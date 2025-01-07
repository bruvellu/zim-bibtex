# Copyleft 2023 Bruno C. Vellutini <https://brunovellutini.com>
#
# Import BibTeX references to Zim Desktop Wiki
#
# This plugin converts the entries in a BibTeX file to pages in Zim. This
# allows one to link to these references directly from other pages.


import logging
import os
from datetime import datetime

import bibtexparser
from bibtexparser.bparser import BibTexParser
from zim.actions import action
from zim.formats import get_format
from zim.gui.pageview import PageViewExtension
from zim.notebook import Path
from zim.plugins import PluginClass

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

    # TODO: Add option to remove pages that disappeared from bibfile
    # TODO: Add option for alphabetical or year sorting?

    plugin_preferences = ()

    plugin_notebook_properties = (
        (
            "rootpage",
            "namespace",
            _("Library root page"),
            Path(":References"),
        ),  # T: preference option
        ("bibfile", "file", _("Path to .bib file"), ""),  # T: preference option
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
        except ImportError:
            logger.debug("bibtexparser is not installed")
            has_bibv1 = False

        return has_bibv1, [("python3-bibtexparser (v1)", has_bibv1, True)]


class BibTeXPageViewExtension(PageViewExtension):
    def __init__(self, plugin, pageview):
        PageViewExtension.__init__(self, plugin, pageview)

        # Define class variables
        self.properties = None
        self.rootpage = ""
        self.bibfile = ""
        self.bibdata = None

        # Fill variables
        self.get_notebook_properties()

    def get_notebook_properties(self):
        self.properties = self.plugin.notebook_properties(self.pageview.notebook)
        self.rootpage = self.properties["rootpage"]
        self.bibfile = self.properties["bibfile"]
        logger.debug(f"BibTeX: Namespace is '{self.rootpage}'")
        logger.debug(f"BibTeX: Filename is '{self.bibfile}'")

    @action(_("Import _BibTeX"), menuhints="tools")  # T: Menu item
    def load_bibfile(self):
        self.get_notebook_properties()
        self.navigation.open_page(self.rootpage)
        self.bibdata = BibTeXLibrary(self.bibfile)
        self.update_stats()

    # TODO: Split into update_root and update_stats
    def update_stats(self):
        """Update statistics about the BibTeX library."""
        # Get page
        page = self.pageview.notebook.get_page(self.rootpage)

        # Generate dictionary statistics as a list
        stats_content = [
            f"**Library** | "
            f"[[{self.bibfile}|{os.path.basename(self.bibfile)}]] | "
            f"{self.bibdata.num_entries} entries | "
            f"{self.bibdata.updated}",
        ]

        # Define page format
        page_format = get_format("wiki")

        # Append statistics to existing content list
        if page.hascontent:
            # Get page contents as a list
            page_tree = page.get_parsetree()
            page_content = page_format.Dumper().dump(page_tree)
            # Keep only title and creation
            page_content = page_content[:2]
            page_content.append("\n")
            page_content.extend(stats_content)
        else:
            page_content = [
                "====== References ======\n",
                f"Created {datetime.now().strftime('%A %d %B %Y')}",
                "\n",
            ]
            page_content.extend(stats_content)

        # Convert content list to plain text
        page_text = "".join(page_content)

        # Parse text to regenerate content tree
        tree = page_format.Parser().parse(page_text)

        # Save updated library page
        page.set_parsetree(tree)
        self.pageview.notebook.store_page(page)

        logger.debug(
            f"BibTeX: Generated statistics for {self.bibfile} on {self.rootpage}"
        )


class BibTeXLibrary:

    # TODO: Make template for individual entries
    # TODO: Generate alphabetical directory structure

    def __init__(self, bibfile):
        self.bibtex = os.path.expanduser(bibfile)
        self.parser = BibTexParser(ignore_nonstandard_types=False)
        self.library = None
        self.num_entries = 0
        self.updated = datetime.now().astimezone().replace(microsecond=0).isoformat()

        with open(self.bibtex) as file:
            logger.debug(f"BibTeX: Importing {file.name}... (this might take a while)")
            self.library = bibtexparser.load(file, self.parser)
            self.num_entries = len(self.library.entries)
            logger.debug(
                f"BibTeX: Loaded {self.num_entries} entries from {os.path.basename(file.name)}"
            )

# TODO: Make class to keep track of file timestamp and other variables
