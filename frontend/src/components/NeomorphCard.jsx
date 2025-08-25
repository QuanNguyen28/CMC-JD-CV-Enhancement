import { motion } from "framer-motion";
import clsx from "clsx";

export default function NeomorphCard({ className, children, as:Tag="div" }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: .35, ease: "easeOut" }}
      className={clsx("neo p-5", className)}
      as={Tag}
    >
      {children}
    </motion.div>
  );
}