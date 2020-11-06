# Wagtail audio / video module


A module for Wagtail that provides functionality similar to `wagtail.wagtaildocs` module,
but for audio and video files.


## Models

### Essential

* Extend the existing `Document` model or introduce new model for audio/video files (like `Image`).
* The model should contain at least: duration (for audio and video), dimensions (for video), thumbnail (for video).

### Optional

* Get duration of audio files automatically.
* Get duration and dimensions of video files automatically.
* Generate thumbnail automatically.

### Out of scope

* Uploaded videos will not be converted / compressed / resized

## Admin

### Essential

* Allow users to manage audio / video.
* Allow users to upload custom thumbnail to videos.
* Provide custom `StreamField` blocks for media items.

### Optional

* Preview video / audio in an embedded player.
* Allow users to insert audio / video files within the rich text editor.
* Support oEmbed.
    * Note this removes the previous requirement, since oEmbed is already supported by the rich text editor.
    * Requires us to provide audio and video players within the app (because we need to generate the HTML code that initializes the player).
* Template tags, providing shortcuts for template designers. This feature also requires a player.

## Tests

Comprehensive unit test coverage.

## Documentation

A detailed README in the Github project, for site implementers and module developers.
