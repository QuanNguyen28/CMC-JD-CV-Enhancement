import { motion } from "framer-motion";
import clsx from "clsx";

export default function NeumorphicCard({
  title,
  subtitle,
  actions,
  className = "",
  children,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={clsx("neo p-5", className)}
    >
      {(title || actions) && (
        <div className="mb-4 flex items-center justify-between">
          <div>
            {title && <h3 className="text-lg font-semibold">{title}</h3>}
            {subtitle && (
              <p className="text-sm text-muted mt-1">{subtitle}</p>
            )}
          </div>
          {actions && <div className="flex gap-2">{actions}</div>}
        </div>
      )}
      {children}
    </motion.div>
  );
}