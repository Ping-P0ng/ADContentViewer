# ADContentViewer

ADContentViewer is a simple web viewer for active directory objects.

Currently only one format is supported - ADFind default. The search is performed by the parameter sAMAccountName. Hash file must be in the pwd format.

# Installation

Install python packages: `pip3 install tornado argparse`

# Usage

Example: `python3 ADContentViewer.py -db adcontent.db -u ./test/users.txt -g ./test/groups.txt -c ./test/computers.txt -pwd ./test/dcsync.pwd`

This command parse files content and add to db. Tornado server listening on http://127.0.0.1:16600.

Example: `python3 ADContentViewer.py -db adcontent.db`

This command use existing db.

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

Two formats are used to update hashes:
- pwd
- NT:password (output hashcat)

![Alt text](/image/tools.png?raw=true "Tools page")
