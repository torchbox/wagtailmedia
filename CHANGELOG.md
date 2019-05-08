# Changelog

## [0.3.0] - 2019-05-08

### Added

- Support Wagtail 2.4 & 2.5 ([#43](https://github.com/torchbox/wagtailmedia/pull/43)). Thanks to [@DanSGraham](https://github.com/DanSGraham), [@evanwinter](https://github.com/evanwinter), [@kaduuuken](https://github.com/kaduuuken), [@pahacofome](https://github.com/pahacofome), [@kaedroho](https://github.com/kaedroho), [@thibaudcolas](https://github.com/thibaudcolas) for submitting various issues & PRs for this 🎉.
- In CI, unit tests now run against combinations of Python 3.5, 3.6, 3.7, Django 1.11, 2.0, 2.1, 2.2, Wagtail 2.2, 2.3, 2.4, 2.5. ([#43](https://github.com/torchbox/wagtailmedia/pull/43), thanks to [@kaedroho](https://github.com/kaedroho)).

### Changed

- Thanks to the [Wagtail 2.2 chooser API upgrade](https://docs.wagtail.io/en/v2.4/releases/2.2.html?highlight=render_modal_workflow#javascript-templates-in-modal-workflows-are-deprecated), it should now be possible to use `wagtailmedia` with a Content Security Policy without [`unsafe-eval`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src) ([#43](https://github.com/torchbox/wagtailmedia/pull/43)).

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
