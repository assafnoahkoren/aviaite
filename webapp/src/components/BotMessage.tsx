import React from 'react';
import { motion } from 'framer-motion';

interface BotMessageProps {
  text: string;
}

const BotMessage: React.FC<BotMessageProps> = ({ text }) => (
  <motion.div 
    className="message-received bg-gray-100 dark:bg-gray-700 rounded-lg p-x3 max-w-[80%] self-start"
    initial={{ x: -50, opacity: 0 }}
    animate={{ x: 0, opacity: 1 }}
    transition={{ duration: 0.15 }}
  >
    <p className="text-sm text-gray-800 dark:text-gray-200">{text}</p>
  </motion.div>
);

export default BotMessage; 