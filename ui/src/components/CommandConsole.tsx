import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Send,
  Loader2,
  Terminal,
  AlertTriangle,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Radio,
} from 'lucide-react';
import { ThemeConfig } from '../utils/theme';
import { sound } from '../utils/audio';
import { CommandResult } from '../lib/api';
import { MIC_LABEL, MicState } from '../lib/speech';

interface CommandConsoleProps {
  theme: ThemeConfig;
  connected: boolean;
  sending: boolean;
  onSend: (command: string) => Promise<CommandResult | null>;
  // Voice
  micState: MicState;
  interim: string;
  micSupported: boolean;
  onToggleMic: () => void;
  speechEnabled: boolean;
  onToggleSpeech: () => void;
  speaking: boolean;
}

const MIC_ACTIVE: MicState[] = ['listening', 'starting'];

/**
 * Bottom-dock command console: type or speak. Spoken input is transcribed by the
 * browser's Web Speech API and sent through the same `/api/command` pipeline as
 * typed text, so voice and keyboard are exactly equivalent.
 */
export const CommandConsole: React.FC<CommandConsoleProps> = ({
  theme,
  connected,
  sending,
  onSend,
  micState,
  interim,
  micSupported,
  onToggleMic,
  speechEnabled,
  onToggleSpeech,
  speaking,
}) => {
  const [value, setValue] = useState('');
  const [reply, setReply] = useState<{ text: string; ok: boolean } | null>(null);

  const submit = async () => {
    const command = value.trim();
    if (!command || sending) return;
    sound.playClick(1500);
    setValue('');
    const result = await onSend(command);
    if (!result) {
      setReply({ text: 'CORE UNREACHABLE — IS THE PYTHON BACKEND RUNNING?', ok: false });
      sound.playAlert();
      return;
    }
    const text = result.error || result.text || 'No response.';
    setReply({ text: text.toUpperCase(), ok: result.success !== false && !result.error });
    if (result.success === false || result.error) sound.playAlert();
  };

  const micActive = MIC_ACTIVE.includes(micState);
  const micBusy = micState === 'blocked' || micState === 'error';

  return (
    <div className="flex flex-col gap-1 w-full max-w-[600px] font-mono">
      {/* Response / live dictation readout */}
      <div className="h-4 px-1 overflow-hidden">
        <AnimatePresence mode="wait">
          {interim ? (
            <motion.div
              key="interim"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-[9px] tracking-wide truncate flex items-center gap-1.5 text-orange-300/90"
            >
              <Radio className="w-2.5 h-2.5 shrink-0 text-orange-400 animate-pulse" />
              <span className="truncate">“{interim}”</span>
            </motion.div>
          ) : reply ? (
            <motion.div
              key={reply.text}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`text-[9px] tracking-wide truncate flex items-center gap-1.5 ${
                reply.ok ? 'text-cyan-300/90' : 'text-orange-400'
              }`}
            >
              {reply.ok ? (
                <Terminal className="w-2.5 h-2.5 shrink-0" style={{ color: theme.primaryHex }} />
              ) : (
                <AlertTriangle className="w-2.5 h-2.5 shrink-0 text-orange-400" />
              )}
              <span className="truncate">{reply.text}</span>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>

      <div
        className="flex items-center gap-1.5 px-2 py-1.5 rounded border bg-black/70 backdrop-blur-sm transition-colors"
        style={{
          borderColor: micActive
            ? `${theme.accentHex}99`
            : connected
              ? `${theme.primaryHex}55`
              : 'rgba(255,84,0,0.5)',
          boxShadow: micActive ? `0 0 14px ${theme.accentGlow}` : 'none',
        }}
      >
        {/* Microphone */}
        <button
          onClick={() => {
            sound.playClick(micActive ? 700 : 1400);
            onToggleMic();
          }}
          disabled={!micSupported || !connected}
          title={micSupported ? MIC_LABEL[micState] : 'Web Speech API unsupported — use Chrome'}
          className={`shrink-0 flex items-center gap-1 px-1.5 py-1 rounded border transition-all disabled:opacity-30 disabled:cursor-not-allowed ${
            micActive ? 'animate-pulse' : ''
          }`}
          style={{
            borderColor: micBusy
              ? 'rgba(255,84,0,0.8)'
              : micActive
                ? `${theme.accentHex}`
                : `${theme.primaryHex}66`,
            color: micBusy ? '#ff5400' : micActive ? theme.accentHex : theme.primaryHex,
            background: micActive ? `${theme.accentHex}1f` : 'transparent',
          }}
        >
          {micActive ? <Mic className="w-3 h-3" /> : <MicOff className="w-3 h-3" />}
        </button>

        <span
          className="hidden sm:block text-[8px] font-bold tracking-[0.14em] shrink-0 w-[86px] truncate"
          style={{ color: micActive ? theme.accentHex : `${theme.primaryHex}99` }}
        >
          {micSupported ? MIC_LABEL[micState] : 'NO MIC'}
        </span>

        <input
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') void submit();
          }}
          disabled={!connected}
          placeholder={
            connected
              ? micActive
                ? 'LISTENING… OR TYPE — “SYSTEM STATUS”, “OPEN CHROME”'
                : 'ASK JARVIS ANYTHING — OR CLICK THE MIC'
              : 'BACKEND OFFLINE — RUN: python main.py --web'
          }
          className="flex-1 bg-transparent outline-none text-[10px] text-cyan-100 placeholder:text-cyan-500/35 tracking-wider disabled:cursor-not-allowed min-w-0"
        />

        {/* Spoken replies */}
        <button
          onClick={() => {
            const next = !speechEnabled;
            sound.playClick(next ? 1500 : 800);
            onToggleSpeech();
          }}
          disabled={!connected}
          title={speaking ? 'Jarvis is speaking' : speechEnabled ? 'Spoken replies on' : 'Spoken replies off'}
          className="shrink-0 p-1 rounded border transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          style={{
            borderColor: `${theme.primaryHex}66`,
            color: speaking ? theme.accentHex : theme.primaryHex,
          }}
        >
          {speechEnabled ? (
            <Volume2 className={`w-3 h-3 ${speaking ? 'animate-pulse' : ''}`} />
          ) : (
            <VolumeX className="w-3 h-3" />
          )}
        </button>

        <button
          onClick={() => void submit()}
          disabled={!connected || sending || !value.trim()}
          className="shrink-0 flex items-center gap-1 px-2 py-1 rounded border text-[9px] font-bold tracking-widest transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-125"
          style={{
            borderColor: `${theme.primaryHex}88`,
            color: theme.primaryHex,
            background: `${theme.primaryHex}12`,
          }}
        >
          {sending ? <Loader2 className="w-2.5 h-2.5 animate-spin" /> : <Send className="w-2.5 h-2.5" />}
          SEND
        </button>
      </div>
    </div>
  );
};
