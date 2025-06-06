# Dialogues

Load various e-communication media formats (.msg, .eml, .pst, ...) into a single Dialogue object.

Available formats:

* __.msg__  - Outlook stores a single email.  When you drag-and-drop an email from Outlook to a folder on your computer, the email message is converted into an MSG file. This file stores the email text, metadata (who sent the email, who received it and when, etc),links and attachments from the email.
* __.pst__ - Outlook and Teams stores groups of emails or posts.  Personal Storage Table of your mailbox.
* __.edb__ - Microsoft stores PSTs on its Exchange Server.
* __.ost__ - Outlook stores groups of email, offline.  Outlook syncs your PSTs with the Exchange Server, but stores offline data in the Offline Storage Table (OST). When you get back online, it syncs the OST with its corresponding PST.
* __.eml__ - Single emails you can open without Outlook.  Stored as plain text files.
* __.mbox__ - Groups of emails you can open without Outlook.  Like PSTs, but stores all your emails in plain text, in sequence – with a separating line between each of them.
* __.json, Teams ()__ 
  - [for RAG implementation](https://github.com/mario-guerra/teams-channel-content-export)


Note

The following repos are integrated:
* [Demisto Dev](https://github.com/demisto/parse-emails)

Additional useful repos:
* .msg - [TeamMsgExtractor/msg-extractor](https://github.com/TeamMsgExtractor/msg-extractor)
* .eml - [GOVCERT-LU/eml_parser](GOVCERT-LU/eml_parser)
* .pst, .mbox - [libratom/libratom](https://github.com/libratom/libratom)
* .ost - [libyal/libpff/wiki/Python-development](https://github.com/libyal/libpff/wiki/Python-development)



## ToDo

* ~~use minimal files from parse-emails project, [Demisto Dev](https://github.com/demisto/parse-emails)~~
  - ~~get email dict~~
  - ~~complete tests~~
* add .pst, .mbox with [libratom](https://github.com/libratom/libratom)
  - minimal files
  - complete tests
* extract entity information
  - name
  - address
* perform entity-matching
  - may be personal emails interleaved
* create dialogue threads by 'Show as Conversations'
  - group by Subject Line - Outlook groups emails that have the same subject line into one conversation.
  - group by Message References - Outlook also checks hidden information in the email (called "headers") to find links to earlier messages.  This helps it group replies and forwards into the same conversation, even if the subject line changes a bit. [ref](https://answers.microsoft.com/en-us/outlook_com/forum/all/understanding-email-grouping-in-outlooks-show-as/498a3b66-16f6-4fa5-b7e3-5dafbca0becb)
  - sequence on datetime
* ...