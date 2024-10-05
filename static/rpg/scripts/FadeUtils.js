import * as Phaser from 'https://cdn.jsdelivr.net/npm/phaser@3.60.0/dist/phaser.esm.js'

export class FadeUtils {
  static fadeIn(scene, duration = 1000, callback) {
    // starts from black screen and fades in to the scene
    scene.cameras.main.fadeIn(duration, 0, 0, 0)

    if (callback) {
      scene.cameras.main.once(
        Phaser.Cameras.Scene2D.Events.FADE_IN_COMPLETE,
        () => callback()
      )
    }
  }

  static fadeOut(scene, duration = 1000, callback) {
    // fades out to black screen
    scene.cameras.main.fadeOut(duration, 0, 0, 0)

    if (callback) {
      scene.cameras.main.once(
        Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE,
        () => callback()
      )
    }
  }
}
