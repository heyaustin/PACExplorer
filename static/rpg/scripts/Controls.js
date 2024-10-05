// Controls.ts
import * as Phaser from 'https://cdn.jsdelivr.net/npm/phaser@3.60.0/dist/phaser.esm.js'

export class Controls {
  constructor(scene) {
    this.scene = scene
    this.keys = {
      one: this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.ONE),
      two: this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.TWO),
      three: this.scene.input.keyboard.addKey(
        Phaser.Input.Keyboard.KeyCodes.THREE
      ),
      four: this.scene.input.keyboard.addKey(
        Phaser.Input.Keyboard.KeyCodes.FOUR
      ),
      w: this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.W),
      a: this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.A),
      s: this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      d: this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.D),
      space: this.scene.input.keyboard.addKey(
        Phaser.Input.Keyboard.KeyCodes.SPACE
      ),
      shift: this.scene.input.keyboard.addKey(
        Phaser.Input.Keyboard.KeyCodes.SHIFT
      ),
      esc: this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.ESC),
      up: this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.UP),
      down: this.scene.input.keyboard.addKey(
        Phaser.Input.Keyboard.KeyCodes.DOWN
      ),
      left: this.scene.input.keyboard.addKey(
        Phaser.Input.Keyboard.KeyCodes.LEFT
      ),
      right: this.scene.input.keyboard.addKey(
        Phaser.Input.Keyboard.KeyCodes.RIGHT
      )
    }
  }

  isDown(key) {
    if (this.keys[key]) {
      return this.keys[key].isDown
    }
    return false
  }

  justDown(key) {
    if (this.keys[key]) {
      return Phaser.Input.Keyboard.JustDown(this.keys[key])
    }
    return false
  }
}
