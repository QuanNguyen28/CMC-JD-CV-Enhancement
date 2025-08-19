// src/components/NeumorphicCard.jsx
import React from 'react'
import { motion } from 'framer-motion'

export default function NeumorphicCard({ className = '', children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`neo p-4 ${className}`}
    >
      {children}
    </motion.div>
  )
}
