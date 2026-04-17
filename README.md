Physical Music Archive is a custom, full-stack web application designed for the high-fidelity management and technical logging of a physical and digital music collection. Migrated from a legacy Access environment to a modern Linux/Python/MySQL architecture, this application provides a centralized "Master" view of an artist's discography while allowing for granular tracking of specific physical and digital versions.

The app comprises:

* Integrated Master/Version CRUD: A dual-entry system that links a "Master Release" (the original album) to multiple "Other Versions" (specific CD, Vinyl, or Hi-Res Digital copies).

* Dynamic AJAX Lookups: Real-time data validation during entry. Inputting a Master ID instantly confirms the Artist and Album title, preventing data-entry errors before they hit the database.

* Archival-Grade Technical Logging: Specialized fields for Bit Depth, Sample Rate, Dynamic Range (DR) scores, and Storage Locations, tailored for the audiophile and archivist.

* "Kiosk-Ready" Dark UI: A high-contrast Black, Grey, and Emerald Green interface optimized for low-light terminal environments and tablet displays.

* Media Interaction Tracking: A dedicated log for tracking "plays" and interactions, allowing for the generation of future listening reports and archival statistics.

* Mobile-Optimized Layout: Tabular data structures designed to look consistent across desktop monitors and tablet "Web-App" wrappers.

The app utilises the following technical stack:

* Backend: Python 3 / Flask

* Database: MySQL (relational structure with Foreign Key integrity) / MariaDB

* Frontend: HTML5 / CSS3 / JavaScript (Vanilla AJAX)

* Environment: Raspberry Pi / Linux
