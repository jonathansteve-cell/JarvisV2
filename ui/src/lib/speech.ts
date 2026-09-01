// Browser voice: always-on microphone dictation + spoken replies.
//
// This restores (and extends) what the retired dashboard/static/index.html did:
// continuous recognition with debounce, barge-in protection so the mic never
// hears Jarvis talk to itself, and an en-GB male voice at rate 0.92 / pitch 0.55
// to match the `dark_synthetic` Python persona.
//
// The Web Speech API is not in TypeScript's lib.dom, so the surface we use is
// declared here.

import { useCallback, useEffect, useRef, useState } from 'react';

// ---------------------------------------------------------------------------
// Minimal Web Speech API typings
// ---------------------------------------------------------------------------

interface SpeechRecognitionAlternative {
  readonly transcript: string;
  readonly confidence: number;
}

interface SpeechRecognitionResult {
  readonly isFinal: boolean;
  readonly length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionResultList {
  readonly length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionEventLike extends Event {
  readonly resultIndex: number;
  readonly results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEventLike extends Event {
  readonly error: string;
  readonly message: string;
}

interface SpeechRecognitionLike extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEventLike) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
}

type SpeechRecognitionCtor = new () => SpeechRecognitionLike;

function recognitionConstructor(): SpeechRecognitionCtor | null {
  if (typeof window === 'undefined') return null;
  const w = window as unknown as {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

export const speechRecognitionSupported = (): boolean => recognitionConstructor() !== null;
export const speechSynthesisSupported = (): boolean =>
  typeof window !== 'undefined' && 'speechSynthesis' in window;

// ---------------------------------------------------------------------------
// Dictation
// ---------------------------------------------------------------------------

export type MicState =
  | 'unsupported'
  | 'off'
  | 'starting'
  | 'listening'
  | 'blocked'
  | 'paused'
  | 'error';

export const MIC_LABEL: Record<MicState, string> = {
  unsupported: 'UNSUPPORTED — USE CHROME',
  off: 'MIC OFF',
  starting: 'STARTING…',
  listening: 'LISTENING',
  blocked: 'BLOCKED — CLICK TO RETRY',
  paused: 'STANDBY',
  error: 'MIC ERROR — CLICK TO RETRY',
};

export interface UseVoiceCommandOptions {
  /** Called with each completed, debounced utterance. */
  onCommand: (text: string) => void | Promise<void>;
  /** Recognition language. */
  lang?: string;
  /** Silence, in ms, that closes an utterance. */
  debounceMs?: number;
  /** Hard off switch — no restart attempts at all. */
  enabled?: boolean;
  /** Soft pause (e.g. Jarvis is speaking). Restarts when lifted. */
  paused?: boolean;
  /** When set, ignore utterances that do not contain one of these phrases. */
  wakeWords?: string[];
  /** Start listening automatically once the browser allows it. */
  autoStart?: boolean;
}

export interface UseVoiceCommandResult {
  micState: MicState;
  /** Live partial transcript, so the HUD captions you while you talk. */
  interim: string;
  supported: boolean;
  start: () => void;
  stop: () => void;
  toggle: () => void;
  clearInterim: () => void;
}

/** Strip a leading wake word so the caption reads like the real command. */
function stripWakeWord(text: string, wakeWords: string[]): string {
  let out = text.trim();
  for (const word of wakeWords) {
    const pattern = new RegExp(`^\\s*${word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[\\s,]*`, 'i');
    if (pattern.test(out)) {
      out = out.replace(pattern, '');
      break;
    }
  }
  return out.trim();
}

export function useVoiceCommand(options: UseVoiceCommandOptions): UseVoiceCommandResult {
  const {
    onCommand,
    lang = 'en-US',
    debounceMs = 900,
    enabled = true,
    paused = false,
    wakeWords = [],
    autoStart = false,
  } = options;

  const [micState, setMicState] = useState<MicState>(() =>
    recognitionConstructor() ? 'off' : 'unsupported'
  );
  const [interim, setInterim] = useState('');

  const supported = recognitionConstructor() !== null;

  const recognition = useRef<SpeechRecognitionLike | null>(null);
  const buffer = useRef('');
  const debounce = useRef<number | null>(null);
  const restarting = useRef<number | null>(null);
  const mounted = useRef(true);

  // Latest options without re-creating the recognition instance.
  const latest = useRef({ onCommand, debounceMs, wakeWords, paused, enabled });
  latest.current = { onCommand, debounceMs, wakeWords, paused, enabled };

  const stopRecognition = useCallback(() => {
    if (restarting.current !== null) {
      window.clearTimeout(restarting.current);
      restarting.current = null;
    }
    const instance = recognition.current;
    if (instance) {
      try {
        instance.abort();
      } catch {
        /* already stopped */
      }
    }
  }, []);

  const flush = useCallback(() => {
    const text = buffer.current.trim();
    buffer.current = '';
    setInterim('');
    if (!text) return;

    const words = latest.current.wakeWords;
    const command = words.length ? stripWakeWord(text, words) : text;
    if (!command) return;
    void latest.current.onCommand(command);
  }, []);

  const startRecognition = useCallback(() => {
    if (!supported || !latest.current.enabled || latest.current.paused) return;

    if (!recognition.current) {
      const Ctor = recognitionConstructor();
      if (!Ctor) {
        setMicState('unsupported');
        return;
      }
      const instance = new Ctor();
      instance.lang = lang;
      instance.continuous = true;
      instance.interimResults = true;
      instance.maxAlternatives = 1;

      instance.onresult = (event) => {
        let finalText = '';
        let partial = '';
        for (let i = event.resultIndex; i < event.results.length; i += 1) {
          const result = event.results[i];
          if (result.isFinal) finalText += result[0].transcript;
          else partial += result[0].transcript;
        }
        if (partial) setInterim(partial.trim());

        if (finalText.trim()) {
          buffer.current = `${buffer.current} ${finalText}`.trim();
          if (debounce.current !== null) window.clearTimeout(debounce.current);
          debounce.current = window.setTimeout(() => {
            debounce.current = null;
            flush();
          }, latest.current.debounceMs);
        }
      };

      // Continuous recognition ends on its own; restart unless we were told to stop.
      instance.onend = () => {
        if (!mounted.current) return;
        const { enabled: on, paused: hold } = latest.current;
        if (!on || hold) {
          setMicState(hold ? 'paused' : 'off');
          return;
        }
        setMicState('starting');
        restarting.current = window.setTimeout(() => {
          restarting.current = null;
          try {
            instance.start();
            if (mounted.current) setMicState('listening');
          } catch {
            if (mounted.current) setMicState('error');
          }
        }, 300);
      };

      instance.onerror = (event) => {
        if (!mounted.current) return;
        // 'no-speech' and 'aborted' are routine in continuous mode.
        if (event.error === 'no-speech' || event.error === 'aborted') return;
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          setMicState('blocked');
          return;
        }
        setMicState('error');
      };

      recognition.current = instance;
    }

    try {
      recognition.current.start();
      setMicState('listening');
    } catch {
      // Thrown when already started — harmless.
      setMicState((state) => (state === 'listening' ? state : 'listening'));
    }
  }, [flush, lang, supported]);

  const stop = useCallback(() => {
    buffer.current = '';
    if (debounce.current !== null) {
      window.clearTimeout(debounce.current);
      debounce.current = null;
    }
    setInterim('');
    stopRecognition();
    setMicState('off');
  }, [stopRecognition]);

  const start = useCallback(() => {
    if (!supported) {
      setMicState('unsupported');
      return;
    }
    setMicState('starting');
    startRecognition();
  }, [startRecognition, supported]);

  const toggle = useCallback(() => {
    if (micState === 'listening' || micState === 'starting') stop();
    else start();
  }, [micState, start, stop]);

  // Auto-start once, after a tick so the browser has a user gesture to attach to.
  useEffect(() => {
    if (!autoStart || !supported) return;
    const timer = window.setTimeout(() => {
      if (latest.current.enabled && !latest.current.paused) startRecognition();
    }, 600);
    return () => window.clearTimeout(timer);
  }, [autoStart, startRecognition, supported]);

  // Pause / resume when `paused` flips (barge-in protection, sleep mode).
  useEffect(() => {
    if (!supported || !enabled) return;
    if (paused) {
      buffer.current = '';
      setInterim('');
      stopRecognition();
      setMicState('paused');
    } else if (micState === 'paused' || micState === 'off') {
      startRecognition();
    }
    // `micState` intentionally omitted: reacting to it would loop with onend.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paused, enabled, supported, startRecognition, stopRecognition]);

  // Hard off switch tears everything down.
  useEffect(() => {
    if (!enabled) stop();
  }, [enabled, stop]);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      if (debounce.current !== null) window.clearTimeout(debounce.current);
      if (restarting.current !== null) window.clearTimeout(restarting.current);
      const instance = recognition.current;
      if (instance) {
        try {
          instance.abort();
        } catch {
          /* ignore */
        }
      }
      recognition.current = null;
    };
  }, []);

  return {
    micState,
    interim,
    supported,
    start,
    stop,
    toggle,
    clearInterim: () => setInterim(''),
  };
}

// ---------------------------------------------------------------------------
// Spoken replies
// ---------------------------------------------------------------------------

/** Matches the Python `dark_synthetic` persona: slow, low, commanding. */
export const JARVIS_VOICE = { rate: 0.92, pitch: 0.55, volume: 1 } as const;

export interface UseSpeechOptions {
  enabled?: boolean;
  lang?: string;
}

export interface UseSpeechResult {
  speak: (text: string) => void;
  cancel: () => void;
  speaking: boolean;
  supported: boolean;
  enabled: boolean;
  setEnabled: (value: boolean) => void;
  voiceName: string | null;
}

export function useSpeech(options: UseSpeechOptions = {}): UseSpeechResult {
  const { lang = 'en-GB' } = options;
  const [enabled, setEnabled] = useState(options.enabled ?? true);
  const [speaking, setSpeaking] = useState(false);
  const [voiceName, setVoiceName] = useState<string | null>(null);

  const supported = speechSynthesisSupported();
  const enabledRef = useRef(enabled);
  enabledRef.current = enabled;

  // Voices load asynchronously in Chrome; re-resolve when they arrive.
  const pickVoice = useCallback((): SpeechSynthesisVoice | null => {
    if (!supported) return null;
    const voices = window.speechSynthesis.getVoices();
    if (!voices.length) return null;
    const choice =
      voices.find(
        (voice) =>
          /en-gb/i.test(voice.lang) && /male|david|george|guy|daniel/i.test(voice.name)
      ) ??
      voices.find((voice) => /en-gb/i.test(voice.lang)) ??
      voices.find((voice) => /^en/i.test(voice.lang)) ??
      voices[0];
    return choice ?? null;
  }, [supported]);

  useEffect(() => {
    if (!supported) return;
    const update = () => setVoiceName(pickVoice()?.name ?? null);
    update();
    window.speechSynthesis.addEventListener('voiceschanged', update);
    return () => window.speechSynthesis.removeEventListener('voiceschanged', update);
  }, [pickVoice, supported]);

  const cancel = useCallback(() => {
    if (!supported) return;
    window.speechSynthesis.cancel();
    setSpeaking(false);
  }, [supported]);

  const speak = useCallback(
    (text: string) => {
      if (!supported || !enabledRef.current) return;
      const clean = text.trim();
      if (!clean) return;

      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(clean);
      const voice = pickVoice();
      if (voice) utterance.voice = voice;
      utterance.lang = voice?.lang ?? lang;
      utterance.rate = JARVIS_VOICE.rate;
      utterance.pitch = JARVIS_VOICE.pitch;
      utterance.volume = JARVIS_VOICE.volume;
      utterance.onstart = () => setSpeaking(true);
      utterance.onend = () => setSpeaking(false);
      utterance.onerror = () => setSpeaking(false);

      setSpeaking(true);
      window.speechSynthesis.speak(utterance);
    },
    [lang, pickVoice, supported]
  );

  // Muting mid-sentence should stop immediately, not just suppress the next line.
  useEffect(() => {
    if (!enabled && speaking) cancel();
  }, [cancel, enabled, speaking]);

  useEffect(() => () => {
    if (supported) window.speechSynthesis.cancel();
  }, [supported]);

  return { speak, cancel, speaking, supported, enabled, setEnabled, voiceName };
}
