import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Trash2, RefreshCw, CheckCircle2 } from 'lucide-react';
import { ThemeConfig } from '../utils/theme';
import { sound } from '../utils/audio';

interface RecycleBinWidgetProps {
  theme: ThemeConfig;
}

export const RecycleBinWidget: React.FC<RecycleBinWidgetProps> = ({ theme }) => {
  const [itemsCount, setItemsCount] = useState(14);
  const [sizeMb, setSizeMb] = useState(4.1);
  const [isPurging, setIsPurging] = useState(false);

  const handlePurge = () => {
    if (itemsCount === 0) return;
    setIsPurging(true);
    sound.playPurge();

    setTimeout(() => {
      setItemsCount(0);
      setSizeMb(0);
      setIsPurging(false);
      sound.playConfirm();
    }, 600);
  };

  const handleRestore = () => {
    sound.playClick();
    setItemsCount(14);
    setSizeMb(4.1);
  };

  return (
    <div className="relative p-2 rounded border border-cyan-500/40 bg-[#040c16]/80 backdrop-blur-sm w-full max-w-[210px] font-mono text-[9px]">
      {/* Corner Bracket Accents */}
      <div className="absolute -top-[1px] -left-[1px] w-2 h-2 border-t-2 border-l-2 border-cyan-400" />
      <div className="absolute -top-[1px] -right-[1px] w-2 h-2 border-t-2 border-r-2 border-cyan-400" />
      <div className="absolute -bottom-[1px] -left-[1px] w-2 h-2 border-b-2 border-l-2 border-cyan-400" />
      <div className="absolute -bottom-[1px] -right-[1px] w-2 h-2 border-b-2 border-r-2 border-cyan-400" />

      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-cyan-500/30 pb-0.5 mb-1.5">
        <span
          className="text-[10px] font-bold text-cyan-300 tracking-wider flex items-center gap-1"
          style={{ fontFamily: "'Orbitron', sans-serif" }}
        >
          RECYCLE BIN
        </span>
        <span
          className={`text-[8px] font-bold px-1 rounded ${
            itemsCount > 0
              ? 'bg-orange-950 text-orange-400 border border-orange-500/40'
              : 'bg-cyan-950 text-cyan-400 border border-cyan-500/40'
          }`}
        >
          {itemsCount > 0 ? 'FULL' : 'EMPTY'}
        </span>
      </div>

      {/* Main Content: Wireframe Trash Bin & Info Block */}
      <div className="flex items-center gap-2">
        {/* Wireframe Trash Container */}
        <div
          onClick={itemsCount > 0 ? handlePurge : handleRestore}
          title={itemsCount > 0 ? 'Click to Purge Recycle Bin' : 'Click to Restore Test Items'}
          className="relative w-12 h-12 flex items-center justify-center border border-cyan-500/50 rounded bg-black/60 cursor-pointer hover:border-cyan-300 group transition-all"
        >
          <AnimatePresence mode="wait">
            {isPurging ? (
              <motion.div
                key="purging"
                initial={{ rotate: 0 }}
                animate={{ rotate: 360 }}
                transition={{ duration: 0.6, repeat: Infinity, ease: 'linear' }}
              >
                <RefreshCw className="w-5 h-5 text-orange-400" />
              </motion.div>
            ) : itemsCount > 0 ? (
              <motion.div
                key="full"
                className="relative flex items-center justify-center text-cyan-300 group-hover:text-orange-400 transition-colors"
              >
                <Trash2 className="w-5 h-5" />
                <span className="absolute text-[8px] font-bold bottom-0.5">
                  {itemsCount}
                </span>
              </motion.div>
            ) : (
              <motion.div key="empty" className="text-cyan-500/60">
                <CheckCircle2 className="w-5 h-5 text-cyan-400" />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Glowing indicator dot */}
          <span
            className={`absolute top-1 right-1 w-1.5 h-1.5 rounded-full ${
              itemsCount > 0 ? 'bg-orange-500 animate-pulse' : 'bg-cyan-500'
            }`}
          />
        </div>

        {/* Right Info Specification */}
        <div className="flex-1 flex flex-col justify-between border border-cyan-500/30 rounded p-1 bg-black/40 text-[8px]">
          <div className="flex justify-between text-cyan-400/80">
            <span>STATUS</span>
            <span className={itemsCount > 0 ? 'text-orange-300 font-bold' : 'text-cyan-300'}>
              {itemsCount > 0 ? 'ACTIVE' : 'PURGED'}
            </span>
          </div>
          <div className="flex justify-between text-cyan-400/80">
            <span>ITEMS</span>
            <span className="text-cyan-200 font-semibold">{itemsCount}</span>
          </div>
          <div className="flex justify-between text-cyan-400/80">
            <span>SIZE</span>
            <span className="text-cyan-200 font-semibold">{sizeMb.toFixed(1)} MB</span>
          </div>
        </div>
      </div>
    </div>
  );
};
