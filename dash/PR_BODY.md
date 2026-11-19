Adds an unofficial Russian-language MDN HTML docset maintained by @Omogobicoyu.

- 1233 translated MDN articles and 3405 searchable entries.
- Mostly machine-translated prose (Argos en-ru 1.9); 233 introductions are from mdn/translated-content. Original MDN source-code blocks are preserved.
- 139 remote mdnplay examples rebuilt locally from recorded HTML/CSS/JS. Web navigation/sidebars are hidden for narrow documentation views. Optional online audio/video is linked explicitly.
- A collapsed section in the `<form>` article links to an original educational PHP/MySQL form-processing project. It includes commented source, centered authentication forms, a numeric phone mask, and a phpMyAdmin GUI guide. The displayed PHP/JS source is escaped text, not executed by the docset.
- Frozen input URL, verified checksum, build script, source snapshot, source/image attribution, and licenses are documented in README.

Validation: SQLite integrity, all indexed file/fragment targets, unchanged MDN code blocks, exact embedded/downloadable project source, safe tar members, and browser checks at 400px and 1100px with external requests blocked. A few intentional missing-image error demonstrations are retained from upstream.

Known limitations: machine-translation quality and a frozen MDN snapshot (HTML revision 157); native Dash import still needs a macOS check. This has not been presented as an official Mozilla/Kapeli translation. Bug reports: https://github.com/Omogobicoyu/html-forms-docset/issues.
