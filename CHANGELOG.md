# Changelog

## [Unreleased]

- Support for Wagtail 7.2
- Support for Python 3.14

## [0.17.2] - 2025-10-18

### Fixed

- Uploads in the media chooser with Wagtail 7.1

## [0.17.1] - 2025-09-01

### Fixed

- Tabs not initialising for Wagtail < 7.1

## [0.17.0] - 2025-08-20

### Added

- Support for Wagtail 7.1 ([#262](https://github.com/torchbox/wagtailmedia/pull/262)) @damwaingames

### Fixed

- Pagination when using typed choosers ([#260](https://github.com/torchbox/wagtailmedia/pull/260)) @WilliamHenryTanza

### Changed

- Use the new Tabs controller with Wagtail 7.1  @zerolab
  This no longer includes the modified `tabs.js` as a workaround.

## [0.16.0] - 2025-05-06

### Added

- Support for Wagtail 7.0 (and 6.3, 6.4) ([#250](https://github.com/torchbox/wagtailmedia/pull/250), [#251](https://github.com/torchbox/wagtailmedia/pull/251), [#255](https://github.com/torchbox/wagtailmedia/pull/255), [#257](https://github.com/torchbox/wagtailmedia/pull/257) @gasman, @JakubMastalerz and @zerolab
- SPDX license expressions ([#257](https://github.com/torchbox/wagtailmedia/pull/257))
  More info at https://peps.python.org/pep-0639/, https://hugovk.dev/blog/2025/improving-licence-metadata/

## [0.15.2] - 2024-06-12

### Added

- Add support for Wagtail 6.1 ([#243](https://github.com/torchbox/wagtailmedia/pull/243)) @katdom13
- Romanian translation

### Changed

- Updated Russian translation ([#242](https://github.com/torchbox/wagtailmedia/pull/242)) @ACK1D

### Removed

- Drop support for Wagtail < 5.2 and Django < 4.2. ([#243](https://github.com/torchbox/wagtailmedia/pull/243)) @katdom13

## [0.15.1] - 2024-02-05

### Fixed

- The action buttons on the Media index in Wagtail 6.0

## [0.15.0] - 2024-02-05

### Added

- Means to override the edit form action ([#229](https://github.com/torchbox/wagtailmedia/pull/229)) @davidwtbuxton
- Official compatibility with Wagtail 6

### Changed

- Switched to Ruff for everything
- Tidied up configuration

## [0.14.5] - 2023-11-01

### Added

- Support for Wagtail 5.2 (and Python 3.12) @zerolab

### Changed

- Switched to using `icon_name` instead of `classnames` in `MediaSearchArea` @zerolab, @jamesbiggs
- Cleaned up static files ([#221](https://github.com/torchbox/wagtailmedia/pull/221)) @kiranrokkam09

### Removed

- Official support for Wagtail 4.2/5.0 (they still work just fine)

## [0.14.4] - 2023-08-01

### Changed

- Usage of `insert_editor_css` with `insert_global_admin_css` ([#218](https://github.com/torchbox/wagtailmedia/pull/218)) @jamesbiggs

## [0.14.3] - 2023-07-19

### Added

- Support for Wagtail 5.1

### Changed

- Switched to trusted PyPI publishing
- Clarified the defaults for `WAGTAILMEDIA` in README
- Improved coverage configuration

### Fixed

- Long-running buttons for Wagtail 5+
- Tag field initialisation when using the generic media chooser
- Title population from file name.


## [0.14.2] - 2023-06-08

### Changed

- Fixed the edit url in choosers. @zerolab


## [0.14.1] - 2023-05-05

### Changed

- Updated the `SearchField` definition to remove `partial_match` and add corresponding `AutocompleteField`. by @jamesbiggs
  Reference: https://docs.wagtail.org/en/stable/releases/5.0.html#elasticsearch-backend-no-longer-performs-partial-matching-on-search

## [0.14.0] - 2023-04-23

### Added

- Audio/Video icons. you can use them with `{% icon "wagtailmedia-audio" %}` and `{% icon "wagtailmedia-video" %}`
- Support for Wagtail 5.0

### Changed

- Started using [ruff](https://github.com/charliermarsh/ruff) instead of isort/flake8
- Switched to [flit](https://flit.pypa.io/en/latest/) for packaging

## [0.13.0] - 2023-02-15

### Changed

- Testing against Wagtail 4.2 ([#193](https://github.com/torchbox/wagtailmedia/pull/193)) by @katdom13

### Removed

- Support for Wagtail < 4.1 ([#193](https://github.com/torchbox/wagtailmedia/pull/193)) by @katdom13

## [0.12.0] - 2022-11-01

### Added

- Russian translation ([#177](https://github.com/torchbox/wagtailmedia/pull/177)) by @vl-tk
  Note: the authors of this package have nothing against the Russian languge. They do, however condemn the actions of the russian state and their war against Ukraine.
- Wagtail 4.1 support ([#181](https://github.com/torchbox/wagtailmedia/pull/181)) by @zerolab
- Media field and block comparison ([#184](https://github.com/torchbox/wagtailmedia/pull/184)) by @zerolab
- API viewset and serializer ([#185](https://github.com/torchbox/wagtailmedia/pull/185)) by @zerolab and @hallpower

### Fixed

- Further UI fixes and improvements for Wagtail 4 ([#176](https://github.com/torchbox/wagtailmedia/pull/176)) by @thibaudcolas
- On-delete errors when cleaning up thumbnails ([#178](https://github.com/torchbox/wagtailmedia/pull/178)) by @jsma

### Changed

- Updated GitHub Actions versions
- Testing against Python 3.11
- Expanded PyPI trove classifiers

## [0.11.1] - 2021-10-07

### Fixed

- Further UI tidy ups for Wagtail 4 ([#173](https://github.com/torchbox/wagtailmedia/issues/173)). Thanks @thibaudcolas
- Non-field errors not displayed in choosers ([#174](https://github.com/torchbox/wagtailmedia/pull/174)). Thanks @niarferuto
- Chooser buttons not visible in Wagtail 4.0.2. Note this is a temporary fix until https://github.com/wagtail/wagtail/issues/9260 is addressed

## [0.11.0] - 2021-09-02

### Added

- Added support for Wagtail 4.0 ([#169](https://github.com/torchbox/wagtailmedia/pull/169)).
  With thanks to @th3hamm0r for testing and follow-up fix ([#172](https://github.com/torchbox/wagtailmedia/pull/172)).

### Fixed

- Sorting in the media index and chooser.
- Tabs script dependency in the chooser. ([#170](https://github.com/torchbox/wagtailmedia/pull/170)). Thanks @jhnbkr.

### Changed

- Updated German translations ([#171](https://github.com/torchbox/wagtailmedia/pull/171)). Thanks @th3hamm0r.

## [0.10.1] - 2022-06-20

### Fixed

- Fixed comment tag in template ([#163](https://github.com/torchbox/wagtailmedia/pull/163)). Thanks @th3hamm0r

## [0.10.0] - 2022-06-10

### Added

- Wagtail 3.0 support
- CodeQL configuration. Thanks @thibaudcolas

### Changed

- Updated French translations ([#159](https://github.com/torchbox/wagtailmedia/pull/159)). Thanks @hoccau, @Antoine

### Removed

- Support for Wagtail < 2.15

## [0.9.0] - 2022-02-22

### Added
- Wagtail 2.15 support ([#143](https://github.com/torchbox/wagtailmedia/pull/143)). Thanks @gasman
- Ukrainian translation ([#145](https://github.com/torchbox/wagtailmedia/pull/145)). Thanks [@yuriifabirovskyi](https://github.com/yuriifabirovskyi)
- Wagtail 2.16 and Django 4.0 support
- Note about `collectstatic` in installation notes. Thanks [@G-kodes](https://github.com/G-kodes)

### Fixed
- Import issues due to module-level call to `get_media_base_form()` ([#148](https://github.com/torchbox/wagtailmedia/pull/148)). Thanks [@jsma](https://github.com/jsma)

## [0.8.0] - 2021-09-11

- Updated test targets to include Wagtail 2.14
- Changed the chooser uploader forms to use correctly instantiated forms ([#135](https://github.com/torchbox/wagtailmedia/pull/135))
- Fixed the media chooser block compatibility with Wagtail 2.13 ([#136](https://github.com/torchbox/wagtailmedia/pull/136). Thanks [@efes](https://github.com/ephes))
- Added tag-based filters ([#132](https://github.com/torchbox/wagtailmedia/pull/132). Thanks [@th3hamm0r](https://github.com/th3hamm0r))
- Added `default_auto_field` for Django 3.2+ ([#134](https://github.com/torchbox/wagtailmedia/pull/134). Thanks [@hyperstown](https://github.com/hyperstown))
- Refactored project structure and updated tooling ([#137](https://github.com/torchbox/wagtailmedia/pull/137))
- Added specialized StreamField blocks and support media type filter in `MediaChooserPanel` ([#139](https://github.com/torchbox/wagtailmedia/pull/139))
- Added file extension validation ([#140](https://github.com/torchbox/wagtailmedia/pull/140))

  Thumbnails limited to `gif`, `png`, `jpg`/`jpeg`, `webp`. Audio to `aac`, `aiff`, `flac`, `m4a`, `m4b`, `mp3`, `ogg` and `wav`.
  Video to `avi`, `h264`, `m4v`, `mkv`, `mov`, `mp4`, `mpeg`, `mpg`, `ogv` and `webm`
- Switched to a unified `WAGTAILMEDIA` setting dictionary ([#140](https://github.com/torchbox/wagtailmedia/pull/140))

## [0.7.1] - 2021-06-12

- Fixed chooser tabs with Wagtail 2.13 ([#130](https://github.com/torchbox/wagtailmedia/pull/130)). Thanks to [@jams2](https://github.com/jams2)

## [0.7.0] - 2020-11-06

- Made the duration field optional, and altered it from PositiveIntegerField to FloatField. If you rely on integer output of duration in templates use `{{ media.duration|floatformat:"0" }}` instead of `{{ media.duration }}` to restore the previous behavior ([#100](https://github.com/torchbox/wagtailmedia/issues/100), [#106](https://github.com/torchbox/wagtailmedia/issues/106), [#108](https://github.com/torchbox/wagtailmedia/pull/108), [#110](https://github.com/torchbox/wagtailmedia/pull/110)). Thanks to [@thenewguy](https://github.com/thenewguy)!
- Fixed deprecation warnings with Django 3.0 ([#94](https://github.com/torchbox/wagtailmedia/issues/94), [#109](https://github.com/torchbox/wagtailmedia/pull/109)).
- Excluded tests folder from published package’s sdist ([#107](https://github.com/torchbox/wagtailmedia/pull/107))).
- Added Chinese (China) translations ([#114](https://github.com/torchbox/wagtailmedia/pull/114)). Thanks to [@Dannykey](https://github.com/Dannykey) and [@BrianXu20](https://github.com/BrianXu20)
- Removed declared support for Python 3.5, Wagtail 2.8, Wagtail 2.9 ([#116](https://github.com/torchbox/wagtailmedia/pull/116))
- Added declared support for Python 3.9, Wagtail 2.11, Django 3.1 ([#116](https://github.com/torchbox/wagtailmedia/pull/116))

## [0.6.0] - 2020-08-14

- Added filtering of media files by user permission in chooser panel ([#25](https://github.com/torchbox/wagtailmedia/pull/25)). Thanks to [@snj](https://github.com/snj)
- Added French translations ([#61](https://github.com/torchbox/wagtailmedia/pull/61)). Thanks to [@jeromelebleu](https://github.com/jeromelebleu).
- Add `{% block action %}` template block to allow overriding of form action in `add.html` template ([#102](https://github.com/torchbox/wagtailmedia/pull/102)). Thanks to [@thenewguy](https://github.com/thenewguy)
- Fix expected NotImplementedError in Wagtail 1.6+ ([#104](https://github.com/torchbox/wagtailmedia/pull/104)). Thanks to [@chosak](https://github.com/chosak) and [@Scotchester](https://github.com/Scotchester).
- Add support for uploading media files via the media chooser, just like images and documents ([#22](https://github.com/torchbox/wagtailmedia/issues/22), [#97](https://github.com/torchbox/wagtailmedia/pull/97)). Thanks to [@teixas](https://github.com/teixas)! 🎉

## [0.5.0] - 2020-02-20

- Added interactive demo ([#82](https://github.com/torchbox/wagtailmedia/pull/82)). Thanks to [@thenewguy](https://github.com/thenewguy)
- Added setting `WAGTAILMEDIA_MEDIA_FORM_BASE` to simplify customization of the media form ([#83](https://github.com/torchbox/wagtailmedia/pull/83)). Thanks to [@thenewguy](https://github.com/thenewguy)
- Fix Wagtail > 2.8 compatibility (reshuffled imports)
- Fix Django 3 compatibility issues ([#88](https://github.com/torchbox/wagtailmedia/pull/88)). Thanks to [@lohmander](https://github.com/lohmander)

## [0.4.0] - 2019-12-06

- Added `construct_media_chooser_queryset` hook ([#60](https://github.com/torchbox/wagtailmedia/pull/60)). Thanks to [@jeromelebleu](https://github.com/jeromelebleu)
- Added further template blocks ([#79](https://github.com/torchbox/wagtailmedia/pull/79)). Thanks to [@thenewguy](https://github.com/thenewguy)
- Added support for media renditions ([#67](https://github.com/torchbox/wagtailmedia/pull/67)). Thanks to [@thenewguy](https://github.com/thenewguy)
- Fixed Wagtail 2.7 compatibility ([#63](https://github.com/torchbox/wagtailmedia/pull/63)). Thanks to [@Chris-May](https://github.com/Chris-May)

### New template blocks

- [wagtailmedia/media/edit.html](https://github.com/torchbox/wagtailmedia/blob/master/wagtailmedia/templates/wagtailmedia/media/edit.html) has the new `form_row` and `media_stats` blocks
- [wagtailmedia/media/index.htm](https://github.com/torchbox/wagtailmedia/blob/master/wagtailmedia/templates/wagtailmedia/media/index.html) has the new `add_actions` block

## [0.3.1] - 2019-05-22

### Changed

- Update edit handler `AdminMediaChooser` API to be compatible with Wagtail 2.0 and above ([#34](https://github.com/torchbox/wagtailmedia/issues/34), [#40](https://github.com/torchbox/wagtailmedia/pull/40)). Thanks to [@pahacofome](https://github.com/pahacofome)

### Upgrade considerations

`BaseMediaChooserPanel` is deprecated, and will be removed in a future release. Please use `AdminMediaChooser` instead ([#40](https://github.com/torchbox/wagtailmedia/pull/40)):

```diff
- from wagtailmedia.edit_handlers import BaseMediaChooserPanel
+ from wagtailmedia.edit_handlers import MediaChooserPanel

# [...]

content_panels = Page.content_panels + [
    # [...]
-    BaseMediaChooserPanel('video_media'),
+    MediaChooserPanel('video_media'),
    # [...]
```

## [0.3.0] - 2019-05-08

### Added

- Support Wagtail 2.4 & 2.5 ([#43](https://github.com/torchbox/wagtailmedia/pull/43)). Thanks to [@DanSGraham](https://github.com/DanSGraham), [@evanwinter](https://github.com/evanwinter), [@kaduuuken](https://github.com/kaduuuken), [@pahacofome](https://github.com/pahacofome), [@kaedroho](https://github.com/kaedroho), [@thibaudcolas](https://github.com/thibaudcolas) for submitting various issues & PRs for this 🎉.
- In CI, unit tests now run against combinations of Python 3.5, 3.6, 3.7, Django 1.11, 2.0, 2.1, 2.2, Wagtail 2.2, 2.3, 2.4, 2.5. ([#43](https://github.com/torchbox/wagtailmedia/pull/43), thanks to [@kaedroho](https://github.com/kaedroho)).

### Changed

- Thanks to the [Wagtail 2.2 chooser API upgrade](https://docs.wagtail.org/en/v2.4/releases/2.2.html?highlight=render_modal_workflow#javascript-templates-in-modal-workflows-are-deprecated), it should now be possible to use `wagtailmedia` with a Content Security Policy without [`unsafe-eval`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src) ([#43](https://github.com/torchbox/wagtailmedia/pull/43)).

### Removed

- Remove support for Wagtail 2.1, 2.0, and below. For compatibility with Wagtail 2.1 and 2.0, use the [v0.2.0 release](https://pypi.org/project/wagtailmedia/0.2.0/).

## [0.2.0] - 2018-05-24

### Added

- Compatibility with Wagtail 2.0 (@Rotund)
- Change log


## [0.1.5] - 2017-11-02


## [0.1.4] - 2017-04-16

### Added
- Enable the optional thumbnail field for audio form. Useful for an album cover (@thenewguy)
- Fix: video form no longer fails if a custom model do not have editable width and height fields. Useful if you automatically set these fields in your project (@thenewguy)

## [0.1.3] - 2017-04-15

### Added
- Make compatible with Wagtail 1.6.3+ (thanks @nimasmi and @MechanisM)


## [0.1.2] - Apr 15, 2017

### Added
- Make compatible with Wagtail 1.5+ (thanks @nimasmi and @MechanisM)


## [0.1.1] - 2016-05-26

Initial release

---

[unreleased]: https://github.com/torchbox/wagtailmedia/compare/v0.16.0...HEAD
[0.17.2]: https://github.com/torchbox/wagtailmedia/compare/v0.17.1...v0.17.2
[0.17.1]: https://github.com/torchbox/wagtailmedia/compare/v0.17.0...v0.17.1
[0.17.0]: https://github.com/torchbox/wagtailmedia/compare/v0.16.0...v0.17.0
[0.16.0]: https://github.com/torchbox/wagtailmedia/compare/v0.15.2...v0.16.0
[0.15.2]: https://github.com/torchbox/wagtailmedia/compare/v0.15.1...v0.15.2
[0.15.1]: https://github.com/torchbox/wagtailmedia/compare/v0.15.0...v0.15.1
[0.15.0]: https://github.com/torchbox/wagtailmedia/compare/v0.14.0...v0.15.0
[0.14.4]: https://github.com/torchbox/wagtailmedia/compare/v0.14.4...v0.14.5
[0.14.4]: https://github.com/torchbox/wagtailmedia/compare/v0.14.3...v0.14.4
[0.14.3]: https://github.com/torchbox/wagtailmedia/compare/v0.14.2...v0.14.3
[0.14.2]: https://github.com/torchbox/wagtailmedia/compare/v0.14.1...v0.14.2
[0.14.1]: https://github.com/torchbox/wagtailmedia/compare/v0.14.0...v0.14.1
[0.14.0]: https://github.com/torchbox/wagtailmedia/compare/v0.13.0...v0.14.0
[0.13.0]: https://github.com/torchbox/wagtailmedia/compare/v0.12.0..v0.13.0
[0.12.0]: https://github.com/torchbox/wagtailmedia/compare/v0.11.0..v0.12.0
[0.11.1]: https://github.com/torchbox/wagtailmedia/compare/v0.11.0..v0.11.1
[0.11.0]: https://github.com/torchbox/wagtailmedia/compare/v0.10.1..0.11.0
[0.10.1]: https://github.com/torchbox/wagtailmedia/compare/v0.10.0..v0.10.1
[0.10.0]: https://github.com/torchbox/wagtailmedia/compare/v0.9.0..v0.10.0
[0.9.0]: https://github.com/torchbox/wagtailmedia/compare/v0.8.0..v0.9.0
[0.8.0]: https://github.com/torchbox/wagtailmedia/compare/v0.7.1..v0.8.0
[0.7.1]: https://github.com/torchbox/wagtailmedia/compare/v0.7.0..v0.7.1
[0.7.0]: https://github.com/torchbox/wagtailmedia/compare/v0.6.0..v0.7.0
[0.6.0]: https://github.com/torchbox/wagtailmedia/compare/v0.5.0..v0.6.0
[0.5.0]: https://github.com/torchbox/wagtailmedia/compare/v0.4.0..v0.5.0
[0.4.0]: https://github.com/torchbox/wagtailmedia/compare/v0.3.1..v0.4.0
[0.3.1]: https://github.com/torchbox/wagtailmedia/compare/v0.3.0..v0.3.1
[0.3.0]: https://github.com/torchbox/wagtailmedia/compare/v0.2.0..v0.3.0
[0.2.0]: https://github.com/torchbox/wagtailmedia/compare/v0.1.5..v0.2.0
[0.1.5]: https://github.com/torchbox/wagtailmedia/compare/v0.1.4..v0.1.5
[0.1.4]: https://github.com/torchbox/wagtailmedia/compare/v0.1.3..v0.1.4
[0.1.3]: https://github.com/torchbox/wagtailmedia/compare/v0.1.2..v0.1.3
[0.1.2]: https://github.com/torchbox/wagtailmedia/compare/v0.1.1..v0.1.2
[0.1.1]: https://github.com/torchbox/wagtailmedia/compare/3baf37cb..v0.1.1
