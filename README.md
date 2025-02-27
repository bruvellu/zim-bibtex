# :books: BibTeX plugin for Zim

Import bibliographic references to Zim Desktop Wiki.

## Description

This plugin imports references from a BibTeX file (.bib) into your Zim notebook. 
Each entry becomes a page containing the entry type as a tag (@article, @book, @chapter, etc.) and the bibliographic fields as regular text (title, authors, journal, etc.).
The bibkey becomes the page name/title.
References are organized into subfolders based on the first letter of their bibkey (usually alphabetical order).
Subfolders are accessible through links in the index page, which is configurable (default: ":References") and also displays some library statistics.
After importing, you can search references by their metadata and cite them by simply linking to their pages.
It works great for reviews, note making, or academic digital gardens.

## Install

To parse BibTeX files, we need the `bibtexparser` library.
It can be installed via `pip` or `apt` (python3-bibtexparser).
But make sure you install version 1.4.1, since version 2 is not yet supported.

Then, place the `bibtex.py` file in your Zim plugins folder (e.g., `~/.local/share/zim/plugins/`).

## Configure
1. In Zim, go to Edit > Preferences > Plugins and enable the BibTeX plugin.
2. Set the root page for your library. Your references will be child pages from the root. The contents of the root page will be updated automatically every time you import/update your library.
3. Set the BibTeX file that holds your library. You need to keep this file updated by yourself. Many reference managers can export or keep BibTeX files of your library up-to-date.

## Usage
1. After configuring the plugin, select Tools > Import BibTeX Entries.
2. The plugin will create a page for each entry in your BibTeX file.
3. To cite a reference in your notes, simply create a link to its page (e.g., `[[References:S:Smith2023]]`).
4. You can find references by using Zim's search function or by browsing the alphabetical subfolders.

## Limitations
- For large libraries, the import process may take some time. The interface might become unresponsive during import.
- The plugin doesn't automatically update when your BibTeX file changes. You need to run the import function again.

