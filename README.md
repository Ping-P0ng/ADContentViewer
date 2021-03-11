# ADContentViewer

ADContentViewer is a simple web viewer for active directory objects.

Currently only one format is supported - ADFind default. The search is performed by the parameter sAMAccountName.

# Installation

Install python packages: `pip3 install tornado argparse`

# Usage

Tornado server listening on http://127.0.0.1:16600.

Example: `python3 ADContentViewer.py -db adcontent.db`

This command use existing db or create new.

Нou can add objects dumps. via the tools page.

# Screenshots

Home page.

![Alt text](/image/home.png?raw=true "Home page")

Users page.

![Alt text](/image/users.png?raw=true "Users page")

Computers page.

![Alt text](/image/computers.png?raw=true "Computers page")

Groups page.

![Alt text](/image/groups.png?raw=true "Groups page")

Info object page.

![Alt text](/image/user_info.png?raw=true "Info object page")

Tools page.

Formats used for updating or adding:
- Hashe
	- pwd
	- NT:password (output hashcat)
- Objects
	- adfind default

![Alt text](/image/tools.png?raw=true "Tools page")
