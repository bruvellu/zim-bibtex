# Copyleft 2023 Bruno C. Vellutini <https://brunovellutini.com>
#
# Import BibTeX references to Zim Desktop Wiki
#
# This plugin converts the entries in a BibTeX file to pages in Zim. This
# allows one to link to these references directly from other pages.


import logging
import os
from collections import OrderedDict
from datetime import datetime

from zim.actions import action
from zim.formats import get_format
from zim.gui.pageview import PageViewExtension
from zim.notebook import Path
from zim.plugins import PluginClass

logger = logging.getLogger("zim.plugins.bibtex")


# Try importing bibtexparser dependency
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
        return has_bibv1, [("python3-bibtexparser (v1)", has_bibv1, True)]


class BibTeXPageViewExtension(PageViewExtension):
    def __init__(self, plugin, pageview):
        PageViewExtension.__init__(self, plugin, pageview)

        # Define class variables
        self.properties = None
        self.rootpage = ""
        self.bibfile = ""
        self.bibdata = None
        self.format = get_format("wiki")

        # Fill variables
        self.get_notebook_properties()

    @action(_("_Load BibTeX Library"), menuhints="tools")  # T: Menu item
    def load_bibtex(self):
        self.get_notebook_properties()
        self.navigation.open_page(self.rootpage)
        self.bibdata = BibTeXLibrary(self.bibfile)
        self.update_root()

    @action(_("Import _BibTeX Entries"), menuhints="tools")  # T: Menu item
    def import_bibtex(self):
        self.import_entries()

    def get_notebook_properties(self):
        self.properties = self.plugin.notebook_properties(self.pageview.notebook)
        self.rootpage = self.properties["rootpage"]
        self.bibfile = self.properties["bibfile"]
        logger.debug(f"BibTeX: Namespace is '{self.rootpage}'")
        logger.debug(f"BibTeX: Filename is '{self.bibfile}'")

    def update_root(self):
        """Update root page with library information."""
        # Get content list with the rootpage's title
        page = self.pageview.notebook.get_page(self.rootpage)
        content = self.get_page_title(page, "References")

        # Add library statistics
        content.extend(self.get_stats_list())

        # Add list of folders
        content.extend(self.get_folder_list())

        # Update content tree and save page
        page.set_parsetree(self.get_content_tree(content))
        self.pageview.notebook.store_page(page)

        logger.debug(
            f"BibTeX: Generated statistics for {self.bibfile} on {self.rootpage}"
        )

    def get_stats_list(self):
        stats_list = [
            "\n===== Library ======\n",
            f"* [[{self.bibdata.bibfile}|{self.bibdata.bibname}]] | "
            f"{self.bibdata.num_entries} entries | "
            f"{self.bibdata.updated}\n",
        ]
        return stats_list

    def get_folder_list(self):
        folder_list = [
            "\n===== Folders =====\n",
        ]
        for folder in self.bibdata.folders:
            folder_list.append(f"* [[+{folder}|{folder}]]\n")
        return folder_list

    def get_page_title(self, page, title):
        if page.hascontent:
            # Get content tree and dump as a list
            page_tree = page.get_parsetree()
            page_content = self.format.Dumper().dump(page_tree)
            # Only keep title and creation date
            page_content = page_content[:2]
        else:
            # Generate content list with new title
            page_content = [
                f"====== {title} ======\n",
                f"Created {datetime.now().strftime('%A %d %B %Y')}\n",
            ]
        return page_content

    def get_content_tree(self, content):
        """Convert page content list back to tree."""
        # Convert list to text and parse to regenerate content tree
        text = "".join(content)
        tree = self.format.Parser().parse(text)
        return tree

    def import_entries(self):
        for entry in self.bibdata.library.entries:
            # Convert to ordered dictionary
            ordbib = OrderedDict(entry)
            bibkey = ordbib.pop("ID")
            bibtype = ordbib.pop("ENTRYTYPE")
            folder = bibkey[0].upper()

            # bibkey = entry["ID"]
            name = f"{self.rootpage}:{folder}:{bibkey}"
            path = Path(Path.makeValidPageName(name))
            logger.debug(f"BibTeX: Importing @{bibtype} @{bibkey} to {path.name}")
            page = self.pageview.notebook.get_page(path)
            content = self.get_page_title(page, bibkey)

            # Add bibkey
            content.extend([f"\n@{entry['ENTRYTYPE']}\n"])
            content.append("\n")

            for k, v in reversed(ordbib.items()):
                content.append(f"**{k}:** {v.replace('\n', ' ')}\n")

            # Update content tree and save page
            page.set_parsetree(self.get_content_tree(content))
            self.pageview.notebook.store_page(page)


class BibTeXLibrary:
    def __init__(self, bibfile):
        self.bibfile = bibfile
        self.bibpath = os.path.expanduser(bibfile)
        self.bibname = os.path.basename(self.bibpath)
        self.parser = bibtexparser.bparser.BibTexParser(ignore_nonstandard_types=False)
        self.library = None
        self.num_entries = 0
        self.folders = []
        # TODO: Replace by file timestamp?
        self.updated = datetime.now().astimezone().replace(microsecond=0).isoformat()

        # Load entries from BibTeX file
        with open(self.bibpath) as file:
            logger.debug(
                f"BibTeX: Importing {self.bibpath}... (this might take a while)"
            )
            self.library = bibtexparser.load(file, self.parser)

        # Generate library statistics
        self.num_entries = len(self.library.entries)
        self.folders = self.generate_folders()

        logger.debug(f"BibTeX: Loaded {self.num_entries} entries from {self.bibname}")

    def generate_folders(self):
        folders = {key[0].upper() for key in self.library.entries_dict.keys()}
        sorted_folders = sorted(folders)
        return sorted_folders
