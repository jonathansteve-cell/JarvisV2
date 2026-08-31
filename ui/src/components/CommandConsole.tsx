import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Send, Loader2, Terminal, AlertTriangle } from 'lucide-react';
import { ThemeConfig } from '../utils/theme';
import { sound } from '../utils/audio';
import { CommandResult } from '../lib/api';

interface CommandConsoleProps {
  theme: ThemeConfig;
  connected: boolean;
  sending: boolean;
  onSend: (command: string) => Promise<CommandResult | null>;
}

/**
 * Bottom-dock command console. Sends natural language through the same Jarvis
 * pipeline the desktop HUD and CLI use, so anything Jarvis understands works
 * here: "system status", "open chrome then volume 40", "add task ship it".
 */
export const CommandConsole: React.FC<CommandConsoleProps> = ({
  theme,
  connected,
  sending,
  onSend,
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

  return (
    <div className="flex flex-col gap-1 w-full max-w-[560px] font-mono">
      {/* Last response readout */}
      <div className="h-4 px-1 overflow-hidden">
        <AnimatePresence mode="wait">
          {reply && (
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
          )}
        </AnimatePresence>
      </div>

      <div
        className="flex items-center gap-2 px-2.5 py-1.5 rounded border bg-black/70 backdrop-blur-sm transition-colors"
        style={{ borderColor: connected ? `${theme.primaryHex}55` : 'rgba(255,84,0,0.5)' }}
      >
        <span
          className="text-[9px] font-bold tracking-[0.2em] shrink-0"
          style={{ color: connected ? theme.primaryHex : '#ff5400' }}
        >
          {connected ? 'CMD' : 'OFFLINE'}
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
              ? 'ASK JARVIS ANYTHING — "SYSTEM STATUS", "OPEN CHROME", "ADD TASK CALL MOM"'
              : 'BACKEND OFFLINE — RUN: python main.py --web'
          }
          className="flex-1 bg-transparent outline-none text-[10px] text-cyan-100 placeholder:text-cyan-500/35 tracking-wider disabled:cursor-not-allowed min-w-0"
        />

        <button
          onClick={() => void submit()}
          disabled={!connected || sending || !value.trim()}
          className="shrink-0 flex items-center gap-1 px-2 py-0.5 rounded border text-[9px] font-bold tracking-widest transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-125"
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
