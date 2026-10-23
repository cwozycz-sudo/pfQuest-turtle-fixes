# Copyright, attribution and scope

This project redistributes modified copies of two MIT-licensed public projects:

- **pfQuest**: originally Eric Mauser (Shagu), with txtsd and contributors. Current source: https://github.com/The-Kludge-Bureau/pfQuest ; original project: https://github.com/shagu/pfQuest . Original LICENSE is retained verbatim at `AddOns/pfQuest/LICENSE`.
- **pfQuest-turtle**: originally Eric Mauser (Shagu), with Gurky, Antealis, HumbleKagu, KasVital, Haaxor1689, IcemanHHW, fatpowaranga and other upstream contributors. Current source: https://github.com/The-Kludge-Bureau/pfQuest-turtle ; original project: https://github.com/shagu/pfQuest-turtle . Original LICENSE is retained verbatim at `AddOns/pfQuest-turtle/LICENSE`.

Additional repair overlay, packaging, documentation and tests: Copyright (c) 2026 cwozycz-sudo, MIT licensed. This attribution does not claim ownership of upstream code or data. The root LICENSE preserves the upstream copyright and MIT permission notices.

## Changes in this distribution

- Adds `objective-fixes.lua`, derived exclusively from public base objective tables, with guarded application to curated missing-objective records.
- Adds the overlay load line before `patchtable.lua` and an `X-ObjectiveFixes-Version` TOC metadata field.
- Packages the Vanilla runtime files, upstream language data and necessary images; omits developer tooling, TBC/Wrath-specific files and upstream CI configuration.
- Adds documentation, tests, a patch installer, packaging tools and source provenance.
- Leaves bundled upstream LICENSE files, Author and Contributor fields intact. Upstream README files are included as upstream documentation, separate from this bundle's install instructions.

## Exclusions and endorsement

No client executables, MPQ/DBC game assets, server binaries, private database exports, credentials, personal profiles or server-specific quest texts are included. The bundle contains public addon files from the commits listed in `upstream-provenance.json`; it does not assert new rights over third-party game assets or trademarks.

This is a community modification and is not endorsed by Shagu, txtsd, The-Kludge-Bureau, TurtleWoW or Blizzard. Bug reports about this overlay belong in this repository, not automatically in an upstream project's tracker.
