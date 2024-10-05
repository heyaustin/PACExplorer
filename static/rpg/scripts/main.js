import * as Phaser from 'https://cdn.jsdelivr.net/npm/phaser@3.60.0/dist/phaser.esm.js'

import { LoadingScene } from "./scene/LoadingScene.js"
import { MainMenuScene } from "./scene/MainMenuScene.js"
import { OptionsScene } from "./scene/OptionsScene.js"
import { GameScene } from "./scene/GameScene.js"

const gameConfig = {
  type: Phaser.CANVAS,
  pixelArt: true,
  scale: {
    parent: "game-container",
    width: 800,
    height: 600
  },
  backgroundColor: "#000000",
  scene: [LoadingScene, MainMenuScene, OptionsScene, GameScene],
  physics: {
    default: "arcade",
    arcade: {
      debug: false
    }
  }
}

const game = new Phaser.Game(gameConfig)
