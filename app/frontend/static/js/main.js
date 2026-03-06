// ============================================
// SYSTÈME DE LOGS CONDITIONNELS
// ============================================

/**
 * À passer à false en production
 */
const DEBUG = false;

/**
 * Système de logs conditionnels
 * Les logs de debug ne s'affichent que si DEBUG = true
 * Les erreurs et warnings s'affichent toujours
 */
window.log = {

  debug: (...args) => {
    if (DEBUG) {
      console.log('🔍 [DEBUG]', ...args);
    }
  },

  info: (...args) => {
    if (DEBUG) {
      console.info('ℹ️ [INFO]', ...args);
    }
  },

  warn: (...args) => {
    console.warn('⚠️ [WARN]', ...args);
  },

  error: (...args) => {
    console.error('❌ [ERROR]', ...args);
  }
};

// Pour rétrocompatibilité avec debug()
window.debug = window.log.debug;
