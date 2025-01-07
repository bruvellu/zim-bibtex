# Zim BibTeX plugin

Import your bibliographic references to Zim Desktop Wiki.

## Description

This plugin imports entries from a BibTeX file into Zim as regular pages, so that you can cite references by simply linking to that page.

## Install

To parse BibTeX files, we need the `bibtexparser` library.
It can be installed via `pip` or `apt` (python3-bibtexparser).
But make sure you install version 1.4.1, since version 2 is not yet supported.

## Configure

1. Set the root page for your library. Your references will be child pages from the root. The contents of the root page will be updated automatically every time you import/update your library.
2. Set the BibTeX file that holds your library. You need to keep this file updated by yourself. Many references managers can export or keep BibTeX files of your library up-to-date.