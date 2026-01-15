"""
音频管理器模块

负责游戏音效（SFX）和背景音乐（BGM）的播放与音量管理。

特点：
- 单例模式：全局唯一实例
- 事件订阅：自动响应 GameEvent（跳跃/金币/受伤/通关等）播放对应音效
- 资源自愈：若 assets/audio 下缺少音频文件，会自动生成一套简单的 wav 占位资源
- 容错：无音频设备/初始化失败时自动降级为静默模式，不影响游戏运行
"""

from __future__ import annotations

import json
import math
import os
import random
import struct
import sys
import wave
from typing import Dict, Optional

import pygame

from ..settings import (
    APP_NAME,
    BASE_DIR,
    AUDIO_DIR,
    SFX_DIR,
    MUSIC_DIR,
    DEFAULT_MUSIC_VOLUME,
    DEFAULT_SFX_VOLUME,
    get_user_data_dir,
)
from .event_system import EventSystem, GameEvent


class AudioManager:
    """
    音频管理器（单例）

    用法：
        audio = AudioManager()
        audio.init()
        audio.play_music("menu")
        audio.play_sfx("coin")
    """

    _instance = None

    # 配置文件（全局，不跟随存档）
    if getattr(sys, "frozen", False):
        _CONFIG_PATH = os.path.join(get_user_data_dir(APP_NAME), "config", "audio_settings.json")
    else:
        _CONFIG_PATH = os.path.join(BASE_DIR, "config", "audio_settings.json")

    # 资源映射（相对 MUSIC_DIR / SFX_DIR）
    _SFX_FILES = {
        "coin": "coin.wav",
        "jump": "jump.wav",
        "land": "land.wav",
        "stomp": "stomp.wav",
        "damage": "damage.wav",
        "death": "death.wav",
        "power_up": "power_up.wav",
        "invincible": "invincible.wav",
        "block_hit": "block_hit.wav",
        "brick_break": "brick_break.wav",
        "ui_hover": "ui_hover.wav",
        "ui_click": "ui_click.wav",
        "level_complete": "level_complete.wav",
    }

    # 音乐文件：优先使用 v2（更丰富），不存在则回退到旧版
    _MUSIC_FILES = {
        "menu": ["menu_v2.wav", "menu.wav"],
        "game": ["game_v2.wav", "game.wav"],
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.enabled: bool = False
        self.music_volume: float = DEFAULT_MUSIC_VOLUME
        self.sfx_volume: float = DEFAULT_SFX_VOLUME

        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._current_music: Optional[str] = None
        self._events_hooked: bool = False
        
        # 音效防抖：记录每个音效上次播放的时间戳
        self._sfx_last_played: Dict[str, float] = {}
        self._sfx_cooldown: float = 0.05  # 同一音效的最小间隔（秒）

        self._load_settings()
        self._initialized = True

    # -----------------------------
    # Public API
    # -----------------------------

    def init(self) -> None:
        """初始化 mixer（失败则静默降级）。"""
        if self.enabled:
            return

        try:
            # 某些环境下 mixer 需要显式 init
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=256)
        except Exception as e:
            print(f"音频初始化失败（将静默运行）: {e}")
            self.enabled = False
            return

        # 准备资源（自动生成缺失文件）
        try:
            self._ensure_default_audio_assets()
        except Exception as e:
            print(f"音频资源准备失败（将继续静默）: {e}")
            self.enabled = False
            return

        self.enabled = True
        self.set_music_volume(self.music_volume)
        self.set_sfx_volume(self.sfx_volume)
        try:
            pygame.mixer.set_num_channels(32)
        except Exception:
            pass

        # 预加载常用音效，避免首次播放有“读盘延迟”
        self._preload_sfx()

        # 订阅事件（只订阅一次）
        self._hook_events_once()

    def _preload_sfx(self) -> None:
        if not self.enabled:
            return
        for name in self._SFX_FILES.keys():
            try:
                self._get_sound(name)
            except Exception:
                pass

    def shutdown(self) -> None:
        """关闭音频系统（可选）。"""
        try:
            if pygame.mixer.get_init() is not None:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception:
            pass
        self.enabled = False

    def set_music_volume(self, volume: float) -> None:
        self.music_volume = float(max(0.0, min(1.0, volume)))
        if self.enabled and pygame.mixer.get_init() is not None:
            try:
                pygame.mixer.music.set_volume(self.music_volume)
            except Exception:
                pass

    def set_sfx_volume(self, volume: float) -> None:
        self.sfx_volume = float(max(0.0, min(1.0, volume)))
        # 已缓存的 Sound 也一起更新
        if self.enabled:
            for s in self._sounds.values():
                try:
                    s.set_volume(self.sfx_volume)
                except Exception:
                    pass

    def save_settings(self) -> None:
        """保存音量设置到 config/audio_settings.json。"""
        try:
            os.makedirs(os.path.dirname(self._CONFIG_PATH), exist_ok=True)
            with open(self._CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "music_volume": self.music_volume,
                        "sfx_volume": self.sfx_volume,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as e:
            print(f"音频设置保存失败: {e}")

    def play_sfx(self, name: str) -> None:
        """播放音效（不存在/初始化失败则忽略）。添加防抖机制防止重复播放。"""
        if not self.enabled:
            return
        
        # 防抖检查：同一音效在短时间内不重复播放
        import time
        current_time = time.time()
        last_played = self._sfx_last_played.get(name, 0)
        if current_time - last_played < self._sfx_cooldown:
            return  # 冷却中，跳过播放
        
        snd = self._get_sound(name)
        if snd is None:
            return
        try:
            snd.play()
            self._sfx_last_played[name] = current_time
        except Exception:
            pass

    def play_music(self, track: str, loops: int = -1, fade_ms: int = 250) -> None:
        """播放背景音乐（会切歌；track: menu/game）。"""
        if not self.enabled:
            return
        if track == self._current_music:
            return

        path = self._get_music_path(track)
        if not path or not os.path.exists(path):
            return

        try:
            pygame.mixer.music.fadeout(max(0, int(fade_ms)))
        except Exception:
            pass

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops=loops, fade_ms=max(0, int(fade_ms)))
            self._current_music = track
        except Exception as e:
            print(f"播放背景音乐失败 [{track}]: {e}")

    def stop_music(self, fade_ms: int = 200) -> None:
        if not self.enabled:
            return
        try:
            pygame.mixer.music.fadeout(max(0, int(fade_ms)))
        except Exception:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        self._current_music = None

    def pause_music(self) -> None:
        if not self.enabled:
            return
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass

    def resume_music(self) -> None:
        if not self.enabled:
            return
        try:
            pygame.mixer.music.unpause()
        except Exception:
            pass

    # -----------------------------
    # Internal: settings / cache
    # -----------------------------

    def _load_settings(self) -> None:
        try:
            if os.path.exists(self._CONFIG_PATH):
                with open(self._CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.music_volume = float(data.get("music_volume", DEFAULT_MUSIC_VOLUME))
                self.sfx_volume = float(data.get("sfx_volume", DEFAULT_SFX_VOLUME))
        except Exception:
            # 配置损坏时忽略
            self.music_volume = DEFAULT_MUSIC_VOLUME
            self.sfx_volume = DEFAULT_SFX_VOLUME

        self.music_volume = float(max(0.0, min(1.0, self.music_volume)))
        self.sfx_volume = float(max(0.0, min(1.0, self.sfx_volume)))

    def _get_music_path(self, track: str) -> Optional[str]:
        candidates = self._MUSIC_FILES.get(track)
        if not candidates:
            return None
        for filename in candidates:
            path = os.path.join(MUSIC_DIR, filename)
            if os.path.exists(path):
                return path
        # 都不存在时返回第一个（让生成逻辑知道要生成哪个）
        return os.path.join(MUSIC_DIR, candidates[0])

    def _get_sfx_path(self, name: str) -> Optional[str]:
        filename = self._SFX_FILES.get(name)
        if not filename:
            return None
        return os.path.join(SFX_DIR, filename)

    def _get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        if name in self._sounds:
            return self._sounds[name]

        path = self._get_sfx_path(name)
        if not path or not os.path.exists(path):
            return None

        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(self.sfx_volume)
            self._sounds[name] = snd
            return snd
        except Exception:
            return None

    # -----------------------------
    # Internal: event hooks
    # -----------------------------

    def _hook_events_once(self) -> None:
        if self._events_hooked:
            return

        es = EventSystem()
        es.subscribe(GameEvent.COIN_COLLECT, lambda _d: self.play_sfx("coin"))
        es.subscribe(GameEvent.PLAYER_JUMP, lambda _d: self.play_sfx("jump"))
        es.subscribe(GameEvent.PLAYER_LAND, lambda _d: self.play_sfx("land"))
        es.subscribe(GameEvent.ENEMY_STOMP, lambda _d: self.play_sfx("stomp"))
        es.subscribe(GameEvent.PLAYER_DAMAGE, lambda _d: self.play_sfx("damage"))
        es.subscribe(GameEvent.PLAYER_DEATH, lambda _d: self.play_sfx("death"))
        es.subscribe(GameEvent.PLAYER_POWER_UP, lambda _d: self.play_sfx("power_up"))
        es.subscribe(GameEvent.PLAYER_INVINCIBLE, lambda _d: self.play_sfx("invincible"))
        es.subscribe(GameEvent.BLOCK_HIT, lambda _d: self.play_sfx("block_hit"))
        es.subscribe(GameEvent.BRICK_BREAK, lambda _d: self.play_sfx("brick_break"))
        es.subscribe(GameEvent.LEVEL_COMPLETE, lambda _d: self.play_sfx("level_complete"))

        self._events_hooked = True

    # -----------------------------
    # Internal: generate default wav assets
    # -----------------------------

    def _ensure_default_audio_assets(self) -> None:
        os.makedirs(SFX_DIR, exist_ok=True)
        os.makedirs(MUSIC_DIR, exist_ok=True)

        # 生成 SFX
        for name, filename in self._SFX_FILES.items():
            path = os.path.join(SFX_DIR, filename)
            if not os.path.exists(path):
                self._generate_sfx_wav(name, path)

        # 生成 BGM（只生成优先候选，也就是 v2 文件名）
        for track, filenames in self._MUSIC_FILES.items():
            if not filenames:
                continue
            path = os.path.join(MUSIC_DIR, filenames[0])
            if not os.path.exists(path):
                self._generate_music_wav(track, path)

    @staticmethod
    def _write_wav_mono_16bit(path: str, samples: list[int], sample_rate: int) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            frames = b"".join(struct.pack("<h", max(-32768, min(32767, s))) for s in samples)
            wf.writeframes(frames)

    @staticmethod
    def _sine_samples(freq: float, duration: float, sample_rate: int, amplitude: float, fade: float = 0.01) -> list[int]:
        n = max(1, int(duration * sample_rate))
        a = max(0.0, min(1.0, amplitude))
        fade_n = int(fade * sample_rate)
        out: list[int] = []
        for i in range(n):
            t = i / sample_rate
            v = math.sin(2.0 * math.pi * freq * t)
            # 简单包络，减少爆音
            env = 1.0
            if fade_n > 0:
                if i < fade_n:
                    env = i / fade_n
                elif i > n - fade_n:
                    env = max(0.0, (n - i) / fade_n)
            out.append(int(v * env * a * 32767))
        return out

    def _generate_sfx_wav(self, name: str, path: str) -> None:
        sr = 22050
        silence = lambda d: [0] * max(1, int(d * sr))

        if name == "coin":
            samples = self._sine_samples(1046.5, 0.06, sr, 0.35) + self._sine_samples(1318.5, 0.05, sr, 0.30)
        elif name == "jump":
            samples = self._sine_samples(440.0, 0.05, sr, 0.30) + self._sine_samples(660.0, 0.06, sr, 0.28)
        elif name == "land":
            samples = self._sine_samples(140.0, 0.05, sr, 0.20) + silence(0.01) + self._sine_samples(90.0, 0.06, sr, 0.18)
        elif name == "stomp":
            samples = self._sine_samples(110.0, 0.08, sr, 0.35)
        elif name == "damage":
            samples = self._sine_samples(220.0, 0.05, sr, 0.35) + self._sine_samples(160.0, 0.07, sr, 0.30)
        elif name == "death":
            samples = self._sine_samples(220.0, 0.06, sr, 0.35) + self._sine_samples(180.0, 0.06, sr, 0.32) + self._sine_samples(140.0, 0.10, sr, 0.28)
        elif name == "power_up":
            samples = self._sine_samples(523.25, 0.06, sr, 0.30) + self._sine_samples(659.25, 0.06, sr, 0.30) + self._sine_samples(783.99, 0.08, sr, 0.28)
        elif name == "invincible":
            samples = (
                self._sine_samples(784.0, 0.05, sr, 0.22)
                + silence(0.01)
                + self._sine_samples(988.0, 0.05, sr, 0.22)
                + silence(0.01)
                + self._sine_samples(1175.0, 0.06, sr, 0.22)
            )
        elif name == "block_hit":
            samples = self._sine_samples(330.0, 0.04, sr, 0.28) + self._sine_samples(220.0, 0.05, sr, 0.24)
        elif name == "brick_break":
            samples = self._sine_samples(180.0, 0.06, sr, 0.30) + self._sine_samples(140.0, 0.06, sr, 0.25)
        elif name == "ui_hover":
            samples = self._sine_samples(880.0, 0.03, sr, 0.18)
        elif name == "ui_click":
            samples = self._sine_samples(660.0, 0.03, sr, 0.20) + self._sine_samples(550.0, 0.04, sr, 0.18)
        elif name == "level_complete":
            samples = (
                self._sine_samples(523.25, 0.07, sr, 0.30)
                + self._sine_samples(659.25, 0.07, sr, 0.30)
                + self._sine_samples(783.99, 0.09, sr, 0.30)
            )
        else:
            samples = self._sine_samples(440.0, 0.05, sr, 0.2)

        self._write_wav_mono_16bit(path, samples, sr)

    def _generate_music_wav(self, track: str, path: str) -> None:
        sr = 22050
        bpm = 120
        beat = 60.0 / bpm
        bar = beat * 4
        step = beat / 4  # 16分音符

        # 生成更丰富一点的 8-bit 风味 BGM（单声道）
        # - 旋律：分解和弦
        # - 低音：每拍/每小节强调根音
        # - 打击：简单噪声“踩镲”
        if track == "menu":
            # C 大调：C F G C
            chords = [
                (261.63, 329.63, 392.00),  # C
                (349.23, 440.00, 523.25),  # F
                (392.00, 493.88, 587.33),  # G
                (261.63, 329.63, 392.00),  # C
            ]
            bars = 12
            mel_amp = 0.10
            bass_amp = 0.12
        else:  # game
            # A 小调味道：Am F G Em
            chords = [
                (220.00, 261.63, 329.63),  # Am
                (174.61, 220.00, 261.63),  # F
                (196.00, 246.94, 293.66),  # G
                (164.81, 196.00, 246.94),  # Em
            ]
            bars = 16
            mel_amp = 0.11
            bass_amp = 0.13

        samples: list[int] = []

        total_steps = int((bars * bar) / step)
        for s in range(total_steps):
            bar_idx = int((s * step) / bar)
            chord = chords[bar_idx % len(chords)]

            # 旋律：16分音符分解和弦，偶尔加一个高八度点缀
            arp_idx = s % 8
            arp_note = chord[arp_idx % 3]
            if arp_idx == 6 and (bar_idx % 2 == 1):
                arp_note *= 2  # 偶数小节末尾提亮
            mel = self._sine_samples(arp_note, step * 0.95, sr, mel_amp, fade=0.003)

            # 低音：每拍根音（更低一八度）
            if s % 4 == 0:
                bass_freq = chord[0] / 2
                bass = self._sine_samples(bass_freq, step * 0.95, sr, bass_amp, fade=0.005)
            else:
                bass = [0] * len(mel)

            # “踩镲”：offbeat 的短噪声
            hat = [0] * len(mel)
            if s % 4 == 2:
                for i in range(min(len(hat), int(0.03 * sr))):
                    # 衰减噪声
                    env = 1.0 - (i / max(1, int(0.03 * sr)))
                    hat[i] = int((random.random() * 2 - 1) * env * 0.05 * 32767)

            mixed = []
            for i in range(len(mel)):
                v = mel[i] + bass[i] + hat[i]
                mixed.append(max(-32768, min(32767, v)))
            samples.extend(mixed)

        # 末尾淡出避免循环爆音
        fade_sec = 0.15
        fade_n = int(fade_sec * sr)
        n = len(samples)
        for i in range(max(0, n - fade_n), n):
            k = (n - i) / max(1, fade_n)
            samples[i] = int(samples[i] * k)

        self._write_wav_mono_16bit(path, samples, sr)

