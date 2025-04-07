import React from 'react';
import { motion } from 'framer-motion';

interface UserMessageProps {
  text: string;
}

const UserMessage: React.FC<UserMessageProps> = ({ text }) => (
  <motion.div 
    className="message-sent bg-blue-500 dark:bg-blue-600 rounded-lg p-x3 max-w-[80%] self-end text-white"
    initial={{ x: 50, opacity: 0 }}
    animate={{ x: 0, opacity: 1 }}
    transition={{ duration: 0.15 }}
  >
    <p className="text-sm">{text}</p>
  </motion.div>
);

export default UserMessage; 