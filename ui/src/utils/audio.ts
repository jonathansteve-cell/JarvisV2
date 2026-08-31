// Web Audio API Synthesizer for Sci-Fi HUD Sound Effects

class SoundFX {
  private ctx: AudioContext | null = null;
  private enabled: boolean = true;
  private humGain: GainNode | null = null;
  private humOsc: OscillatorNode | null = null;
  private isHumming: boolean = false;

  private init() {
    if (!this.ctx && typeof window !== 'undefined') {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  public setEnabled(enabled: boolean) {
    this.enabled = enabled;
    if (!enabled && this.isHumming) {
      this.stopHum();
    }
  }

  public isSoundEnabled() {
    return this.enabled;
  }

  // Futuristic click blip
  public playClick(freq = 1200) {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(freq * 0.4, this.ctx.currentTime + 0.04);

      gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.04);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.05);
    } catch {
      // AudioContext might be blocked until user gesture
    }
  }

  // Subtle hover tick
  public playHover() {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(2400, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(3200, this.ctx.currentTime + 0.02);

      gain.gain.setValueAtTime(0.03, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.02);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.025);
    } catch {
      // ignore
    }
  }

  // Diagnostic scan sweep
  public playScanSweep() {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(400, this.ctx.currentTime);
      osc.frequency.linearRampToValueAtTime(1800, this.ctx.currentTime + 0.3);
      osc.frequency.linearRampToValueAtTime(600, this.ctx.currentTime + 0.6);

      gain.gain.setValueAtTime(0.06, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.6);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.65);
    } catch {
      // ignore
    }
  }

  // Confirmation chime (two-tone)
  public playConfirm() {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;

      const now = this.ctx.currentTime;
      const osc1 = this.ctx.createOscillator();
      const osc2 = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc1.type = 'sine';
      osc2.type = 'sine';

      osc1.frequency.setValueAtTime(880, now);
      osc1.frequency.setValueAtTime(1320, now + 0.08);

      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

      osc1.connect(gain);
      gain.connect(this.ctx.destination);

      osc1.start(now);
      osc1.stop(now + 0.26);
    } catch {
      // ignore
    }
  }

  // Alert beep
  public playAlert() {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;

      const now = this.ctx.currentTime;
      for (let i = 0; i < 2; i++) {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'square';
        osc.frequency.setValueAtTime(950, now + i * 0.12);

        gain.gain.setValueAtTime(0.05, now + i * 0.12);
        gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.12 + 0.08);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now + i * 0.12);
        osc.stop(now + i * 0.12 + 0.09);
      }
    } catch {
      // ignore
    }
  }

  // Trash bin purge sound
  public playPurge() {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;

      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(800, now);
      osc.frequency.exponentialRampToValueAtTime(80, now + 0.4);

      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.42);
    } catch {
      // ignore
    }
  }

  // Toggle ambient reactor hum
  public toggleHum(): boolean {
    if (this.isHumming) {
      this.stopHum();
      return false;
    } else {
      this.startHum();
      return true;
    }
  }

  private startHum() {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;

      this.humOsc = this.ctx.createOscillator();
      this.humGain = this.ctx.createGain();

      this.humOsc.type = 'sine';
      this.humOsc.frequency.setValueAtTime(55, this.ctx.currentTime); // Low 55Hz reactor tone

      this.humGain.gain.setValueAtTime(0.015, this.ctx.currentTime);

      this.humOsc.connect(this.humGain);
      this.humGain.connect(this.ctx.destination);

      this.humOsc.start();
      this.isHumming = true;
    } catch {
      // ignore
    }
  }

  private stopHum() {
    try {
      if (this.humOsc) {
        this.humOsc.stop();
        this.humOsc.disconnect();
        this.humOsc = null;
      }
      this.isHumming = false;
    } catch {
      // ignore
    }
  }
}

export const sound = new SoundFX();
