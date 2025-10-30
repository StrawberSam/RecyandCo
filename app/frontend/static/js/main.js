// ============================================
// SYSTÈME DE LOGS CONDITIONNELS
// ============================================

/**
 * Configuration du mode debug
 * À passer à false en production
 */
const DEBUG = true; // ← Change en false pour pro

/**
 * Système de logs conditionnels
 * Les logs de debug ne s'affichent que si DEBUG = true
 * Les erreurs et warnings s'affichent toujours
 */
window.log = {
  /**
   * Log de debug (développement uniquement)
   */
  debug: (...args) => {
    if (DEBUG) {
      console.log('🔍 [DEBUG]', ...args);
    }
  },

  /**
   * Log d'information (développement uniquement)
   */
  info: (...args) => {
    if (DEBUG) {
      console.info('ℹ️ [INFO]', ...args);
    }
  },

  /**
   * Avertissement (toujours affiché)
   */
  warn: (...args) => {
    console.warn('⚠️ [WARN]', ...args);
  },

  /**
   * Erreur (toujours affiché)
   */
  error: (...args) => {
    console.error('❌ [ERROR]', ...args);
  }
};

// Pour rétrocompatibilité avec debug()
window.debug = window.log.debug;
