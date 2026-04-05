## [0.30.0] - 2026-04-05

### Added
- Real support for snake image assets, also a full default example called `default red`.
- New docs folder with new documents to better split up the documentation into their respective places.

### Changed
- Upgraded the publishing tool even more to be more reliable. Also will soon in the future publish it as another project under MIT license.
- Cleaned up the release post text.
- Up2026-04-05d README to reflect the latest changes.
- Updated and refactored a lot of code in main file.
- Moved and organized code to other files like the custom modules getting imported.
- Special effects settings now each have their own settings and there is also a global toggle `draw special effects`.

### Fixed
- Image assets setting.
- Special effects settings.

---

## [0.29.4] - 2026-04-03

### Fixed
- Added write permissions to the GitHub workflow.

---

## [0.29.3] - 2026-04-03

### Fixed
- Added asset name to the build file to enable correct uploads to GitHub releases.

---

## [0.29.2] - 2026-04-03

### Fixed
- Fixed Windows build icon file for PyInstaller.

---

## [0.29.1] - 2026-04-03

### Fixed
- Fixed Windows build executable YAML configuration.

---

## [0.29.0] - 2026-04-03

### Added
- Added bundled version of the game for other os's (windows and linux).
- A .spec file for compiling (bundling) the project correctly and easily in the future.

### Changed
- Moved all kinds of files and folders that are primarily as read only into the `.assets` folder.
- The integrity file, it now also includes checking subfolders and their content.
- All asset loading to modify their location at runtime based on the environment for bundled versions.
- Upgraded and improved publishing tool. All kinds of general tweaks.

### Fixed
- All kinds of problems with the publishing tool also refined AI prompts.

---

## [0.28.1] - 2026-04-02

### Fixed
- Version displaying

---

## [0.28.0] - 2026-04-02

### Added
- Github releases for new version, fully automated as well.
- rgb like panel to the crt screen effect
- Options to customize the panel color, draw methods and properties
- A local AI model to write version descriptions based on the changelog. As well as come up with a version code name *Changelog is still written by a human*

### Changed
- Removed the build version or the build number, since I wasn't using it like one and it isn't useful for this type of projects release anyways
- Upgraded once again the publishing tool to be more automated and improved the new user experience

### Fixed
- To open the settings menu, you need to press the correct button now, accidentally wasn't bound to just that key.

---

## [0.27.1-Build.0] - 2026-03-22

### Fixed
- Documentation for function parameters. A Sequence object can contain only 1 argument.
- Moved requests module import inside the function itself, since the function isn't used in the game.

---

## [0.27.0-Build.0] - 2026-03-22

### Added
- Some new fonts, also change the default one to one of them.
- The option to change window icon as well a new one.
- A way to add special effects, the only one currently available is the crt screen effect.
- Added documentation about default keys

### Changed
- The changelog now is ordered in chronological order, with the most recent version at the top, and the oldest at the bottom, to make it easier to read and find the latest changes.
- The music notification's music name only contains the file name itself or the song, instead of the full path.
- Updated all of the settings and config documentation. (Warning! Could be false)

### Fixed
- The documentation for default keys

---

## [0.26.0-Build.0] - 2026-03-20

### Added
- A clean and easy way to develop new blittable texts `simple_text_blit`, for developers.
- A safe and clean alternative to exiting the game
- A custom animated cursor, with the ability to add your own and customize it.
- A settings menu, in the start menu to able to change settings. Will be improved in the future!

### Changed
- Optimized the start menu, to use less resources.
- The start menu text to reflect actual keybinds the user is using.
- Moved all start ups to be after the start menu, just in case user quits.
- Removed the timestamp from the commit message.
- Settings now accept both special key names (e.g., `kp_plus`) and standard keys (e.g., `j`).

### Fixed
- SETTINGS.md url in the README.
- Fixed the inability to switch from a special key, like the `kp_plus` to an average key, like `j`

---

## [0.25.1-Build.0] - 2026-03-14

### Changed
- Refactored and cleaned up most of the documentation to improve user onboarding.
- Upgraded the development version release process to an automatic and consistent system for enhanced release experience.
- Removed the second 10000 runs archived file, it isn't needed, the first one without all of the play times written is enough.

---

## [0.25.0-Build.0] — 2026-03-13

### Fixed
- Resolved bugs affecting Windows users.
- Improved compatibility and stability on Windows platforms.

---

## [0.24.1-Build.1] — 2026-03-13

### Fixed

- Fixed the extra versions saved inside one another, sorry for the mistake.

---

## [0.24.1-Build.0] — 2026-03-13

### Added
- Major feature expansion across gameplay and UI.
- New game modes and customization options.
- Enhanced bot intelligence and behaviors.

### Changed
- Improved performance and responsiveness.
- Refined visual effects and animations.

---

## [0.0.0-Beta.1.9] — 2026-01-17

### Added
- Nearly all planned features for the first beta.
- Survey-driven improvements pending for Beta.2.

### Changed
- Minor adjustments based on user feedback.

---

## [0.0.0-Beta.1] — 2026-01-03

### Added
- Basic snake gameplay mechanics.
- Bot support for automated play.