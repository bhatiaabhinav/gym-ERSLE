import gymGame
import os.path as osp

DIR_NAME = osp.dirname(__file__)

ambulance = gymGame.SimpleSprite.load(osp.join(DIR_NAME, 'ambulance.png'))
base = gymGame.SimpleSprite.load(osp.join(DIR_NAME, 'base.png'))
base_level = gymGame.SimpleSprite.load(osp.join(DIR_NAME, 'base_level.png'))
hospital = gymGame.SimpleSprite.load(osp.join(DIR_NAME, 'hospital.png'))
requestNew = gymGame.SimpleSprite.load(osp.join(DIR_NAME, 'requestNew.png'))
requestOld = gymGame.SimpleSprite.load(osp.join(DIR_NAME, 'requestOld.png'))
clock = gymGame.SimpleSprite.load(osp.join(DIR_NAME, 'clock.png'))